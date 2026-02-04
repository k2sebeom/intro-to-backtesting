---
title: "Chapter 3: 데이터 전처리와 수익률"
weight: 3
bookToc: true
---

# Chapter 3: 데이터 전처리와 수익률

이 챕터에서는 다운로드한 금융 데이터를 백테스팅에 적합한 형태로 전처리하는 방법을 배웁니다. 결측치 처리, 이상치 탐지, 데이터 정합성 검증을 다루고, 단순 수익률과 로그 수익률의 차이를 이해합니다.

## 3.1 데이터 전처리의 필요성

### 왜 전처리가 중요한가?

다운로드한 원시 데이터(Raw Data)는 다음과 같은 문제를 가질 수 있습니다:

1. **결측치 (Missing Values)**: 휴장일, 상장폐지, 데이터 수집 오류
2. **이상치 (Outliers)**: 비현실적인 가격 변동, 데이터 입력 오류
3. **중복 데이터**: 동일한 날짜의 중복 레코드
4. **데이터 불일치**: 논리적으로 맞지 않는 관계 (예: High < Low)
5. **타임존 문제**: 서로 다른 타임존의 데이터 혼재

이러한 문제들을 해결하지 않으면:
- ❌ 잘못된 백테스팅 결과
- ❌ 비현실적인 수익률 계산
- ❌ 전략 실행 오류 (NaN, Inf 등)

## 3.2 결측치 처리

### 결측치 확인

```python
import pandas as pd

# 데이터 로드
data = pd.read_csv('data/AAPL_5y.csv', index_col='Date', parse_dates=True)

# 결측치 확인
print(data.isnull().sum())

# 결측치 비율
missing_pct = (data.isnull().sum() / len(data)) * 100
print(f"\n결측치 비율:")
print(missing_pct)
```

### 결측치 처리 방법

**방법 1: 삭제 (Deletion)**
```python
# 결측치가 있는 행 삭제
data_clean = data.dropna()

# 특정 컬럼의 결측치만 삭제
data_clean = data.dropna(subset=['Close', 'Volume'])
```

**장점**: 간단하고 명확
**단점**: 데이터 손실, 시계열 연속성 깨짐

**방법 2: 전방 채우기 (Forward Fill)**
```python
# 이전 값으로 채우기
data_filled = data.fillna(method='ffill')

# 또는
data_filled = data.ffill()
```

**장점**: 시계열 연속성 유지
**단점**: 장기간 결측 시 부정확

**방법 3: 보간 (Interpolation)**
```python
# 선형 보간
data_interpolated = data.interpolate(method='linear')

# 시계열 보간
data_interpolated = data.interpolate(method='time')
```

**장점**: 더 정확한 추정
**단점**: 실제 데이터 아님

### 권장 사항

금융 데이터의 경우:
- **가격 데이터**: Forward fill 사용 (주말/휴장일은 이전 종가 유지)
- **거래량**: 0으로 채우거나 삭제
- **긴 공백**: 삭제 권장 (데이터 신뢰성 문제)

## 3.3 이상치 탐지

### 이상치란?

**이상치(Outlier)**는 다른 데이터와 크게 다른 값입니다. 금융 데이터에서:

- **정상적 이상치**: 실제 극단적 시장 상황 (블랙 먼데이, 플래시 크래시)
- **비정상적 이상치**: 데이터 오류, 입력 실수

### 이상치 탐지 방법

**방법 1: 통계적 방법 (Z-Score)**

$$Z = \frac{X - \mu}{\sigma}$$

$|Z| > 3$ 이면 이상치로 간주

**방법 2: IQR (Interquartile Range)**

$$IQR = Q3 - Q1$$
$$Outlier: X < Q1 - 1.5 \times IQR \text{ or } X > Q3 + 1.5 \times IQR$$

**중요**: 금융 데이터에서는 **이상치를 삭제하지 않는 것이 원칙**입니다!

이유:
- 실제 시장 상황 반영
- 극단적 상황에서의 전략 테스트 필요
- 리스크 관리 검증

## 3.4 데이터 정합성 검증

### 가격 논리 검증

OHLCV 데이터는 다음 관계를 만족해야 합니다:

$$High \geq \max(Open, Close)$$
$$Low \leq \min(Open, Close)$$
$$High \geq Low$$
$$Volume \geq 0$$

## 3.5 수익률 계산

### 단순 수익률 (Simple Returns)

**정의**:
$$R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1$$

**특징**:
- ✅ 직관적이고 이해하기 쉬움
- ✅ 실제 손익과 직접 연결
- ❌ 시간 가산성 없음 (여러 기간 합산 불가)

```python
# Pandas로 계산
simple_returns = data['Close'].pct_change()

# 수동 계산
simple_returns = (data['Close'] / data['Close'].shift(1)) - 1
```

### 로그 수익률 (Log Returns)

**정의**:
$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$$

**특징**:
- ✅ 시간 가산성: $r_{total} = r_1 + r_2 + ... + r_n$
- ✅ 대칭성: 상승 10%, 하락 10%가 대칭적
- ✅ 통계적 특성 우수 (정규분포에 가까움)
- ❌ 직관적이지 않음

```python
# Pandas로 계산
log_returns = np.log(data['Close'] / data['Close'].shift(1))

# 또는
log_returns = np.log(data['Close']).diff()
```

### 단순 vs. 로그 수익률 비교

**언제 무엇을 사용할까?**

| 용도 | 권장 |
|------|------|
| 일반 백테스팅 | 단순 수익률 |
| 통계 분석 | 로그 수익률 |
| 포트폴리오 최적화 | 로그 수익률 |
| 사용자 리포트 | 단순 수익률 |
| 리스크 모델링 | 로그 수익률 |

### 누적 수익률 계산

**단순 수익률의 누적**:
$$R_{cumulative} = \prod_{t=1}^{n}(1 + R_t) - 1$$

```python
# 방법 1: cumprod
cumulative_returns = (1 + simple_returns).cumprod() - 1

# 방법 2: 가격 비율
cumulative_returns = data['Close'] / data['Close'].iloc[0] - 1
```

**로그 수익률의 누적**:
$$r_{cumulative} = \sum_{t=1}^{n} r_t$$

```python
cumulative_log_returns = log_returns.cumsum()

# 단순 수익률로 변환
cumulative_simple_from_log = np.exp(cumulative_log_returns) - 1
```

## 3.6 벤치마크 비교

### 벤치마크란?

**벤치마크(Benchmark)**는 전략 성과를 평가하기 위한 비교 기준입니다.

일반적인 벤치마크:
- **S&P 500 (SPY)**: 미국 대형주
- **Nasdaq 100 (QQQ)**: 미국 기술주
- **Russell 2000 (IWM)**: 미국 소형주
- **국채 ETF (TLT)**: 채권
- **개별 종목**: 해당 종목의 Buy & Hold

### 초과 수익률 (Excess Returns)

전략의 실제 가치는 **벤치마크 대비 초과 수익률**로 측정됩니다.

$$\text{Excess Return} = R_{strategy} - R_{benchmark}$$

## 3.7 실습: 데이터 전처리 파이프라인

이제 완전한 데이터 전처리 파이프라인을 실행해봅시다.

### 코드 실행

```bash
cd codes
uv run chapter03/01_data_preprocessing.py
```

### 스크립트 개요

이 스크립트는 다음을 수행합니다:

1. **원시 데이터 로드**: Chapter 2에서 다운로드한 AAPL 데이터
2. **데이터 품질 분석**: 결측치, 중복, 이상치 확인
3. **전처리 실행**: 결측치 처리, 정합성 검증
4. **수익률 계산**: 단순 및 로그 수익률
5. **벤치마크 비교**: S&P 500 (SPY) 대비 성과
6. **시각화**: 전처리 전후 비교, 수익률 분포, 벤치마크 비교

## 3.8 다음 단계

### 이 챕터에서 배운 것

✅ **결측치 처리**: Forward fill, 삭제, 보간 방법
✅ **이상치 탐지**: Z-Score, IQR 방법
✅ **데이터 검증**: 가격 논리, 시계열 연속성
✅ **수익률 계산**: 단순 vs. 로그 수익률
✅ **벤치마크 비교**: 초과 수익률, 상대 성과
✅ **전처리 파이프라인**: 완전한 데이터 정제 프로세스

### 실습 과제

1. **다른 종목 전처리**: Tesla (TSLA) 또는 Microsoft (MSFT) 데이터를 전처리하고 AAPL과 비교해보세요.

2. **이상치 영향 분석**: 이상치를 포함한 경우와 제외한 경우의 통계를 비교해보세요.

3. **다양한 벤치마크**: SPY 외에 QQQ, IWM 등 다른 벤치마크와 비교해보세요.

4. **수익률 변환**: 단순 수익률과 로그 수익률의 차이가 큰 경우를 찾아보세요.

### 다음 챕터 미리보기

**Chapter 4: Backtrader 프레임워크 기초**에서는:
- Backtrader 아키텍처 이해 (Cerebro, Strategy, Data Feeds)
- 첫 번째 전략: Buy & Hold 구현
- 주문 실행과 포지션 관리
- 기본 성과 분석 (Analyzers 사용)
- 실전 백테스팅 시작

---

**💡 핵심 메시지**

깨끗한 데이터는 신뢰할 수 있는 백테스팅의 기초입니다. 결측치, 이상치, 데이터 불일치를 체계적으로 처리하고, 올바른 수익률 계산 방법을 사용하며, 항상 벤치마크와 비교하여 전략의 실제 가치를 평가해야 합니다.

다음 챕터에서는 드디어 Backtrader를 사용하여 실제 트레이딩 전략을 구현해봅시다!
