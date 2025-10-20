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

### 챕터 1: 설정과 기초

```bash
# 1. 기본 데이터 다운로드 및 분석
uv run chapter01/01_basic_data_download.py

# 2. matplotlib 기초 플롯팅
uv run chapter01/02_matplotlib_basics.py

# 3. 첫 번째 백테스트
uv run chapter01/03_first_backtest.py
```

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