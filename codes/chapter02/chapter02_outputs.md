# Chapter 2 실행 결과 및 출력

## 개요
이 문서는 Chapter 2의 모든 스크립트 실행 결과와 생성된 출력물을 정리한 것입니다.

## 실행된 스크립트

### 1. 01_data_download_multiple_timeframes.py
**목적**: NVIDIA 주식 데이터를 여러 타임프레임(1년, 5년, 10년)으로 다운로드

**실행 결과**:
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

==================================================
데이터 다운로드 완료!

다운로드된 파일 목록:
  📁 NVDA_1year.csv (29,647 bytes)
  📁 NVDA_5years.csv (148,302 bytes)
  📁 NVDA_10years.csv (295,923 bytes)
```

**생성된 파일**:
- `codes/data/NVDA_1year.csv` - 1년간 NVIDIA 주식 데이터
- `codes/data/NVDA_5years.csv` - 5년간 NVIDIA 주식 데이터  
- `codes/data/NVDA_10years.csv` - 10년간 NVIDIA 주식 데이터

### 2. 02_data_preprocessing.py
**목적**: 다운로드된 데이터의 전처리 및 정제

**주요 처리 과정**:
- 결측값 확인 및 제거
- 중복 날짜 검사 및 제거
- 데이터 정렬
- 기술적 지표 추가 (일일 수익률, 가격 범위, 20일 이동평균 거래량)
- 데이터 품질 검사

**실행 결과 요약**:
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

**생성된 파일**:
- `codes/data/NVDA_1year_processed.csv` - 전처리된 1년 데이터
- `codes/data/NVDA_5years_processed.csv` - 전처리된 5년 데이터
- `codes/data/NVDA_10years_processed.csv` - 전처리된 10년 데이터

### 3. 03_data_quality_validation.py
**목적**: 데이터 품질 검증 및 시각화

**검증 항목**:
- 완전성 검사 (데이터 누락 확인)
- 일관성 검사 (가격 및 거래량 논리적 일관성)
- 이상치 검사 (극단적 가격 변동 및 수익률)
- 결측값 패턴 분석
- 분포 분석

**최종 검증 요약**:
```
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

**생성된 시각화 파일**:
- `data_quality_summary.png` - 전체 데이터 품질 요약 차트
- `nvidia_1year_analysis.png` - 1년 데이터 상세 분석
- `nvidia_5years_analysis.png` - 5년 데이터 상세 분석
- `nvidia_10years_analysis.png` - 10년 데이터 상세 분석

## 주요 발견사항

### 데이터 품질
1. **높은 완전성**: 모든 타임프레임에서 96% 이상의 완전성 달성
2. **일관성 통과**: 가격 및 거래량 데이터의 논리적 일관성 확인
3. **최소한의 결측값**: 각 데이터셋당 20개의 결측값 (주로 계산된 지표)

### NVIDIA 주식 성과
1. **10년 수익률**: 26,420.87% (연평균 약 264배 성장)
2. **5년 수익률**: 1,276.99% (연평균 약 13배 성장)
3. **1년 수익률**: 27.67% (최근 1년간 성장)

### 변동성 분석
- 10년: 3.15% (일일 표준편차)
- 5년: 3.29% (일일 표준편차)
- 1년: 3.11% (일일 표준편차)

### 극단적 움직임
- **최대 일일 상승**: 29.81% (10년 데이터)
- **최대 일일 하락**: -18.76% (10년 데이터)

## 파일 구조

```
codes/
├── chapter02/
│   ├── 01_data_download_multiple_timeframes.py
│   ├── 02_data_preprocessing.py
│   ├── 03_data_quality_validation.py
│   ├── images/
│   │   ├── data_quality_summary.png
│   │   ├── nvidia_1year_analysis.png
│   │   ├── nvidia_5years_analysis.png
│   │   └── nvidia_10years_analysis.png
│   └── chapter02_outputs.md
├── data/
│   ├── NVDA_1year.csv
│   ├── NVDA_1year_processed.csv
│   ├── NVDA_5years.csv
│   ├── NVDA_5years_processed.csv
│   ├── NVDA_10years.csv
│   └── NVDA_10years_processed.csv
└── static/images/chapter02/
    ├── data_quality_summary.png
    ├── nvidia_1year_analysis.png
    ├── nvidia_5years_analysis.png
    └── nvidia_10years_analysis.png
```

## 사용 방법

각 스크립트는 독립적으로 실행 가능하지만, 순서대로 실행하는 것을 권장합니다:

```bash
# codes 디렉토리에서 실행
uv run chapter02/01_data_download_multiple_timeframes.py
uv run chapter02/02_data_preprocessing.py
uv run chapter02/03_data_quality_validation.py
```

모든 스크립트는 `__file__` 기반의 상대 경로를 사용하여 어느 위치에서든 실행 가능합니다.