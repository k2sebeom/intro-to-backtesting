# 백테스팅 입문 - 코드 예제

이 디렉토리에는 "백테스팅 입문" 책의 모든 코드 예제가 포함되어 있습니다.

## 설정

1. 이 디렉토리로 이동:
```bash
cd codes
```

2. Python 환경 초기화 (이미 되어있다면 생략):
```bash
uv init
```

3. 의존성 설치:
```bash
uv sync
```

## 사용법

각 챕터의 코드를 실행하려면:

```bash
uv run chapter01/download_data.py
uv run chapter01/basic_plotting.py
uv run chapter01/first_backtest.py
```

## 챕터별 코드

- `chapter01/`: 설정과 기초
  - `download_data.py`: 주식 데이터 다운로드
  - `basic_plotting.py`: 기본 차트 그리기
  - `first_backtest.py`: 첫 번째 백테스트

더 많은 챕터가 추가될 예정입니다.