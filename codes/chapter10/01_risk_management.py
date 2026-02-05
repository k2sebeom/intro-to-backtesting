"""
Chapter 10: 리스크 관리와 손절매
Risk Management and Stop Loss using Backtrader

이 스크립트는 다양한 손절매/익절매 전략을 구현하고 비교합니다:
- 손절매 없는 전략 (기준선)
- 고정 비율 손절매/익절매
- ATR 기반 손절매
- 추적 손절매
"""

import os
import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class NoStopStrategy(bt.Strategy):
    """
    손절매 없는 기준 전략

    SMA 크로스오버만 사용
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('printlog', False),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 @ ${order.executed.price:.2f}')
            elif order.issell():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 @ ${order.executed.price:.2f}')
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.order = self.buy()
        else:
            if self.crossover < 0:
                self.order = self.close()


class FixedStopStrategy(bt.Strategy):
    """
    고정 비율 손절매/익절매 전략

    진입가 대비 고정 비율로 손절/익절
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('stop_loss_percent', 0.02),  # 2% 손절
        ('take_profit_percent', 0.04),  # 4% 익절
        ('printlog', False),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 @ ${order.executed.price:.2f}')
            elif order.issell():
                if self.params.printlog:
                    pnl = self.data.close[0] - self.entry_price
                    print(f'{self.data.datetime.date(0)}: 매도 @ ${order.executed.price:.2f}, PnL: ${pnl:.2f}')
                self.entry_price = None
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 골든 크로스: 매수
            if self.crossover > 0:
                self.order = self.buy()
        else:
            # 손절매 확인
            stop_price = self.entry_price * (1 - self.params.stop_loss_percent)
            if self.data.close[0] <= stop_price:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 손절매 @ ${self.data.close[0]:.2f}')
                self.order = self.close()
                return

            # 익절매 확인
            take_profit_price = self.entry_price * (1 + self.params.take_profit_percent)
            if self.data.close[0] >= take_profit_price:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 익절매 @ ${self.data.close[0]:.2f}')
                self.order = self.close()
                return

            # 데드 크로스: 매도
            if self.crossover < 0:
                self.order = self.close()


class ATRStopStrategy(bt.Strategy):
    """
    ATR 기반 손절매 전략

    변동성에 따라 동적으로 손절매 거리 조정
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('atr_period', 14),
        ('atr_multiplier', 2.0),  # 2×ATR
        ('printlog', False),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.order = None
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                if self.params.printlog:
                    atr_stop = self.atr[0] * self.params.atr_multiplier
                    print(f'{self.data.datetime.date(0)}: 매수 @ ${order.executed.price:.2f}, ATR Stop: ${atr_stop:.2f}')
            elif order.issell():
                if self.params.printlog:
                    pnl = self.data.close[0] - self.entry_price if self.entry_price else 0
                    print(f'{self.data.datetime.date(0)}: 매도 @ ${order.executed.price:.2f}, PnL: ${pnl:.2f}')
                self.entry_price = None
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 골든 크로스: 매수
            if self.crossover > 0:
                self.order = self.buy()
        else:
            # ATR 기반 손절매
            stop_distance = self.atr[0] * self.params.atr_multiplier
            stop_price = self.entry_price - stop_distance

            if self.data.close[0] <= stop_price:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: ATR 손절매 @ ${self.data.close[0]:.2f}')
                self.order = self.close()
                return

            # 데드 크로스: 매도
            if self.crossover < 0:
                self.order = self.close()


class TrailingStopStrategy(bt.Strategy):
    """
    추적 손절매 전략

    고점 대비 일정 비율 아래로 떨어지면 청산
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('trail_percent', 0.05),  # 5% 추적
        ('printlog', False),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.entry_price = None
        self.highest_price = 0

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                self.highest_price = order.executed.price
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 @ ${order.executed.price:.2f}')
            elif order.issell():
                if self.params.printlog:
                    pnl = self.data.close[0] - self.entry_price if self.entry_price else 0
                    print(f'{self.data.datetime.date(0)}: 매도 @ ${order.executed.price:.2f}, PnL: ${pnl:.2f}')
                self.entry_price = None
                self.highest_price = 0
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 골든 크로스: 매수
            if self.crossover > 0:
                self.order = self.buy()
        else:
            # 최고가 업데이트
            if self.data.close[0] > self.highest_price:
                self.highest_price = self.data.close[0]
                if self.params.printlog:
                    trail_stop = self.highest_price * (1 - self.params.trail_percent)
                    print(f'{self.data.datetime.date(0)}: 최고가 업데이트: ${self.highest_price:.2f}, 추적 손절: ${trail_stop:.2f}')

            # 추적 손절매
            trail_stop = self.highest_price * (1 - self.params.trail_percent)

            if self.data.close[0] <= trail_stop:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 추적 손절매 @ ${self.data.close[0]:.2f}')
                self.order = self.close()
                return

            # 데드 크로스: 매도
            if self.crossover < 0:
                self.order = self.close()


def run_backtest(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01',
                 strategy_class=NoStopStrategy):
    """백테스트 실행"""
    # 데이터 다운로드
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Multi-index 컬럼 처리
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    # Backtrader 데이터 피드 생성
    data_feed = bt.feeds.PandasData(dataname=data)

    # Cerebro 엔진 초기화
    cerebro = bt.Cerebro()

    # 전략 추가
    cerebro.addstrategy(strategy_class, printlog=False)

    # 데이터 피드 추가
    cerebro.adddata(data_feed)

    # 초기 자금 설정
    cerebro.broker.setcash(10000.0)

    # 수수료 설정
    cerebro.broker.setcommission(commission=0.001)

    # 포지션 크기 설정
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    # Analyzers 추가
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                        riskfreerate=0.0, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # 백테스트 실행
    initial_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    return cerebro, results[0], initial_value, final_value, data


def print_performance(strategy_name, initial_value, final_value, analyzers):
    """성과 지표 출력"""
    print(f"\n{'='*60}")
    print(f"=== {strategy_name} ===")
    print(f"{'='*60}")

    # 기본 지표
    total_return = ((final_value - initial_value) / initial_value) * 100
    print(f"\n총 수익률: {total_return:+.2f}%")
    print(f"최종 자금: ${final_value:,.2f}")

    # Sharpe Ratio
    sharpe = analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', None)
    if sharpe_ratio is not None:
        print(f"Sharpe Ratio: {sharpe_ratio:.3f}")

    # Drawdown
    drawdown = analyzers.drawdown.get_analysis()
    print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")

    # Trade Statistics
    trades = analyzers.trades.get_analysis()
    total_trades = trades.get('total', {}).get('total', 0)

    if total_trades > 0:
        won = trades.get('won', {}).get('total', 0)
        lost = trades.get('lost', {}).get('total', 0)
        win_rate = (won / total_trades * 100) if total_trades > 0 else 0

        print(f"\n거래 통계:")
        print(f"- 총 거래: {total_trades}")
        print(f"- 승: {won}, 패: {lost}")
        print(f"- 승률: {win_rate:.1f}%")

        if won > 0:
            avg_win = trades['won']['pnl']['average']
            print(f"- 평균 수익: ${avg_win:.2f}")

        if lost > 0:
            avg_loss = trades['lost']['pnl']['average']
            print(f"- 평균 손실: ${avg_loss:.2f}")

            # 손익비
            if won > 0:
                reward_risk = abs(avg_win / avg_loss)
                print(f"- 손익비 (R:R): {reward_risk:.2f}:1")


def visualize_results(results_dict, data, ticker='AAPL'):
    """결과 시각화"""
    fig = plt.figure(figsize=(15, 10))

    # 1. 수익률 비교
    ax1 = plt.subplot(2, 2, 1)

    methods = []
    returns_list = []
    sharpe_list = []
    mdd_list = []

    for method_name, (_, strategy, initial, final, _) in results_dict.items():
        methods.append(method_name)

        ret = ((final - initial) / initial) * 100
        returns_list.append(ret)

        sharpe = strategy.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', 0)
        sharpe_list.append(sharpe_ratio if sharpe_ratio else 0)

        mdd = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']
        mdd_list.append(mdd)

    x = np.arange(len(methods))
    width = 0.35

    bars = ax1.bar(x, returns_list, width, alpha=0.8, color='steelblue')

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{returns_list[i]:.1f}%',
                ha='center', va='bottom', fontsize=8)

    ax1.set_title('Total Return Comparison', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Return (%)', fontsize=9)
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=15, ha='right', fontsize=8)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. Sharpe Ratio 비교
    ax2 = plt.subplot(2, 2, 2)

    bars2 = ax2.bar(x, sharpe_list, width, alpha=0.8, color='orange')

    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{sharpe_list[i]:.2f}',
                ha='center', va='bottom', fontsize=8)

    ax2.set_title('Sharpe Ratio Comparison', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Sharpe Ratio', fontsize=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, rotation=15, ha='right', fontsize=8)
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. Maximum Drawdown 비교
    ax3 = plt.subplot(2, 2, 3)

    bars3 = ax3.bar(x, [-mdd for mdd in mdd_list], width, alpha=0.8, color='coral')

    for i, bar in enumerate(bars3):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{mdd_list[i]:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

    ax3.set_title('Maximum Drawdown Comparison', fontsize=11, fontweight='bold')
    ax3.set_ylabel('MDD (%)', fontsize=9)
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods, rotation=15, ha='right', fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. 승률과 거래 횟수
    ax4 = plt.subplot(2, 2, 4)

    win_rates = []
    trade_counts = []

    for method_name, (_, strategy, _, _, _) in results_dict.items():
        trades = strategy.analyzers.trades.get_analysis()
        total = trades.get('total', {}).get('total', 0)
        won = trades.get('won', {}).get('total', 0)

        trade_counts.append(total)
        win_rate = (won / total * 100) if total > 0 else 0
        win_rates.append(win_rate)

    ax4_twin = ax4.twinx()

    bars4_1 = ax4.bar(x - width/2, trade_counts, width, label='Trade Count',
                      alpha=0.8, color='lightblue')
    bars4_2 = ax4_twin.bar(x + width/2, win_rates, width, label='Win Rate (%)',
                           alpha=0.8, color='lightgreen')

    ax4.set_title('Trade Statistics', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Trade Count', fontsize=9, color='lightblue')
    ax4_twin.set_ylabel('Win Rate (%)', fontsize=9, color='lightgreen')
    ax4.set_xticks(x)
    ax4.set_xticklabels(methods, rotation=15, ha='right', fontsize=8)
    ax4.tick_params(axis='y', labelcolor='lightblue')
    ax4_twin.tick_params(axis='y', labelcolor='lightgreen')
    ax4.grid(True, alpha=0.3, axis='y')

    # 범례
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'risk_management.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Chapter 10: 리스크 관리와 손절매")
    print("=" * 60)

    # 설정
    ticker = 'AAPL'
    start_date = '2019-01-01'
    end_date = '2024-01-01'
    initial_cash = 10000.0

    print(f"\n=== 백테스트 설정 ===")
    print(f"- 티커: {ticker}")
    print(f"- 기간: {start_date} ~ {end_date}")
    print(f"- 초기 자금: ${initial_cash:,.2f}")
    print(f"- 기본 전략: SMA(50/200) 크로스오버")

    print(f"\n{'='*60}")
    print("백테스트 실행 중...")
    print(f"{'='*60}")

    results = {}

    # 1. 손절매 없는 전략 (기준선)
    print("\n[1/4] 손절매 없는 전략...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=NoStopStrategy
    )
    results['손절매 없음'] = result
    _, strategy1, initial1, final1, data = result
    print_performance("손절매 없음", initial1, final1, strategy1.analyzers)

    # 2. 고정 비율 손절매/익절매
    print("\n[2/4] 고정 비율 (2% 손절, 4% 익절)...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=FixedStopStrategy
    )
    results['고정 비율 (2%/4%)'] = result
    _, strategy2, initial2, final2, _ = result
    print_performance("고정 비율 (2%/4%)", initial2, final2, strategy2.analyzers)

    # 3. ATR 기반 손절매
    print("\n[3/4] ATR 기반 (2×ATR) 손절매...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=ATRStopStrategy
    )
    results['ATR (2x)'] = result
    _, strategy3, initial3, final3, _ = result
    print_performance("ATR (2×ATR)", initial3, final3, strategy3.analyzers)

    # 4. 추적 손절매
    print("\n[4/4] 추적 손절매 (5%)...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=TrailingStopStrategy
    )
    results['추적 손절 (5%)'] = result
    _, strategy4, initial4, final4, _ = result
    print_performance("추적 손절매 (5%)", initial4, final4, strategy4.analyzers)

    # 비교 요약
    print(f"\n{'='*60}")
    print("=== 리스크 관리 방법 비교 요약 ===")
    print(f"{'='*60}")

    print(f"\n{'방법':<25} {'수익률':>12} {'Sharpe':>10} {'MDD':>10} {'거래':>8}")
    print("-" * 70)

    for method_name, (_, strategy, initial, final, _) in results.items():
        ret = ((final - initial) / initial) * 100
        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        mdd = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']
        trades = strategy.analyzers.trades.get_analysis().get('total', {}).get('total', 0)

        print(f"{method_name:<25} {ret:>11.2f}% {sharpe:>9.2f} {mdd:>9.2f}% {trades:>8}")

    # 시각화
    print("\n차트 생성 중...")
    visualize_results(results, data, ticker)

    print(f"\n{'='*60}")
    print("리스크 관리 백테스트 완료!")
    print(f"{'='*60}")

    print("\n주요 인사이트:")
    print("- 손절매는 최대 낙폭(MDD)을 크게 감소시킴")
    print("- ATR 기반 손절매는 변동성에 적응적")
    print("- 추적 손절매는 큰 수익을 보호")
    print("- 적절한 손익비 설정이 중요 (최소 1:2)")
    print("- 승률보다 손익비가 더 중요할 수 있음")
    print("\n다음 챕터에서는 여러 자산에 분산투자하는")
    print("포트폴리오 구성 방법을 배워봅시다!")


if __name__ == '__main__':
    main()
