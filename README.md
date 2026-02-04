# 파이썬으로 배우는 백테스팅 입문
## Introduction to Backtesting with Python

실전 트레이딩 전략 개발을 위한 체계적인 백테스팅 학습서

---

## 📖 소개

이 책은 Python을 사용하여 체계적으로 백테스팅을 학습하고, 실전에서 사용할 수 있는 트레이딩 전략을 개발하는 방법을 다룹니다. 기초적인 데이터 다운로드부터 머신러닝 기반 전략, 실전 배포까지 전 과정을 포괄합니다.

### 주요 특징

- ✅ **18개 챕터** - 기초부터 고급까지 체계적 학습
- ✅ **실행 가능한 코드** - 모든 챕터에 Python 예제 코드 포함
- ✅ **한국어 + 영어** - 한국어 설명에 영어 기술 용어 병행
- ✅ **수학적 엄밀성** - LaTeX 수식으로 이론적 배경 제공
- ✅ **실전 중심** - 실제 시장 데이터와 거래 비용 고려

### 대상 독자

- 기본적인 Python 지식을 가진 학습자 (변수, 반복문, 함수)
- 퀀트 트레이딩에 관심 있는 개발자
- 체계적인 백테스팅 방법론을 배우고 싶은 트레이더

---

## 📚 목차

### Part 1: Foundations & Data (기초와 데이터) - Chapters 1-4

#### [Chapter 1: 백테스팅 시작하기](content/docs/chapter01.md)
- 백테스팅의 개념과 필요성
- 흔한 함정: Look-ahead bias, Overfitting, Survivorship bias
- 개발 환경 구축 (Python, uv, 필수 라이브러리)
- 프로젝트 구조 설계

#### [Chapter 2: 금융 데이터 다운로드와 이해](content/docs/chapter02.md)
- OHLCV 데이터 구조
- yfinance로 데이터 다운로드
- 배당금과 주식 분할 조정 (Adjusted Close)
- 다중 종목 및 다중 타임프레임 데이터

#### [Chapter 3: 데이터 전처리와 수익률](content/docs/chapter03.md)
- 결측치 및 이상치 처리
- 데이터 정합성 검증
- 수익률 계산: 단순 수익률 vs 로그 수익률
- 벤치마크 비교

#### [Chapter 4: Backtrader 프레임워크 기초](content/docs/chapter04.md)
- Backtrader 아키텍처 (Cerebro, Strategy, Data Feeds, Analyzers)
- 첫 번째 전략: Buy & Hold
- 주문 실행과 포지션 관리
- 기본 성과 분석

### Part 2: Technical Analysis Strategies (기술적 분석 전략) - Chapters 5-8

#### [Chapter 5: 이동평균 전략](content/docs/chapter05.md)
- 단순 이동평균 (SMA), 지수 이동평균 (EMA)
- 크로스오버 전략 (Golden Cross / Death Cross)
- 파라미터 최적화
- 전략 성과 분석

#### [Chapter 6: 모멘텀과 변동성 지표](content/docs/chapter06.md)
- RSI (Relative Strength Index) 과매수/과매도 전략
- MACD (Moving Average Convergence Divergence) 크로스오버
- Bollinger Bands 평균 회귀 전략
- ATR (Average True Range) 활용

#### [Chapter 7: 추세 추종과 평균 회귀](content/docs/chapter07.md)
- 추세 vs 범위 시장 (Trend vs Range-bound markets)
- Donchian Channels와 Breakout 전략
- Bollinger Bands 반전 전략
- 시장 체제에 따른 전략 선택

#### [Chapter 8: 다중 지표 결합 전략](content/docs/chapter08.md)
- 지표 간 상관관계 분석
- 확인 지표 (Confirmation indicators)
- 필터링 기법
- 시그널 가중 결합

### Part 3: Risk & Portfolio Management (리스크와 포트폴리오 관리) - Chapters 9-11

#### [Chapter 9: 리스크 관리](content/docs/chapter09.md)
- 포지션 사이징 (Fixed vs Percentage, Kelly Criterion)
- 손절매와 익절매 (Stop Loss / Take Profit)
- ATR 기반 동적 손절매
- 리스크-보상 비율 (Risk-Reward Ratio)

#### [Chapter 10: 포트폴리오 구성과 리밸런싱](content/docs/chapter10.md)
- 다종목 포트폴리오 백테스팅
- 상관관계와 분산투자
- 리밸런싱 전략 (Time-based, Threshold-based)
- 섹터별 배분

#### [Chapter 11: 포트폴리오 최적화](content/docs/chapter11.md)
- 현대 포트폴리오 이론 (Modern Portfolio Theory)
- 효율적 프론티어 (Efficient Frontier)
- Risk Parity
- 최소 분산 포트폴리오 (Minimum Variance Portfolio)

### Part 4: Performance Analysis (성과 분석) - Chapters 12-13

#### [Chapter 12: 성과 지표와 리스크 측정](content/docs/chapter12.md)
- 수익률 지표: Total Return, Annualized Return, CAGR
- 리스크 지표: Volatility, Maximum Drawdown
- 리스크 조정 수익률: Sharpe Ratio, Sortino Ratio, Calmar Ratio
- 승률, Profit Factor, Expectancy

#### [Chapter 13: 백테스트 결과 분석과 시각화](content/docs/chapter13.md)
- Equity Curve와 Drawdown 차트
- Monthly/Yearly Returns Heatmap
- 거래 분석 (Trade Duration, Win/Loss Distribution)
- 슬리피지와 수수료 영향 분석

### Part 5: Advanced Techniques (고급 기법) - Chapters 14-16

#### [Chapter 14: 과최적화 방지와 검증](content/docs/chapter14.md)
- In-Sample vs Out-of-Sample
- 워크포워드 분석 (Walk-Forward Analysis)
- 몬테카를로 시뮬레이션
- 로버스트성 테스트

#### [Chapter 15: 머신러닝 기반 전략 (1)](content/docs/chapter15.md)
- 특성 엔지니어링 (Feature Engineering): 기술적 지표를 ML 특성으로
- 분류 문제로서의 트레이딩 (Classification approach)
- 모델 학습: Logistic Regression, Random Forest
- Cross-Validation과 과적합 방지

#### [Chapter 16: 머신러닝 기반 전략 (2)](content/docs/chapter16.md)
- 시계열 특화 모델 (Time series specific models)
- Feature importance 분석
- 앙상블 방법 (Ensemble methods)
- Backtrader에 ML 모델 통합하기

### Part 6: Real-World Application (실전 적용) - Chapters 17-18

#### [Chapter 17: 실전 트레이딩 고려사항](content/docs/chapter17.md)
- 슬리피지 모델링 (Slippage modeling)
- 거래 비용과 세금 (Commission, fees, taxes)
- 시장 영향과 체결 가능성 (Market impact, fill probability)
- 주문 유형 (Market, Limit, Stop orders)
- 시장 체제 감지와 적응형 전략

#### [Chapter 18: 완전한 전략 개발 프로세스](content/docs/chapter18.md)
- Case Study: 실제 주식 시장 전략 개발
- 아이디어 → 가설 → 백테스트 → 검증 → 개선
- 여러 시장에서의 테스트 (주식, ETF)
- 실전 배포 체크리스트
- 나만의 전략 개발하기

---

## 🚀 시작하기

### 필수 요구사항

- Python 3.10 이상
- uv (Python 패키지 관리자)

### 설치

```bash
# 저장소 클론
git clone https://github.com/k2sebeom/intro-to-backtesting.git
cd intro-to-backtesting

# Python 환경 설정 (codes 디렉토리에서)
cd codes
uv sync

# Hugo 사이트 실행 (선택사항)
hugo server
```

### 코드 실행

```bash
# codes 디렉토리에서
cd codes

# 챕터별 코드 실행
uv run chapter01/01_basic_data_download.py
uv run chapter02/01_data_download_multiple_timeframes.py
uv run chapter03/01_sma_calculation.py

# 다른 챕터들도 동일한 방식으로...
uv run chapter18/01_complete_strategy_framework.py
```

---

## 📊 프로젝트 구조

```
intro-to-backtesting/
├── content/docs/          # Hugo 책 내용 (마크다운)
│   ├── chapter01.md       # 각 챕터의 이론과 설명
│   ├── chapter02.md
│   └── ...
├── codes/                 # 실행 가능한 Python 코드
│   ├── chapter01/         # 챕터별 코드 파일
│   │   ├── 01_basic_data_download.py
│   │   ├── 02_matplotlib_basics.py
│   │   └── images/        # 생성된 차트
│   ├── chapter02/
│   ├── ...
│   ├── data/              # 다운로드된 주식 데이터 (CSV)
│   ├── pyproject.toml     # uv로 관리되는 Python 의존성
│   └── README.md          # 코드 실행 가이드 (한국어)
├── references/            # 라이브러리 참고 문서
│   ├── backtrader.md      # Backtrader 프레임워크 가이드
│   └── yfinance.md        # yfinance API 참고
├── hugo.toml              # Hugo 설정
├── TABLE_OF_CONTENTS.md   # 전체 목차 및 학습 경로
└── README.md              # 이 파일
```

---

## 🛠️ 주요 라이브러리

- **yfinance**: Yahoo Finance에서 주식 데이터 다운로드
- **pandas**: 데이터 조작 및 분석
- **matplotlib**: 차트 생성 및 시각화
- **seaborn**: 통계 시각화
- **backtrader**: 백테스팅 프레임워크
- **numpy**: 수치 계산
- **scikit-learn**: 머신러닝 모델
- **scipy**: 과학 계산 및 최적화

---

## 📖 학습 경로

### 빠른 시작 경로 (6 chapters)
Chapters 1-2 → 4-5 → 9 → 12
*기초 개념과 첫 전략을 빠르게 학습*

### 기술적 분석 중심 경로 (10 chapters)
Chapters 1-8 → 9 → 12-13
*전통적인 기술적 분석 전략에 집중*

### 머신러닝 중심 경로 (11 chapters)
Chapters 1-4 → 6 → 9 → 12-13 → 15-16
*데이터 기반 머신러닝 전략 개발*

### 포트폴리오 관리 중심 경로 (11 chapters)
Chapters 1-4 → 9-13 → 17-18
*다종목 포트폴리오 구성과 리스크 관리*

### 완전 학습 경로 (18 chapters)
Chapters 1-18 순서대로
*모든 내용을 체계적으로 학습*

---

## 🎯 책의 균형

- **기술적 분석 전략**: 40%
- **포트폴리오 관리**: 25%
- **머신러닝**: 20%
- **기초 및 실전 적용**: 15%

---

## 📝 라이선스

이 프로젝트는 교육 목적으로 제공됩니다.

---

## 🤝 기여

버그 리포트, 제안, 개선사항은 Issues를 통해 제출해주세요.

---

## 📬 연락처

질문이나 피드백이 있으시면 Issues를 통해 연락해주세요.

---

## ⚠️ 면책 조항

이 책의 내용은 교육 목적으로만 제공됩니다. 실제 투자 결정에 사용하기 전에 충분한 검증과 리스크 관리가 필요합니다. 투자 손실에 대한 책임은 투자자 본인에게 있습니다.

---

**축하합니다! 백테스팅 입문 과정이 완료되었습니다.**
**성공적인 트레이딩을 기원합니다! 🚀📈**
