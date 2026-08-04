# 리서치 문서 검증 — 다각도 시장/경쟁사 리서치 검증 (기본 스펙) (round 1)

**Verdict: REVISE**  ·  Score: 78/100  ·  섹션 10개 · 1268단어 · 인용 17건

선택 렌즈: market_dynamics, financial_forensics, payments_regulatory_economics, engineering_diligence, incentive_integrity, org_culture_signal, closed_platform_ethnography

## Deterministic checks

| Check | Status | Evidence |
|---|---|---|
| 주장 대비 인용 밀도 | PASS | 근사 문장수 63, 인용 17건 (비율 0.270, 휴리스틱 근사치) |
| 출처 다양성(자사발행 비중) | NOT_CONFIGURED | spec.subject_owned_domains 미설정 |
| 수치 일관성(동일 문구 반복 수치 대조) | PASS | 동일 문구에 서로 다른 수치가 붙은 사례 없음(휴리스틱 탐지 기준) |
| 접근 한계 정직 표기 | N/A | 정직 표기 문구 0건 발견(해당 없으면 리서치 범위 내 접근 제약이 없었다는 뜻일 수도 있음) |
| 인센티브 리뷰 언급 스캔 | WARN | 키워드 발견: 인센티브 — 인용된 후기가 이 인센티브의 영향을 받았는지 discourse 라운드에서 재확인 필요 |
| 인용 최신성 | PASS | 임계값(2년) 초과 연도 없음 |
| 인용 URL 응답 확인 | FAIL | 데드링크 3건: https://www.bls.gov/ooh/Management/Food-service-managers.htm (HEAD=403, GET=403), https://www.bls.gov/ooh/Management/Food-service-managers.htm (HEAD=403, GET=403), https://www.bls.gov/ooh/Management/Food-service-managers.htm (HEAD=403, GET=403) |

## 정량 요약

- 감점 근거:
  - [P2] 바리스타·시프트리더·매니저의 차이 -5점 — 스타벅스 공식 직무 소개(Starbucks Coffeehouse Roles)를 인용해 매니저를 '매장 바닥에서 직원·고객과 연결되고 즉시 코칭하며 결과 개선점을 찾는 리더'로 규정한다.
  - [P1] 결론 -12점 — 문서는 노원구(2025)·강북구(2026) 카페 매니저/부매니저 공고를 '국내 카페 매니저' 직무를 대표하는 중립적 시장 증거로 인용하고, 잡코리아 민간 공고와 나란히 두어 '서로 다른 자료가 같은 역할 구조를 가리킨다'는 삼각검증 논거로 사용한다.
  - [P2] 출처 -5점 — 문서 전체가 매장 운영·인력관리·조직문화 관련 주장(실제 업무 범위, 성과지표, 필요 역량, 매장 형태별 차이 등)의 근거로 삼는 17개 인용을 검토한 결과, 전부 고용주측 하향식 자료(정부 노동통계, 채용공고, 기업 공식 채용페이지)이며 근무자(바리스타·매니저) 본인의 목소리를 담은 자료(설문, 리뷰, 퇴사 인터뷰, 근속 데이터 등)는 하나도 없다.
- 커버리지 갭: 0건

## Coverage Verification (리서치 브리프 앵글 충족 여부)

REQ ID는 브리프를 코드가 결정론적으로 번호매김한 것 — LLM이 빠뜨린 REQ-ID는 코드가 강제로 MISSING 처리한다(#8).

(브리프 미제공 — 검증 생략)

## Citation Status 요약 (코드가 실제 원문 재요청·대조로 산정, LLM 판정 아님)

| Status | Count |
|---|---|
| UNFETCHED | 2 |
| FETCH_FAILED | 0 |
| QUOTE_MATCHED | 0 |
| QUOTE_NOT_FOUND | 1 |

## Findings

허용 label: "market_dynamics", "financial_forensics", "payments_regulatory_economics", "engineering_diligence", "incentive_integrity", "org_culture_signal", "closed_platform_ethnography"

| ID | Priority | Label | Lens | Reviewer | Section | Citation | Citation Status (code-verified) | LLM Citation Status (advisory) | Claim | Evidence | Recommendation | Discourse result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| org_culture_signal-1 | P1 | org_culture_signal | org_culture_signal | Adam Grant | 결론 | [2] | UNFETCHED | UNVERIFIED | 문서는 노원구(2025)·강북구(2026) 카페 매니저/부매니저 공고를 '국내 카페 매니저' 직무를 대표하는 중립적 시장 증거로 인용하고, 잡코리아 민간 공고와 나란히 두어 '서로 다른 자료가 같은 역할 구조를 가리킨다'는 삼각검증 논거로 사용한다. | 두 공고의 출처 도메인 50plus.or.kr은 서울시50플러스재단으로, WebSearch로 확인한 결과 40~64세 중장년 대상 재취업·생애설계 지원을 전담하는 서울시 산하 공공기관이다([2][3][10][11][12] 모두 이 재단 발행). 즉 국내 근거 3건 중 2건이 '일반 노동시장 채용'이 아니라 특정 연령대 재취업 지원 프로그램이라는 단일 채널에서 나왔다. 문서의 '한계' 섹션은 '공공 운영 카페 두 곳'이라고만 적어 공공기관 발행이라는 점은 밝히지만, 이 공공기관이 중장년 재취업 특화 프로그램이라는 표본편향 축은 어디에도 언급하지 않는다. PDF 원문 자체(연령 자격요건, 프로그램 성격 명시 여부)는 접근 제한으로 대조하지 못했다. | '한계' 섹션에 두 공고가 서울시50플러스재단(중장년 재취업 지원 플랫폼) 발행이라는 점과 그로 인한 표본편향 가능성을 명시하고, 가능하면 연령 특화 채널이 아닌 일반 채용 플랫폼(사람인·잡코리아 등)의 카페 매니저 공고를 추가로 표본에 포함해 교차검증할 것을 권장. | move1(engineering_diligence, AGREE, medium)과 move12(closed_platform_ethnography, AGREE, high) 두 독립 렌즈가 각각 별도 WebSearch로 50plus.or.kr의 중장년 특화 성격 및 폐쇄 회원제 구조를 재확인. engineering_diligence-1·closed_platform_ethnography-1의 동일 사실 지적(move2, move4, move13)을 흡수하는 대표 finding으로 채택. 단 move1이 지적한 대로 개별 공고의 연령 자격요건·PDF 원문 대조는 미해결로 남음. |
| incentive_integrity-1 | P2 | incentive_integrity | incentive_integrity | Cory Doctorow | 바리스타·시프트리더·매니저의 차이 | 7 | QUOTE_NOT_FOUND | VERIFIED | 스타벅스 공식 직무 소개(Starbucks Coffeehouse Roles)를 인용해 매니저를 '매장 바닥에서 직원·고객과 연결되고 즉시 코칭하며 결과 개선점을 찾는 리더'로 규정한다. | 해당 소스는 careers.starbucks.com — 스타벅스가 구직자를 유치하기 위해 자사 발행한 채용 마케팅 페이지다(URL 자체가 채용career 목적을 명시). 문서의 '한계' 섹션은 국내 채용공고([2][3][4])에 대해서만 '고용주가 기대하는 역할을 보여줄 뿐 실제 권한·업무량과 정확히 같다고 볼 수 없다'는 편향 경고를 명시했지만, 동일하게 구인 유인을 가진 [7]/[16](Starbucks Coffeehouse Roles)과 [8]/[17](Tata Starbucks Store Manager 공고)에는 같은 caveat를 적용하지 않았다. | '한계' 섹션에 스타벅스 채용 마케팅 자료([7],[16],[17])는 구인 목적의 자사 발행 콘텐츠로 직무를 매력적으로 서술할 유인이 있다는 점을, 국내 채용공고 caveat와 동일한 수준으로 명시한다. | move10(org_culture_signal, AGREE, confidence=high)이 Schein의 표방가치/실행문화 구분과 자기보고 편향 이론틀이라는 독립적 new_evidence로 caveat 누락 지적을 재확인함. |
| org_culture_signal-2 | P2 | org_culture_signal | org_culture_signal | Adam Grant | 출처 | UNKNOWN | UNFETCHED | VERIFIED | 문서 전체가 매장 운영·인력관리·조직문화 관련 주장(실제 업무 범위, 성과지표, 필요 역량, 매장 형태별 차이 등)의 근거로 삼는 17개 인용을 검토한 결과, 전부 고용주측 하향식 자료(정부 노동통계, 채용공고, 기업 공식 채용페이지)이며 근무자(바리스타·매니저) 본인의 목소리를 담은 자료(설문, 리뷰, 퇴사 인터뷰, 근속 데이터 등)는 하나도 없다. | 인용 [1][5][6][9][14][15]=BLS/O*NET(정부 통계), [2][3][10][11][12]=구인공고, [4][13]=구인공고, [7][8][16][17]=스타벅스 공식 채용페이지. 17건 모두 '조직이 스스로 기대하는 역할'을 서술한 자료이며, 실제 근무 경험을 보고하는 소스가 구조적으로 부재하다. 이는 단일 리뷰 플랫폼 과신 문제와 반대 극단으로, 근무자 관점 데이터가 전무해 조직문화·직무경험 관련 주장을 현장에서 검증할 방법이 없다. | '한계' 섹션에 '모든 근거가 고용주측 발행 자료이며 근무자 관점 데이터(리뷰·설문·인터뷰)는 포함되지 않았다'는 점을 명시적으로 추가. 후속 조사에서는 표본크기를 명시한 근무자 대상 설문이나 다수 리뷰를 반영하되, 특정 리뷰 플랫폼 하나에만 의존하지 않도록 설계할 것을 권장. | move5(incentive_integrity, AGREE, medium)가 Jobvite 설문·AMJ RJP 메타분석이라는 독립 new_evidence로 '고용주측 자료=낙관 편향'이라는 인과 메커니즘을 보강, 근무자 목소리 부재 지적을 확증. |

### 검증 필요 사항 (근거 부족으로 finding 미승격)

- [market_dynamics] 문서 전체에 시장점유율·경쟁구도·진입장벽·대체재·구매자/공급자 교섭력 등 Five Forces 또는 구조적 vs 일시적 경쟁우위에 해당하는 주장이 존재하지 않음 — 이 문서는 개별 매장 매니저의 직무 범위를 다루는 인력·운영 리서치이며 시장/경쟁사 분석 문서가 아님. 따라서 Market Dynamics 렌즈로 검증할 대상 주장 자체가 확인되지 않음(스코프 불일치).
- [financial_forensics] 문서 전체에 특정 기업(또는 프랜차이즈)의 매출·원가·인건비 등 감사보고서·DART 기반 수치 주장이 없음 — Financial Forensics 렌즈가 대조할 '서사 vs 숫자' 대상 자체가 문서에 존재하지 않음
- [financial_forensics] '성과를 볼 때 유용한 지표' 절의 KPI 항목(인건비율, 재료원가율, 폐기율, 현금·POS 차이 등)은 저자가 '특정 브랜드의 의무 기준이 아니라... 권장 점수판'이라고 명시적으로 한정해 제시함 — 실제 재무수치로 오인될 소지는 문서 내에서 발견되지 않음
- [financial_forensics] '한 지표만 밀어붙이면 부작용이 생긴다'(인건비율↓→대기시간·소진↑, 폐기율↓→품절↑) 서술은 인용번호 없이 제시되나 '~수 있다'로 헤지된 가설적 추론이라 사실오류로 볼 근거는 없음 — 원출처 대조 불가로만 표시
- [financial_forensics] Tata Starbucks 공고([8]/[17])가 '월간 보고, 분기 사업 검토'를 실제로 명시하는지는 원문 대조 없이는 확인 불가 — 재무 수치가 아닌 직무기술 항목이라 이 렌즈의 치명도는 낮음
- [payments_regulatory_economics] 문서 전체에 결제수단·카드수수료·적격비용·PG/VAN 구조 등 'Payments & Regulatory Economics' 렌즈가 판단할 대상인 결제/수수료 비즈니스 모델 관련 서술이 없음. 'POS'는 3회 등장하나('머신·그라인더·POS를 점검한다', '시재와 예약·단체 주문·프로모션을 확인', '현금·카드·POS를 대조') 모두 매장 운영자가 마감 시 정산·점검하는 장비/절차를 지칭할 뿐, 카드수수료율·가맹점수수료·정산주기·PG사 구조 등 규제 변화(카드수수료 인하, 적격비용 재산정)에 노출되는 수익모델에 대한 주장은 전혀 없음. 이 문서는 카페 매니저 직무기술 리서치이며 결제산업 비즈니스 모델 문서가 아니므로, 이 렌즈의 핵심 질문('결제/수수료 구조가 규제 변화에서 살아남는가')을 적용할 근거 자체가 문서에 존재하지 않음. 근거 없이 의심을 지어내지 않기 위해 findings는 비움.
- [engineering_diligence] BLS 페이지에 실제로 '혼잡 시 서빙·결제·정리 지원, 청소·시설 유지보수, 예산·비용, 급여·직원기록, 마감 현금·장비·잠금상태' 내용이 그대로 있는지 — WebFetch 차단으로 미확인
- [engineering_diligence] O*NET 페이지의 Tasks 중요도 랭킹이 문서 서술(현금·입금, 위생 기록, 스케줄, 불만 해결 등)과 정확히 일치하는지 — 미확인
- [engineering_diligence] careers.starbucks.com 페이지가 매니저를 '매장 바닥에서 즉시 코칭하는 리더'로 명시적으로 설명하는지 — 미확인
- [engineering_diligence] Tata Starbucks 채용공고에 '현금·재고 관리, 월간 보고, 분기 사업 검토' 문구가 실제로 있는지 — 미확인
- [engineering_diligence] 50plus.or.kr의 노원구·강북구 PDF 공고 링크가 현재도 살아있고 서술된 세부 업무 항목과 원문이 일치하는지 — 미확인
- [engineering_diligence] jobkorea 민간 공고([4]/[13])가 만료·삭제되지 않고 서술된 업무 범위와 일치하는지 — 채용공고 특성상 링크 소멸 가능성 있으나 미확인
- [engineering_diligence] POS·설비 관련 서술에 구체적 벤더/기술스택 주장이 없어 이 렌즈(기술스택·조직규모 1차자료 재검증)가 적용될 지점 자체가 문서 내 거의 없음
- [incentive_integrity] 문서는 소비자·직원 후기 사이트(잡플래닛, Glassdoor, 네이버 리뷰 등)나 평점·리뷰 이벤트·협찬 콘텐츠를 전혀 인용하지 않는다. 인용원은 정부 통계(BLS·O*NET), 채용공고 3건, 스타벅스 채용 페이지 2건뿐이므로, '금전적 유인이 개입된 후기·평점'이라는 이 렌즈의 핵심 검증 대상 자체가 문서 내에 존재하지 않는다.
- [incentive_integrity] Tata Starbucks Store Manager 채용공고([8]/[17])가 'KPI' 섹션에서 운영 모범사례처럼 인용됐는데, 이것이 '한계' 섹션의 일반 채용공고 caveat 적용 대상에 포함되는지 문서상 명시적이지 않아 의도적 배제인지 단순 누락인지 확인 불가.
- [org_culture_signal] 50plus.or.kr 공고([2][3][10][11][12]) 원문 PDF에 실제 연령 자격요건(예: 만 50세 이상) 문구가 명시돼 있는지, 상시채용인지 단기 프로그램(사회공헌활동/인턴십 등)인지는 원문 접근 제한으로 대조하지 못함.
- [org_culture_signal] 잡코리아 민간 공고([4][13])가 특정 프랜차이즈 브랜드 소속인지 완전 개인 카페인지 문서에 명시되지 않아, 세 번째 국내 표본이 실제로 얼마나 '독립적'인지 추가 판단 불가.
- [closed_platform_ethnography] 노원구·강북구 공고가 실제로 '공공 운영(사회공헌/시니어 일자리) 카페'인지 여부는 50plus.or.kr 발행 채널 정황상 개연성은 있으나 PDF 원문 대조로 확인되지 않음.
- [closed_platform_ethnography] BLS·O*NET 인용의 '2025년/2026년 update' 표기가 현재 해당 사이트 표기와 일치하는지 웹 접근 없이 대조 불가.
- [closed_platform_ethnography] jobkorea 공고([4]/[13])가 현재도 원문 인용 내용과 동일하게 존재하는지 접근 불가로 확인 못함.

## Good Things (유지할 리서치 관행)

| Section | Good practice | Why it should be preserved |
|---|---|---|
| 한계 | 표본 규모와 출처별 제약을 명시적으로 표기 | 국내 근거가 "공공 운영 카페 두 곳과 민간 공개 공고 한 곳"에 불과함을 정확히 기록했고, BLS/O*NET이 미국 자료임을 명시해 한국 맥락과의 간극을 독자가 인지하도록 함 |
| 결론 및 각 섹션 | 주요 주장 뒤에 출처 링크 명시 및 최종 출처 목록 정리 | 각 결론과 구체적 사례(예: "2025년 서울 노원구의 카페 매니저 공고도 음료 제조·판매뿐 아니라...")에 즉시 참고 자료 [노원구 카페 매니저 공고(2025)]를 표기해 검증 가능성 확보 |
| 하루는 보통 이렇게 흘러간다 | 분석 내용의 출처 명시와 한계 표기 | "여러 직무자료를 합쳐 재구성한 대표적인 흐름이다. 매장 영업시간과 본사 분업 수준에 따라 달라진다"고 명시해 이 섹션이 사실이 아닌 분석임을 명확히 함 |
| 조사 범위 | 대상을 처음부터 명확히 정의하고 제외 범위 명시 | "한국의 일반 유인 카페 한 매장을 책임지는 매니저... 소유주·본사 슈퍼바이저·여러 매장을 맡는 지역매니저는 제외했다"고 기술해 리서치 대상의 경계를 독자가 정확히 이해하도록 함 |
| 성과를 볼 때 유용한 지표 | 권장 사항임을 명시적으로 표기 | "아래는 특정 브랜드의 의무 기준이 아니라, 위 업무를 실제로 관리하기 위한 권장 점수판이다"고 선언해 규정과 제안을 혼동하지 않도록 함 |

## Discourse audit

| Round | Move | Lens | Target | Detail | New evidence |
|---|---|---|---|---|---|
| 1 | AGREE | engineering_diligence | org_culture_signal-1 | 50plus.or.kr을 독립 WebSearch로 재검증. 재단 공식 홈페이지(50plus.or.kr) 자체가 스스로를 '4060 중장년 생애설계, 직업교육, 일자리' 전담 포털로 명시하고 있어, [2][3] 인용이 '중립적 국내 노동시장 증거'가 아니라 특정 연령대 재취업 지원 프로그램 채널이라는 원 finding의 표본편향 주장을 뒷받침한다. 다만 카페 매니저/부매니저 개별 공고의 연령 자격요건 자체(예: 만50세 이상)는 검색으로 특정하지 못했고, 재단 '정규직원' 채용은 만18세 이상으로 확인돼 이 부분은 원문 PDF 대조 없이는 완전히 닫히지 않는다. | WebSearch로 50plus.or.kr 메타 설명 확인: '서울시 50플러스포털 | 4060 중장년 생애설계, 직업교육, 일자리 정보몽땅' — 기관 미션이 공식적으로 중장년 특화임을 재단 1차 자료로 재확인. |
| 1 | CONNECT | engineering_diligence | org_culture_signal-1 | org_culture_signal-1과 closed_platform_ethnography-1은 동일 근본 원인을 서로 다른 각도에서 지적한다: 둘 다 [2]([11])와 [3]([12])이 50plus.or.kr이라는 단일 발행 주체에서 나온 동질 자료임을 지적하면서, org_culture_signal-1은 '표본편향'(중장년 재취업 채널 편중) 프레임으로, closed_platform_ethnography-1은 '가짜 삼각검증'(동일 출처를 서로 다른 자료인 것처럼 결론에서 카운트) 프레임으로 접근한다. 두 지적은 상충하지 않고 중첩·강화 관계이며, 판정 시 별개 P1/P2로 따로 채점하면 동일 결함을 이중으로 반영하지 않도록 유의할 필요가 있다. |  |
| 1 | CONNECT | engineering_diligence | org_culture_signal-2 | org_culture_signal-2(근무자 목소리 부재, 17개 인용 전부 고용주측 하향식 자료)와 closed_platform_ethnography-2(가맹점 권한 구조 서술에 인용 자체가 없음)는 동일한 구조적 공백을 가리킨다: 이 문서의 근거 자료군(정부 통계·구인공고·기업 공식 채용페이지) 어디에도 '조직 내부 실제 권한 배분'을 보여주는 1차 자료가 없다는 것. 아래 SURFACE finding은 이 공백에 대해 실제로 존재하는 대안 1차 자료(가맹사업법상 정보공개서)를 제시해 이 두 finding이 지적하는 공백이 '자료가 아예 없어서'가 아니라 '있는 자료를 안 썼다'는 문제일 수 있음을 보완한다. |  |
| 1 | CONNECT | incentive_integrity | org_culture_signal-1 | org_culture_signal-1, closed_platform_ethnography-1, engineering_diligence-1 세 렌즈가 독립적으로 동일 사실(50plus.or.kr 중복 발행처)을 각자 발견했다는 수렴 자체가 신호다. 국내 근거 4건 중 2건이 사실상 한 발행처인데도 [2][3][4]를 나란히 배열해 '서로 다른 자료의 수렴'처럼 결론에 쓴 것은 — 실제 표본 다양성보다 '인용 개수로 보이는 다양성'을 우선한 문서 구성 유인을 드러낸다. 누구 이익? 독자에게 삼각검증된 것처럼 보여 결론의 신뢰도를 사는 저자(또는 이 리포트를 발주한 주체)의 이익. |  |
| 1 | AGREE | incentive_integrity | org_culture_signal-2 | 17개 인용 전부 고용주측 자료라는 지적에 '왜 문제인가'의 인과 메커니즘을 보강. 채용공고는 장르 자체가 지원자 유인을 위해 역할을 낙관적으로 포장하는 구인 마케팅 텍스트다 — 근무자 경험과 체계적으로 괴리된다는 점이 독립적으로 문서화돼 있다. | 2023 Jobvite 설문: 신규 입사자 50%가 '채용 시 설명된 업무'와 실제 업무가 달랐다고 응답. Academy of Management Journal 메타분석(Realistic Job Preview, 40개 연구)도 표준 채용공고가 긍정 편향돼 있고 이를 교정하지 않으면 이직·기대불일치가 커진다는 결과를 보고. 즉 이 문서가 근거로 쓴 자료 유형(구인공고·기업 공식 채용페이지) 자체가 '조직이 지원자에게 팔고 싶은 역할'이지 '실제 역할'이 아니라는 것이 별도 연구로 확인됨 — 근무자 목소리 부재는 단순 커버리지 공백이 아니라 체계적 낙관 편향 유입 경로. |
| 1 | CONNECT | incentive_integrity | engineering_diligence-2 | engineering_diligence-2(정부 통계에 근거 없는 '2026 update'/'2025 update' 라벨 부여)와 closed_platform_ethnography-3(휘발성 구인공고 URL엔 연도·조회일 아예 없음)을 함께 보면 비대칭이 드러난다. 이미 권위 있는 자료(BLS·O*NET)엔 없는 정밀함을 지어 붙여 더 엄밀해 보이게 하고, 정작 정밀함이 절실한 불안정 자료(마감되면 사라지는 구인공고)엔 날짜를 생략했다. 엄밀함을 실제로 적용하기보다 '엄밀해 보이는 인상'을 선택적으로 연출한 것 — 이득은 문서 신뢰도를 검증 없이 통과시키는 저자 측. |  |
| 1 | CONNECT | incentive_integrity | engineering_diligence-3 | engineering_diligence-3(Tata Starbucks 인도 합작법인 자료를 미국 본사 careers.starbucks.com과 구분 없이 '스타벅스'로 통칭)은 org_culture_signal-2(17건 전부 고용주 발신)와 결합하면 문제가 한 단계 더 커진다. 서로 다른 법인의 채용 텍스트를 단일 '스타벅스' 브랜드 권위로 뭉쳐, 마치 하나의 글로벌 표준 운영 지침이 있는 것처럼 인용 근거를 부풀렸다. 한국 카페를 다루면서 정작 한국 법인(SCK컴퍼니) 자료는 없이 인도 자회사 자료로 '스타벅스 공식' 권위를 빌려온 구조. |  |
| 1 | SURFACE | incentive_integrity | new:incentive_integrity-1 | '성과를 볼 때 유용한 지표' 섹션이 채용공고상 업무 책임 나열(현금·재고 관리, 월간 보고, 분기 사업 검토)을 '성과 지표'로 재해석해 쓴 문제 — surfaced 배열 참고. |  |
| 1 | CONNECT | org_culture_signal | engineering_diligence-1 | engineering_diligence-1과 closed_platform_ethnography-1은 동일 사실([2]/[3]이 모두 50plus.or.kr 발행)을 서로 다른 렌즈에서 지적했다. 조직문화 신호 해석 관점에서 이는 단순 출처 중복이 아니라 '표본 군집화(clustering)' 문제다 — 두 공고가 동일 발행기관(서울시50플러스재단)의 표준 템플릿을 공유한다면 응답자(작성 주체)가 사실상 1개로 수렴하므로, 국내 표본의 실효 독립 N은 2가 아니라 1에 가깝다. 결론부의 '서로 다른 자료가 같은 역할 구조를 가리킨다'는 삼각검증(triangulation) 수사는 이 군집 구조 하에서 통계적으로 성립하지 않는 유사복제(pseudo-replication)다. |  |
| 1 | AGREE | org_culture_signal | incentive_integrity-1 | careers.starbucks.com·Tata Starbucks 채용페이지에 국내 공고와 동일한 편향 caveat가 누락됐다는 지적에 동의하며, 이를 뒷받침할 방법론적 근거를 추가한다. | 조직행동론에서 Schein(1985)이 구분한 '표방 가치(espoused values)'와 '실행 가치/실연 문화(enacted culture)' 프레임을 적용하면, 채용 마케팅 페이지는 정확히 표방 층위의 데이터다 — 조직이 되고 싶어하는 모습을 기술할 뿐, 매장 현장에서 매니저가 실제로 무엇을 하는지 관찰한 자료가 아니다. 이는 설문·인터뷰 기반 조직 연구에서 흔히 지적되는 자기보고/사회적 바람직성 편향(self-report/social-desirability bias)의 구조적 아날로그로, incentive_integrity-1의 지적을 독립적 이론 틀에서 재확인한다. |
| 1 | CONNECT | org_culture_signal | engineering_diligence-3 | engineering_diligence-3(Tata Starbucks 인도 합작법인과 Starbucks Corp 미국 본사를 '스타벅스' 하나로 뭉뚱그린 개체 혼동)과 incentive_integrity-1(두 출처 모두 편향 caveat 누락)은 동일 인용([7]/[16], [8]/[17])에 중첩된 두 개의 독립적 타당도 위협을 보여준다. 조직문화 신호 관점에서: 인도 합작법인의 채용 마케팅 문구(문화적으로 다른 모집단)를 표방-실행 편향 보정 없이 한국 카페 매니저 역할의 근거로 사용한 것이며, 문화 간 일반화(cross-cultural generalization) 오류와 표방-실행 편향이 결합해 해당 인용의 증거력을 원문이 인지한 것보다 더 약화시킨다. |  |
| 1 | AGREE | closed_platform_ethnography | org_culture_signal-1 | 50plus.or.kr이 공공기관 발행이라는 점을 넘어, 로그인·회원가입 필요한 폐쇄형 취업지원 포털이라는 접근성 축을 독립 검색으로 재확인. 이력서 등록·지원이 플랫폼 내부 회원 기능으로만 이뤄지고 '중장년(4060) 일자리' 전용 카테고리로 별도 노출됨. 국내 카페 매니저 근거 2건은 일반 노동시장 표본이 아니라 가입한 40~64세만 접근하는 단일 폐쇄 채널 표본 — 대표성 문제가 원 finding이 지적한 것보다 한 축 더 있음(공공기관=중립 아님 + 폐쇄 회원제=일반 접근 아님, 두 겹). | WebSearch('50plus.or.kr 구인 공고 회원가입 로그인 열람 서울시50플러스재단') 결과: 사이트가 로그인 후 이력서 관리·지원 가능한 회원제 구조로 운영되며, 중장년 전용 일자리 카테고리에 한정 게시(999건, 2026-08-04 확인 시점). 원 finding이 인용한 재단 성격(중장년 재취업 지원) 확인과는 별도의 독립 검색 경로로, 접근 게이트 존재라는 새 사실을 추가 확인. |
| 1 | CONNECT | closed_platform_ethnography | engineering_diligence-1 | engineering_diligence-1(출처 독립성: [2]/[3]이 동일 플랫폼)과 org_culture_signal-1(대표성 편향: 해당 플랫폼이 중장년 재취업 특화 채널)은 같은 근본원인의 양면 — 50plus.or.kr은 로그인 필요한 단일 폐쇄 포털이라, (a) 두 공고가 독립 시장 참여자가 아니라는 점과 (b) 이 채널 자체가 일반 노동시장을 대표 못한다는 점이 동시에 성립한다. '폐쇄 플랫폼 표본 하나를 삼각검증 자료처럼 제시'라는 단일 결함으로 두 finding을 합쳐 봐야 함. |  |
