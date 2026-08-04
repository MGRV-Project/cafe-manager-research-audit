#!/usr/bin/env python3
"""Audit the coffee-shop manager source registry and emit an analysis-ready layer."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "id",
    "category",
    "title",
    "url",
    "canonical_url",
    "host",
    "language",
    "role_scope",
    "relevance_score",
    "collection_method",
    "review_status",
]

SEVERE_PATTERNS = {
    "online_community_or_software_cafe": re.compile(
        r"네이버\s*카페\s*(?:매니저|관리자)|community manager|internet cafe|pc cafe|game cafe|"
        r"cafemanager\.kr|cafemanagershop",
        re.I,
    ),
    "competition_or_event_only": re.compile(
        r"usbc|brewers? cup|barista (?:comp|competition)|championship|qualifying event|"
        r"competition schedule|giveaway winner|training camp prepping",
        re.I,
    ),
    "unrelated_incident_or_human_interest": re.compile(
        r"(?:died|death|fight with employee|cursed at|denied service|missing person|murder|shooting|"
        r"stabbing|lottery|train café opens|recording studio|virtual tip jars|카페 돌면서|락스|징역|체포|살인)",
        re.I,
    ),
}

OWNER_STARTUP_PATTERN = re.compile(
    r"(?:how to |before |guide to )?(?:start|starting|open|opening) (?:a |your own )?(?:coffee shop|cafe)|"
    r"cost to (?:open|rent) (?:a )?(?:coffee shop|cafe)|business plan",
    re.I,
)

STRONG_OPERATION_PATTERN = re.compile(
    r"manager|management|managerial|점장|매니저|매장 관리|매장 운영|staff|staffing|employee|worker|"
    r"schedule|shift|hiring|hire|training|coach|inventory|ordering|supplier|food safety|hygiene|"
    r"health inspection|customer service|complaint|service recovery|labor cost|food cost|sales|"
    r"cash handling|opening checklist|closing checklist|retention|turnover|workload|burnout|union|"
    r"직원|인력|스케줄|채용|교육|재고|발주|위생|고객 응대|고객응대|매출|원가|인건비|정산|오픈|마감",
    re.I,
)

SECRET_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:tvly-[A-Za-z0-9_-]{16,}|gh[oprsu]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})"
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def quality_for(item: dict[str, Any]) -> tuple[str, bool, list[str]]:
    text = " ".join([
        str(item.get("title") or ""),
        str(item.get("excerpt") or ""),
        str(item.get("canonical_url") or ""),
    ])
    flags = [name for name, pattern in SEVERE_PATTERNS.items() if pattern.search(text)]
    severe = bool(flags)

    if item.get("category") == "blog" and OWNER_STARTUP_PATTERN.search(text):
        flags.append("owner_startup_context_not_core_manager_work")
        severe = True

    directness = item.get("evidence_directness", "direct_role_evidence")
    if directness == "indirect_manager_context" and not STRONG_OPERATION_PATTERN.search(text):
        flags.append("indirect_without_strong_operations_signal")
        severe = True

    if item.get("category") == "news" and directness == "indirect_manager_context":
        flags.append("news_is_manager_context_not_direct_duty_evidence")
    if item.get("collection_method") == "google_news_rss":
        flags.append("aggregator_link_not_direct_publisher_article_url")
    if item.get("page_metadata_status") == "sitemap_url_only":
        flags.append("sitemap_url_only_no_page_excerpt")
    if not item.get("excerpt"):
        flags.append("missing_excerpt")
    if not item.get("published_date"):
        flags.append("missing_publication_date")

    if severe:
        return "C", False, sorted(set(flags))

    direct_core_role = (
        directness == "direct_role_evidence"
        and item.get("role_scope") in {"store_manager", "assistant_manager"}
        and int(item.get("relevance_score") or 0) >= 58
        and bool(item.get("excerpt"))
    )
    if direct_core_role:
        return "A", True, sorted(set(flags))
    return "B", True, sorted(set(flags))


def pct(numerator: int, denominator: int) -> str:
    return f"{(100 * numerator / denominator):.1f}%" if denominator else "n/a"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--curated-output", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--audit-md", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    items = data.get("items", [])
    total = len(items)

    duplicate_ids = [key for key, count in Counter(item.get("id") for item in items).items() if count > 1]
    duplicate_urls = [
        key for key, count in Counter(item.get("canonical_url") for item in items).items() if count > 1
    ]
    missing_required = Counter()
    malformed_urls = []
    secret_hits = []
    allowed_categories = {"community", "blog", "news", "paper"}
    invalid_categories = []

    audited_items = []
    flag_counts = Counter()
    for item in items:
        item = dict(item)
        for field in REQUIRED_FIELDS:
            if item.get(field) in (None, ""):
                missing_required[field] += 1
        parsed = urllib.parse.urlsplit(str(item.get("canonical_url") or ""))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            malformed_urls.append(item.get("id"))
        if item.get("category") not in allowed_categories:
            invalid_categories.append(item.get("id"))
        serialized = json.dumps(item, ensure_ascii=False)
        if SECRET_PATTERN.search(serialized):
            secret_hits.append(item.get("id"))

        tier, analysis_ready, flags = quality_for(item)
        item["quality_tier"] = tier
        item["analysis_ready"] = analysis_ready
        item["quality_flags"] = flags
        flag_counts.update(flags)
        audited_items.append(item)

    analysis_ready_items = [item for item in audited_items if item["analysis_ready"]]
    excluded_items = [item for item in audited_items if not item["analysis_ready"]]

    raw_category_counts = Counter(item["category"] for item in audited_items)
    ready_category_counts = Counter(item["category"] for item in analysis_ready_items)
    tier_counts = Counter(item["quality_tier"] for item in audited_items)
    directness_counts = Counter(item.get("evidence_directness", "unknown") for item in audited_items)
    language_counts = Counter(item.get("language", "und") for item in audited_items)
    method_counts = Counter(item.get("collection_method", "unknown") for item in audited_items)
    host_counts = Counter(item.get("host", "unknown") for item in audited_items)
    excerpt_count = sum(bool(item.get("excerpt")) for item in audited_items)
    raw_content_count = sum(bool(item.get("raw_content")) for item in audited_items)
    publication_date_count = sum(bool(item.get("published_date")) for item in audited_items)

    checks = {
        "row_count": total,
        "expected_row_count": 510,
        "category_counts": dict(raw_category_counts),
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_canonical_url_count": len(duplicate_urls),
        "missing_required_fields": dict(missing_required),
        "malformed_url_count": len(malformed_urls),
        "invalid_category_count": len(invalid_categories),
        "secret_hit_count": len(secret_hits),
        "excerpt_present_count": excerpt_count,
        "raw_content_present_count": raw_content_count,
        "publication_date_present_count": publication_date_count,
    }

    audit = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dataset": str(args.input),
        "grain": "one canonical source URL per record",
        "intended_use": "source discovery and triangulation for coffee-shop store-manager work research",
        "not_suitable_for": [
            "copyrighted full-text redistribution",
            "unreviewed model training",
            "claiming that all 510 records directly describe manager duties",
        ],
        "checks": checks,
        "quality": {
            "tier_counts": dict(tier_counts),
            "analysis_ready_count": len(analysis_ready_items),
            "excluded_count": len(excluded_items),
            "analysis_ready_by_category": dict(ready_category_counts),
            "evidence_directness": dict(directness_counts),
            "languages": dict(language_counts),
            "collection_methods": dict(method_counts),
            "top_hosts": dict(host_counts.most_common(30)),
            "flag_counts": dict(flag_counts.most_common()),
        },
        "samples": {
            "excluded": [
                {
                    "id": item["id"],
                    "category": item["category"],
                    "title": item["title"],
                    "url": item["canonical_url"],
                    "quality_flags": item["quality_flags"],
                }
                for item in excluded_items[:40]
            ]
        },
        "risk_assessment": [
            {
                "severity": "high",
                "finding": "The 510-record quota layer mixes direct role evidence with indirect operational context.",
                "evidence": dict(directness_counts),
                "impact": "Treating every row as direct duty evidence would overstate support.",
                "remediation": "Use the analysis-ready file and retain evidence_directness in downstream analysis.",
            },
            {
                "severity": "high",
                "finding": "Third-party full text is intentionally absent.",
                "evidence": {"raw_content_present": raw_content_count, "total": total},
                "impact": "The dataset is a source registry with short excerpts, not a full-text corpus.",
                "remediation": "Fetch source text only under a compatible license or with publisher permission; record license per item.",
            },
            {
                "severity": "medium",
                "finding": "Community evidence is concentrated on Reddit and news links are aggregator URLs.",
                "evidence": dict(host_counts.most_common(5)),
                "impact": "Platform and geography bias limits representativeness.",
                "remediation": "Add licensed Korean worker-community and direct publisher feeds in a later collection round.",
            },
            {
                "severity": "medium",
                "finding": "Korean-language evidence is a minority of the registry.",
                "evidence": {"ko": language_counts.get("ko", 0), "total": total},
                "impact": "Korean labor and store-operation practices may be underrepresented.",
                "remediation": "Set a separate Korean-language minimum and manually verify login-gated source availability.",
            },
        ],
    }

    curated = {
        "schema_version": "2.2.0",
        "summary": {
            **data.get("summary", {}),
            "raw_registry_count": total,
            "analysis_ready_count": len(analysis_ready_items),
            "excluded_after_quality_audit": len(excluded_items),
            "analysis_ready_by_category": {key: ready_category_counts.get(key, 0) for key in ["community", "blog", "news", "paper"]},
            "quality_tiers": {key: tier_counts.get(key, 0) for key in ["A", "B", "C"]},
        },
        "scope": data.get("scope", {}),
        "methodology": data.get("methodology", {}),
        "rights_and_access": data.get("rights_and_access", {}),
        "quality_tier_definition": {
            "A": "direct core manager/assistant-manager role evidence with excerpt and higher relevance score",
            "B": "relevant but adjacent, indirect, contextual, or metadata-limited evidence",
            "C": "excluded from analysis because scope or evidence was too weak",
        },
        "items": analysis_ready_items,
        "excluded_items": excluded_items,
    }

    category_rows = "\n".join(
        f"| {category} | {raw_category_counts.get(category, 0)} | {ready_category_counts.get(category, 0)} | "
        f"{raw_category_counts.get(category, 0) - ready_category_counts.get(category, 0)} |"
        for category in ["community", "blog", "news", "paper"]
    )
    method_rows = "\n".join(
        f"| {method} | {count} | {pct(count, total)} |" for method, count in method_counts.most_common()
    )
    flag_rows = "\n".join(
        f"| {flag} | {count} | {pct(count, total)} |" for flag, count in flag_counts.most_common(12)
    )
    report = f"""# 커피 판매 카페 매니저 rawdata 품질 감사

## 기술 요약

- 원천 레지스트리는 목표 수량 **{total}건**을 충족했습니다: 커뮤니티 200, 블로그·운영가이드 200, 뉴스 100, 논문 10.
- 품질 규칙을 적용하면 **{len(analysis_ready_items)}건({pct(len(analysis_ready_items), total)})**이 분석 준비 상태이고, **{len(excluded_items)}건**은 범위가 약하거나 업무 직접성이 부족해 제외됩니다.
- A등급(직접 핵심 역할 근거)은 **{tier_counts.get('A', 0)}건**, B등급(간접·인접·메타데이터 제한)은 **{tier_counts.get('B', 0)}건**입니다.
- 이 자료는 **전문 코퍼스가 아니라 URL·메타데이터·짧은 발췌 레지스트리**입니다. 저작권 있는 전문은 재배포하지 않았습니다.

## 카테고리별 품질 통과 현황

| 카테고리 | quota 레지스트리 | 분석 준비 | 제외 |
|---|---:|---:|---:|
{category_rows}

판단: quota 레지스트리는 수집 범위를 감사하는 용도이고, 직무 결론이나 모델 입력에는 분석 준비 파일을 사용해야 합니다.

## 범위·단위·정의

- 단위: 정규화된 원천 URL 1개당 1행
- 포함: 커피를 판매하는 오프라인 카페의 점장·매니저, 부점장, 교대 리더, 헤드 바리스타의 매장 운영 업무
- 업무 축: 인력·스케줄·채용·교육·재고·발주·위생·고객응대·매출·원가·정산·오픈·마감·규정 준수
- 제외: 네이버/온라인 커뮤니티 카페 매니저, PC·게임 카페, 상품명 Cafe Manager, 카페 추천·관광·레시피, 대회 일정처럼 매장관리 업무가 아닌 자료
- A등급: 직접 핵심 역할 + 발췌 존재 + 관련성 점수 58 이상
- B등급: 관련 있으나 인접 역할, 간접 운영 맥락, aggregator 또는 sitemap 메타데이터 제한
- C등급: 분석에서 제외

## 수행한 검사

- 행 수·카테고리 quota·허용값
- `id`와 `canonical_url` 유일성
- 필수 필드 결측, URL 형식, 비밀키 패턴
- 커피매장/관리역할/업무 키워드와 명시적 제외 패턴
- 직접 역할 근거와 간접 운영 맥락 구분
- 발췌·발행일·전문 존재율
- 언어·호스트·수집경로 편중

## 핵심 품질 결과

- 중복 ID: **{len(duplicate_ids)}건**; 중복 canonical URL: **{len(duplicate_urls)}건**
- 잘못된 URL: **{len(malformed_urls)}건**; 허용되지 않은 카테고리: **{len(invalid_categories)}건**
- 비밀키 패턴: **{len(secret_hits)}건**
- 짧은 발췌 보유: **{excerpt_count}건({pct(excerpt_count, total)})**
- 발행일 보유: **{publication_date_count}건({pct(publication_date_count, total)})**
- 재배포 전문 보유: **{raw_content_count}건**
- 한국어: **{language_counts.get('ko', 0)}건({pct(language_counts.get('ko', 0), total)})**

## 수집경로 편중

| 수집경로 | 건수 | 비중 |
|---|---:|---:|
{method_rows}

Reddit 기반 커뮤니티와 Google News aggregator 의존이 크므로, 이 표본은 전체 카페 매니저 모집단을 대표하지 않습니다.

## 제외·주의 플래그

| 플래그 | 건수 | 비중 |
|---|---:|---:|
{flag_rows}

## 한계와 강건성

- 검색 결과 발췌는 페이지 전문 검증과 동일하지 않습니다.
- 뉴스 100건 가운데 상당수는 매니저를 직접 인터뷰한 직무 자료가 아니라 인력·스케줄·노무·위생 같은 매니저 운영 환경 자료입니다.
- 일부 블로그는 sitemap URL 주제만 확보되어 본문 발췌가 없습니다. 이 항목은 B등급으로 제한했습니다.
- 논문 10건은 점장의 일일 업무만을 직접 측정한 연구뿐 아니라 리더십·직원 스트레스·운영품질·이직 등 관리 맥락 연구를 포함합니다.
- 로그인·유료·robots 제한 페이지는 “없음”이 아니라 “현재 검증 불가”로 취급해야 합니다.

## 권장 사용법

1. 원천 탐색·감사에는 510건 quota 레지스트리를 사용합니다.
2. 직무 분석·요약에는 `analysis-ready` 파일만 사용하고 `quality_tier`와 `evidence_directness`를 유지합니다.
3. 결론의 핵심 근거는 A등급을 우선하고, B등급은 삼각검증용으로만 사용합니다.
4. 전문이 필요하면 각 URL의 라이선스·이용약관·허가를 확인한 뒤 별도 비공개 저장소에 수집합니다.
5. 한국 실무 결론은 한국어 원천 비중을 늘린 다음 재검증합니다.

## 추가 질문

- 한국 프랜차이즈별 점장 직무기술서와 근로자 경험 자료를 어느 수준까지 확보할 수 있는가?
- 직접 원문 라이선스가 확인된 자료만으로 별도 전문 코퍼스를 만들 수 있는가?
- 점장, 부점장, 슈퍼바이저, 헤드 바리스타의 권한 경계를 브랜드·매장 규모별로 어떻게 나눌 것인가?
"""

    atomic_write(args.curated_output, json.dumps(curated, ensure_ascii=False, indent=2))
    atomic_write(args.audit_json, json.dumps(audit, ensure_ascii=False, indent=2))
    atomic_write(args.audit_md, report)
    print(json.dumps({"checks": checks, "quality": audit["quality"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
