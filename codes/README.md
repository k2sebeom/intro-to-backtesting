# 백테스팅 입문 - 코드 예제

이 디렉토리에는 "파이썬으로 배우는 백테스팅 입문" 책의 모든 코드 예제가 포함되어 있습니다.

## 환경 설정

### 1. uv 설치 (macOS)

```bash
# Homebrew를 사용한 설치
brew install uv

# 또는 curl을 사용한 설치
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 의존성 설치

```bash
# 프로젝트 디렉토리에서
uv sync
```

## 챕터별 실행 방법

### Chapter 1: 백테스팅 시작하기

```bash
# 환경 검증 및 첫 번째 스크립트 실행
uv run chapter01/01_hello_trading.py
```

이 스크립트는 다음을 수행합니다:
- 모든 필수 라이브러리 설치 확인
- 간단한 수익률 계산 예제
- 기본 통계 분석
- 시각화 차트 생성 (저장 위치: `chapter01/images/hello_trading.png`)

### Chapter 2: 금융 데이터 다운로드와 이해

```bash
# 실제 주식 데이터 다운로드 및 탐색
uv run chapter02/01_download_and_explore.py
```

이 스크립트는 다음을 수행합니다:
- Apple (AAPL) 주식 5년 데이터 다운로드
- OHLCV 기본 통계 및 캔들스틱 패턴 분석
- 다중 종목 비교 (AAPL, MSFT, GOOGL, NVDA)
- 다중 타임프레임 분석 (일봉, 주봉, 월봉)
- 종합 시각화 차트 생성 (저장 위치: `chapter02/images/data_exploration.png`)
- 데이터 캐싱 (`data/AAPL_5y.csv`)

### Chapter 3: 데이터 전처리와 수익률

```bash
# 데이터 품질 분석 및 전처리
uv run chapter03/01_data_preprocessing.py
```

이 스크립트는 다음을 수행합니다:
- 원시 데이터 품질 분석 (결측치, 중복, 이상치)
- 가격 논리 검증 (High >= Low, Volume >= 0 등)
- Z-Score를 사용한 이상치 탐지
- 단순 수익률 vs. 로그 수익률 계산 및 비교
- 벤치마크 (SPY) 대비 성과 분석
- 종합 시각화 (저장 위치: `chapter03/images/data_preprocessing.png`)

### Chapter 4: Backtrader 프레임워크 기초

```bash
# Buy & Hold 전략 백테스트
uv run chapter04/01_buy_and_hold.py
```

이 스크립트는 다음을 수행합니다:
- Backtrader로 Buy & Hold 전략 구현
- 초기 자금 $10,000, 수수료 0.1% 설정
- Analyzers를 사용한 성과 분석 (Sharpe Ratio, Drawdown, Returns)
- 벤치마크 (SPY) 비교
- 포트폴리오 가치 시각화 (저장 위치: `chapter04/images/buy_and_hold.png`)

### Chapter 5: 이동평균 전략

```bash
# 이동평균 크로스오버 전략
uv run chapter05/01_moving_average_strategy.py
```

이 스크립트는 다음을 수행합니다:
- SMA(50/200) 및 EMA(50/200) 크로스오버 전략 구현
- 골든 크로스/데드 크로스 신호 생성
- Buy & Hold 대비 성과 비교
- 추세 추종 전략의 장단점 분석
- 차트 저장 (저장 위치: `chapter05/images/moving_average_strategy.png`)

### Chapter 6: RSI 및 과매수/과매도 전략

```bash
# RSI 과매수/과매도 전략
uv run chapter06/01_rsi_strategy.py
```

이 스크립트는 다음을 수행합니다:
- RSI(14) 지표를 사용한 과매수/과매도 전략
- 기본 RSI(30/70), 보수적 RSI(20/80), 추세 필터 RSI 전략 비교
- 역추세(mean reversion) 전략 구현
- RSI와 가격 차트 시각화
- 차트 저장 (저장 위치: `chapter06/images/rsi_strategy.png`)

### Chapter 7: Bollinger Bands 전략

```bash
# Bollinger Bands 변동성 기반 전략
uv run chapter07/01_bollinger_bands_strategy.py
```

이 스크립트는 다음을 수행합니다:
- Bollinger Bands(20, 2) 계산 및 시각화
- 밴드 반등(Mean Reversion) 전략 구현
- 밴드 돌파(Breakout) 전략 구현
- %B 지표 기반 전략
- Bandwidth를 통한 변동성 분석
- 차트 저장 (저장 위치: `chapter07/images/bollinger_bands_strategy.png`)

### Chapter 8: 다중 지표 결합 전략

```bash
# 여러 지표를 결합한 전략
uv run chapter08/01_multi_indicator_strategy.py
```

이 스크립트는 다음을 수행합니다:
- 추세 확인 + 과매도 진입 전략 (SMA + RSI + BB)
- 골든 크로스 + 모멘텀 확인 전략 (SMA + RSI)
- 종합 신호 점수 전략 (다중 지표 가중 합산)
- 단일 지표 vs. 다중 지표 성과 비교
- 모든 지표를 한 화면에 시각화
- 차트 저장 (저장 위치: `chapter08/images/multi_indicator_strategy.png`)

### Chapter 9: 포지션 크기 결정

```bash
# 다양한 포지션 크기 결정 방법
uv run chapter09/01_position_sizing.py
```

이 스크립트는 다음을 수행합니다:
- 고정 비율 (95%, 50%) 포지션 크기
- 고정 위험 (1%) 포지션 크기
- 켈리 기준 (Half-Kelly) 포지션 크기
- 각 방법의 성과 비교 (수익률, Sharpe Ratio, MDD)
- 포트폴리오 가치 성장 곡선 시각화
- 차트 저장 (저장 위치: `chapter09/images/position_sizing.png`)

### Chapter 10: 리스크 관리와 손절매

```bash
# 손절매 및 익절매 전략
uv run chapter10/01_risk_management.py
```

이 스크립트는 다음을 수행합니다:
- 손절매 없는 전략 (기준선)
- 고정 비율 손절매/익절매 (2%/4%)
- ATR 기반 동적 손절매 (2×ATR)
- 추적 손절매 (5%)
- 손익비 및 승률 분석
- 위험-수익 프로파일 비교
- 차트 저장 (저장 위치: `chapter10/images/risk_management.png`)

### Chapter 11: 포트폴리오 구성과 분산투자

```bash
# 다중 자산 포트폴리오 전략
uv run chapter11/01_portfolio_diversification.py
```

이 스크립트는 다음을 수행합니다:
- 단일 자산 (AAPL) 전략
- 균등 비중 포트폴리오 (AAPL, MSFT, GOOGL, AMZN)
- 역변동성 포트폴리오
- 분기별 리밸런싱 구현
- 자산 간 상관관계 분석 및 히트맵
- 위험-수익 산점도
- 차트 저장 (저장 위치: `chapter11/images/portfolio_diversification.png`)

## 생성되는 파일들

- `data/`: 다운로드된 주식 데이터 (CSV 형식)
- `chapter*/images/`: 각 챕터에서 생성된 차트 이미지들

### Chapter 12: 성과 지표와 리스크 측정

```bash
# 종합 성과 분석 대시보드
uv run chapter12/01_performance_metrics.py
```

이 스크립트는 다음을 수행합니다:
- 수익률 지표: Total Return, Annualized Return, CAGR
- 리스크 지표: Volatility, Maximum Drawdown
- 리스크 조정 수익률: Sharpe, Sortino, Calmar Ratio
- 거래 통계: Win Rate, Profit Factor, Expectancy
- 종합 성과 대시보드 생성
- 차트 저장 (저장 위치: `chapter12/images/performance_dashboard.png`)

### Chapter 13: 백테스트 결과 분석과 시각화

```bash
# Equity Curve와 Drawdown 분석
uv run chapter13/01_equity_drawdown_charts.py

# 수익률 분포와 월별 히트맵
uv run chapter13/02_returns_analysis.py

# 개별 거래 분석
uv run chapter13/03_trade_analysis.py
```

이 스크립트들은 다음을 수행합니다:
- Equity Curve와 Drawdown 시각화
- 수익률 분포, Q-Q Plot, 정규성 검정
- 월별/연별 수익률 히트맵
- 거래 지속 기간 및 승패 분석
- 연속 승패 통계
- 차트 저장 (저장 위치: `chapter13/images/`)

### Chapter 14: 과최적화 방지와 검증

```bash
# Walk-Forward 분석
uv run chapter14/01_walk_forward_analysis.py

# Monte Carlo 시뮬레이션
uv run chapter14/02_monte_carlo_simulation.py
```

이 스크립트들은 다음을 수행합니다:
- 롤링 및 앵커드 Walk-Forward 분석
- Walk-Forward Efficiency (WFE) 계산
- Monte Carlo 거래 재샘플링
- 통계적 신뢰구간 계산
- 과최적화 여부 판단
- 차트 저장 (저장 위치: `chapter14/images/`)

### Chapter 15: 머신러닝 기반 전략 (Part 1)

```bash
# 특성 엔지니어링
uv run chapter15/01_feature_engineering.py

# ML 전략 구현
uv run chapter15/02_ml_strategy.py
```

이 스크립트들은 다음을 수행합니다:
- 기술적 지표를 ML 특성으로 변환
- Logistic Regression, Random Forest 모델 학습
- Time Series Split으로 교차 검증
- 모델 평가 (Accuracy, Precision, Recall, F1, AUC)
- Feature correlation 분석
- 차트 저장 (저장 위치: `chapter15/images/`)

### Chapter 16: 머신러닝 기반 전략 (Part 2)

```bash
# ML과 Backtrader 통합
uv run chapter16/01_ml_backtrader_integration.py
```

이 스크립트는 다음을 수행합니다:
- ML 모델을 Backtrader에 통합
- 확률 임계값 기반 거래
- 다양한 임계값으로 성과 비교
- 최적 확률 임계값 찾기
- 실전 ML 전략 구현

### Chapter 17: 실전 트레이딩 고려사항

```bash
# 거래 비용 영향 분석
uv run chapter17/01_realistic_trading_costs.py
```

이 스크립트는 다음을 수행합니다:
- 다양한 수수료 시나리오 테스트 (0%, 0.1%, 0.3%)
- 슬리피지 영향 분석 (0%, 0.05%, 0.1%)
- 현실적 비용 조합 테스트
- 거래 비용이 성과에 미치는 영향 정량화
- 비용별 성과 비교 차트
- 차트 저장 (저장 위치: `chapter17/images/`)

### Chapter 18: 완전한 전략 개발 프로세스

```bash
# 종합 전략 프레임워크
uv run chapter18/01_complete_strategy_framework.py
```

이 스크립트는 다음을 수행합니다:
- 전체 전략 개발 프로세스 시연
- In-Sample / Out-of-Sample 분할
- Walk-Forward Efficiency 계산
- 전략 배포 준비도 체크리스트
- 종합 성과 리포트 생성
- 실전 배포 가이드라인

## 생성되는 파일들

- `data/`: 다운로드된 주식 데이터 (CSV 형식)
- `chapter*/images/`: 각 챕터에서 생성된 차트 이미지들

## 주의사항

- 인터넷 연결이 필요합니다 (yfinance를 통한 데이터 다운로드)
- 생성된 이미지는 GUI 없이 파일로 저장됩니다
- 한글 폰트 관련 경고는 무시해도 됩니다 (차트는 정상적으로 생성됨)
- 일부 ML 모델 학습은 시간이 걸릴 수 있습니다

## 패키지 정보

주요 의존성:
- `yfinance`: Yahoo Finance 데이터 다운로드
- `pandas`: 데이터 조작 및 분석
- `matplotlib`: 데이터 시각화
- `seaborn`: 통계 시각화
- `backtrader`: 백테스팅 프레임워크
- `numpy`: 수치 계산
- `scikit-learn`: 머신러닝 모델
- `scipy`: 과학 계산 및 최적화

## 추천 학습 순서

1. **빠른 시작**: Chapters 1-2 → 4-5 → 9 → 12
2. **기술적 분석 중심**: Chapters 1-8 → 9 → 12-13
3. **머신러닝 중심**: Chapters 1-4 → 6 → 9 → 12-13 → 15-16
4. **포트폴리오 관리**: Chapters 1-4 → 9-13 → 17-18
5. **완전 학습**: Chapters 1-18 순서대로

---

**축하합니다! 모든 18개 챕터의 코드 예제가 준비되었습니다.**
**성공적인 백테스팅과 트레이딩을 기원합니다! 🚀📈**