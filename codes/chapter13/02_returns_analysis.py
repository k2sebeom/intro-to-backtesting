"""
Chapter 13: 백테스트 결과 분석과 시각화
Returns Distribution and Heatmap Analysis

이 스크립트는 수익률 분포와 월별/연별 히트맵을 시각화합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from scipy import stats

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def analyze_returns_distribution(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01'):
    """수익률 분포 분석"""

    # 데이터 다운로드
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return

    # 일별 수익률 계산
    returns = data['Close'].pct_change().dropna()

    # 통계 계산
    mean_return = returns.mean()
    std_return = returns.std()
    skewness = stats.skew(returns)
    kurtosis = stats.kurtosis(returns)

    # 월별 수익률
    monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)

    # 연도와 월 분리
    monthly_returns_pivot = monthly_returns.to_frame('return')
    monthly_returns_pivot['year'] = monthly_returns_pivot.index.year
    monthly_returns_pivot['month'] = monthly_returns_pivot.index.month

    # 피벗 테이블 생성
    heatmap_data = monthly_returns_pivot.pivot(index='year', columns='month', values='return')

    # 시각화
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    fig.suptitle(f'{symbol} - Returns Analysis', fontsize=16, fontweight='bold')

    # 1. 수익률 히스토그램과 정규분포
    ax1 = fig.add_subplot(gs[0, :2])
    n, bins, patches = ax1.hist(returns, bins=50, density=True, alpha=0.7, color='blue', edgecolor='black')

    # 정규분포 곡선 추가
    mu, sigma = returns.mean(), returns.std()
    x = np.linspace(returns.min(), returns.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, label='Normal Distribution')

    ax1.axvline(mean_return, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_return:.4f}')
    ax1.axvline(mean_return + std_return, color='orange', linestyle=':', linewidth=1, alpha=0.7)
    ax1.axvline(mean_return - std_return, color='orange', linestyle=':', linewidth=1, alpha=0.7, label='±1 Std Dev')

    ax1.set_title('Daily Returns Distribution')
    ax1.set_xlabel('Return')
    ax1.set_ylabel('Density')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 통계 정보
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')

    stats_text = f"""
    Statistics:

    Mean: {mean_return:.4f}
    Std Dev: {std_return:.4f}

    Skewness: {skewness:.4f}
    Kurtosis: {kurtosis:.4f}

    Min: {returns.min():.4f}
    Max: {returns.max():.4f}

    Annualized:
    Return: {mean_return * 252:.2%}
    Volatility: {std_return * np.sqrt(252):.2%}
    """

    ax2.text(0.1, 0.9, stats_text, transform=ax2.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 왜도와 첨도 해석
    skew_text = "Right-skewed (큰 이익 가능)" if skewness > 0 else "Left-skewed (큰 손실 가능)"
    kurt_text = "Fat tails (극단적 사건)" if kurtosis > 3 else "Thin tails"

    ax2.text(0.1, 0.3, f"Skewness:\n{skew_text}\n\nKurtosis:\n{kurt_text}",
             transform=ax2.transAxes, fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    # 3. Q-Q Plot (정규성 검정)
    ax3 = fig.add_subplot(gs[1, 0])
    stats.probplot(returns, dist="norm", plot=ax3)
    ax3.set_title('Q-Q Plot (Normality Test)')
    ax3.grid(True, alpha=0.3)

    # 4. 월별 수익률 바 차트
    ax4 = fig.add_subplot(gs[1, 1:])
    colors = ['g' if x > 0 else 'r' for x in monthly_returns]
    monthly_returns.plot(kind='bar', ax=ax4, color=colors, alpha=0.7)
    ax4.set_title('Monthly Returns')
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Return')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.grid(True, alpha=0.3, axis='y')
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # 5. 월별 수익률 히트맵
    ax5 = fig.add_subplot(gs[2, :])

    # 월 이름으로 변경
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    heatmap_data.columns = [month_names[i-1] for i in heatmap_data.columns]

    sns.heatmap(heatmap_data, annot=True, fmt='.2%', cmap='RdYlGn', center=0,
                cbar_kws={'label': 'Return'}, ax=ax5, linewidths=0.5)
    ax5.set_title('Monthly Returns Heatmap')
    ax5.set_xlabel('Month')
    ax5.set_ylabel('Year')

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'returns_distribution_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()

    # 해석 출력
    print("\n" + "=" * 60)
    print("수익률 분포 해석")
    print("=" * 60)

    print(f"\n왜도 (Skewness): {skewness:.4f}")
    if abs(skewness) < 0.5:
        print("  → 거의 대칭적인 분포")
    elif skewness > 0:
        print("  → 오른쪽 꼬리가 긴 분포 (큰 이익이 가능)")
    else:
        print("  → 왼쪽 꼬리가 긴 분포 (큰 손실이 가능)")

    print(f"\n첨도 (Kurtosis): {kurtosis:.4f}")
    if kurtosis > 3:
        print("  → 정규분포보다 뾰족함 (극단적 사건 가능성 높음)")
    elif kurtosis < 3:
        print("  → 정규분포보다 평평함")
    else:
        print("  → 정규분포와 유사")

    # Jarque-Bera 정규성 검정
    jb_stat, jb_pvalue = stats.jarque_bera(returns)
    print(f"\nJarque-Bera Test:")
    print(f"  통계량: {jb_stat:.4f}")
    print(f"  p-value: {jb_pvalue:.4f}")
    if jb_pvalue < 0.05:
        print("  → 정규분포를 따르지 않음 (p < 0.05)")
    else:
        print("  → 정규분포를 따름 (p >= 0.05)")

    # 월별 성과 요약
    print("\n" + "=" * 60)
    print("월별 성과 요약")
    print("=" * 60)

    monthly_avg = heatmap_data.mean()
    print("\n평균 월별 수익률:")
    for month, ret in monthly_avg.items():
        print(f"  {month}: {ret:.2%}")

    best_month = monthly_avg.idxmax()
    worst_month = monthly_avg.idxmin()
    print(f"\n최고 성과 월: {best_month} ({monthly_avg[best_month]:.2%})")
    print(f"최저 성과 월: {worst_month} ({monthly_avg[worst_month]:.2%})")


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 13: Returns Distribution Analysis")
    print("=" * 60)

    analyze_returns_distribution(
        symbol='NVDA',
        start_date='2020-01-01',
        end_date='2024-01-01'
    )

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
