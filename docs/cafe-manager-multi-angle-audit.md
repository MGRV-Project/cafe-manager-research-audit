# 카페 매니저 직무 리서치 다각도 검토 결과 (2026-08-04)

### 목적

이 문서는 `outputs/cafe-manager-research.md`에 대해 더 많은 관점으로 교차 검토한 결과를 정리한 공개 레포용 요약본이다.

### 검토 설정

- 도구: `research-loop` `review`  
- Spec: `specs/default.toml`  
- 사용 렌즈(전체 7개 선택): `market_dynamics`, `financial_forensics`, `payments_regulatory_economics`, `engineering_diligence`, `incentive_integrity`, `org_culture_signal`, `closed_platform_ethnography`  
- 모델: `sonnet` / `haiku`  
- 실행: round 1 / concurrency 4 / max-rounds 1  
- 출력: `review_cafe_manager/`  

### 판정 요약

- Verdict: `REVISE`
- Score: `78/100`
- Coverage gap: `0`
- 독립 교차검토(P1/P2)에서 보완이 필요한 포인트가 확인됨

### 핵심 리스크(우선순위 높은 순)

1. **근거 편향: 고용주 발행자료 편중**
   - 인용 수치 17건 중 고유 출처는 7개에 불과하며, 실제로는 정부 통계, 채용공고, 브랜드 공식 채용 페이지 중심의 고용주측 자료가 대부분이다.
   - 근무자(바리스타/매니저) 경험 인터뷰, 설문, 퇴사 인터뷰 등 종사자 관점 1차 증거가 포함되지 않았다.
   - 결과적으로 직무의 실제 수행 실태는 "구인·채용 문구"와 "현장 실무" 사이에서 벌어질 괴리를 검증하기 어렵다.

2. **국내 표본의 대표성 및 접근성 한계(50+ 채널)**
   - 노원구·강북구 공고는 동일 플랫폼 기반(서울시50플러스재단)으로, 모집군·채용형태 특성(재취업/시니어 대상)이 분명히 드러날 수 있어 전체 국내 카페 매니저를 대표한다는 결론은 과장될 수 있다.
   - 해당 채고 채널은 로그인·회원제 성격이라 "일반 노동시장 샘플"로의 일반화에 제한이 따른다.

3. **자사 채용 콘텐츠의 홍보 목적 caveat 미반영**
   - Starbucks/Tata Starbucks의 공식 채용 페이지는 역할을 구인 관점에서 제시한다는 점은 맞지만, 같은 수준의 caveat가 국내 채용공고처럼 매니저 역할 비교 섹션에 일관되게 반영되지 않았다.

4. **중복 인용과 증거 강도 과신**
   - 동일 근거를 여러 번 재인용하면서 "독립 표본"처럼 보이는 부분이 있으며, 동일 출처 반복으로 인한 과잉 확신 가능성이 있다.

5. **URL 검증 이슈**
   - 일부 BLS URL은 실제 HTTP 재확인에서 403으로 실패해 자동 검증 단계에서 FAILED 처리됨(브라우저/브로큰 가드 차이 가능성은 있음).

### 유지할 점(좋은 관행)

- 대상 범위를 "점주/본사 슈퍼바이저/지역매니저 제외"로 분명히 한 점
- 서울권 공공채용·민간채용·해외 프랜차이즈 공개자료를 명시적으로 구분한 점
- KPI는 의무 기준이 아닌 권장 지표로 표시한 점
- 한계 섹션에서 한국-해외, 공공/민간 샘플 제한을 적어 둔 점

### 권고 액션 (즉시 반영 우선순위)

1. 근로자 관점 1차 자료(리뷰/인터뷰/설문)를 1개 이상 추가하고 샘플 조건을 투명하게 기재
2. 50+ 채널 공고는 모집 유형(정규직/단기/프로그램형), 연령 조건, 고용형태를 별도 검증
3. `Starbucks`·`Tata Starbucks` 공식 채용 자료는 "자사 홍보성/채용마케팅 성격" caveat와 함께 표기로 통일
4. 중복 인용/중복 출처를 정리해 고유 출처 개수와 실제 인용 근거를 분리 표시
5. KPI 항목 옆에 실측/벤치마크 출처(있다면) 또는 "검증 예정" 라벨 부착

### 진행 반영 (2026-08-04)

- **1번 조치 반영 완료(부분)**: 블라인드, Reddit r/barista, Reddit r/smallbusiness의 근무자 관점 증언을 반영해 `docs/cafe-manager-research.md`에 ‘커뮤니티 기반 다각도 보강’ 섹션을 추가했습니다.
- 반영 요지: 근무시간 초과/포괄임금제, 오픈 전 준비 부담, 스케줄링 실패지점(교대 규칙/교체 승인/비용 통제) 등 익명 커뮤니티에서 반복 제기되는 실무 리스크를 별도 장으로 정리했습니다.
- 보완 필요: 2번~5번 조치는 동일 작업에서 추가로 후속 검증(특히 공개 채용군 메타데이터 정합성, KPI 실측 라벨)을 별도 라운드로 이어갈 예정입니다.

### 첨부

- `review_cafe_manager/report.md` (full audit report)
- `review_cafe_manager/improve.md` (개선 제안 5건)
- `review_cafe_manager/state.json` (review run metadata)
- `review_cafe_manager/deterministic-results.json` (자동 검증 요약)

---

### 재실행 방법

```bash
cargo run --release -- review \
  --spec /Users/kimjaehyun/Documents/Codex/2026-08-04/new-chat-2/work/research-loop/specs/default.toml \
  --document /Users/kimjaehyun/Documents/Codex/2026-08-04/new-chat-2/outputs/cafe-manager-research.md \
  --out /Users/kimjaehyun/Documents/Codex/2026-08-04/new-chat-2/work/mgrv-raw_data/review_cafe_manager \
  --lenses market_dynamics,financial_forensics,payments_regulatory_economics,engineering_diligence,incentive_integrity,org_culture_signal,closed_platform_ethnography \
  --concurrency 4 \
  --max-rounds 1 \
  --model sonnet \
  --cheap-model haiku
```
