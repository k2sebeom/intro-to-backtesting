---
title: "Chapter 2: 금융 데이터 다운로드와 이해"
weight: 2
bookToc: true
---

# Chapter 2: 금융 데이터 다운로드와 이해

이 챕터에서는 백테스팅의 필수 재료인 **금융 데이터**를 다루는 방법을 배웁니다. yfinance 라이브러리를 사용하여 실제 주식 데이터를 다운로드하고, OHLCV 데이터 구조를 이해하며, 배당금과 주식 분할을 처리하는 방법을 알아봅니다.

## 2.1 OHLCV 데이터 구조

### OHLCV란?

금융 시장 데이터의 표준 형식인 **OHLCV**는 다음 5가지 정보로 구성됩니다:

- **Open (시가)**: 해당 기간의 첫 거래 가격
- **High (고가)**: 해당 기간의 최고 거래 가격
- **Low (저가)**: 해당 기간의 최저 거래 가격
- **Close (종가)**: 해당 기간의 마지막 거래 가격
- **Volume (거래량)**: 해당 기간의 총 거래된 주식 수

### 시간 프레임 (Timeframe)

OHLCV 데이터는 다양한 시간 단위로 제공됩니다:

- **1분봉 (1-minute)**: 매 1분마다의 OHLCV
- **1시간봉 (1-hour)**: 매 1시간마다의 OHLCV
- **일봉 (Daily)**: 매 거래일마다의 OHLCV
- **주봉 (Weekly)**: 매 주마다의 OHLCV
- **월봉 (Monthly)**: 매 월마다의 OHLCV

### 캔들스틱 해석

하나의 OHLCV 데이터는 **캔들스틱(Candlestick)**으로 시각화됩니다:

```
High (고가)
   |
   |------- Close (종가가 시가보다 높으면 상승 캔들)
   |      |
   |      |
   |------- Open (시가)
   |
Low (저가)
```

**상승 캔들 (Bullish Candle)**:
- Close > Open (종가가 시가보다 높음)
- 보통 녹색 또는 흰색으로 표시
- 매수 압력이 강했음을 의미

**하락 캔들 (Bearish Candle)**:
- Close < Open (종가가 시가보다 낮음)
- 보통 빨간색 또는 검은색으로 표시
- 매도 압력이 강했음을 의미

### 캔들스틱의 수학적 특성

각 캔들스틱에서 계산할 수 있는 유용한 지표들:

**1. 몸통 크기 (Body Size)**:
$$\text{Body} = |Close - Open|$$

큰 몸통은 강한 추세를 의미합니다.

**2. 위 꼬리 길이 (Upper Shadow)**:
$$\text{Upper Shadow} = High - \max(Open, Close)$$

긴 위 꼬리는 상승 시도가 거부당했음을 의미합니다.

**3. 아래 꼬리 길이 (Lower Shadow)**:
$$\text{Lower Shadow} = \min(Open, Close) - Low$$

긴 아래 꼬리는 하락 시도가 거부당했음을 의미합니다.

**4. True Range (진정한 변동폭)**:
$$TR = \max(High - Low, |High - Close_{prev}|, |Low - Close_{prev}|)$$

True Range는 갭(Gap)을 고려한 실제 변동성을 측정합니다.

## 2.2 yfinance로 데이터 다운로드

### yfinance란?

**yfinance**는 Yahoo Finance에서 금융 데이터를 무료로 다운로드할 수 있는 Python 라이브러리입니다.

**장점**:
- ✅ 완전 무료
- ✅ 수천 개의 주식, ETF, 인덱스 지원
- ✅ 과거 데이터 제공 (최대 수십 년)
- ✅ 배당금 및 주식 분할 자동 조정
- ✅ 간단한 API

**단점**:
- ⚠️ 실시간 데이터 아님 (15-20분 지연)
- ⚠️ 일부 소형주는 데이터가 없을 수 있음
- ⚠️ API 변경 가능성 (Yahoo에서 공식 지원하지 않음)

### 기본 사용법

단일 종목 다운로드:

```python
import yfinance as yf

# 애플 주식 데이터 다운로드
ticker = yf.Ticker("AAPL")
data = ticker.history(period="1y")  # 최근 1년

print(data.head())
```

결과:
```
                 Open       High        Low      Close    Volume  Dividends  Stock Splits
Date
2024-01-02  187.15  188.44  185.83  185.64  82488400       0.0          0.0
2024-01-03  185.89  186.67  183.43  184.25  58414400       0.0          0.0
2024-01-04  184.35  186.40  183.92  185.59  54480100       0.0          0.0
...
```

### 다양한 기간 옵션

```python
# 방법 1: 기간(period) 지정
data = ticker.history(period="1mo")   # 최근 1개월
data = ticker.history(period="1y")    # 최근 1년
data = ticker.history(period="5y")    # 최근 5년
data = ticker.history(period="max")   # 모든 데이터

# 방법 2: 시작일과 종료일 지정
data = ticker.history(start="2020-01-01", end="2023-12-31")
```

### 다양한 시간 프레임

```python
# 일봉 (기본값)
data = ticker.history(period="1y", interval="1d")

# 주봉
data = ticker.history(period="2y", interval="1wk")

# 월봉
data = ticker.history(period="5y", interval="1mo")

# 1시간봉 (최근 60일까지만 가능)
data = ticker.history(period="1mo", interval="1h")

# 1분봉 (최근 7일까지만 가능)
data = ticker.history(period="1d", interval="1m")
```

## 2.3 배당금과 주식 분할 조정

### Adjusted Close의 중요성

**문제 상황**:
- 2020년 1월 1일: Apple 주가 $300
- 2020년 8월 31일: 4:1 주식 분할 실행
- 2020년 9월 1일: Apple 주가 $100 (분할 후)

만약 조정하지 않으면, 8월 31일에서 9월 1일로 넘어갈 때 -66%의 손실이 발생한 것처럼 보입니다! 하지만 실제로는 가치가 변하지 않았습니다.

### Adjusted Close란?

**Adjusted Close (조정 종가)**는 다음을 고려하여 과거 가격을 조정한 값입니다:

1. **배당금 (Dividends)**: 배당금 지급으로 인한 가격 하락 반영
2. **주식 분할 (Stock Splits)**: 주식 분할로 인한 가격 변화 반영

### 조정 공식

**주식 분할 조정**:
- 4:1 분할이 발생하면, 분할 이전의 모든 가격을 1/4로 조정

**배당금 조정**:
$$P_{adjusted} = P_{actual} \times \frac{Close_{today}}{Close_{today} + Dividend}$$

### yfinance의 자동 조정

yfinance는 기본적으로 조정된 가격을 제공합니다:

```python
data = ticker.history(period="5y")

# Close: 조정된 종가 (Adjusted Close)
# 이미 배당금과 주식 분할이 반영되어 있음
print(data['Close'])
```

**중요**: 백테스팅에서는 **반드시 Adjusted Close를 사용**해야 합니다. 그렇지 않으면 잘못된 수익률을 계산하게 됩니다.

## 2.4 다중 종목 데이터 다운로드

### 여러 종목 동시 다운로드

```python
import yfinance as yf

# 여러 종목을 한 번에 다운로드
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
data = yf.download(tickers, start="2020-01-01", end="2023-12-31")

# 결과는 MultiIndex DataFrame
print(data['Close'])  # 모든 종목의 종가
```

결과:
```
Ticker         AAPL    MSFT   GOOGL    TSLA
Date
2020-01-02   73.06   158.78   67.42   29.53
2020-01-03   72.34   157.32   67.11   29.17
...
```

### 개별 종목 추출

```python
# 단일 종목 추출
aapl_close = data['Close']['AAPL']

# 여러 종목 추출
tech_stocks = data['Close'][['AAPL', 'MSFT', 'GOOGL']]
```

## 2.5 다중 타임프레임 분석

### 왜 다중 타임프레임인가?

**큰 그림 파악**: 일봉에서는 하락 추세지만, 주봉에서는 상승 추세일 수 있습니다.

**트레이딩 전략 예시**:
- **주봉**: 전체 추세 파악 (상승 추세인가?)
- **일봉**: 진입 시점 찾기 (언제 매수할까?)
- **1시간봉**: 정확한 타이밍 (지금 바로 매수할까?)

### 다중 타임프레임 데이터 수집

```python
ticker = yf.Ticker("SPY")

# 여러 타임프레임 데이터
daily = ticker.history(period="1y", interval="1d")
weekly = ticker.history(period="2y", interval="1wk")
monthly = ticker.history(period="5y", interval="1mo")
```

### 타임프레임 간 전환

pandas의 `resample()` 함수로 타임프레임 변환:

```python
# 일봉 → 주봉
weekly_from_daily = daily.resample('W').agg({
    'Open': 'first',   # 주의 첫 거래일 시가
    'High': 'max',     # 주 중 최고가
    'Low': 'min',      # 주 중 최저가
    'Close': 'last',   # 주의 마지막 거래일 종가
    'Volume': 'sum'    # 주간 총 거래량
})
```

## 2.6 종목 정보 조회

### 기본 정보

```python
ticker = yf.Ticker("AAPL")

# 회사 정보
info = ticker.info

print(f"회사명: {info['longName']}")
print(f"섹터: {info['sector']}")
print(f"산업: {info['industry']}")
print(f"시가총액: ${info['marketCap']:,}")
print(f"직원 수: {info['fullTimeEmployees']:,}")
```

### 재무 데이터

```python
# 재무제표
income_stmt = ticker.income_stmt        # 손익계산서
balance_sheet = ticker.balance_sheet    # 재무상태표
cash_flow = ticker.cashflow             # 현금흐름표

# 배당금 이력
dividends = ticker.dividends
print(dividends.tail())

# 주식 분할 이력
splits = ticker.splits
print(splits)
```

## 2.7 실습: 주식 데이터 탐색

이제 실제 코드를 실행해봅시다.

### 코드 실행

```bash
cd codes
uv run chapter02/01_download_and_explore.py
```

### 스크립트 개요

이 스크립트는 다음을 수행합니다:

1. **단일 종목 다운로드**: Apple (AAPL) 주식 데이터
2. **OHLCV 분석**: 기본 통계 및 캔들스틱 패턴
3. **다중 종목 비교**: AAPL, MSFT, GOOGL, NVDA
4. **타임프레임 비교**: 일봉 vs. 주봉 vs. 월봉
5. **시각화**: 가격 차트, 거래량, 캔들스틱 차트

### 실행 결과

실제로 스크립트를 실행한 결과입니다:

```
==========================================
Chapter 2: 금융 데이터 다운로드와 이해
==========================================

=== AAPL 데이터 다운로드 ===
기간: 2021-02-06 ~ 2026-02-05 (5년)
총 데이터 포인트: 1254개

회사 정보:
- 이름: Apple Inc.
- 섹터: Technology
- 시가총액: $4,063,829,426,176

==========================================
=== OHLCV 기본 통계 ===
==========================================
평균 종가: $181.96
최고가: $288.62 (2025-12-03)
최저가: $113.29 (2021-03-08)

일일 변동폭 (High-Low):
- 평균: $3.75 (2.09%)
- 최대: $28.62 (14.44%)

==========================================
=== 캔들스틱 패턴 분석 ===
==========================================
상승 캔들: 671개 (53.5%)
하락 캔들: 583개 (46.5%)

평균 몸통 크기: $1.86
평균 위 꼬리: $0.95
평균 아래 꼬리: $0.94

==========================================
=== 다중 종목 비교 (최근 1y) ===
==========================================
AAPL: +19.5%
MSFT: +1.0%
GOOGL: +74.7%
NVDA: +39.6%

==========================================
=== SPY 타임프레임 비교 ===
==========================================
일봉 (1년):
  데이터 포인트: 251개
  수익률: +14.9%
  변동성 (일일): 1.22%
주봉 (2년):
  데이터 포인트: 105개
  수익률: +40.3%
  변동성 (일일): 2.07%
월봉 (5년):
  데이터 포인트: 60개
  수익률: +85.5%
  변동성 (일일): 4.44%

차트 저장 완료: chapter02/images/data_exploration.png
```

### 결과 분석

![데이터 탐색 차트](/images/chapter02/data_exploration.png)

생성된 차트는 6개의 서브플롯으로 구성되어 있으며, 각각 다른 측면의 데이터를 보여줍니다:

#### 1. AAPL 가격 추세 (좌상단)
- **5년간 추세**: $113 (2021년 최저점) → $288 (2025년 최고점)
- **주요 구간**:
  - 2021-2022: 완만한 상승 ($113 → $175)
  - 2023: 횡보 구간
  - 2024-2025: 급격한 상승 ($175 → $288)
  - 2026년 초: 소폭 조정
- **거래량**: 가격이 급변할 때 거래량도 함께 증가하는 패턴

#### 2. 캔들스틱 차트 60일 (우상단)
- 최근 60일간의 상세 가격 변동
- **녹색 캔들**: 상승일 (종가 > 시가)
- **빨간색 캔들**: 하락일 (종가 < 시가)
- 긴 위/아래 꼬리는 장중 변동성이 컸음을 의미

#### 3. 다중 종목 비교 (좌하단)
- **정규화된 비교** (시작점을 100으로 통일)
- **GOOGL이 가장 높은 성과**: 초기 대비 180% 상승
- **NVDA도 강한 상승세**: 약 140% 상승
- **AAPL과 MSFT**: 상대적으로 안정적인 상승 (120% 수준)
- **핵심 인사이트**: 같은 기술 섹터라도 종목별 성과는 크게 다릅니다

#### 4. 타임프레임 비교 (우하단)
- **일봉 (파란색)**: 노이즈가 많지만 단기 트렌드 파악 가능
- **주봉 (녹색)**: 더 부드러운 추세선, 중기 추세 명확
- **월봉 (주황색)**: 가장 부드러운 곡선, 장기 추세만 보임
- **전략 적용**: 장기 투자자는 월봉, 단기 트레이더는 일봉 활용

### 데이터 품질 관찰

**캔들스틱 패턴 분석 결과**:
- 상승 캔들 비율 53.5%는 장기적으로 상승 추세임을 의미
- 평균 몸통 크기 $1.86는 일일 평균 변동폭
- 위/아래 꼬리가 비슷하다는 것은 매수/매도 압력이 균형적임을 의미

**일일 변동폭**:
- 평균 2.09%는 AAPL이 안정적인 대형주임을 보여줍니다
- 최대 변동폭 14.44%는 극단적 시장 상황(실적 발표, 시장 폭락 등)
- 이러한 이상치는 리스크 관리에서 중요한 고려사항입니다

## 2.8 데이터 저장 및 관리

### CSV로 저장

```python
# 데이터 저장
data.to_csv('data/AAPL_daily_2020_2023.csv')

# 데이터 불러오기
import pandas as pd
data = pd.read_csv('data/AAPL_daily_2020_2023.csv',
                   index_col='Date',
                   parse_dates=True)
```

### 데이터 캐싱 전략

**문제**: yfinance로 매번 다운로드하면 시간이 걸립니다.

**해결책**: 로컬에 저장하고 재사용

```python
from pathlib import Path
import pandas as pd
import yfinance as yf

def get_stock_data(ticker, start, end, force_download=False):
    """
    주식 데이터를 가져오는 함수 (캐싱 포함)

    Parameters:
    -----------
    ticker : str
        종목 심볼
    start : str
        시작일
    end : str
        종료일
    force_download : bool
        True면 항상 새로 다운로드

    Returns:
    --------
    pd.DataFrame
        OHLCV 데이터
    """
    cache_dir = Path('data')
    cache_dir.mkdir(exist_ok=True)

    cache_file = cache_dir / f"{ticker}_{start}_{end}.csv"

    # 캐시 파일이 있고, 강제 다운로드가 아니면 캐시 사용
    if cache_file.exists() and not force_download:
        print(f"캐시에서 {ticker} 데이터 로드 중...")
        return pd.read_csv(cache_file, index_col='Date', parse_dates=True)

    # 새로 다운로드
    print(f"Yahoo Finance에서 {ticker} 다운로드 중...")
    data = yf.download(ticker, start=start, end=end, progress=False)

    # 캐시 저장
    data.to_csv(cache_file)
    print(f"캐시 저장 완료: {cache_file}")

    return data
```

사용 예:
```python
# 첫 실행: 다운로드 후 저장
data = get_stock_data("AAPL", "2020-01-01", "2023-12-31")

# 두 번째 실행: 캐시에서 즉시 로드
data = get_stock_data("AAPL", "2020-01-01", "2023-12-31")
```

## 2.9 데이터 품질 확인

### 결측치 확인

```python
# 결측치 확인
print(data.isnull().sum())

# 결측치 비율
missing_pct = (data.isnull().sum() / len(data)) * 100
print(f"결측치 비율: {missing_pct:.2f}%")
```

### 데이터 연속성 확인

```python
# 거래일 간 간격 확인
date_diff = data.index.to_series().diff()

# 3일 이상 간격이 있는 경우 찾기 (주말 제외)
gaps = date_diff[date_diff > pd.Timedelta(days=3)]
if len(gaps) > 0:
    print(f"데이터 간격 발견: {len(gaps)}개")
    print(gaps)
```

### 이상치 탐지

```python
# 일일 수익률 계산
returns = data['Close'].pct_change()

# 극단적 수익률 (±10% 이상)
extreme_returns = returns[abs(returns) > 0.10]
print(f"극단적 변동: {len(extreme_returns)}일")
print(extreme_returns)
```

## 2.10 다음 단계

### 이 챕터에서 배운 것

✅ **OHLCV 데이터 구조**: Open, High, Low, Close, Volume의 의미
✅ **yfinance 사용법**: 단일/다중 종목, 다양한 기간과 타임프레임
✅ **Adjusted Close**: 배당금과 주식 분할 조정의 중요성
✅ **다중 타임프레임**: 일봉, 주봉, 월봉 데이터 활용
✅ **데이터 관리**: 저장, 캐싱, 품질 확인

### 실습 과제

1. **다른 종목 탐색**: Tesla (TSLA), Amazon (AMZN) 데이터를 다운로드하고 비교해보세요.

2. **ETF 분석**: S&P 500 ETF (SPY)와 Nasdaq ETF (QQQ)의 최근 5년 성과를 비교해보세요.

3. **타임프레임 비교**: 같은 종목의 일봉과 월봉 차트를 그려보고, 어떤 차이가 있는지 관찰하세요.

4. **주식 분할 탐색**: Apple이나 Tesla의 주식 분할 이력을 조회하고, Adjusted vs. Unadjusted Close를 비교해보세요.

### 다음 챕터 미리보기

**Chapter 3: 데이터 전처리와 수익률**에서는:
- 결측치 및 이상치 처리 방법
- 데이터 정합성 검증 기법
- 단순 수익률 vs. 로그 수익률 비교
- 벤치마크 대비 초과 수익률 계산
- 완전한 데이터 전처리 파이프라인 구축

---

**💡 핵심 메시지**

데이터는 백테스팅의 기초입니다. 양질의 데이터 없이는 신뢰할 수 있는 백테스트 결과를 얻을 수 없습니다. yfinance는 무료로 사용할 수 있는 훌륭한 도구지만, 항상 데이터의 품질을 확인하고, Adjusted Close를 사용하며, 적절한 캐싱 전략을 구현하는 것이 중요합니다.

다음 챕터에서는 다운로드한 데이터를 정제하고 수익률을 계산하는 방법을 배워봅시다!
