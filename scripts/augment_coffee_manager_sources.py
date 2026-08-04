#!/usr/bin/env python3
"""Augment Tavily results with transparent public indexes.

Sources:
- PullPush Reddit index for community posts
- Bing Web RSS for blogs, career guides, and job descriptions
- Google News RSS for journalism
- OpenAlex for academic works

Only metadata and short excerpts are stored. Third-party full text is not
republished.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from collect_coffee_manager_sources import (
    ACADEMIC_HINTS,
    BLOG_HOST_HINTS,
    COMMUNITY_HOSTS,
    COFFEE_TERMS,
    EXCLUDE_TERMS,
    ROLE_TERMS,
    TARGETS,
    WORK_TERMS,
    assess,
    canonicalize,
    clean_excerpt,
    detect_language,
    host_of,
    infer_region,
    matches_host,
    role_scope,
    utc_now,
)


PULLPUSH_QUERIES = [
    ("barista", "manager"),
    ("barista", "management"),
    ("barista", "shift supervisor"),
    ("barista", "assistant manager"),
    ("barista", "head barista"),
    ("barista", "general manager"),
    ("Coffee", "coffee shop manager"),
    ("Coffee", "cafe manager"),
    ("Coffee", "store manager"),
    ("starbucks", "store manager"),
    ("starbucks", "shift supervisor"),
    ("starbucks", "manager workload"),
    ("CafeOwners", "manager"),
    ("CafeOwners", "shop manager"),
    ("smallbusiness", "coffee shop manager"),
]

BLOG_QUERIES = [
    '"coffee shop manager" duties',
    '"coffee shop manager" responsibilities',
    '"cafe manager" job description',
    '"café manager" job description',
    '"coffee shop manager" daily operations',
    '"day in the life" "coffee shop manager"',
    '"coffee shop manager" staffing scheduling',
    '"coffee shop manager" inventory ordering',
    '"coffee shop manager" staff training',
    '"coffee shop manager" customer complaints',
    '"coffee shop manager" food safety hygiene',
    '"coffee shop manager" opening closing',
    '"coffee shop manager" labor cost sales',
    '"coffee shop manager" performance management',
    '"coffee shop general manager" responsibilities',
    '"coffee shop assistant manager" duties',
    '"coffee shop shift supervisor" duties',
    '"head barista" responsibilities training inventory',
    '"cafe operations manager" responsibilities',
    '"coffeehouse manager" job description',
    '"coffee store manager" job description',
    '"specialty coffee" manager responsibilities',
    '"independent cafe" manager staffing',
    '"coffee shop" manager checklist',
    '"coffee shop" manager KPI',
    '"cafe manager" rota inventory',
    '"cafe manager" health inspection',
    '"cafe manager" service recovery',
    '"cafe manager" cash handling',
    '"cafe manager" supplier ordering',
    '"Starbucks store manager" responsibilities',
    '"Costa Coffee store manager" responsibilities',
    '"Pret shop manager" responsibilities',
    '"Dunkin store manager" responsibilities coffee',
    '"Tim Hortons restaurant manager" responsibilities coffee',
    '카페 점장 업무 커피전문점',
    '카페 매니저 직무 직원관리',
    '커피숍 점장 재고 발주 업무',
    '커피전문점 점장 스케줄 관리',
    '카페 점장 위생 고객응대 매출',
    '카페 매니저 하루 일과',
    '카페 점장 오픈 마감 체크리스트',
    '카페 점장 직원 교육 채용',
    '카페 매니저 원가 인건비 관리',
    '스타벅스 점장 업무 매장 운영',
    '이디야 점장 업무',
    '투썸플레이스 점장 업무',
    '메가커피 점장 업무',
]

NEWS_QUERIES_EN = [
    '"coffee shop manager" staffing workload',
    '"coffee shop manager" labor shortage',
    '"coffee shop manager" wages overtime',
    '"coffee shop manager" schedule employees',
    '"coffee shop manager" hiring training',
    '"coffee shop manager" burnout turnover',
    '"coffee shop manager" minimum wage costs',
    '"coffee shop manager" food safety inspection',
    '"coffee shop manager" customer service staff',
    '"coffee shop manager" inventory supply chain',
    '"coffee shop manager" union labor',
    '"coffee shop manager" day in the life',
    '"cafe manager" staffing workload',
    '"cafe manager" wages hours',
    '"cafe manager" employees training',
    '"cafe manager" health safety',
    '"Starbucks store manager" workload staffing',
    '"Starbucks store manager" scheduling labor',
    '"Starbucks store manager" union',
    '"Starbucks shift supervisor" workload',
    '"Costa Coffee" manager staffing',
    '"Pret" shop manager staffing',
    '"Dunkin" store manager labor',
    '"Tim Hortons" manager staffing',
    'coffee chain store managers employee scheduling',
    'independent coffee shops managers labor costs',
]

NEWS_QUERIES_KO = [
    '커피전문점 점장 업무 인력난',
    '카페 매니저 노동시간 업무',
    '카페 점장 직원관리 노동',
    '스타벅스 점장 업무 인력 운영',
    '스타벅스 점장 노동 스케줄',
    '커피전문점 매장 관리자 채용',
    '카페 점장 위생 관리',
    '커피 매장 점장 고객 응대',
    '카페 점장 인건비 매출 운영',
    '이디야 점장 매장 운영',
    '투썸 점장 직원 관리',
    '메가커피 점장 업무',
]

PAPER_QUERIES = [
    "coffee shop management employees",
    "coffee shop managerial practices",
    "cafe manager leadership barista",
    "coffee shop emotional labor management",
    "barista job stress management",
    "coffee shop employee turnover management",
    "coffee shop service quality management employees",
    "coffee shop food waste managerial",
    "coffee shop food safety management employees",
    "coffee shop labor scheduling operations",
    "coffee shop job satisfaction leadership",
    "coffeehouse employee performance management",
    "커피전문점 종사자 감정노동 직무스트레스",
    "커피전문점 점장 리더십 직무만족",
    "커피전문점 직원 이직의도 서비스품질",
]

SITEMAP_ROOTS = [
    "https://perfectdailygrind.com/sitemap_index.xml",
    "https://www.7shifts.com/sitemap.xml",
    "https://www.lightspeedhq.com/sitemap-blog.xml",
    "https://squareup.com/us/en/sitemap.xml",
    "https://www.deputy.com/sitemap_index.xml",
    "https://www.joinhomebase.com/sitemap.xml",
    "https://www.workstream.us/sitemap.xml",
    "https://www.baristamagazine.com/sitemap_index.xml",
    "https://freshcup.com/sitemap_index.xml",
    "https://pos.toasttab.com/sitemap.xml",
]

SITEMAP_COFFEE_PATTERN = re.compile(r"(coffee[-_/]shops?|cafe|caf%C3%A9|barista)", re.I)
SITEMAP_WORK_PATTERN = re.compile(
    r"(?:^|[-_/])(manag(?:e|er|ement|ing)?|staff(?:ing)?|schedul(?:e|ing)?|inventory|labou?r|"
    r"hir(?:e|ing)|train(?:er|ing)?|cost(?:s|ing)?|profit(?:s|able)?|service|safety|hygiene|"
    r"order(?:ing)?|suppl(?:y|ies|ier)|open(?:ing)?|clos(?:e|ing)?|retention|turnover|customer(?:s)?|"
    r"checklist|employee(?:s)?|workforce|operations?)(?:[-_/]|$)",
    re.I,
)
SITEMAP_EXCLUDE_PATTERN = re.compile(
    r"(?:/tag/|/category/|/wp-content/|producer|farm|green-coffee|supply-chain|export|import|"
    r"coffee-roast|roaster|roastery|competition|championship|giveaway|winner|\.jpe?g|\.png|\.gif|"
    r"\.webp|\.svg|\.avif)",
    re.I,
)

NEWS_OPERATION_TERMS = [
    "staff",
    "worker",
    "employee",
    "labor",
    "union",
    "wage",
    "salary",
    "pay",
    "hour",
    "schedule",
    "shift",
    "hiring",
    "training",
    "turnover",
    "burnout",
    "workload",
    "shortage",
    "cost",
    "safety",
    "inspection",
    "operations",
    "업무",
    "노동",
    "직원",
    "인력",
    "채용",
    "근무",
    "스케줄",
    "위생",
    "운영",
    "인건비",
    "매출",
]

NEWS_INCIDENT_EXCLUDES = [
    "accused",
    "arrested",
    "charged",
    "murder",
    "killed",
    "shooting",
    "shot",
    "stabbing",
    "stole",
    "theft",
    "embezzl",
    "bleach",
    "crash",
    "missing",
    "sexual",
    "assault",
    "lottery",
    "징역",
    "체포",
    "살인",
    "폭행",
    "절도",
    "횡령",
    "락스",
    "사망",
    "실종",
]


def strip_html(value: str) -> str:
    value = re.sub(r"<script.*?</script>|<style.*?</style>", " ", value or "", flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def fetch_bytes(url: str, *, timeout: int = 45, retries: int = 3) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 cafe-manager-research-audit/2.0"},
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            if attempt + 1 == retries:
                raise RuntimeError(f"GET failed {url}: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def cache_key(method: str, query: str) -> str:
    return hashlib.sha256(f"{method}\0{query}".encode()).hexdigest()


def save_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_pullpush(query_spec: tuple[str, str]) -> dict[str, Any]:
    subreddit, query = query_spec
    params = urllib.parse.urlencode({"q": query, "subreddit": subreddit, "size": 100})
    url = f"https://api.pullpush.io/reddit/search/submission/?{params}"
    return json.loads(fetch_bytes(url, timeout=60).decode("utf-8"))


def fetch_bing(query: str) -> str:
    url = "https://www.bing.com/search?" + urllib.parse.urlencode({"format": "rss", "q": query})
    return fetch_bytes(url).decode("utf-8", errors="replace")


def fetch_duckduckgo(query: str) -> str:
    locale = "kr-kr" if re.search(r"[가-힣]", query) else "us-en"
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query, "kl": locale})
    return fetch_bytes(url).decode("utf-8", errors="replace")


def fetch_brave(query: str) -> str:
    url = "https://search.brave.com/search?" + urllib.parse.urlencode({"q": query, "source": "web"})
    return fetch_bytes(url).decode("utf-8", errors="replace")


def xml_locations(data: bytes) -> list[str]:
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []
    return [
        node.text.strip()
        for node in root.iter()
        if node.tag.endswith("loc") and node.text and node.text.strip()
    ]


def fetch_sitemap_urls(root_url: str) -> list[str]:
    first = xml_locations(fetch_bytes(root_url, timeout=60))
    urls: list[str] = []
    for location in first:
        if location.lower().endswith((".xml", ".xml.gz")) or "sitemap" in location.lower():
            try:
                urls.extend(xml_locations(fetch_bytes(location, timeout=60)))
            except RuntimeError:
                continue
        else:
            urls.append(location)
    print(f"sitemap parsed {root_url}: {len(urls)} URLs", flush=True)
    return sorted(set(urls))


def metadata_value(page: str, key: str) -> str:
    patterns = [
        rf'<meta[^>]+(?:name|property)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\']{re.escape(key)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.I | re.S)
        if match:
            return strip_html(match.group(1))
    return ""


def fetch_page_metadata(url: str) -> dict[str, str]:
    page = fetch_bytes(url, timeout=30, retries=2).decode("utf-8", errors="replace")[:500_000]
    title_match = re.search(r"<title[^>]*>(.*?)</title>", page, flags=re.I | re.S)
    title = strip_html(title_match.group(1)) if title_match else ""
    description = metadata_value(page, "description") or metadata_value(page, "og:description")
    return {"title": title, "description": description}


def fetch_google_news(spec: tuple[str, str]) -> str:
    query, locale = spec
    if locale == "ko":
        params = {"q": query + " when:10y", "hl": "ko", "gl": "KR", "ceid": "KR:ko"}
    else:
        params = {"q": query + " when:10y", "hl": "en-US", "gl": "US", "ceid": "US:en"}
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)
    return fetch_bytes(url).decode("utf-8", errors="replace")


def fetch_openalex(query: str) -> dict[str, Any]:
    params = urllib.parse.urlencode({"search": query, "per-page": 50})
    return json.loads(fetch_bytes(f"https://api.openalex.org/works?{params}", timeout=60).decode("utf-8"))


def make_record(
    *,
    category: str,
    title: str,
    url: str,
    excerpt: str,
    query: str,
    method: str,
    published_date: str | None = None,
    source_subtype: str | None = None,
    extra: dict[str, Any] | None = None,
    allow_indirect_news: bool = False,
    allow_indirect_operations: bool = False,
) -> dict[str, Any] | None:
    title = re.sub(r"\s+", " ", title or "").strip()
    url = (url or "").strip()
    excerpt = clean_excerpt(strip_html(excerpt or ""))
    if not title or not url:
        return None
    canonical = canonicalize(url)
    host = host_of(canonical)
    relevant, relevance_score, evidence = assess(title, excerpt, canonical)
    combined = f"{title} {excerpt}".casefold()
    indirect_news = False
    indirect_operations = False
    if category == "blog" and allow_indirect_operations and not relevant:
        coffee_context = any(term.casefold() in combined for term in COFFEE_TERMS)
        excluded = any(term.casefold() in combined for term in EXCLUDE_TERMS)
        # Callers may set this only after a separate coffee+cafe-operations
        # prefilter (the publisher sitemap path filter in this collector).
        indirect_operations = coffee_context and not excluded
        if indirect_operations:
            relevant = True
            relevance_score = max(48, relevance_score)
    if category == "news":
        operational = any(term.casefold() in combined for term in NEWS_OPERATION_TERMS)
        incident = any(term.casefold() in combined for term in NEWS_INCIDENT_EXCLUDES)
        if allow_indirect_news and not relevant:
            coffee_context = any(term.casefold() in combined for term in COFFEE_TERMS)
            excluded = any(term.casefold() in combined for term in EXCLUDE_TERMS)
            indirect_news = coffee_context and operational and not incident and not excluded
            if indirect_news:
                relevant = True
                relevance_score = max(48, relevance_score)
        relevant = relevant and operational and not incident
    if category == "paper":
        managerial = any(term.casefold() in combined for term in [
            "manager", "management", "managerial", "leadership", "supervisor", "operations",
            "점장", "매니저", "관리", "리더십", "운영",
        ])
        relevant = relevant and managerial
    if not relevant:
        return None
    language = detect_language(f"{title} {excerpt}")
    record = {
        "id": "src_" + hashlib.sha256(canonical.encode()).hexdigest()[:16],
        "category": category,
        "source_subtype": source_subtype or category,
        "title": title,
        "url": url,
        "canonical_url": canonical,
        "host": host,
        "language": language,
        "region_inference": infer_region(language, host, query),
        "role_scope": "manager_operational_context" if (indirect_news or indirect_operations) else role_scope(f"{title} {excerpt}"),
        "search_query": query,
        "search_rank": None,
        "tavily_score": None,
        "published_date": published_date,
        "excerpt": excerpt,
        "relevance_score": relevance_score,
        "relevance_evidence": evidence,
        "raw_content": None,
        "full_text_status": "not_republished_copyright_or_site_terms",
        "collection_method": method,
        "collected_at": utc_now(),
        "review_status": "strict_scope_pass",
        "evidence_directness": "indirect_manager_context" if (indirect_news or indirect_operations) else "direct_role_evidence",
    }
    if extra:
        record.update(extra)
    return record


def records_from_pullpush(query_spec: tuple[str, str], payload: dict[str, Any]) -> list[dict[str, Any]]:
    subreddit, query = query_spec
    records = []
    for post in payload.get("data", []):
        permalink = post.get("permalink") or ""
        if permalink.startswith("/"):
            permalink = "https://www.reddit.com" + permalink
        created = post.get("created_utc")
        published = None
        if isinstance(created, (int, float)):
            published = dt.datetime.fromtimestamp(created, tz=dt.timezone.utc).isoformat()
        record = make_record(
            category="community",
            title=str(post.get("title") or ""),
            url=permalink,
            excerpt=str(post.get("selftext") or ""),
            query=f"r/{subreddit}: {query}",
            method="pullpush_reddit_index",
            published_date=published,
            source_subtype="reddit_post",
            extra={
                "community": f"r/{subreddit}",
                "reddit_post_id": post.get("id"),
                "reddit_score_at_index_time": post.get("score"),
                "reddit_comment_count_at_index_time": post.get("num_comments"),
            },
        )
        if record:
            records.append(record)
    return records


def parse_rss(xml_text: str) -> list[dict[str, str]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    rows = []
    for item in root.findall(".//item"):
        source = item.find("source")
        rows.append({
            "title": item.findtext("title") or "",
            "link": item.findtext("link") or "",
            "description": item.findtext("description") or "",
            "pubDate": item.findtext("pubDate") or "",
            "source_name": source.text if source is not None and source.text else "",
            "source_url": source.get("url") if source is not None else "",
        })
    return rows


def records_from_bing(query: str, xml_text: str) -> list[dict[str, Any]]:
    records = []
    for row in parse_rss(xml_text):
        host = host_of(row["link"])
        if matches_host(host, COMMUNITY_HOSTS) or matches_host(host, ACADEMIC_HINTS):
            continue
        subtype = "blog_or_guide"
        if any(term in host for term in ["indeed", "ziprecruiter", "workable", "job", "career", "talent"]):
            subtype = "job_description_or_career_guide"
        elif matches_host(host, BLOG_HOST_HINTS):
            subtype = "personal_or_platform_blog"
        record = make_record(
            category="blog",
            title=row["title"],
            url=row["link"],
            excerpt=row["description"],
            query=query,
            method="bing_web_rss",
            source_subtype=subtype,
        )
        if record:
            records.append(record)
    return records


def parse_duckduckgo(html_text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        flags=re.I | re.S,
    )
    rows = []
    for href, title, snippet in pattern.findall(html_text):
        href = html.unescape(href)
        if href.startswith("//"):
            href = "https:" + href
        parsed = urllib.parse.urlsplit(href)
        params = urllib.parse.parse_qs(parsed.query)
        direct = params.get("uddg", [href])[0]
        rows.append({
            "title": strip_html(title),
            "link": urllib.parse.unquote(direct),
            "description": strip_html(snippet),
        })
    return rows


def records_from_duckduckgo(query: str, html_text: str) -> list[dict[str, Any]]:
    records = []
    for row in parse_duckduckgo(html_text):
        host = host_of(row["link"])
        if matches_host(host, COMMUNITY_HOSTS) or matches_host(host, ACADEMIC_HINTS):
            continue
        subtype = "blog_or_guide"
        if any(term in host for term in ["indeed", "ziprecruiter", "workable", "job", "career", "talent", "interview"]):
            subtype = "job_description_or_career_guide"
        elif matches_host(host, BLOG_HOST_HINTS):
            subtype = "personal_or_platform_blog"
        record = make_record(
            category="blog",
            title=row["title"],
            url=row["link"],
            excerpt=row["description"],
            query=query,
            method="duckduckgo_html",
            source_subtype=subtype,
        )
        if record:
            records.append(record)
    return records


def parse_brave(html_text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r'<div class="snippet [^>]*data-type="web".*?'
        r'<a href="(https?://[^"]+)"[^>]*class="[^"]*\bl1\b[^"]*">.*?'
        r'<div class="title [^"]*" title="([^"]+)">.*?</div></a>.*?'
        r'<div class="generic-snippet [^"]*">.*?'
        r'<div class="content [^"]*">(.*?)</div>',
        flags=re.I | re.S,
    )
    return [
        {"link": html.unescape(url), "title": strip_html(title), "description": strip_html(snippet)}
        for url, title, snippet in pattern.findall(html_text)
    ]


def records_from_brave(query: str, html_text: str) -> list[dict[str, Any]]:
    records = []
    for row in parse_brave(html_text):
        host = host_of(row["link"])
        if matches_host(host, COMMUNITY_HOSTS) or matches_host(host, ACADEMIC_HINTS):
            continue
        subtype = "blog_or_guide"
        if any(term in host for term in ["indeed", "ziprecruiter", "workable", "job", "career", "talent", "interview"]):
            subtype = "job_description_or_career_guide"
        elif matches_host(host, BLOG_HOST_HINTS):
            subtype = "personal_or_platform_blog"
        record = make_record(
            category="blog",
            title=row["title"],
            url=row["link"],
            excerpt=row["description"],
            query=query,
            method="brave_search_html",
            source_subtype=subtype,
        )
        if record:
            records.append(record)
    return records


def records_from_google_news(spec: tuple[str, str], xml_text: str) -> list[dict[str, Any]]:
    query, locale = spec
    records = []
    for row in parse_rss(xml_text):
        record = make_record(
            category="news",
            title=row["title"],
            url=row["link"],
            excerpt=row["description"],
            query=query,
            method="google_news_rss",
            published_date=row["pubDate"] or None,
            source_subtype="news_article_via_google_news",
            extra={
                "publisher_name": row["source_name"],
                "publisher_homepage": row["source_url"],
                "aggregator_link_note": "Google News RSS link; publisher homepage retained separately",
                "search_locale": locale,
            },
            allow_indirect_news=True,
        )
        if record:
            records.append(record)
    return records


def abstract_from_inverted(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    max_position = max((position for positions in index.values() for position in positions), default=-1)
    words = [""] * (max_position + 1)
    for word, positions in index.items():
        for position in positions:
            if 0 <= position < len(words):
                words[position] = word
    return " ".join(words)


def records_from_openalex(query: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for work in payload.get("results", []):
        location = work.get("primary_location") or {}
        landing = location.get("landing_page_url") or work.get("doi") or work.get("id") or ""
        source = location.get("source") or {}
        authors = []
        for authorship in work.get("authorships") or []:
            author = authorship.get("author") or {}
            if author.get("display_name"):
                authors.append(author["display_name"])
        record = make_record(
            category="paper",
            title=str(work.get("title") or ""),
            url=landing,
            excerpt=abstract_from_inverted(work.get("abstract_inverted_index")),
            query=query,
            method="openalex_api",
            published_date=work.get("publication_date"),
            source_subtype="academic_work_metadata",
            extra={
                "openalex_id": work.get("id"),
                "doi": work.get("doi"),
                "publication_year": work.get("publication_year"),
                "work_type": work.get("type"),
                "journal_or_venue": source.get("display_name"),
                "authors": authors,
                "cited_by_count": work.get("cited_by_count"),
                "open_access": work.get("open_access"),
            },
        )
        if record:
            records.append(record)
    return records


def run_jobs(
    *,
    method: str,
    specs: list[Any],
    fetcher: Callable[[Any], Any],
    cache: dict[str, Any],
    cache_path: Path,
    workers: int,
) -> list[tuple[Any, Any]]:
    missing = [spec for spec in specs if cache_key(method, json.dumps(spec, ensure_ascii=False)) not in cache]
    if missing:
        print(f"{method}: fetching {len(missing)} uncached queries", flush=True)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {executor.submit(fetcher, spec): spec for spec in missing}
            for future in as_completed(future_map):
                spec = future_map[future]
                key = cache_key(method, json.dumps(spec, ensure_ascii=False))
                try:
                    response = future.result()
                except RuntimeError as exc:
                    print(f"{method} ERROR {spec!r}: {exc}", flush=True)
                    continue
                cache[key] = {"method": method, "spec": spec, "response": response, "fetched_at": utc_now()}
                save_cache(cache_path, cache)
                print(f"{method} OK {spec!r}", flush=True)
    rows = []
    for spec in specs:
        key = cache_key(method, json.dumps(spec, ensure_ascii=False))
        if key in cache:
            rows.append((spec, cache[key]["response"]))
    return rows


def source_quality(item: dict[str, Any]) -> int:
    method = item.get("collection_method") or "tavily_search_api"
    base = {
        "openalex_api": 50,
        "pullpush_reddit_index": 35,
        "tavily_search_api": 30,
        "bing_web_rss": 25,
        "duckduckgo_html": 25,
        "brave_search_html": 25,
        "publisher_sitemap_page_metadata": 28,
        "google_news_rss": 20,
    }.get(method, 10)
    if item.get("excerpt"):
        base += min(10, len(item["excerpt"]) // 120)
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--skip-brave", action="store_true")
    parser.add_argument("--skip-sitemap-fetch", action="store_true")
    parser.add_argument("--sitemap-url-only", action="store_true")
    args = parser.parse_args()

    base = json.loads(args.base.read_text(encoding="utf-8"))
    cache = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    candidates: list[dict[str, Any]] = []
    for item in base.get("items", []) + base.get("overflow_strict_scope_items", []):
        item = dict(item)
        item.setdefault("collection_method", "tavily_search_api")
        item.setdefault("source_subtype", item.get("category"))
        item.setdefault("evidence_directness", "direct_role_evidence")
        candidates.append(item)

    for spec, response in run_jobs(
        method="pullpush_reddit_index",
        specs=PULLPUSH_QUERIES,
        fetcher=fetch_pullpush,
        cache=cache,
        cache_path=args.cache,
        workers=min(args.workers, 5),
    ):
        candidates.extend(records_from_pullpush(spec, response))

    for spec, response in run_jobs(
        method="bing_web_rss",
        specs=BLOG_QUERIES,
        fetcher=fetch_bing,
        cache=cache,
        cache_path=args.cache,
        workers=args.workers,
    ):
        candidates.extend(records_from_bing(spec, response))

    for spec, response in run_jobs(
        method="duckduckgo_html",
        specs=BLOG_QUERIES,
        fetcher=fetch_duckduckgo,
        cache=cache,
        cache_path=args.cache,
        workers=min(args.workers, 4),
    ):
        candidates.extend(records_from_duckduckgo(spec, response))

    brave_specs = (
        [entry["spec"] for entry in cache.values() if entry.get("method") == "brave_search_html"]
        if args.skip_brave else BLOG_QUERIES
    )
    for spec, response in run_jobs(
        method="brave_search_html",
        specs=brave_specs,
        fetcher=fetch_brave,
        cache=cache,
        cache_path=args.cache,
        workers=min(args.workers, 2),
    ):
        candidates.extend(records_from_brave(spec, response))

    sitemap_specs = (
        [entry["spec"] for entry in cache.values() if entry.get("method") == "publisher_sitemap"]
        if args.skip_sitemap_fetch else SITEMAP_ROOTS
    )
    sitemap_urls: list[str] = []
    for _, response in run_jobs(
        method="publisher_sitemap",
        specs=sitemap_specs,
        fetcher=fetch_sitemap_urls,
        cache=cache,
        cache_path=args.cache,
        workers=min(args.workers, 5),
    ):
        sitemap_urls.extend(response)
    sitemap_candidates = []
    for url in sorted(set(sitemap_urls)):
        path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
        if (
            SITEMAP_COFFEE_PATTERN.search(path)
            and SITEMAP_WORK_PATTERN.search(path)
            and not SITEMAP_EXCLUDE_PATTERN.search(path)
        ):
            sitemap_candidates.append(url)
    print(f"publisher_sitemap: {len(sitemap_candidates)} coffee-operations candidate URLs", flush=True)
    metadata_specs = (
        [entry["spec"] for entry in cache.values() if entry.get("method") == "publisher_sitemap_page_metadata"]
        if args.sitemap_url_only else sitemap_candidates
    )
    sitemap_metadata = dict(run_jobs(
        method="publisher_sitemap_page_metadata",
        specs=metadata_specs,
        fetcher=fetch_page_metadata,
        cache=cache,
        cache_path=args.cache,
        workers=min(args.workers, 12),
    ))
    for url in sitemap_candidates:
        metadata = sitemap_metadata.get(url, {})
        derived_title = urllib.parse.unquote(url.rstrip("/").rsplit("/", 1)[-1]).replace("-", " ")
        page_description = metadata.get("description") or ""
        record = make_record(
            category="blog",
            title=metadata.get("title") or derived_title,
            url=url,
            excerpt=" ".join(part for part in [page_description, derived_title] if part),
            query="publisher sitemap: coffee/cafe + store-operations URL",
            method="publisher_sitemap_page_metadata",
            source_subtype="industry_blog_or_operations_guide",
            extra={
                "page_metadata_status": "fetched" if metadata else "sitemap_url_only",
                "sitemap_evidence": "URL slug matched coffee-shop/cafe/barista plus a store-operations term",
                "sitemap_derived_topic": derived_title,
            },
            allow_indirect_operations=True,
        )
        if record:
            record["excerpt"] = clean_excerpt(page_description)
            candidates.append(record)

    news_specs = [(query, "en") for query in NEWS_QUERIES_EN] + [(query, "ko") for query in NEWS_QUERIES_KO]
    for spec, response in run_jobs(
        method="google_news_rss",
        specs=news_specs,
        fetcher=fetch_google_news,
        cache=cache,
        cache_path=args.cache,
        workers=args.workers,
    ):
        candidates.extend(records_from_google_news(spec, response))

    for spec, response in run_jobs(
        method="openalex_api",
        specs=PAPER_QUERIES,
        fetcher=fetch_openalex,
        cache=cache,
        cache_path=args.cache,
        workers=min(args.workers, 5),
    ):
        candidates.extend(records_from_openalex(spec, response))

    deduped: dict[str, dict[str, Any]] = {}
    for item in candidates:
        canonical = item["canonical_url"]
        previous = deduped.get(canonical)
        key = (int(item.get("relevance_score") or 0), source_quality(item), len(item.get("excerpt") or ""))
        if previous is None:
            deduped[canonical] = item
            continue
        previous_key = (
            int(previous.get("relevance_score") or 0),
            source_quality(previous),
            len(previous.get("excerpt") or ""),
        )
        if key > previous_key:
            deduped[canonical] = item

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in deduped.values():
        grouped[item["category"]].append(item)
    for category in grouped:
        grouped[category].sort(
            key=lambda item: (
                -int(item.get("relevance_score") or 0),
                -source_quality(item),
                -(int(item.get("cited_by_count") or 0) if category == "paper" else 0),
                item["canonical_url"],
            )
        )

    items: list[dict[str, Any]] = []
    overflow: list[dict[str, Any]] = []
    for category, target in TARGETS.items():
        items.extend(grouped[category][:target])
        overflow.extend(grouped[category][target:])
    items.sort(key=lambda item: (list(TARGETS).index(item["category"]), item["canonical_url"]))
    for index, item in enumerate(items, start=1):
        item["record_number"] = index

    category_counts = Counter(item["category"] for item in items)
    method_counts = Counter(item.get("collection_method", "unknown") for item in items)
    language_counts = Counter(item.get("language", "und") for item in items)
    region_counts = Counter(item.get("region_inference", "unknown") for item in items)
    role_counts = Counter(item.get("role_scope", "unknown") for item in items)
    host_counts = Counter(item.get("host", "") for item in items)
    tag_counts = Counter(tag for item in items for tag in item.get("relevance_evidence", {}).get("work_tags", []))
    subtype_counts = Counter(item.get("source_subtype", "unknown") for item in items)

    output = {
        "schema_version": "2.1.0",
        "summary": {
            "generated_at": utc_now(),
            "subject": "coffee-selling brick-and-mortar cafe / coffee-shop store managers",
            "subject_ko": "커피를 판매하는 오프라인 카페의 매장 매니저·점장",
            "targets": TARGETS,
            "actual_strict_scope": {key: category_counts.get(key, 0) for key in TARGETS},
            "unique_strict_scope_candidates": len(deduped),
            "overflow_strict_scope_count": len(overflow),
            "collection_methods": dict(sorted(method_counts.items())),
            "source_subtypes": dict(sorted(subtype_counts.items())),
            "languages": dict(sorted(language_counts.items())),
            "regions": dict(sorted(region_counts.items())),
            "role_scope": dict(sorted(role_counts.items())),
            "work_tags": dict(sorted(tag_counts.items())),
            "top_hosts": dict(host_counts.most_common(40)),
        },
        "scope": base["scope"],
        "methodology": {
            **base["methodology"],
            "collection_methods": {
                "tavily_search_api": "Primary multi-query web discovery; 59 successful cached queries before the supplied plan returned HTTP 432",
                "pullpush_reddit_index": "Reddit community metadata and self-post excerpts; source links point to Reddit",
                "bing_web_rss": "Direct web-result links for blogs, career guides, and job descriptions",
                "duckduckgo_html": "Direct web-result links for blogs, career guides, and job descriptions; used after Bing RSS quality checks",
                "brave_search_html": "Direct web-result links and search snippets for blogs, career guides, and job descriptions",
                "publisher_sitemap_page_metadata": "Direct page metadata from coffee-industry and workforce-operations publisher sitemaps",
                "google_news_rss": "News metadata via Google News; aggregator article link plus publisher name/homepage",
                "openalex_api": "Academic metadata, DOI/landing URL, citation count, and abstract excerpt where indexed",
            },
            "quota_rule": "Targets are filled only from strict-scope records; no rejected item is used as padding",
            "ranking": "Relevance score, collection-source quality, excerpt completeness; academic ties also use citation count",
        },
        "rights_and_access": base["rights_and_access"],
        "items": items,
        "overflow_strict_scope_items": overflow,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
