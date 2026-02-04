"""
Chapter 3: 데이터 전처리와 수익률
데이터 품질 분석, 전처리, 수익률 계산, 벤치마크 비교

이 스크립트는 다음을 수행합니다:
1. 원시 데이터 로드 및 품질 분석
2. 결측치 및 이상치 탐지
3. 데이터 정합성 검증
4. 단순 수익률 vs. 로그 수익률 계산
5. 벤치마크 (SPY) 대비 성과 비교
6. 종합 시각화
"""

import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf


def print_header():
    """프로그램 헤더 출력"""
    print("=" * 42)
    print("Chapter 3: 데이터 전처리와 수익률")
    print("=" * 42)
    print()


def load_data(data_dir):
    """원시 데이터 로드"""
    print("=== 원시 데이터 로드 ===")

    # Chapter 2에서 저장한 데이터 로드
    data_file = data_dir / "AAPL_5y.csv"

    if not data_file.exists():
        print(f"데이터 파일이 없습니다: {data_file}")
        print("Chapter 2를 먼저 실행하여 데이터를 다운로드하세요.")
        sys.exit(1)

    data = pd.read_csv(data_file, index_col='Date', parse_dates=True)

    print(f"데이터 기간: {data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"총 데이터 포인트: {len(data)}개\n")

    return data


def analyze_data_quality(data):
    """데이터 품질 분석"""
    print("=" * 42)
    print("=== 데이터 품질 분석 ===")
    print("=" * 42)

    # 결측치
    missing = data.isnull().sum()
    print("결측치:")
    for col in missing.index:
        print(f"{col:10s}: {missing[col]:3d}")

    # 중복
    duplicates = data.index.duplicated().sum()
    print(f"\n중복 날짜: {duplicates}개")

    # 정렬
    is_sorted = data.index.is_monotonic_increasing
    print(f"시간 순 정렬: {'✓' if is_sorted else '✗'}")

    # 거래일 간격
    date_diff = data.index.to_series().diff()
    weekday_diffs = date_diff[date_diff <= pd.Timedelta(days=3)]
    avg_gap = weekday_diffs.mean()
    print(f"평균 거래일 간격: {avg_gap}")

    print()


def validate_price_logic(data):
    """가격 논리 검증"""
    print("=" * 42)
    print("=== 가격 논리 검증 ===")
    print("=" * 42)

    checks = {
        'High >= Close': (data['High'] >= data['Close']).all(),
        'High >= Open': (data['High'] >= data['Open']).all(),
        'Low <= Close': (data['Low'] <= data['Close']).all(),
        'Low <= Open': (data['Low'] <= data['Open']).all(),
        'High >= Low': (data['High'] >= data['Low']).all(),
        'Volume >= 0': (data['Volume'] >= 0).all(),
    }

    for check, result in checks.items():
        print(f"{check}: {'✓' if result else '✗'}")

    all_passed = all(checks.values())
    print(f"전체 검증: {'통과 ✓' if all_passed else '실패 ✗'}")
    print()

    return all_passed


def detect_outliers(data, column='Close', threshold=3):
    """이상치 탐지 (Z-Score 방법)"""
    print("=" * 42)
    print(f"=== 이상치 탐지 (Z-Score) ===")
    print("=" * 42)

    # 수익률 계산
    returns = data[column].pct_change().dropna()

    # Z-Score 계산 (numpy로 직접 계산)
    mean = returns.mean()
    std = returns.std()
    z_scores = np.abs((returns - mean) / std)

    # 이상치 판단
    outliers = z_scores > threshold
    outlier_count = outliers.sum()

    print(f"발견된 이상치: {outlier_count}개")

    if outlier_count > 0:
        outlier_dates = returns[outliers].index.tolist()[:5]  # 처음 5개만
        print("이상치 날짜 (처음 5개):")
        for date in outlier_dates:
            ret = returns.loc[date]
            print(f"{date.strftime('%Y-%m-%d')}: {ret:+.4f} ({ret*100:+.2f}%)")

    print()
    return outliers


def calculate_returns(data):
    """수익률 계산"""
    print("=" * 42)
    print("=== 수익률 계산 ===")
    print("=" * 42)

    # 단순 수익률
    simple_returns = data['Close'].pct_change().dropna()

    # 로그 수익률
    log_returns = np.log(data['Close'] / data['Close'].shift(1)).dropna()

    # 통계
    print("단순 수익률:")
    print(f"- 평균: {simple_returns.mean():.4f} ({simple_returns.mean()*100:.2f}%)")
    print(f"- 표준편차: {simple_returns.std():.4f} ({simple_returns.std()*100:.2f}%)")
    print(f"- 최대: {simple_returns.max():+.4f} ({simple_returns.max()*100:+.2f}%)")
    print(f"- 최소: {simple_returns.min():+.4f} ({simple_returns.min()*100:+.2f}%)")

    print("\n로그 수익률:")
    print(f"- 평균: {log_returns.mean():.4f} ({log_returns.mean()*100:.2f}%)")
    print(f"- 표준편차: {log_returns.std():.4f} ({log_returns.std()*100:.2f}%)")
    print(f"- 최대: {log_returns.max():+.4f} ({log_returns.max()*100:+.2f}%)")
    print(f"- 최소: {log_returns.min():+.4f} ({log_returns.min()*100:+.2f}%)")

    # 누적 수익률
    cum_simple = (1 + simple_returns).prod() - 1
    cum_log = np.exp(log_returns.sum()) - 1

    print(f"\n누적 수익률:")
    print(f"- 단순 수익률: {cum_simple:+.4f} ({cum_simple*100:+.2f}%)")
    print(f"- 로그 수익률: {cum_log:+.4f} ({cum_log*100:+.2f}%)")
    print()

    return simple_returns, log_returns


def compare_benchmark(aapl_data):
    """벤치마크 (SPY) 비교"""
    print("=" * 42)
    print("=== 벤치마크 비교 (vs SPY) ===")
    print("=" * 42)

    # SPY 데이터 다운로드
    start_date = aapl_data.index[0]
    end_date = aapl_data.index[-1]

    spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)

    # 수익률 계산
    aapl_ret = (aapl_data['Close'].iloc[-1] / aapl_data['Close'].iloc[0] - 1) * 100

    # Handle potential multi-index from yfinance
    if isinstance(spy_data.columns, pd.MultiIndex):
        spy_close = spy_data[('Close', 'SPY')]
    else:
        spy_close = spy_data['Close']

    spy_ret = (spy_close.iloc[-1] / spy_close.iloc[0] - 1) * 100
    excess_ret = aapl_ret - spy_ret

    print(f"AAPL 수익률: {aapl_ret:+.2f}%")
    print(f"SPY 수익률: {spy_ret:+.2f}%")
    print(f"초과 수익률: {excess_ret:+.2f}%")

    # 일일 승률
    aapl_daily = aapl_data['Close'].pct_change().dropna()
    spy_daily = spy_close.pct_change().dropna()

    # 공통 날짜만 사용
    common_dates = aapl_daily.index.intersection(spy_daily.index)

    if len(common_dates) > 0:
        aapl_common = aapl_daily.loc[common_dates]
        spy_common = spy_daily.loc[common_dates]
        win_days = (aapl_common > spy_common).sum()
        win_rate = (win_days / len(common_dates)) * 100
        print(f"일일 승률: {win_rate:.1f}%")
    else:
        print("일일 승률: 계산 불가 (공통 날짜 없음)")

    print()

    return spy_close, excess_ret


def create_visualizations(data, simple_returns, log_returns, spy_close):
    """종합 시각화"""
    print("차트 생성 중...")

    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(16, 12))

    # 1. 가격 및 거래량
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(data.index, data['Close'], linewidth=2, color='#2E86AB', label='AAPL')
    ax1.set_title('AAPL Price (5 Years)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 단순 수익률 분포
    ax2 = plt.subplot(3, 2, 2)
    ax2.hist(simple_returns * 100, bins=50, alpha=0.7, color='#2E86AB', edgecolor='black')
    ax2.axvline(simple_returns.mean() * 100, color='red', linestyle='--', linewidth=2, label=f'Mean: {simple_returns.mean()*100:.2f}%')
    ax2.set_title('Simple Returns Distribution', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Return (%)')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. 로그 수익률 분포
    ax3 = plt.subplot(3, 2, 3)
    ax3.hist(log_returns * 100, bins=50, alpha=0.7, color='#A23B72', edgecolor='black')
    ax3.axvline(log_returns.mean() * 100, color='red', linestyle='--', linewidth=2, label=f'Mean: {log_returns.mean()*100:.2f}%')
    ax3.set_title('Log Returns Distribution', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Return (%)')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. 누적 수익률 비교
    ax4 = plt.subplot(3, 2, 4)
    cum_simple = (1 + simple_returns).cumprod() - 1
    cum_log = np.exp(log_returns.cumsum()) - 1

    ax4.plot(cum_simple.index, cum_simple * 100, linewidth=2, label='Simple Returns', color='#2E86AB')
    ax4.plot(cum_log.index, cum_log * 100, linewidth=2, label='Log Returns', color='#A23B72', linestyle='--')
    ax4.set_title('Cumulative Returns Comparison', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Cumulative Return (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 5. AAPL vs SPY 정규화 비교
    ax5 = plt.subplot(3, 2, 5)
    aapl_norm = (data['Close'] / data['Close'].iloc[0]) * 100
    spy_norm = (spy_close / spy_close.iloc[0]) * 100

    ax5.plot(aapl_norm.index, aapl_norm, linewidth=2, label='AAPL', color='#2E86AB')
    ax5.plot(spy_norm.index, spy_norm, linewidth=2, label='SPY', color='#F18F01')
    ax5.set_title('AAPL vs SPY (Normalized)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Normalized Price (Start = 100)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 6. 일일 수익률 시계열
    ax6 = plt.subplot(3, 2, 6)
    ax6.plot(simple_returns.index, simple_returns * 100, linewidth=1, alpha=0.7, color='#2E86AB')
    ax6.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax6.axhline(simple_returns.mean() * 100, color='red', linestyle='--', linewidth=1, label='Mean')
    ax6.set_title('Daily Returns Time Series', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Return (%)')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()

    # 저장
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    images_dir.mkdir(exist_ok=True)

    output_path = images_dir / "data_preprocessing.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def main():
    """메인 함수"""
    # 헤더
    print_header()

    # 데이터 디렉토리
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    # 1. 데이터 로드
    data = load_data(data_dir)

    # 2. 품질 분석
    analyze_data_quality(data)

    # 3. 가격 논리 검증
    validate_price_logic(data)

    # 4. 이상치 탐지
    outliers = detect_outliers(data)

    # 5. 수익률 계산
    simple_returns, log_returns = calculate_returns(data)

    # 6. 벤치마크 비교
    spy_close, excess_ret = compare_benchmark(data)

    # 7. 시각화
    output_path = create_visualizations(data, simple_returns, log_returns, spy_close)
    print(f"차트 저장 완료: {output_path.relative_to(Path.cwd())}")

    # 완료 메시지
    print("\n" + "=" * 42)
    print("데이터 전처리 완료!")
    print("=" * 42)
    print("\n주요 인사이트:")
    print("- 데이터 품질 검증 완료")
    print("- 단순 vs. 로그 수익률 비교")
    print("- 벤치마크 대비 성과 분석")
    print("- 이상치 탐지 및 분석")
    print("\n다음 챕터에서는 Backtrader로")
    print("실제 트레이딩 전략을 구현해봅시다!")


if __name__ == "__main__":
    main()
