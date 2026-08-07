# 카페 매니저 AX 전환 검토 리서치

> **이 저장소는 무엇인가:** 카페 매장 매니저 직무의 AX(자동화·디지털 전환) 전환 가능성을 검토하기 위한 리서치 저장소. "매니저가 실제로 무엇을 하는가"를 국내외 자료로 조사하고, MGRV-Project 자사 제품(MangroveCafeOrder: 카페 주문·POS 시스템)이 그 업무를 얼마나 대체할 수 있는지 매핑한다.

## 왜 이 저장소가 필요한가

MangroveCafeOrder가 매니저 직무를 어떻게 바꾸는지 판단하려면, 먼저 "매니저가 실제로 하는 일"에 대한 근거 있는 정의가 있어야 한다. 이 저장소는 그 정의(리서치)와 검증(다각도 감사), 그리고 자사 제품과의 매핑(AX 전환 직무기술서)까지의 전 과정을 보관한다.

## 핵심 산출물 3개 (읽는 순서 추천)

1. [카페 매니저 리서치 원문](docs/cafe-manager-research.md) — 업무 정의의 원 자료, 2026-08-04 원문 재검증으로 정정 반영됨
2. [직무기술서 상세판](docs/cafe-manager-job-description.md) — 리서치를 업무 7가지로 정리
3. [카페 매니저 AX 전환 직무기술서](docs/cafe-manager-ax-job-description.md) — 업무 7가지 중 MangroveCafeOrder가 자동화하는 부분과 매니저에게 남는 부분을 매핑한 최종 결론 문서(도식 포함, 2026-08-07)

## 저장소 구조

| 경로 | 내용 |
|---|---|
| `docs/` | 리서치 본문·요약·시각자료·직무기술서·AX 매핑 문서 |
| `raw_data/` | 출처 레지스트리·원천 데이터(JSON), 데이터 품질 감사 |
| `review_cafe_manager/` | 리서치 원문에 대한 다각도 검증 결과(판정·점수·개선 제안) |
| `scripts/` | 원천데이터 수집·보강·감사 스크립트 |

### `docs/` 전체 목록

- [카페 매니저 AX 전환 직무기술서](docs/cafe-manager-ax-job-description.md)
- [카페 매니저 리서치 원문](docs/cafe-manager-research.md)
- [직무기술서 상세판](docs/cafe-manager-job-description.md)
- [한 장 요약 (팀 공유용)](docs/cafe-manager-summary.md) — 핵심만 압축, 가장 중요한 정정 사항 포함
- [리서치 감사 조서 (시각 자료)](docs/cafe-manager-dossier.html) — Mermaid 다이어그램 6개, 조사 과정 전체
- [다각도 검토 요약](docs/cafe-manager-multi-angle-audit.md)
- [커뮤니티 근거 보강 노트](docs/cafe-manager-community-evidence.md)

### `review_cafe_manager/` 전체 목록

- [review 전체 보고서](review_cafe_manager/report.md)
- [개선 제안 5건](review_cafe_manager/improve.md)
- [상태 메타데이터](review_cafe_manager/state.json)
- [자동 검증 결과](review_cafe_manager/deterministic-results.json)

### `raw_data/` 전체 목록

- [510건 출처 레지스트리](raw_data/coffee-shop-manager-source-registry-510-2026-08-04.json): 커뮤니티 200, 블로그 200, 뉴스 100, 논문 10
- [분석 적합본](raw_data/coffee-shop-manager-analysis-ready-2026-08-04.json): A·B등급 422건과 제외된 C등급 88건을 함께 보존
- [데이터 품질 감사](raw_data/coffee-shop-manager-data-quality-audit-2026-08-04.md): 중복, 범위, 메타데이터, 관련성, 저작권·접근 한계 점검
- [기계 판독용 감사 결과](raw_data/coffee-shop-manager-data-quality-audit-2026-08-04.json)
- [Tavily 보충 원천데이터 231건 + 큐레이션](raw_data/README.md) — 추가 검색 배치, A/B/C 등급 분류

## 리서치 원문 검증 결과 (한 줄 정리)

- 판정: `REVISE`
- 점수: `78 / 100`
- 핵심 리스크: 근거 편향(고용주 발행 자료 집중), 대표성(표본/채널 편향), 자사 채용 콘텐츠의 채용마케팅 성격 반영 미비
- **주의:** 이 점수는 최초 리서치 버전 기준이다. 2026-08-04 원문 PDF 재검증으로 국내 근거 2건이 정정됐으나(PR #4), 재검증 라운드의 점수는 이 저장소에 아직 반영되지 않았다.
- **가장 중요한 정정:** 원 리서치가 국내 근거로 쓴 노원구·강북구 채용공고를 PDF 원문 대조한 결과, 둘 다 민간 카페 매니저 채용이 아니라 **각 구청이 직영하는 관광시설 부속 카페의 공무원·기간제 근로자 채용**으로 확인됐다. 상세는 [한 장 요약](docs/cafe-manager-summary.md) 또는 [`docs/cafe-manager-research.md`](docs/cafe-manager-research.md)의 '한계' 섹션 참고.

## 진행 이력

- **2026-08-07** — [AX 전환 직무기술서](docs/cafe-manager-ax-job-description.md) 작성: 업무 7가지를 MangroveCafeOrder 설계 문서와 매핑, 이후 Mermaid 도식 3개(자동화 매핑·주문 라이프사이클·역할 축 이동) 보강.
- **2026-08-04** — 원문 재검증 + 시각화: 노원구·강북구 공고 PDF 원문 대조로 정정, 감사 조서·요약·직무기술서 상세판 추가.
- **2026-08-04** — 신규 원천데이터 510건 레지스트리 추가(커뮤니티 200·블로그 200·뉴스 100·논문 10), 분석 적합본(A·B등급 422건) 분리, 데이터 품질 감사 수행. 기존 파일은 재현성을 위해 유지하며, 신규 분석에는 `coffee-shop-manager-*` 파일을 우선 사용.

## 라이선스/공지

- 공개 자료는 검토 목적의 산출물입니다.
- 문서에 인용된 외부 링크는 발행 시점 기준으로 검증되었으며, 시간 경과에 따라 접근성이 바뀔 수 있습니다.
- 저작권이 있는 외부 본문 전문은 재배포하지 않습니다. 원천데이터에는 URL, 메타데이터, 짧은 검색 발췌만 포함합니다.
- 기존 파일은 재현성과 변경 이력 보존을 위해 삭제하지 않았습니다. 신규 분석에는 `coffee-shop-manager-*` 파일을 우선 사용하십시오.
