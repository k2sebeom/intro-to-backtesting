"""
Chapter 14: 과최적화 방지와 검증
Walk-Forward Analysis

이 스크립트는 워크포워드 분석을 구현합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt
from datetime import datetime, timedelta

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class OptimizableSMAStrategy(bt.Strategy):
    """최적화 가능한 이동평균 전략"""

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


def optimize_parameters(data, fast_range, slow_range):
    """파라미터 최적화"""

    best_sharpe = -np.inf
    best_params = None

    for fast in fast_range:
        for slow in slow_range:
            if fast >= slow:
                continue

            cerebro = bt.Cerebro()
            data_feed = bt.feeds.PandasData(dataname=data)
            cerebro.adddata(data_feed)
            cerebro.addstrategy(OptimizableSMAStrategy, fast_period=fast, slow_period=slow)
            cerebro.broker.setcash(100000.0)
            cerebro.broker.setcommission(commission=0.001)
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)

            try:
                results = cerebro.run()
                sharpe = results[0].analyzers.sharpe.get_analysis().get('sharperatio', None)

                if sharpe and sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = (fast, slow)
            except:
                continue

    return best_params, best_sharpe


def backtest_with_params(data, fast, slow):
    """특정 파라미터로 백테스트"""

    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(OptimizableSMAStrategy, fast_period=fast, slow_period=slow)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    initial = cerebro.broker.getvalue()
    cerebro.run()
    final = cerebro.broker.getvalue()

    return_pct = (final - initial) / initial

    return return_pct


def rolling_walk_forward(symbol='NVDA', start_date='2018-01-01', end_date='2024-01-01',
                         train_months=12, test_months=3):
    """롤링 워크포워드 분석"""

    print(f"\n롤링 워크포워드 분석 시작...")
    print(f"훈련 기간: {train_months}개월, 테스트 기간: {test_months}개월")

    # 데이터 다운로드
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return None

    # 파라미터 범위
    fast_range = range(20, 80, 10)
    slow_range = range(100, 250, 25)

    results = []
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    current_start = start

    while True:
        # 훈련 기간
        train_end = current_start + pd.DateOffset(months=train_months)
        if train_end > end:
            break

        # 테스트 기간
        test_start = train_end
        test_end = test_start + pd.DateOffset(months=test_months)
        if test_end > end:
            test_end = end

        # 데이터 분할
        train_data = data[(data.index >= current_start) & (data.index < train_end)]
        test_data = data[(data.index >= test_start) & (data.index < test_end)]

        if len(train_data) < 100 or len(test_data) < 20:
            break

        print(f"\n훈련: {current_start.date()} ~ {train_end.date()}")
        print(f"테스트: {test_start.date()} ~ {test_end.date()}")

        # 파라미터 최적화 (IS)
        best_params, is_sharpe = optimize_parameters(train_data, fast_range, slow_range)

        if best_params is None:
            current_start = test_start
            continue

        fast, slow = best_params
        print(f"최적 파라미터: Fast={fast}, Slow={slow}, Sharpe={is_sharpe:.2f}")

        # 훈련 세트에서 성과
        is_return = backtest_with_params(train_data, fast, slow)

        # 테스트 세트에서 성과 (OOS)
        oos_return = backtest_with_params(test_data, fast, slow)

        print(f"IS 수익률: {is_return:.2%}")
        print(f"OOS 수익률: {oos_return:.2%}")

        results.append({
            'train_start': current_start,
            'train_end': train_end,
            'test_start': test_start,
            'test_end': test_end,
            'fast': fast,
            'slow': slow,
            'is_return': is_return,
            'oos_return': oos_return,
            'is_sharpe': is_sharpe
        })

        # 다음 윈도우로 이동
        current_start = test_start

    return pd.DataFrame(results)


def anchored_walk_forward(symbol='NVDA', start_date='2018-01-01', end_date='2024-01-01',
                          initial_months=12, test_months=3):
    """앵커드 워크포워드 분석"""

    print(f"\n앵커드 워크포워드 분석 시작...")
    print(f"초기 훈련 기간: {initial_months}개월, 테스트 기간: {test_months}개월")

    # 데이터 다운로드
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return None

    # 파라미터 범위
    fast_range = range(20, 80, 10)
    slow_range = range(100, 250, 25)

    results = []
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # 앵커 포인트 (고정)
    anchor_start = start
    test_start = start + pd.DateOffset(months=initial_months)

    while True:
        test_end = test_start + pd.DateOffset(months=test_months)
        if test_end > end:
            test_end = end

        # 데이터 분할 (훈련은 처음부터 누적)
        train_data = data[(data.index >= anchor_start) & (data.index < test_start)]
        test_data = data[(data.index >= test_start) & (data.index < test_end)]

        if len(test_data) < 20:
            break

        print(f"\n훈련: {anchor_start.date()} ~ {test_start.date()}")
        print(f"테스트: {test_start.date()} ~ {test_end.date()}")

        # 파라미터 최적화
        best_params, is_sharpe = optimize_parameters(train_data, fast_range, slow_range)

        if best_params is None:
            test_start = test_end
            continue

        fast, slow = best_params
        print(f"최적 파라미터: Fast={fast}, Slow={slow}")

        # 성과 계산
        is_return = backtest_with_params(train_data, fast, slow)
        oos_return = backtest_with_params(test_data, fast, slow)

        print(f"IS 수익률: {is_return:.2%}")
        print(f"OOS 수익률: {oos_return:.2%}")

        results.append({
            'train_start': anchor_start,
            'train_end': test_start,
            'test_start': test_start,
            'test_end': test_end,
            'fast': fast,
            'slow': slow,
            'is_return': is_return,
            'oos_return': oos_return
        })

        test_start = test_end

    return pd.DataFrame(results)


def plot_walk_forward_results(rolling_results, anchored_results, symbol):
    """워크포워드 결과 시각화"""

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'{symbol} - Walk-Forward Analysis Results', fontsize=16, fontweight='bold')

    # 1. 롤링: IS vs OOS 수익률
    ax1 = axes[0, 0]
    x = range(len(rolling_results))
    ax1.plot(x, rolling_results['is_return'] * 100, 'o-', label='In-Sample', linewidth=2)
    ax1.plot(x, rolling_results['oos_return'] * 100, 's-', label='Out-of-Sample', linewidth=2)
    ax1.set_title('Rolling Walk-Forward: IS vs OOS Returns')
    ax1.set_xlabel('Period')
    ax1.set_ylabel('Return (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=1)

    # 2. 앵커드: IS vs OOS 수익률
    ax2 = axes[0, 1]
    x = range(len(anchored_results))
    ax2.plot(x, anchored_results['is_return'] * 100, 'o-', label='In-Sample', linewidth=2)
    ax2.plot(x, anchored_results['oos_return'] * 100, 's-', label='Out-of-Sample', linewidth=2)
    ax2.set_title('Anchored Walk-Forward: IS vs OOS Returns')
    ax2.set_xlabel('Period')
    ax2.set_ylabel('Return (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1)

    # 3. 롤링: 누적 OOS 수익률
    ax3 = axes[1, 0]
    cumulative_oos = (1 + rolling_results['oos_return']).cumprod() - 1
    cumulative_oos.plot(ax=ax3, linewidth=2, color='green')
    ax3.set_title('Rolling: Cumulative OOS Return')
    ax3.set_xlabel('Period')
    ax3.set_ylabel('Cumulative Return (%)')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='red', linestyle='--', linewidth=1)

    # 4. 통계 테이블
    ax4 = axes[1, 1]
    ax4.axis('off')

    # WFE 계산
    rolling_wfe = (rolling_results['oos_return'].mean() / rolling_results['is_return'].mean() * 100) if rolling_results['is_return'].mean() != 0 else 0
    anchored_wfe = (anchored_results['oos_return'].mean() / anchored_results['is_return'].mean() * 100) if anchored_results['is_return'].mean() != 0 else 0

    stats_data = [
        ['Metric', 'Rolling', 'Anchored'],
        ['', '', ''],
        ['Avg IS Return', f"{rolling_results['is_return'].mean():.2%}", f"{anchored_results['is_return'].mean():.2%}"],
        ['Avg OOS Return', f"{rolling_results['oos_return'].mean():.2%}", f"{anchored_results['oos_return'].mean():.2%}"],
        ['', '', ''],
        ['WFE', f"{rolling_wfe:.1f}%", f"{anchored_wfe:.1f}%"],
        ['', '', ''],
        ['OOS Win Rate', f"{(rolling_results['oos_return'] > 0).mean():.1%}", f"{(anchored_results['oos_return'] > 0).mean():.1%}"],
        ['Periods', f"{len(rolling_results)}", f"{len(anchored_results)}"],
    ]

    table = ax4.table(cellText=stats_data, cellLoc='center', loc='center', colWidths=[0.4, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # 헤더 스타일
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    ax4.set_title('Walk-Forward Statistics', fontweight='bold', pad=20)

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'walk_forward_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 14: Walk-Forward Analysis")
    print("=" * 60)

    symbol = 'NVDA'

    # 롤링 워크포워드
    rolling_results = rolling_walk_forward(
        symbol=symbol,
        start_date='2018-01-01',
        end_date='2024-01-01',
        train_months=12,
        test_months=3
    )

    # 앵커드 워크포워드
    anchored_results = anchored_walk_forward(
        symbol=symbol,
        start_date='2018-01-01',
        end_date='2024-01-01',
        initial_months=12,
        test_months=3
    )

    if rolling_results is not None and anchored_results is not None:
        # 결과 시각화
        plot_walk_forward_results(rolling_results, anchored_results, symbol)

        # WFE 계산
        print("\n" + "=" * 60)
        print("Walk-Forward Efficiency (WFE)")
        print("=" * 60)

        rolling_wfe = (rolling_results['oos_return'].mean() / rolling_results['is_return'].mean() * 100)
        anchored_wfe = (anchored_results['oos_return'].mean() / anchored_results['is_return'].mean() * 100)

        print(f"롤링 WFE: {rolling_wfe:.1f}%")
        print(f"앵커드 WFE: {anchored_wfe:.1f}%")

        print("\n해석:")
        if rolling_wfe > 80:
            print("  롤링 WFE > 80%: 매우 강건한 전략")
        elif rolling_wfe > 60:
            print("  롤링 WFE 60-80%: 양호한 전략")
        else:
            print("  롤링 WFE < 60%: 과최적화 의심")

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
