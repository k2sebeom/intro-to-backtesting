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

## 생성되는 파일들

- `data/`: 다운로드된 주식 데이터 (CSV 형식)
- `chapter*/images/`: 각 챕터에서 생성된 차트 이미지들

## 주의사항

- 인터넷 연결이 필요합니다 (yfinance를 통한 데이터 다운로드)
- 생성된 이미지는 GUI 없이 파일로 저장됩니다
- 한글 폰트 관련 경고는 무시해도 됩니다 (차트는 정상적으로 생성됨)

## 패키지 정보

주요 의존성:
- `yfinance`: Yahoo Finance 데이터 다운로드
- `pandas`: 데이터 조작 및 분석
- `matplotlib`: 데이터 시각화
- `backtrader`: 백테스팅 프레임워크
- `numpy`: 수치 계산
- `seaborn`: 고급 시각화