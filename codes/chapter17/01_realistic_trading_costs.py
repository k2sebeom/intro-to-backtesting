"""
Chapter 17: 실전 트레이딩 고려사항
Realistic Trading Costs Analysis

이 스크립트는 슬리피지와 거래 비용이 전략 성과에 미치는 영향을 분석합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


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


def run_backtest_with_costs(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01',
                            commission=0.0, slippage=0.0):
    """다양한 거래 비용으로 백테스트 실행"""

    # 데이터 다운로드
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        return None

    # Backtrader 설정
    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(SMAStrategy)

    # 초기 자본
    cerebro.broker.setcash(100000.0)

    # 거래 비용 설정
    cerebro.broker.setcommission(commission=commission)

    if slippage > 0:
        cerebro.broker.set_slippage_perc(slippage)

    # 분석기 추가
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # 백테스트 실행
    initial_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    strategy = results[0]

    # 결과 수집
    total_return = (final_value - initial_value) / initial_value
    sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', None)
    max_dd = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)

    trade_analysis = strategy.analyzers.trades.get_analysis()
    total_trades = trade_analysis.get('total', {}).get('total', 0)

    return {
        'commission': commission,
        'slippage': slippage,
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return,
        'sharpe': sharpe if sharpe else 0,
        'max_dd': max_dd,
        'total_trades': total_trades
    }


def analyze_trading_costs(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01'):
    """거래 비용 영향 분석"""

    print(f"\n{symbol} 거래 비용 영향 분석")
    print("=" * 60)

    results = []

    # 1. 기준선 (비용 없음)
    print("\n1. 비용 없음 (이상적인 경우)")
    result = run_backtest_with_costs(symbol, start_date, end_date,
                                      commission=0.0, slippage=0.0)
    if result:
        results.append({**result, 'scenario': 'No Costs'})
        print(f"   총 수익률: {result['total_return']:.2%}")
        print(f"   Sharpe Ratio: {result['sharpe']:.2f}")

    # 2. 수수료만
    print("\n2. 수수료 0.1%")
    result = run_backtest_with_costs(symbol, start_date, end_date,
                                      commission=0.001, slippage=0.0)
    if result:
        results.append({**result, 'scenario': 'Commission 0.1%'})
        print(f"   총 수익률: {result['total_return']:.2%}")
        print(f"   Sharpe Ratio: {result['sharpe']:.2f}")

    # 3. 수수료 높음
    print("\n3. 수수료 0.3%")
    result = run_backtest_with_costs(symbol, start_date, end_date,
                                      commission=0.003, slippage=0.0)
    if result:
        results.append({**result, 'scenario': 'Commission 0.3%'})
        print(f"   총 수익률: {result['total_return']:.2%}")
        print(f"   Sharpe Ratio: {result['sharpe']:.2f}")

    # 4. 슬리피지만
    print("\n4. 슬리피지 0.05%")
    result = run_backtest_with_costs(symbol, start_date, end_date,
                                      commission=0.0, slippage=0.0005)
    if result:
        results.append({**result, 'scenario': 'Slippage 0.05%'})
        print(f"   총 수익률: {result['total_return']:.2%}")
        print(f"   Sharpe Ratio: {result['sharpe']:.2f}")

    # 5. 수수료 + 슬리피지 (현실적)
    print("\n5. 수수료 0.1% + 슬리피지 0.05%")
    result = run_backtest_with_costs(symbol, start_date, end_date,
                                      commission=0.001, slippage=0.0005)
    if result:
        results.append({**result, 'scenario': 'Realistic'})
        print(f"   총 수익률: {result['total_return']:.2%}")
        print(f"   Sharpe Ratio: {result['sharpe']:.2f}")

    # 6. 높은 비용
    print("\n6. 수수료 0.3% + 슬리피지 0.1%")
    result = run_backtest_with_costs(symbol, start_date, end_date,
                                      commission=0.003, slippage=0.001)
    if result:
        results.append({**result, 'scenario': 'High Costs'})
        print(f"   총 수익률: {result['total_return']:.2%}")
        print(f"   Sharpe Ratio: {result['sharpe']:.2f}")

    return pd.DataFrame(results)


def plot_cost_impact(results_df, symbol):
    """거래 비용 영향 시각화"""

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'{symbol} - Trading Costs Impact Analysis', fontsize=16, fontweight='bold')

    scenarios = results_df['scenario'].tolist()
    colors = ['green', 'lightgreen', 'yellow', 'orange', 'coral', 'red']

    # 1. 총 수익률 비교
    ax1 = axes[0, 0]
    bars = ax1.bar(scenarios, results_df['total_return'] * 100, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_title('Total Return by Scenario')
    ax1.set_ylabel('Return (%)')
    ax1.set_xticklabels(scenarios, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=1)

    # 값 표시
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

    # 2. Sharpe Ratio 비교
    ax2 = axes[0, 1]
    bars = ax2.bar(scenarios, results_df['sharpe'], color=colors, alpha=0.7, edgecolor='black')
    ax2.set_title('Sharpe Ratio by Scenario')
    ax2.set_ylabel('Sharpe Ratio')
    ax2.set_xticklabels(scenarios, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=1, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Good threshold')
    ax2.legend()

    # 값 표시
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)

    # 3. 최대 낙폭 비교
    ax3 = axes[1, 0]
    bars = ax3.bar(scenarios, results_df['max_dd'], color=colors, alpha=0.7, edgecolor='black')
    ax3.set_title('Maximum Drawdown by Scenario')
    ax3.set_ylabel('Max Drawdown (%)')
    ax3.set_xticklabels(scenarios, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')

    # 값 표시
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='top', fontsize=9)

    # 4. 비용 영향 요약 테이블
    ax4 = axes[1, 1]
    ax4.axis('off')

    # 기준선 대비 성과 감소
    baseline = results_df.iloc[0]
    impact_data = []

    for _, row in results_df.iterrows():
        return_diff = (row['total_return'] - baseline['total_return']) * 100
        sharpe_diff = row['sharpe'] - baseline['sharpe']

        impact_data.append([
            row['scenario'].replace(' ', '\n'),
            f"{row['total_return']:.1%}",
            f"{return_diff:+.1f}%",
            f"{row['sharpe']:.2f}"
        ])

    table = ax4.table(cellText=impact_data,
                      colLabels=['Scenario', 'Return', 'vs Baseline', 'Sharpe'],
                      cellLoc='center', loc='center',
                      colWidths=[0.3, 0.2, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)

    # 헤더 스타일
    for i in range(4):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # 기준선 행 강조
    for i in range(4):
        table[(1, i)].set_facecolor('#E8F5E9')

    ax4.set_title('Performance Impact Summary', fontweight='bold', pad=20)

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'trading_costs_impact.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 17: Realistic Trading Costs Analysis")
    print("=" * 60)

    # 거래 비용 분석
    results_df = analyze_trading_costs(
        symbol='NVDA',
        start_date='2020-01-01',
        end_date='2024-01-01'
    )

    if results_df is not None and len(results_df) > 0:
        # 결과 시각화
        plot_cost_impact(results_df, 'NVDA')

        # 영향 분석
        print("\n" + "=" * 60)
        print("거래 비용 영향 분석")
        print("=" * 60)

        baseline = results_df.iloc[0]
        realistic = results_df[results_df['scenario'] == 'Realistic'].iloc[0]

        return_impact = (realistic['total_return'] - baseline['total_return']) * 100
        sharpe_impact = realistic['sharpe'] - baseline['sharpe']

        print(f"\n기준선 (비용 없음):")
        print(f"  총 수익률: {baseline['total_return']:.2%}")
        print(f"  Sharpe Ratio: {baseline['sharpe']:.2f}")

        print(f"\n현실적 비용 (수수료 0.1% + 슬리피지 0.05%):")
        print(f"  총 수익률: {realistic['total_return']:.2%}")
        print(f"  Sharpe Ratio: {realistic['sharpe']:.2f}")

        print(f"\n영향:")
        print(f"  수익률 감소: {return_impact:.2f}%p")
        print(f"  Sharpe Ratio 감소: {sharpe_impact:.2f}")

        # 거래당 평균 비용
        total_trades = realistic['total_trades']
        if total_trades > 0:
            avg_cost_per_trade = (baseline['total_return'] - realistic['total_return']) / total_trades
            print(f"\n거래당 평균 비용: {avg_cost_per_trade:.4%}")
            print(f"총 거래 횟수: {total_trades}")

        print("\n해석:")
        if return_impact < -5:
            print("  → 거래 비용이 성과에 큰 영향을 미칩니다")
            print("  → 거래 빈도를 줄이거나 더 높은 수익률을 목표로 해야 합니다")
        elif return_impact < -2:
            print("  → 거래 비용이 상당한 영향을 미칩니다")
            print("  → 비용 대비 수익률을 신중히 고려해야 합니다")
        else:
            print("  → 거래 비용이 관리 가능한 수준입니다")

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
