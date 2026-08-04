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

## 기존 파일

- `cafe-manager-raw-data-2026-08-04.json`
- `cafe-manager-raw-data-2026-08-04.md`

기존 파일은 삭제하지 않았지만 범위·관련성 정제가 덜 되어 있습니다. 신규 분석에는 `coffee-shop-manager-*` 파일을 우선 사용하십시오.

## 권리와 접근

- 저작권이 있는 외부 기사·블로그·커뮤니티 글의 전문은 재배포하지 않습니다.
- 각 레코드는 출처 URL, 제목, 발행·수집 메타데이터, 짧은 검색 발췌를 중심으로 구성됩니다.
- 전문 확인이 필요하면 원 출처의 이용약관과 접근권한을 준수해 직접 열람해야 합니다.
