#!/usr/bin/env python3
"""Collect and filter coffee-shop manager work sources with Tavily Search.

The API key is read only from TAVILY_API_KEY and is never written to disk.
This collector intentionally stores short search-result excerpts rather than
republishing third-party full text.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


API_URL = "https://api.tavily.com/search"
TARGETS = {"community": 200, "blog": 200, "news": 100, "paper": 10}

COMMUNITY_HOSTS = {
    "reddit.com",
    "www.reddit.com",
    "old.reddit.com",
    "quora.com",
    "www.quora.com",
    "a-ha.io",
    "www.a-ha.io",
    "kin.naver.com",
    "m.kin.naver.com",
    "teamblind.com",
    "www.teamblind.com",
    "clien.net",
    "www.clien.net",
    "dcinside.com",
    "gall.dcinside.com",
    "theqoo.net",
    "www.theqoo.net",
    "glassdoor.com",
    "www.glassdoor.com",
    "indeed.com",
    "www.indeed.com",
    "workplace.stackexchange.com",
}

ACADEMIC_HINTS = {
    "doi.org",
    "sciencedirect.com",
    "link.springer.com",
    "emerald.com",
    "tandfonline.com",
    "journals.sagepub.com",
    "onlinelibrary.wiley.com",
    "mdpi.com",
    "frontiersin.org",
    "researchgate.net",
    "semanticscholar.org",
    "pubmed.ncbi.nlm.nih.gov",
    "kci.go.kr",
    "kiss.kstudy.com",
    "dbpia.co.kr",
    "riss.kr",
    "repository.hanyang.ac.kr",
    "oak.chosun.ac.kr",
    "scholarworks.bwise.kr",
}

BLOG_HOST_HINTS = {
    "blog.naver.com",
    "m.blog.naver.com",
    "brunch.co.kr",
    "tistory.com",
    "medium.com",
    "substack.com",
    "wordpress.com",
    "blogspot.com",
}

COFFEE_TERMS = [
    "coffee shop",
    "coffeehouse",
    "coffee house",
    "coffee store",
    "coffee chain",
    "cafe",
    "café",
    "barista",
    "커피전문점",
    "커피 매장",
    "커피숍",
    "카페",
    "스타벅스",
    "이디야",
    "메가커피",
    "투썸",
    "할리스",
    "컴포즈커피",
    "빽다방",
    "starbucks",
    "costa coffee",
    "pret a manger",
    "dunkin",
    "tim hortons",
    "blue bottle coffee",
]

ROLE_TERMS = [
    "coffee shop manager",
    "cafe manager",
    "café manager",
    "store manager",
    "shop manager",
    "general manager",
    "assistant manager",
    "shift supervisor",
    "shift manager",
    "shift lead",
    "head barista",
    "operations manager",
    "managerial",
    "management",
    "coffee shop management",
    "cafe management",
    "café management",
    "점장",
    "매니저",
    "매장 관리자",
    "매장관리자",
    "부점장",
    "슈퍼바이저",
    "관리 책임자",
    "매장 관리",
    "매장 운영",
]

WORK_TERMS = [
    "duties",
    "responsibilities",
    "job description",
    "workload",
    "day in the life",
    "operations",
    "staffing",
    "scheduling",
    "schedule",
    "hiring",
    "training",
    "inventory",
    "ordering",
    "food safety",
    "health inspection",
    "customer service",
    "labor cost",
    "sales target",
    "cash handling",
    "opening checklist",
    "closing checklist",
    "performance review",
    "profit and loss",
    "salary",
    "wage",
    "pay",
    "hours",
    "burnout",
    "turnover",
    "labor",
    "union",
    "promotion",
    "promoted",
    "food waste",
    "job satisfaction",
    "job stress",
    "emotional labor",
    "employee performance",
    "turnover intention",
    "service quality",
    "업무",
    "직무",
    "역할",
    "책임",
    "근무",
    "운영",
    "직원 관리",
    "인력 관리",
    "스케줄",
    "채용",
    "교육",
    "재고",
    "발주",
    "위생",
    "고객 응대",
    "고객응대",
    "매출",
    "정산",
    "원가",
    "마감",
    "오픈",
]

EXCLUDE_TERMS = [
    "네이버 카페 매니저",
    "카페 매니저 위임",
    "카페매니저 쇼핑몰",
    "cafemanager.kr",
    "cafemanagershop",
    "community manager",
    "internet cafe manager",
    "pc cafe manager",
    "cat cafe manager",
    "게임 카페",
    "game cafe",
    "coffee shop recommendations",
    "best cafes in",
    "cafe recommendation",
    "카페 추천",
    "카페 맛집",
    "커피 종류",
    "레시피",
]

WORK_TAGS = {
    "floor_and_beverage": ["barista", "espresso", "beverage", "drink", "음료", "커피 제조", "바리스타", "매장 근무"],
    "staffing_and_leadership": ["staff", "employee", "team", "leadership", "hire", "hiring", "직원", "인력", "채용", "리더십", "팀"],
    "scheduling": ["schedule", "shift", "rota", "스케줄", "근무표", "교대", "시프트"],
    "training_and_coaching": ["train", "training", "coach", "onboarding", "교육", "훈련", "코칭", "온보딩"],
    "inventory_and_ordering": ["inventory", "stock", "ordering", "supplier", "재고", "발주", "거래처", "납품"],
    "food_safety_and_cleanliness": ["food safety", "hygiene", "clean", "health inspection", "위생", "청소", "식품 안전", "보건"],
    "customer_service_and_recovery": ["customer", "complaint", "service recovery", "guest", "고객", "클레임", "민원", "응대"],
    "sales_cost_and_cash": ["sales", "revenue", "labor cost", "food cost", "cash", "budget", "매출", "원가", "인건비", "정산", "현금", "예산"],
    "opening_closing_and_facility": ["opening", "closing", "maintenance", "equipment", "오픈", "마감", "시설", "장비", "기기"],
    "compliance_and_reporting": ["compliance", "policy", "report", "audit", "규정", "보고", "점검", "감사"],
}


QUERIES: dict[str, list[str]] = {
    "community": [
        "site:reddit.com/r/barista coffee shop manager duties responsibilities",
        "site:reddit.com/r/barista cafe manager workload staffing scheduling",
        "site:reddit.com/r/barista store manager inventory ordering training",
        "site:reddit.com/r/barista new coffee shop manager advice",
        "site:reddit.com/r/barista assistant manager shift supervisor responsibilities",
        "site:reddit.com/r/barista head barista manager conflict staff",
        "site:reddit.com/r/barista coffee shop manager salary hours workload",
        "site:reddit.com/r/barista cafe manager hiring firing performance",
        "site:reddit.com/r/barista manager opening closing checklist",
        "site:reddit.com/r/barista manager customer complaints operations",
        "site:reddit.com/r/Coffee coffee shop manager responsibilities staff",
        "site:reddit.com/r/Coffee cafe manager operations inventory",
        "site:reddit.com/r/CafeOwners coffee shop manager hiring duties",
        "site:reddit.com/r/CafeOwners manager scheduling labor cost inventory",
        "site:reddit.com/r/smallbusiness coffee shop manager responsibilities",
        "site:reddit.com coffee shop general manager day to day",
        "site:reddit.com coffee shop shift supervisor workload",
        "site:reddit.com Starbucks store manager workload scheduling",
        "site:reddit.com Starbucks shift supervisor responsibilities",
        "site:reddit.com cafe manager burnout staffing",
        "site:quora.com coffee shop manager duties",
        "site:quora.com cafe manager responsibilities employees inventory",
        "site:a-ha.io 카페 점장 업무 커피 매장",
        "site:a-ha.io 카페 매니저 업무 급여 직원관리",
        "site:kin.naver.com 카페 점장 업무 커피전문점",
        "site:kin.naver.com 카페 매니저 업무 직원 스케줄",
        "site:kin.naver.com 커피숍 점장 직무 재고 발주",
        "site:teamblind.com 스타벅스 점장 업무 매장 운영",
        "site:teamblind.com 커피전문점 매니저 직원 관리",
        "site:clien.net 카페 점장 업무 커피 매장",
        "카페 점장 업무 경험담 커피전문점",
        "카페 매니저 현실 직원관리 재고 발주",
        "커피전문점 점장 스케줄 위생 매출 관리 경험",
        "카페 매니저 하루 일과 매장 운영 후기",
        "스타벅스 점장 근무 업무 경험담",
    ],
    "blog": [
        "coffee shop manager duties responsibilities blog",
        "cafe manager job description daily operations",
        "day in the life coffee shop manager blog",
        "how to manage a coffee shop staff scheduling inventory",
        "coffee shop manager opening closing checklist",
        "coffee shop manager KPI labor cost food cost sales",
        "coffee shop manager staff training performance review",
        "coffee shop manager inventory ordering suppliers",
        "coffee shop manager customer complaints service recovery",
        "coffee shop manager food safety health inspection",
        "coffee shop general manager hiring job description",
        "coffee shop assistant manager responsibilities",
        "coffee shop shift supervisor duties responsibilities",
        "head barista duties team training inventory",
        "specialty coffee shop manager operations guide",
        "independent cafe manager staffing guide",
        "coffee chain store manager operations responsibilities",
        "site:perfectdailygrind.com coffee shop manager",
        "site:lightspeedhq.com blog coffee shop management staff inventory",
        "site:7shifts.com blog coffee shop manager scheduling",
        "site:toasttab.com blog coffee shop manager operations",
        "site:squareup.com coffee shop management staff inventory",
        "site:homebase.com coffee shop manager scheduling staff",
        "site:workstream.us coffee shop manager duties",
        "site:deputy.com coffee shop manager scheduling",
        "site:pos.toasttab.com coffee shop manager job description",
        "site:indeed.com hire coffee shop manager job description",
        "site:workable.com cafe manager job description",
        "site:betterteam.com cafe manager job description",
        "site:resources.workable.com cafe manager job description",
        "site:blog.naver.com 카페 매니저 업무 커피 매장",
        "site:m.blog.naver.com 카페 점장 업무 직원 재고",
        "site:tistory.com 카페 매니저 업무 커피전문점",
        "site:brunch.co.kr 카페 점장 경험 업무",
        "카페 점장 직무기술서 커피전문점",
        "카페 매니저 하루 일과 직원 스케줄 발주",
        "커피전문점 매장관리 노하우 점장",
        "카페 오픈 마감 체크리스트 점장",
        "카페 재고 발주 원가 매출 관리 점장",
        "카페 직원 교육 고객응대 위생 점장",
        "스타벅스 매장 점장 직무 역할",
        "이디야 점장 업무 매장 운영",
        "투썸플레이스 점장 업무 매장관리",
        "메가커피 점장 업무 직원 발주",
    ],
    "news": [
        "coffee shop manager staffing workload news",
        "coffee shop store manager labor shortage news",
        "coffee shop manager wages overtime news",
        "cafe manager scheduling labor law news",
        "coffee chain store manager operations news",
        "coffee shop manager training food safety news",
        "coffee shop manager customer service incident news",
        "coffee shop manager inventory supply chain news",
        "Starbucks store manager workload staffing news",
        "Starbucks store manager scheduling news",
        "Starbucks store managers union workload",
        "Starbucks shift supervisor responsibilities staffing news",
        "Costa Coffee store manager staffing news",
        "Pret cafe manager staffing operations news",
        "independent coffee shop manager labor costs news",
        "coffee shop manager burnout employee turnover news",
        "coffee shop management minimum wage labor cost news",
        "cafe operations manager health inspection news",
        "coffee shop manager hiring crisis news",
        "coffee shop manager employee retention news",
        "커피전문점 점장 업무 인력난 뉴스",
        "카페 매니저 노동시간 업무 뉴스",
        "카페 점장 직원관리 사건 뉴스",
        "스타벅스 점장 업무 인력 운영 기사",
        "스타벅스 점장 노동 스케줄 기사",
        "커피전문점 매장 관리자 채용 기사",
        "카페 점장 위생 관리 기사",
        "커피 매장 점장 고객 응대 기사",
        "카페 점장 인건비 매출 운영 기사",
        "이디야 점장 매장 운영 기사",
    ],
    "paper": [
        "coffee shop manager job demands employee performance study",
        "cafe manager leadership barista job satisfaction paper",
        "coffee shop employees emotional labor burnout study",
        "barista workload job stress coffee shop research",
        "coffee shop service employees turnover intention study",
        "coffee shop manager training service quality research",
        "coffee shop labor scheduling operations research",
        "cafe employee food safety management study",
        "커피전문점 종사자 감정노동 직무스트레스 논문",
        "커피전문점 점장 리더십 직무만족 논문",
        "카페 매니저 직무 역할 연구",
        "커피전문점 직원 이직의도 서비스품질 연구",
    ],
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonicalize(url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return url
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    path = path.rstrip("/") or "/"
    kept = []
    for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=False):
        if key.lower().startswith("utm_") or key.lower() in {
            "ref", "referrer", "source", "fbclid", "gclid", "trackingcode",
            "recommendtrackingcode", "rvid", "targetkeyword", "tl",
        }:
            continue
        kept.append((key, value))
    query = urllib.parse.urlencode(sorted(kept))
    return urllib.parse.urlunsplit(("https", host, path, query, ""))


def host_of(url: str) -> str:
    try:
        return (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def matches_host(host: str, candidates: set[str]) -> bool:
    return any(host == item or host.endswith("." + item) for item in candidates)


def contains_any(text: str, terms: list[str]) -> list[str]:
    lowered = text.casefold()
    return [term for term in terms if term.casefold() in lowered]


def clean_excerpt(value: str, max_words: int = 160, max_chars: int = 1100) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    words = value.split()
    if len(words) > max_words:
        value = " ".join(words[:max_words]) + " …"
    if len(value) > max_chars:
        value = value[:max_chars].rsplit(" ", 1)[0] + " …"
    return value


def detect_language(text: str) -> str:
    korean = len(re.findall(r"[가-힣]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if korean > 20 and korean >= latin * 0.2:
        return "ko"
    return "en" if latin else "und"


def infer_region(language: str, host: str, query: str) -> str:
    if language == "ko" or host.endswith(".kr") or re.search(r"[가-힣]", query):
        return "KR"
    if host.endswith(".uk") or host.endswith(".co.uk"):
        return "GB"
    if host.endswith(".au") or host.endswith(".com.au"):
        return "AU"
    if host.endswith(".ca"):
        return "CA"
    return "global_or_unspecified"


def classify(expected: str, host: str, url: str) -> str:
    if matches_host(host, COMMUNITY_HOSTS):
        return "community"
    if matches_host(host, ACADEMIC_HINTS) or "doi.org/" in url or "/doi/" in url:
        return "paper"
    if matches_host(host, BLOG_HOST_HINTS):
        return "blog"
    return expected


def role_scope(text: str) -> str:
    lowered = text.casefold()
    if any(term in lowered for term in ["shift supervisor", "shift manager", "shift lead", "슈퍼바이저"]):
        return "adjacent_shift_leadership"
    if any(term in lowered for term in ["assistant manager", "부점장"]):
        return "assistant_manager"
    if any(term in lowered for term in ["head barista"]):
        return "adjacent_head_barista"
    return "store_manager"


def assess(title: str, excerpt: str, url: str) -> tuple[bool, int, dict[str, Any]]:
    text = f"{title}\n{excerpt}\n{url}"
    coffee = contains_any(text, COFFEE_TERMS)
    roles = contains_any(text, ROLE_TERMS)
    work = contains_any(text, WORK_TERMS)
    exclusions = contains_any(text, EXCLUDE_TERMS)
    tags = [name for name, terms in WORK_TAGS.items() if contains_any(text, terms)]
    strong_title = bool(contains_any(title, COFFEE_TERMS) and contains_any(title, ROLE_TERMS))

    score = min(35, len(set(coffee)) * 12)
    score += min(35, len(set(roles)) * 14)
    score += min(25, len(set(work)) * 4)
    score += min(10, len(tags) * 2)
    score += 18 if strong_title else 0
    score -= 50 * len(exclusions)
    score = max(0, min(100, score))

    # Strict scope requires an actual coffee context, a management-role signal,
    # and at least one concrete work/operations signal. Strongly titled manager
    # pages can pass with role + coffee because the title itself defines the job.
    relevant = bool(coffee and roles and (work or strong_title) and not exclusions and score >= 45)
    return relevant, score, {
        "coffee_terms": sorted(set(coffee))[:8],
        "role_terms": sorted(set(roles))[:8],
        "work_terms": sorted(set(work))[:12],
        "work_tags": tags,
        "excluded_terms": sorted(set(exclusions)),
        "strong_title_match": strong_title,
    }


def tavily_search(api_key: str, query: str, category: str, retries: int = 3) -> dict[str, Any]:
    payload = {
        "api_key": api_key,
        "query": query,
        "topic": "news" if category == "news" else "general",
        "search_depth": "advanced",
        "max_results": 20,
        "include_answer": False,
        "include_images": False,
        "include_raw_content": False,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "cafe-manager-research-audit/1.0"},
        method="POST",
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            if attempt + 1 == retries:
                raise RuntimeError(f"Tavily request failed for {query!r}: {exc}") from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def load_cache(cache_path: Path) -> dict[str, Any]:
    if not cache_path.exists():
        return {}
    return json.loads(cache_path.read_text(encoding="utf-8"))


def save_cache(cache_path: Path, cache: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--offline-cache", action="store_true")
    parser.add_argument("--categories", default="community,blog,news,paper")
    args = parser.parse_args()

    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("TAVILY_API_KEY is required")

    selected = [item.strip() for item in args.categories.split(",") if item.strip()]
    cache = load_cache(args.cache)
    search_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    jobs: list[tuple[str, int, str, str]] = []
    for category in selected:
        for index, query in enumerate(QUERIES[category], start=1):
            cache_key = hashlib.sha256(f"{category}\0{query}".encode()).hexdigest()
            if cache_key not in cache:
                jobs.append((category, index, query, cache_key))

    def fetch_job(job: tuple[str, int, str, str]) -> tuple[tuple[str, int, str, str], dict[str, Any]]:
        category, _, query, _ = job
        response = tavily_search(api_key, query, category)
        if args.delay:
            time.sleep(args.delay)
        return job, response

    if jobs and args.offline_cache:
        print(f"Offline-cache mode: skipping {len(jobs)} uncached queries", flush=True)
    elif jobs:
        print(f"Fetching {len(jobs)} uncached queries with {args.workers} workers", flush=True)
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            future_map = {executor.submit(fetch_job, job): job for job in jobs}
            for future in as_completed(future_map):
                category, index, query, cache_key = future_map[future]
                try:
                    _, response = future.result()
                except RuntimeError as exc:
                    failures.append({"category": category, "query": query, "error": str(exc)})
                    print(f"[{category} {index}/{len(QUERIES[category])}] ERROR {exc}", flush=True)
                    continue
                cache[cache_key] = {
                    "category": category,
                    "query": query,
                    "response": response,
                    "fetched_at": utc_now(),
                }
                save_cache(args.cache, cache)
                print(
                    f"[{category} {index}/{len(QUERIES[category])}] "
                    f"{len(response.get('results', []))} results",
                    flush=True,
                )

    for category in selected:
        for index, query in enumerate(QUERIES[category], start=1):
            cache_key = hashlib.sha256(f"{category}\0{query}".encode()).hexdigest()
            if cache_key not in cache:
                continue
            entry = cache[cache_key]
            results = entry.get("response", {}).get("results", [])
            for rank, result in enumerate(results, start=1):
                search_rows.append({
                    "expected_category": category,
                    "query": query,
                    "rank": rank,
                    "fetched_at": entry.get("fetched_at"),
                    **result,
                })

    by_url: dict[str, dict[str, Any]] = {}
    rejected: list[dict[str, Any]] = []
    category_priority = {"paper": 4, "community": 3, "news": 2, "blog": 1}

    for row in search_rows:
        url = str(row.get("url") or "").strip()
        title = re.sub(r"\s+", " ", str(row.get("title") or "")).strip()
        excerpt = clean_excerpt(str(row.get("content") or ""))
        if not url or not title:
            continue
        canonical = canonicalize(url)
        host = host_of(canonical)
        category = classify(row["expected_category"], host, canonical)
        relevant, relevance_score, evidence = assess(title, excerpt, canonical)
        language = detect_language(f"{title} {excerpt}")
        base = {
            "id": "src_" + hashlib.sha256(canonical.encode()).hexdigest()[:16],
            "category": category,
            "title": title,
            "url": url,
            "canonical_url": canonical,
            "host": host,
            "language": language,
            "region_inference": infer_region(language, host, row["query"]),
            "role_scope": role_scope(f"{title} {excerpt}"),
            "search_query": row["query"],
            "search_rank": row["rank"],
            "tavily_score": row.get("score"),
            "published_date": row.get("published_date"),
            "excerpt": excerpt,
            "relevance_score": relevance_score,
            "relevance_evidence": evidence,
            "raw_content": None,
            "full_text_status": "not_republished_copyright_or_site_terms",
            "collected_at": row.get("fetched_at"),
            "review_status": "strict_scope_pass" if relevant else "rejected",
        }
        if not relevant:
            rejected.append(base)
            continue
        previous = by_url.get(canonical)
        if previous is None:
            by_url[canonical] = base
            continue
        current_key = (relevance_score, float(row.get("score") or 0), -int(row["rank"]), category_priority[category])
        previous_key = (
            int(previous["relevance_score"]),
            float(previous.get("tavily_score") or 0),
            -int(previous["search_rank"]),
            category_priority[previous["category"]],
        )
        if current_key > previous_key:
            by_url[canonical] = base

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in by_url.values():
        grouped[item["category"]].append(item)
    for category in grouped:
        grouped[category].sort(
            key=lambda item: (
                -int(item["relevance_score"]),
                -float(item.get("tavily_score") or 0),
                item["canonical_url"],
            )
        )

    selected_items: list[dict[str, Any]] = []
    overflow: list[dict[str, Any]] = []
    for category in TARGETS:
        selected_items.extend(grouped[category][: TARGETS[category]])
        overflow.extend(grouped[category][TARGETS[category] :])
    selected_items.sort(key=lambda item: (list(TARGETS).index(item["category"]), item["canonical_url"]))
    for index, item in enumerate(selected_items, start=1):
        item["record_number"] = index

    actual = Counter(item["category"] for item in selected_items)
    language_counts = Counter(item["language"] for item in selected_items)
    region_counts = Counter(item["region_inference"] for item in selected_items)
    host_counts = Counter(item["host"] for item in selected_items)
    role_counts = Counter(item["role_scope"] for item in selected_items)
    tag_counts = Counter(tag for item in selected_items for tag in item["relevance_evidence"]["work_tags"])

    output = {
        "schema_version": "2.0.0",
        "summary": {
            "generated_at": utc_now(),
            "subject": "coffee-selling brick-and-mortar cafe / coffee-shop store managers",
            "subject_ko": "커피를 판매하는 오프라인 카페의 매장 매니저·점장",
            "targets": TARGETS,
            "actual_strict_scope": {key: actual.get(key, 0) for key in TARGETS},
            "candidate_search_results": len(search_rows),
            "unique_strict_scope_candidates": len(by_url),
            "rejected_candidate_count": len(rejected),
            "query_failures": failures,
            "languages": dict(sorted(language_counts.items())),
            "regions": dict(sorted(region_counts.items())),
            "role_scope": dict(sorted(role_counts.items())),
            "work_tags": dict(sorted(tag_counts.items())),
            "top_hosts": dict(host_counts.most_common(30)),
        },
        "scope": {
            "included": [
                "coffee-shop/cafe store manager and general manager",
                "assistant manager when the source describes store-level operations",
                "shift supervisor/shift manager/head barista when the source exposes manager-adjacent duties",
                "staffing, scheduling, training, inventory, ordering, hygiene, customer recovery, sales/cost, opening/closing, compliance",
                "Korean and international sources",
            ],
            "excluded": [
                "Naver/online-community cafe managers and moderators",
                "PC/internet/game cafe managers",
                "cafe recommendation, tourism, recipes, or generic coffee content without manager work evidence",
                "software/products named Cafe Manager",
            ],
        },
        "methodology": {
            "collector": "Tavily Search API",
            "search_depth": "advanced",
            "queries_by_category": {key: len(QUERIES[key]) for key in selected},
            "deduplication": "canonical URL after tracking-parameter removal",
            "strict_filter": "coffee context + store-management role + concrete work/operations signal; exclusions applied",
            "selection": "relevance score, Tavily score, search rank; no quota padding with rejected items",
            "audit_principles": [
                "source diversity",
                "employer/marketing versus worker/community perspective separation",
                "closed-platform access limitations are explicit",
                "search-result evidence is not treated as verified full text",
            ],
        },
        "rights_and_access": {
            "policy": "This public dataset does not republish third-party full text. It stores short search excerpts and source URLs.",
            "raw_content_field": "null unless a future source is public-domain or explicitly redistributable",
            "access_note": "Some community and publisher pages may be login-gated, paywalled, robots-restricted, changed, or deleted after collection.",
        },
        "items": selected_items,
        "overflow_strict_scope_items": overflow,
        "rejected_sample": sorted(rejected, key=lambda item: -int(item["relevance_score"]))[:100],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
