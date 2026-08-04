# 커피 매장 매니저 원천데이터 (raw)

이 폴더는 2026-08-04 기준으로 수집한 **커피를 판매하는 카페의 매장 매니저** 역할·업무 관련 출처(community/blog/news/paper)입니다.

- 사용한 소스: Tavily Search API, PullPush Reddit index, Brave Search, Google News RSS, OpenAlex, 발행사 사이트맵
- API 키는 실행 시 환경변수로만 전달하며 저장소에는 보관하지 않습니다.
- 수집 기준:
  - community: 200건
  - blog: 200건
  - news: 100건
  - paper: 10건

## 권장 파일

- `coffee-shop-manager-source-registry-510-2026-08-04.json`
  - 요청 할당량을 충족한 중복 제거 URL 510건
  - 원본 레지스트리이므로 간접·저관련성 자료도 품질 플래그와 함께 보존
- `coffee-shop-manager-analysis-ready-2026-08-04.json`
  - A·B등급 422건을 `items`에 수록
  - 제외된 C등급 88건도 `excluded_items`에 보존
- `coffee-shop-manager-data-quality-audit-2026-08-04.json`
  - 자동 점검 결과, 카테고리별 적합 수, 품질 등급·경고 집계
- `coffee-shop-manager-data-quality-audit-2026-08-04.md`
  - 사람이 읽는 품질 감사 보고서

## 2026-08-04 Tavily 보충 원문 (미큐레이션)

- `coffee-shop-manager-tavily-raw-2026-08-04.json` / `.md`
  - Claude Code 세션 내 Tavily Search API로 추가 수집한 원문 231건(URL 중복제거, 33개 쿼리)
  - **등급·관련성 재산정 없음** — 검색 노이즈(무관 결과) 포함된 원문 그대로 우선 업로드
  - `matched_queries` 필드로 어떤 검색어에서 나왔는지 추적 가능
- `coffee-shop-manager-tavily-curated-2026-08-04.json` / `.md`
  - 위 231건에 규칙기반 자동 등급(A/B/C) 부여 후 큐레이션
  - A=59건(매니저/점장 직무 직접 언급 또는 학술·정부·비교표준 출처), B=35건(카페 매니저 문맥 간접), C=137건(검색어 오염으로 인한 무관 결과, `excluded_items`에 보존)
  - **사람 검수 아님** — 제목/URL 키워드 매칭 규칙 적용. 재검수 권장
  - 이 배치 중 일부 사실(노원구·강북구 공고 실제 고용형태, 배민 인건비율 벤치마크 등)은 `docs/cafe-manager-research.md`에 반영 완료

## 기존 파일

- `cafe-manager-raw-data-2026-08-04.json`
- `cafe-manager-raw-data-2026-08-04.md`

기존 파일은 삭제하지 않았지만 범위·관련성 정제가 덜 되어 있습니다. 신규 분석에는 `coffee-shop-manager-*` 파일을 우선 사용하십시오.

## 권리와 접근

- 저작권이 있는 외부 기사·블로그·커뮤니티 글의 전문은 재배포하지 않습니다.
- 각 레코드는 출처 URL, 제목, 발행·수집 메타데이터, 짧은 검색 발췌를 중심으로 구성됩니다.
- 전문 확인이 필요하면 원 출처의 이용약관과 접근권한을 준수해 직접 열람해야 합니다.
