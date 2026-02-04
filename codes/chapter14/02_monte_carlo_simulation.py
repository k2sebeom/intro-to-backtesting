"""
Chapter 14: 과최적화 방지와 검증
Monte Carlo Simulation

이 스크립트는 몬테카를로 시뮬레이션으로 전략의 통계적 신뢰도를 검증합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt
from scipy import stats

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class TradeRecorder(bt.Analyzer):
    """거래 기록 분석기"""

    def __init__(self):
        self.trades = []
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
            elif order.issell() and self.entry_price:
                exit_price = order.executed.price
                pnl_pct = (exit_price - self.entry_price) / self.entry_price
                self.trades.append(pnl_pct)
                self.entry_price = None

    def get_analysis(self):
        return {'trades': self.trades}


class SMAStrategy(bt.Strategy):
    """이동평균 크로스오버 전략"""

    params = (
        ('fast_period', 50),
        ('slow_period', 200),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.close()


def run_backtest_with_trades(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01'):
    """백테스트 실행하고 거래 기록 수집"""

    # 데이터 다운로드
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return None, None

    # Backtrader 설정
    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(SMAStrategy)
    cerebro.addanalyzer(TradeRecorder, _name='trade_recorder')
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # 백테스트 실행
    initial_value = cerebro.broker.getvalue()
    strategies = cerebro.run()
    final_value = cerebro.broker.getvalue()

    strategy = strategies[0]
    trades = strategy.analyzers.trade_recorder.get_analysis()['trades']

    actual_return = (final_value - initial_value) / initial_value

    print(f"거래 횟수: {len(trades)}")
    print(f"실제 수익률: {actual_return:.2%}")

    return trades, actual_return


def monte_carlo_simulation(trades, initial_capital=100000, num_simulations=1000):
    """몬테카를로 시뮬레이션"""

    print(f"\n몬테카를로 시뮬레이션 실행 중... (반복: {num_simulations}회)")

    simulation_results = []

    for i in range(num_simulations):
        # 거래 순서 무작위 섞기
        shuffled_trades = np.random.choice(trades, size=len(trades), replace=True)

        # 포트폴리오 가치 계산
        portfolio_value = initial_capital

        for trade_return in shuffled_trades:
            portfolio_value *= (1 + trade_return)

        final_return = (portfolio_value - initial_capital) / initial_capital
        simulation_results.append(final_return)

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{num_simulations} 완료...")

    return np.array(simulation_results)


def calculate_statistics(sim_results, actual_return):
    """통계 계산"""

    stats_dict = {
        'mean': np.mean(sim_results),
        'median': np.median(sim_results),
        'std': np.std(sim_results),
        'min': np.min(sim_results),
        'max': np.max(sim_results),
        'percentile_5': np.percentile(sim_results, 5),
        'percentile_25': np.percentile(sim_results, 25),
        'percentile_75': np.percentile(sim_results, 75),
        'percentile_95': np.percentile(sim_results, 95),
        'actual': actual_return,
        'percentile_rank': stats.percentileofscore(sim_results, actual_return)
    }

    return stats_dict


def plot_monte_carlo_results(sim_results, actual_return, symbol):
    """몬테카를로 결과 시각화"""

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'{symbol} - Monte Carlo Simulation Results', fontsize=16, fontweight='bold')

    # 1. 수익률 분포 히스토그램
    ax1 = axes[0, 0]
    n, bins, patches = ax1.hist(sim_results * 100, bins=50, density=True,
                                  alpha=0.7, color='blue', edgecolor='black')

    # 실제 수익률 표시
    ax1.axvline(actual_return * 100, color='red', linestyle='--',
                linewidth=3, label=f'Actual: {actual_return:.2%}')

    # 5th와 95th percentile
    p5 = np.percentile(sim_results, 5)
    p95 = np.percentile(sim_results, 95)
    ax1.axvline(p5 * 100, color='orange', linestyle=':', linewidth=2,
                label=f'5th percentile: {p5:.2%}')
    ax1.axvline(p95 * 100, color='green', linestyle=':', linewidth=2,
                label=f'95th percentile: {p95:.2%}')

    ax1.set_title('Return Distribution (Monte Carlo)')
    ax1.set_xlabel('Return (%)')
    ax1.set_ylabel('Density')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 누적 분포 함수 (CDF)
    ax2 = axes[0, 1]
    sorted_results = np.sort(sim_results)
    cdf = np.arange(1, len(sorted_results) + 1) / len(sorted_results)
    ax2.plot(sorted_results * 100, cdf * 100, linewidth=2)

    # 실제 수익률 위치
    actual_percentile = stats.percentileofscore(sim_results, actual_return)
    ax2.axvline(actual_return * 100, color='red', linestyle='--', linewidth=2,
                label=f'Actual ({actual_percentile:.1f}th percentile)')
    ax2.axhline(actual_percentile, color='red', linestyle=':', linewidth=1, alpha=0.5)

    ax2.set_title('Cumulative Distribution Function')
    ax2.set_xlabel('Return (%)')
    ax2.set_ylabel('Cumulative Probability (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. 박스플롯
    ax3 = axes[1, 0]
    bp = ax3.boxplot([sim_results * 100], vert=True, patch_artist=True, widths=0.5)
    bp['boxes'][0].set_facecolor('lightblue')

    # 실제 수익률 표시
    ax3.plot(1, actual_return * 100, 'ro', markersize=15, label='Actual Return')

    ax3.set_title('Return Distribution (Box Plot)')
    ax3.set_ylabel('Return (%)')
    ax3.set_xticklabels(['Monte Carlo'])
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. 통계 테이블
    ax4 = axes[1, 1]
    ax4.axis('off')

    stats_dict = calculate_statistics(sim_results, actual_return)

    stats_data = [
        ['Statistic', 'Value'],
        ['', ''],
        ['Mean', f"{stats_dict['mean']:.2%}"],
        ['Median', f"{stats_dict['median']:.2%}"],
        ['Std Dev', f"{stats_dict['std']:.2%}"],
        ['', ''],
        ['Min', f"{stats_dict['min']:.2%}"],
        ['Max', f"{stats_dict['max']:.2%}"],
        ['', ''],
        ['5th Percentile', f"{stats_dict['percentile_5']:.2%}"],
        ['95th Percentile', f"{stats_dict['percentile_95']:.2%}"],
        ['', ''],
        ['Actual Return', f"{stats_dict['actual']:.2%}"],
        ['Percentile Rank', f"{stats_dict['percentile_rank']:.1f}%"],
    ]

    table = ax4.table(cellText=stats_data, cellLoc='left', loc='center', colWidths=[0.6, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # 헤더 스타일
    for i in range(2):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # 실제 수익률 행 강조
    table[(12, 0)].set_facecolor('#FFE4B5')
    table[(12, 1)].set_facecolor('#FFE4B5')
    table[(13, 0)].set_facecolor('#FFE4B5')
    table[(13, 1)].set_facecolor('#FFE4B5')

    ax4.set_title('Monte Carlo Statistics', fontweight='bold', pad=20)

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'monte_carlo_simulation.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()

    return stats_dict


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 14: Monte Carlo Simulation")
    print("=" * 60)

    # 백테스트 실행하고 거래 수집
    trades, actual_return = run_backtest_with_trades(
        symbol='NVDA',
        start_date='2020-01-01',
        end_date='2024-01-01'
    )

    if trades is None or len(trades) < 10:
        print("거래가 충분하지 않습니다.")
        return

    # 몬테카를로 시뮬레이션
    sim_results = monte_carlo_simulation(trades, num_simulations=1000)

    # 결과 시각화
    stats_dict = plot_monte_carlo_results(sim_results, actual_return, 'NVDA')

    # 해석
    print("\n" + "=" * 60)
    print("결과 해석")
    print("=" * 60)

    percentile_rank = stats_dict['percentile_rank']

    print(f"\n실제 수익률: {actual_return:.2%}")
    print(f"몬테카를로 평균: {stats_dict['mean']:.2%}")
    print(f"몬테카를로 중앙값: {stats_dict['median']:.2%}")
    print(f"실제 수익률 순위: {percentile_rank:.1f} percentile")

    print("\n95% 신뢰구간:")
    print(f"  [{stats_dict['percentile_5']:.2%}, {stats_dict['percentile_95']:.2%}]")

    print("\n해석:")
    if percentile_rank > 95:
        print("  → 실제 수익률이 상위 5%: 매우 운이 좋았음")
    elif percentile_rank > 75:
        print("  → 실제 수익률이 상위 25%: 운이 좋았음")
    elif percentile_rank > 25:
        print("  → 실제 수익률이 중간: 정상적인 성과")
    elif percentile_rank > 5:
        print("  → 실제 수익률이 하위 25%: 운이 나빴음")
    else:
        print("  → 실제 수익률이 하위 5%: 매우 운이 나빴음")

    if stats_dict['percentile_5'] > 0:
        print("\n95% 확률로 양수 수익: 강건한 전략")
    elif stats_dict['percentile_25'] > 0:
        print("\n75% 확률로 양수 수익: 합리적인 전략")
    else:
        print("\n양수 수익 확률이 낮음: 전략 개선 필요")

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
