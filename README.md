# CardBridge (CardBridge Pro)
> **AI 핀테크 기반 VVIP 실시간 카드 추천 및 소비 취향 소셜 매칭 플랫폼** > KAIST 비즈니스 애널리틱스와 데이터 마이닝 (Business Analytics & Data Mining) Final Pitch

---

## 1. 프로젝트 개요 (Project Executive Summary)
* **배경 및 문제의식**: 2024년 기준 한국인 1인당 평균 신용카드 보유 매수는 **4.4장**에 달하며, 이는 20년 전 대비 25% 이상 증가한 수치입니다. 그러나 유저들은 계산대 앞에서 어떤 카드가 가장 큰 혜택을 주는지 알지 못하는 **‘결제 순간의 정보 공백’**과 전월 실적 관리의 피로도를 겪고 있습니다.
* **해결 방안**: CardBridge는 실시간 위치 기반(GPS/NFC) 데이터 연동을 통해 지갑 속 최적의 혜택 카드를 실시간으로 골라주는 **'추천 엔진'**과, 검증된 결제 데이터를 바탕으로 상위 0.1% 자산 계층의 소비 취향 유사도를 연산해 안전한 인맥을 형성해주는 **'매칭 엔진(블랙 룰렛)'**을 유기적으로 결합한 혁신적인 데이터 비즈니스 모델입니다.

---

## 2. 핵심 아키텍처 및 로직 (System Architecture)

### 2.1 추천 엔진 (Recommendation Engine)
* **구동 방식**: 유저가 특정 가맹점(Merchant)에 접근 시, 해당 점포의 고유 업종 카테고리와 국내 표준 결제망 업종 코드인 **MCC(Merchant Category Code)**를 Shared DB에서 파싱합니다.
* **최적화 설계**: `card_benefits` 매트릭스 설계 시 **혜택률이 0%인 빈 데이터는 아예 저장하지 않는 구조**를 채택하여, 실시간 `JOIN` 연산 시 불필요한 데이터 검색 트래픽을 원천 차단하고 처리 효율을 극대화했습니다.
* **LLM 연동**: **Google Gemini 2.5 Flash** 모델을 탑재하여 유저의 소비 내역, 실적 제외 가맹점 필터링 정보(공과금, 상품권 등), 보유 카드 컨텍스트를 자동 주입한 개인화 자산 최적화 진단 피드백을 제공합니다.

### 2.2 매칭 엔진: 블랙 룰렛 (Matching Engine: Black Roulette)
* **알고리즘**: 7대 도메인(Cafe, Food, Gas, Shopping, CV, Hospital, Golf)의 소비 패턴 벡터 데이터를 기반으로 **맨하튼 거리(L1 Manhattan Distance) 공식**을 활용해 연산합니다.
  $$\text{Distance} = \sum_{i=1}^{n} |u_i - v_i|$$
  두 유저 간의 카테고리별 소비 비중 퍼센트 차이의 절댓값 합이 `0`에 가까울수록 소비 성향이 데칼코마니처럼 닮았음을 입증합니다. 특정 영역의 일시적 대형 결제로 인한 왜곡을 방지하는 가중치 밸런싱이 적용되어 있습니다.
* **3라운드 점진적 정보 해금 및 긴장감 디자인**:
  * **1 ROUND (신뢰 확률 75%)**: 소비 패턴 영역 및 소비 레이더 분석 대시보드 공개
  * **2 ROUND (신뢰 확률 50%)**: 쌍방 신뢰(`TRUST`) 성공 시, 신상 프로필(혈액형, 키, 현직 업종 명세) 해금
  * **3 ROUND (신뢰 확률 25%)**: 최종 라운드 도달 시, 하이엔드 자산 원장(자가 소유 여부, 부동산 실위치, 보유 차량 브랜드 및 가치 평가액) 해금

---

## 3. 디렉토리 및 파일 데이터 명세 (Directory & File Specification)

```text
📂 cardbridge-root
 ├── 📄 T4_데이터마이닝_Cardbridge.pdf         # 비즈니스 전략 및 UI 템플릿 최종 Pitch Deck
 ├── 📜 DB-CARD.sql                        # 가맹점 마스터(20 rows) 및 카드 마스터(16 rows) 초기 시드 스크립트
 ├── 📜 alert-card.sql                     # 실적 한도 기준액(performance_limit) 및 MCC 표준 코드 보강 쿼리
 ├── 📜 matching_user.sql                  # VVIP 그룹A(실명) & 그룹B(익명) 8대8 대칭 자산 통합 테이블 생성 쿼리
 ├── 💾 final_cardbridge2.py               # Flask 기반 웹 애플리케이션 프로토타입 소스 코드 (Core Logic)
 └── 💾 full-ai-cardbridge.py              # LLM(Gemini) 프롬프트 템플릿 및 매칭 에이전트 자동화 풀 버전# cardbridge
