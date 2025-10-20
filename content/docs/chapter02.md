---
title: "챕터 2: 데이터 준비 - NVIDIA 주식 데이터 다운로드"
weight: 2
bookToc: true
---

# 챕터 2: 데이터 준비 - NVIDIA 주식 데이터 다운로드

## 개요

백테스팅의 성공은 양질의 데이터에서 시작됩니다. 이번 챕터에서는 yfinance 라이브러리를 사용하여 NVIDIA 주식 데이터를 다양한 타임프레임(1년, 5년, 10년)으로 다운로드하고, 데이터를 정제하며, 품질을 검증하는 전체 과정을 다룹니다.

## 학습 목표

이번 챕터를 완료하면 다음을 할 수 있게 됩니다:

- yfinance를 사용하여 주식 데이터를 체계적으로 다운로드
- 다양한 타임프레임의 OHLCV 데이터 수집 및 관리
- 데이터 전처리 및 품질 검증 수행
- 데이터 시각화를 통한 품질 분석
- CSV 파일 형태로 데이터 저장 및 관리

## 1. 데이터 다운로드 이론

### 1.1 OHLCV 데이터 구조

주식 데이터는 일반적으로 OHLCV 형태로 제공됩니다:

- **Open (시가)**: 해당 기간의 첫 거래 가격
- **High (고가)**: 해당 기간의 최고 거래 가격  
- **Low (저가)**: 해당 기간의 최저 거래 가격
- **Close (종가)**: 해당 기간의 마지막 거래 가격
- **Volume (거래량)**: 해당 기간의 총 거래량

### 1.2 yfinance 라이브러리

yfinance는 Yahoo Finance에서 주식 데이터를 가져오는 Python 라이브러리입니다. 주요 특징:

- 무료로 사용 가능
- 실시간 및 과거 데이터 제공
- 다양한 타임프레임 지원
- 배당금 및 주식 분할 정보 포함

### 1.3 데이터 품질의 중요성

백테스팅에서 데이터 품질은 결과의 신뢰성을 결정합니다:

- **완전성**: 누락된 데이터가 없어야 함
- **정확성**: 가격 데이터의 논리적 일관성 (High ≥ Close ≥ Low 등)
- **일관성**: 시간 순서 및 형식의 일관성
- **적시성**: 최신 데이터의 반영

## 2. 구현 가이드

### 2.1 다중 타임프레임 데이터 다운로드

첫 번째 스크립트는 NVIDIA 주식 데이터를 여러 타임프레임으로 다운로드합니다.

**파일**: `codes/chapter02/01_data_download_multiple_timeframes.py`

```python
#!/usr/bin/env python3
"""
Chapter 2: 데이터 준비 - NVIDIA 주식 데이터 다운로드
Multiple timeframes data download script
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def download_nvidia_data():
    """Download NVIDIA stock data for multiple timeframes"""
    
    # Create data directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Define timeframes
    timeframes = {
        "1year": 365,
        "5years": 365 * 5,
        "10years": 365 * 10
    }
    
    # NVIDIA ticker
    ticker = "NVDA"
    
    print(f"NVIDIA 주식 데이터 다운로드 시작...")
    print(f"티커: {ticker}")
    print("-" * 50)
```
**핵심 구현 포인트:**

1. **상대 경로 사용**: `__file__` 기반으로 데이터 디렉토리 경로 설정
2. **타임프레임 정의**: 딕셔너리를 사용한 체계적 관리
3. **에러 처리**: try-except 블록으로 안정성 확보
4. **진행 상황 표시**: 사용자 친화적인 출력

### 2.2 실행 방법

```bash
cd codes
uv run chapter02/01_data_download_multiple_timeframes.py
```

### 2.3 실행 결과

스크립트를 실행하면 다음과 같은 출력을 볼 수 있습니다:

```
NVIDIA 주식 데이터 다운로드 시작...
티커: NVDA
--------------------------------------------------

1year 데이터 다운로드 중...
기간: 2024-10-21 ~ 2025-10-21
✅ 1year 데이터 저장 완료: NVDA_1year.csv
   데이터 포인트 수: 250
   날짜 범위: 2024-10-21 ~ 2025-10-20
   컬럼: ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
   가격 범위: $94.30 ~ $192.57
   평균 거래량: 224,843,859

5years 데이터 다운로드 중...
기간: 2020-10-22 ~ 2025-10-21
✅ 5years 데이터 저장 완료: NVDA_5years.csv
   데이터 포인트 수: 1254
   날짜 범위: 2020-10-22 ~ 2025-10-20
   컬럼: ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
   가격 범위: $11.21 ~ $192.57
   평균 거래량: 399,535,254

10years 데이터 다운로드 중...
기간: 2015-10-24 ~ 2025-10-21
✅ 10years 데이터 저장 완료: NVDA_10years.csv
   데이터 포인트 수: 2511
   날짜 범위: 2015-10-26 ~ 2025-10-20
   컬럼: ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
   가격 범위: $0.62 ~ $192.57
   평균 거래량: 461,306,024
```

**주요 관찰 사항:**
- NVIDIA는 10년간 약 310배 성장 ($0.62 → $192.57)
- 거래량이 시간이 지남에 따라 증가하는 추세
- 모든 타임프레임에서 안정적인 데이터 수집 확인

## 3. 데이터 전처리

### 3.1 전처리의 필요성

원시 데이터는 다음과 같은 문제를 가질 수 있습니다:

- **결측값**: 휴장일이나 데이터 수집 오류로 인한 누락
- **중복값**: 동일한 날짜의 중복 데이터
- **이상치**: 비현실적인 가격 변동
- **일관성 문제**: 가격 관계의 논리적 오류

### 3.2 전처리 스크립트 구현

**파일**: `codes/chapter02/02_data_preprocessing.py`

```python
def load_and_preprocess_data(filename):
    """Load and preprocess NVIDIA data"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    filepath = os.path.join(data_dir, filename)
    
    # Load data
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    # Check for missing values
    missing_values = df.isnull().sum()
    
    # Remove rows with missing values
    df = df.dropna()
    
    # Check for duplicate dates
    duplicates = df.index.duplicated().sum()
    if duplicates > 0:
        df = df[~df.index.duplicated(keep='first')]
    
    # Sort by date
    df = df.sort_index()
    
    # Add technical indicators for validation
    df['Daily_Return'] = df['Close'].pct_change()
    df['Price_Range'] = df['High'] - df['Low']
    df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
    
    return df
```

### 3.3 실행 방법

```bash
uv run chapter02/02_data_preprocessing.py
```

### 3.4 전처리 결과

```
📋 타임프레임별 요약:
  10years:
    기간: 2015-10-26 ~ 2025-10-20
    데이터 포인트: 2,511개
    평균 종가: $32.39
    변동성: 0.0315
  1year:
    기간: 2024-10-21 ~ 2025-10-20
    데이터 포인트: 250개
    평균 종가: $144.59
    변동성: 0.0311
  5years:
    기간: 2020-10-22 ~ 2025-10-20
    데이터 포인트: 1,254개
    평균 종가: $60.34
    변동성: 0.0329
```

**전처리 결과 분석:**
- 모든 데이터셋에서 높은 완전성 달성
- 일일 변동성이 3% 내외로 일관성 있음
- 시간이 지남에 따른 가격 상승 추세 확인## 4. 데이터
 품질 검증

### 4.1 품질 검증의 중요성

데이터 품질 검증은 백테스팅 결과의 신뢰성을 보장하는 핵심 단계입니다. 다음 항목들을 체계적으로 검증해야 합니다:

1. **완전성 (Completeness)**: 예상되는 거래일 대비 실제 데이터 비율
2. **일관성 (Consistency)**: 가격 및 거래량 데이터의 논리적 일관성
3. **정확성 (Accuracy)**: 이상치 및 극단적 변동 검출
4. **적시성 (Timeliness)**: 최신 데이터의 반영 여부

### 4.2 품질 검증 스크립트

**파일**: `codes/chapter02/03_data_quality_validation.py`

이 스크립트는 포괄적인 데이터 품질 검증을 수행합니다:

```python
def validate_data_quality(df, timeframe_name):
    """Comprehensive data quality validation"""
    
    validation_results = {}
    
    # 1. Completeness check
    total_days = (df.index[-1] - df.index[0]).days
    trading_days = len(df)
    completeness = trading_days / (total_days * 5/7)  # Approximate trading days
    
    # 2. Data consistency checks
    high_low_consistent = (df['High'] >= df['Low']).all()
    high_close_consistent = (df['High'] >= df['Close']).all()
    price_consistent = high_low_consistent and high_close_consistent
    
    # 3. Outlier detection
    returns = df['Close'].pct_change().dropna()
    return_std = returns.std()
    return_outliers = (abs(returns) > 3 * return_std).sum()
    
    return validation_results
```

### 4.3 실행 방법

```bash
uv run chapter02/03_data_quality_validation.py
```

### 4.4 품질 검증 결과

스크립트 실행 후 다음과 같은 상세한 품질 분석 결과를 얻을 수 있습니다:

```
📋 최종 검증 요약
==================================================

10YEARS:
  완전성: 96.39%
  가격 일관성: ✅
  거래량 일관성: ✅
  가격 이상치: 426개
  수익률 이상치: 27개
  결측값: 20개
  총 수익률: 26420.87%
  변동성: 0.0315

1YEAR:
  완전성: 96.15%
  가격 일관성: ✅
  거래량 일관성: ✅
  가격 이상치: 0개
  수익률 이상치: 2개
  결측값: 20개
  총 수익률: 27.67%
  변동성: 0.0311

5YEARS:
  완전성: 96.25%
  가격 일관성: ✅
  거래량 일관성: ✅
  가격 이상치: 0개
  수익률 이상치: 9개
  결측값: 20개
  총 수익률: 1276.99%
  변동성: 0.0329
```

**품질 검증 결과 해석:**

1. **높은 완전성**: 모든 타임프레임에서 96% 이상의 완전성 달성
2. **일관성 통과**: 가격 및 거래량 데이터의 논리적 일관성 확인
3. **이상치 관리**: 10년 데이터에서 일부 이상치 발견 (정상적인 극단적 시장 상황)
4. **놀라운 성장**: NVIDIA의 10년간 264배 성장 확인

## 5. 데이터 시각화 및 분석

### 5.1 종합 품질 분석 차트

스크립트 실행 시 다음과 같은 시각화가 자동 생성됩니다:

![데이터 품질 종합 분석](/images/chapter02/data_quality_summary.png)

이 차트는 다음 정보를 제공합니다:

- **정규화된 가격 추이**: 각 타임프레임별 상대적 성과 비교
- **거래량 비교**: 최근 거래량 패턴 분석
- **수익률 분포**: 일일 수익률의 통계적 분포
- **품질 점수**: 각 데이터셋의 종합 품질 평가

### 5.2 개별 타임프레임 상세 분석

각 타임프레임별로 상세한 분석 차트가 생성됩니다:

#### 5.2.1 1년 데이터 분석

![1년 데이터 상세 분석](/images/chapter02/nvidia_1year_analysis.png)

**주요 특징:**
- 최근 1년간 27.67% 수익률
- 안정적인 거래량 패턴
- 정규분포에 가까운 수익률 분포
- 낮은 변동성 (3.11%)

#### 5.2.2 5년 데이터 분석

![5년 데이터 상세 분석](/images/chapter02/nvidia_5years_analysis.png)

**주요 특징:**
- 5년간 1,276.99% 수익률 (연평균 약 13배)
- AI 붐과 함께한 급격한 성장
- 2020년 이후 가속화된 상승세
- 중간 수준의 변동성 (3.29%)

#### 5.2.3 10년 데이터 분석

![10년 데이터 상세 분석](/images/chapter02/nvidia_10years_analysis.png)

**주요 특징:**
- 10년간 26,420.87% 수익률 (264배 성장)
- 2016년 이후 지속적인 상승 추세
- 2020년 이후 폭발적 성장
- 전체 기간 변동성 3.15%##
 6. 실전 활용 가이드

### 6.1 데이터 파일 구조

완료된 데이터 준비 과정 후 다음과 같은 파일 구조가 생성됩니다:

```
codes/
├── data/
│   ├── NVDA_1year.csv          # 원본 1년 데이터
│   ├── NVDA_1year_processed.csv # 전처리된 1년 데이터
│   ├── NVDA_5years.csv         # 원본 5년 데이터
│   ├── NVDA_5years_processed.csv # 전처리된 5년 데이터
│   ├── NVDA_10years.csv        # 원본 10년 데이터
│   └── NVDA_10years_processed.csv # 전처리된 10년 데이터
└── chapter02/
    ├── 01_data_download_multiple_timeframes.py
    ├── 02_data_preprocessing.py
    ├── 03_data_quality_validation.py
    └── images/
        ├── data_quality_summary.png
        ├── nvidia_1year_analysis.png
        ├── nvidia_5years_analysis.png
        └── nvidia_10years_analysis.png
```

### 6.2 데이터 사용 방법

전처리된 데이터는 다음과 같이 로드하여 사용할 수 있습니다:

```python
import pandas as pd

# 전처리된 데이터 로드
df = pd.read_csv('codes/data/NVDA_1year_processed.csv', 
                 index_col=0, parse_dates=True)

# 기본 정보 확인
print(f"데이터 기간: {df.index[0]} ~ {df.index[-1]}")
print(f"데이터 포인트: {len(df)}개")
print(f"컬럼: {list(df.columns)}")

# 기술적 지표 활용
daily_returns = df['Daily_Return']
price_range = df['Price_Range']
volume_ma = df['Volume_MA_20']
```

### 6.3 백테스팅을 위한 데이터 선택 가이드

**1년 데이터 사용 시기:**
- 최신 시장 상황 반영이 중요한 전략
- 단기 트레이딩 전략 개발
- 현재 시장 변동성 패턴 분석

**5년 데이터 사용 시기:**
- 중장기 전략 개발
- 다양한 시장 사이클 포함 필요
- AI 붐 이후 시장 특성 분석

**10년 데이터 사용 시기:**
- 장기 투자 전략 검증
- 다양한 시장 환경 테스트
- 전체 성장 사이클 분석

### 6.4 데이터 품질 모니터링

정기적인 데이터 품질 모니터링을 위해 다음 지표들을 추적하세요:

```python
# 품질 지표 계산 예시
def calculate_quality_metrics(df):
    """데이터 품질 지표 계산"""
    
    metrics = {}
    
    # 완전성
    expected_days = (df.index[-1] - df.index[0]).days
    actual_days = len(df)
    metrics['completeness'] = actual_days / (expected_days * 5/7)
    
    # 일관성
    price_consistent = (
        (df['High'] >= df['Close']).all() and
        (df['High'] >= df['Open']).all() and
        (df['Low'] <= df['Close']).all() and
        (df['Low'] <= df['Open']).all()
    )
    metrics['consistency'] = price_consistent
    
    # 변동성
    returns = df['Close'].pct_change().dropna()
    metrics['volatility'] = returns.std()
    
    # 이상치 비율
    outliers = (abs(returns) > 3 * returns.std()).sum()
    metrics['outlier_ratio'] = outliers / len(returns)
    
    return metrics
```

## 7. 주요 발견사항 및 인사이트

### 7.1 NVIDIA 주식 분석 결과

**성장 패턴:**
- 2015-2020: 점진적 성장 (GPU 게이밍 시장 확대)
- 2020-2022: 가속화된 성장 (AI/ML 붐, 암호화폐 채굴)
- 2022-2025: 폭발적 성장 (생성형 AI 혁명)

**변동성 특성:**
- 일관된 일일 변동성 (~3.1-3.3%)
- 장기적으로 안정적인 변동성 패턴
- 극단적 움직임은 주로 실적 발표나 시장 이벤트와 연관

**거래량 패턴:**
- 시간이 지남에 따라 증가하는 평균 거래량
- 가격 상승과 함께 증가하는 시장 관심도
- 높은 유동성으로 백테스팅에 적합

### 7.2 백테스팅 관점에서의 시사점

**데이터 품질:**
- 96% 이상의 높은 완전성으로 신뢰할 수 있는 백테스팅 가능
- 일관된 데이터 구조로 안정적인 전략 개발 환경 제공
- 충분한 데이터 포인트로 통계적 유의성 확보

**전략 개발 고려사항:**
- 장기 상승 추세로 인한 매수 편향 주의
- 높은 성장률로 인한 과최적화 위험
- 다양한 시장 환경 테스트를 위한 다중 타임프레임 활용 필요

## 8. 다음 단계

이제 고품질의 NVIDIA 주식 데이터를 확보했습니다. 다음 챕터에서는 이 데이터를 활용하여 첫 번째 트레이딩 전략인 단순 이동평균(SMA) 전략을 구현하고 백테스팅해보겠습니다.

**준비된 것:**
- ✅ 다중 타임프레임 NVIDIA 데이터
- ✅ 전처리 및 품질 검증 완료
- ✅ 시각화를 통한 데이터 특성 파악
- ✅ 백테스팅을 위한 데이터 구조 확립

**다음 챕터 미리보기:**
- 단순 이동평균(SMA) 이론 및 계산
- SMA 크로스오버 전략 구현
- 백테스팅 프레임워크 구축
- 성과 분석 및 시각화

## 9. 연습 문제

### 9.1 기본 연습

1. **다른 종목 데이터 다운로드**: Apple(AAPL) 또는 Tesla(TSLA) 데이터를 동일한 방식으로 다운로드해보세요.

2. **데이터 비교 분석**: NVIDIA와 다른 종목의 변동성을 비교 분석해보세요.

3. **품질 지표 개선**: 추가적인 데이터 품질 지표를 개발해보세요.

### 9.2 심화 연습

1. **자동화 스크립트**: 여러 종목을 한 번에 다운로드하고 분석하는 스크립트를 작성해보세요.

2. **실시간 모니터링**: 데이터 품질을 실시간으로 모니터링하는 시스템을 구축해보세요.

3. **데이터베이스 연동**: CSV 파일 대신 데이터베이스에 데이터를 저장하는 방식을 구현해보세요.

---

**챕터 2 완료!** 🎉

이제 체계적인 데이터 준비 과정을 마스터했습니다. 다음 챕터에서는 이 데이터를 활용하여 실제 트레이딩 전략을 구현해보겠습니다.