# 커피 매장 매니저 직무 다각도 리서치·원천데이터

이 저장소는 **커피를 판매하는 카페의 매장 매니저**가 수행하는 업무를 한국·해외 자료로 조사한 결과와 원천 출처 레지스트리를 보관합니다.

## 2026-08-04 신규 데이터

- [510건 출처 레지스트리](raw_data/coffee-shop-manager-source-registry-510-2026-08-04.json): 커뮤니티 200, 블로그 200, 뉴스 100, 논문 10
- [분석 적합본](raw_data/coffee-shop-manager-analysis-ready-2026-08-04.json): A·B등급 422건과 제외된 C등급 88건을 함께 보존
- [데이터 품질 감사](raw_data/coffee-shop-manager-data-quality-audit-2026-08-04.md): 중복, 범위, 메타데이터, 관련성, 저작권·접근 한계 점검
- [기계 판독용 감사 결과](raw_data/coffee-shop-manager-data-quality-audit-2026-08-04.json)
- [수집·보강·감사 스크립트](scripts/)

새 데이터의 분석 적합 수는 커뮤니티 198건, 블로그 135건, 뉴스 79건, 논문 10건입니다. 할당량을 맞춘 원본 510건은 삭제하지 않았으며, 관련성이 약한 88건만 분석 적합본에서 명시적으로 제외했습니다.

## 포함 문서

- [카페 매니저 리서치 원문](docs/cafe-manager-research.md)
- [다각도 검토 요약](docs/cafe-manager-multi-angle-audit.md)
- [커뮤니티 근거 보강 노트](docs/cafe-manager-community-evidence.md)
- [review 전체 보고서](review_cafe_manager/report.md)
- [개선 제안 5건](review_cafe_manager/improve.md)
- [상태 메타데이터](review_cafe_manager/state.json)
- [자동 검증 결과](review_cafe_manager/deterministic-results.json)

## 한 줄 정리

- 판정: `REVISE`
- 점수: `78 / 100`
- 핵심 리스크: 근거 편향(고용주 발행 자료 집중), 대표성(표본/채널 편향), 자사 채용 콘텐츠의 채용마케팅 성격 반영 미비

## 라이선스/공지

- 공개 자료는 검토 목적의 산출물입니다.
- 문서에 인용된 외부 링크는 발행 시점 기준으로 검증되었으며, 시간 경과에 따라 접근성이 바뀔 수 있습니다.
- 저작권이 있는 외부 본문 전문은 재배포하지 않습니다. 원천데이터에는 URL, 메타데이터, 짧은 검색 발췌만 포함합니다.
- 기존 파일은 재현성과 변경 이력 보존을 위해 삭제하지 않았습니다. 신규 분석에는 `coffee-shop-manager-*` 파일을 우선 사용하십시오.
