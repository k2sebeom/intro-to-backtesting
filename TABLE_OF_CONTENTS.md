# 파이썬으로 배우는 백테스팅 입문
## Introduction to Backtesting with Python - Table of Contents

**Total: 18 Chapters**
**Target Audience**: 기본적인 Python 지식을 가진 학습자 (Basic Python knowledge)
**Approach**: 기술적 분석, 머신러닝, 포트폴리오 관리의 균형 잡힌 커버리지

---

## Part 1: Foundations & Data (기초와 데이터) - Chapters 1-4

### Chapter 1: 백테스팅 시작하기
**Getting Started with Backtesting**
- 백테스팅이란 무엇인가? (What is Backtesting?)
- 백테스팅의 필요성과 한계 (Common pitfalls: Look-ahead bias, Overfitting, Survivorship bias)
- 개발 환경 구축 (Python, uv, 필수 라이브러리)
- 프로젝트 구조 설계
- **Code**: Environment setup, "Hello Trading" first script

### Chapter 2: 금융 데이터 다운로드와 이해
**Financial Data Acquisition and Understanding**
- OHLCV 데이터 구조 (Open, High, Low, Close, Volume)
- yfinance로 데이터 다운로드
- 배당금과 주식 분할 조정 (Adjusted Close)
- 다중 종목 및 다중 타임프레임 데이터
- **Code**: Download stock data, explore structure, basic statistics

### Chapter 3: 데이터 전처리와 수익률
**Data Preprocessing and Returns**
- 결측치 및 이상치 처리
- 데이터 정합성 검증
- 수익률 계산: 단순 수익률 $R_t = \frac{P_t - P_{t-1}}{P_{t-1}}$ vs. 로그 수익률 $r_t = \ln(\frac{P_t}{P_{t-1}})$
- 벤치마크 비교
- **Code**: Data cleaning pipeline, return calculations, visualizations

### Chapter 4: Backtrader 프레임워크 기초
**Backtrader Framework Basics**
- Backtrader 아키텍처 (Cerebro, Strategy, Data Feeds, Analyzers)
- 첫 번째 전략: Buy & Hold
- 주문 실행과 포지션 관리
- 기본 성과 분석
- **Code**: Buy & Hold strategy, basic backtest execution

---

## Part 2: Technical Analysis Strategies (기술적 분석 전략) - Chapters 5-8

### Chapter 5: 이동평균 전략
**Moving Average Strategies**
- 단순 이동평균 (SMA), 지수 이동평균 (EMA)
- 크로스오버 전략 (Golden Cross / Death Cross)
- 파라미터 최적화
- 전략 성과 분석
- **Code**: SMA/EMA crossover strategies with parameter tuning

### Chapter 6: 모멘텀과 변동성 지표
**Momentum and Volatility Indicators**
- RSI (Relative Strength Index) 과매수/과매도 전략
- MACD (Moving Average Convergence Divergence) 크로스오버
- Bollinger Bands 평균 회귀 전략
- ATR (Average True Range) 활용
- **Code**: RSI, MACD, Bollinger Bands strategies

### Chapter 7: 추세 추종과 평균 회귀
**Trend Following and Mean Reversion**
- 추세 vs. 범위 시장 (Trend vs. Range-bound markets)
- Donchian Channels와 Breakout 전략
- Bollinger Bands 반전 전략
- 시장 체제에 따른 전략 선택
- **Code**: Trend following and mean reversion implementations

### Chapter 8: 다중 지표 결합 전략
**Multi-Indicator Combined Strategies**
- 지표 간 상관관계 분석
- 확인 지표 (Confirmation indicators)
- 필터링 기법
- 시그널 가중 결합
- **Code**: Combined indicator strategy with filtering

---

## Part 3: Risk & Portfolio Management (리스크와 포트폴리오 관리) - Chapters 9-11

### Chapter 9: 리스크 관리
**Risk Management**
- 포지션 사이징 (Fixed vs. Percentage, Kelly Criterion)
- 손절매와 익절매 (Stop Loss / Take Profit)
- ATR 기반 동적 손절매
- 리스크-보상 비율 (Risk-Reward Ratio)
- **Code**: Position sizing and stop loss implementations

### Chapter 10: 포트폴리오 구성과 리밸런싱
**Portfolio Construction and Rebalancing**
- 다종목 포트폴리오 백테스팅
- 상관관계와 분산투자
- 리밸런싱 전략 (Time-based, Threshold-based)
- 섹터별 배분
- **Code**: Multi-asset portfolio with rebalancing

### Chapter 11: 포트폴리오 최적화
**Portfolio Optimization**
- 현대 포트폴리오 이론 (Modern Portfolio Theory)
- 효율적 프론티어 (Efficient Frontier)
- Risk Parity
- 최소 분산 포트폴리오 (Minimum Variance Portfolio)
- **Code**: Portfolio optimization using scipy

---

## Part 4: Performance Analysis (성과 분석) - Chapters 12-13

### Chapter 12: 성과 지표와 리스크 측정
**Performance Metrics and Risk Measurement**
- 수익률 지표: Total Return, Annualized Return, CAGR
- 리스크 지표: Volatility, Maximum Drawdown
- 리스크 조정 수익률: Sharpe Ratio, Sortino Ratio, Calmar Ratio
- 승률, Profit Factor, Expectancy
- **Code**: Comprehensive performance analysis dashboard

### Chapter 13: 백테스트 결과 분석과 시각화
**Backtest Result Analysis and Visualization**
- Equity Curve와 Drawdown 차트
- Monthly/Yearly Returns Heatmap
- 거래 분석 (Trade Duration, Win/Loss Distribution)
- 슬리피지와 수수료 영향 분석
- **Code**: Complete visualization suite and trade analytics

---

## Part 5: Advanced Techniques (고급 기법) - Chapters 14-16

### Chapter 14: 과최적화 방지와 검증
**Avoiding Overfitting and Validation**
- In-Sample vs. Out-of-Sample
- 워크포워드 분석 (Walk-Forward Analysis)
- 몬테카를로 시뮬레이션
- 로버스트성 테스트
- **Code**: Walk-forward testing and Monte Carlo simulation

### Chapter 15: 머신러닝 기반 전략 (1)
**Machine Learning Strategies (Part 1)**
- 특성 엔지니어링 (Feature Engineering): 기술적 지표를 ML 특성으로
- 분류 문제로서의 트레이딩 (Classification approach)
- 모델 학습: Logistic Regression, Random Forest
- Cross-Validation과 과적합 방지
- **Code**: ML-based signal generation with sklearn

### Chapter 16: 머신러닝 기반 전략 (2)
**Machine Learning Strategies (Part 2)**
- 시계열 특화 모델 (Time series specific models)
- Feature importance 분석
- 앙상블 방법 (Ensemble methods)
- Backtrader에 ML 모델 통합하기
- **Code**: Advanced ML strategy integration

---

## Part 6: Real-World Application (실전 적용) - Chapters 17-18

### Chapter 17: 실전 트레이딩 고려사항
**Real-World Trading Considerations**
- 슬리피지 모델링 (Slippage modeling)
- 거래 비용과 세금 (Commission, fees, taxes)
- 시장 영향과 체결 가능성 (Market impact, fill probability)
- 주문 유형 (Market, Limit, Stop orders)
- 시장 체제 감지와 적응형 전략
- **Code**: Realistic trading simulation with costs

### Chapter 18: 완전한 전략 개발 프로세스
**Complete Strategy Development Process**
- Case Study: 실제 주식 시장 전략 개발
- 아이디어 → 가설 → 백테스트 → 검증 → 개선
- 여러 시장에서의 테스트 (주식, ETF, 암호화폐)
- 실전 배포 체크리스트
- 나만의 전략 개발하기
- **Code**: End-to-end strategy development project

---

## Appendices (부록)

### Appendix A: 주요 Python 라이브러리 치트시트
- Pandas, NumPy, Matplotlib 핵심 사용법
- Backtrader 치트시트
- yfinance 치트시트

### Appendix B: 수학적 배경
- 확률과 통계 기초
- 포트폴리오 이론 수식
- 최적화 기법

### Appendix C: 용어 사전
- 한영 용어 대조
- 금융 용어 설명
- 머신러닝 용어

### Appendix D: 참고 자료
- 추천 도서 및 논문
- 온라인 리소스
- 데이터 소스

---

## 학습 경로 (Learning Paths)

### 빠른 시작 경로 (Quick Start - 6 chapters)
Chapters 1-2 → 4-5 → 9 → 12
*기초 개념과 첫 전략을 빠르게 학습*

### 기술적 분석 중심 경로 (Technical Analysis Focus - 10 chapters)
Chapters 1-8 → 9 → 12-13
*전통적인 기술적 분석 전략에 집중*

### 머신러닝 중심 경로 (ML Focus - 11 chapters)
Chapters 1-4 → 6 → 9 → 12-13 → 15-16
*데이터 기반 머신러닝 전략 개발*

### 포트폴리오 관리 중심 경로 (Portfolio Management Focus - 11 chapters)
Chapters 1-4 → 9-13 → 17-18
*다종목 포트폴리오 구성과 리스크 관리*

### 완전 학습 경로 (Complete Path - 18 chapters)
Chapters 1-18 순서대로
*모든 내용을 체계적으로 학습*

---

## 책의 특징

✅ **균형 잡힌 커버리지**: 기술적 분석 (40%) + 머신러닝 (20%) + 포트폴리오 관리 (25%) + 실전 적용 (15%)

✅ **실용적 접근**: 모든 장에 실행 가능한 Python 코드 포함

✅ **수학적 엄밀성**: 주요 개념에 대한 수식과 이론적 배경 제공

✅ **점진적 학습**: 기초부터 고급까지 단계적 난이도 상승

✅ **실전 중심**: 실제 시장 데이터와 거래 비용을 고려한 현실적 백테스팅
