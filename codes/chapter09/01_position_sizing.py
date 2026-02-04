"""
Chapter 9: 포지션 크기 결정
Position Sizing Strategies using Backtrader

이 스크립트는 다양한 포지션 크기 결정 방법을 구현하고 비교합니다:
- 고정 비율 (Fixed Percentage)
- 고정 위험 (Fixed Risk)
- 켈리 기준 (Kelly Criterion)
- 변동성 기반 (ATR-based)
"""

import os
import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class FixedRiskSizer(bt.Sizer):
    """
    고정 위험 포지션 크기 결정

    거래당 계좌의 일정 비율만 위험에 노출
    """
    params = (
        ('risk_percent', 1.0),  # 거래당 위험 비율 (%)
        ('atr_multiplier', 2.0),  # ATR 배수 (손절매 거리)
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            # 계좌 가치
            account_value = self.broker.getvalue()

            # 위험 금액
            risk_amount = account_value * (self.params.risk_percent / 100)

            # ATR 값 가져오기 (전략에서 계산)
            if hasattr(self.strategy, 'atr'):
                atr = self.strategy.atr[0]
                stop_distance = atr * self.params.atr_multiplier

                # 현재 가격
                price = data.close[0]

                # 주당 위험
                if stop_distance > 0:
                    position_size = risk_amount / stop_distance

                    # 계좌 크기 제한 (최대 80%)
                    max_position_value = account_value * 0.80
                    max_shares = max_position_value / price

                    return int(min(position_size, max_shares))

        return 0


class KellySizer(bt.Sizer):
    """
    켈리 기준 포지션 크기 결정

    Half-Kelly 방법 사용 (보수적)
    """
    params = (
        ('win_rate', 0.55),  # 예상 승률
        ('reward_risk_ratio', 1.5),  # 평균 수익/손실 비율
        ('kelly_fraction', 0.5),  # Kelly 비율 (0.5 = Half-Kelly)
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            # 켈리 공식: (W - (1-W)) / R
            win_rate = self.params.win_rate
            r = self.params.reward_risk_ratio

            kelly = (win_rate - (1 - win_rate)) / r

            # Half-Kelly (보수적)
            safe_kelly = kelly * self.params.kelly_fraction

            # 켈리가 음수면 거래하지 않음
            if safe_kelly <= 0:
                return 0

            # 최대 50%로 제한
            safe_kelly = min(safe_kelly, 0.50)

            # 계좌 가치
            account_value = self.broker.getvalue()

            # 포지션 크기
            position_value = account_value * safe_kelly
            position_size = position_value / data.close[0]

            return int(position_size)

        return 0


class SimpleStrategy(bt.Strategy):
    """
    포지션 크기 테스트를 위한 간단한 전략

    SMA 크로스오버 사용
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('atr_period', 14),
        ('printlog', False),
    )

    def __init__(self):
        # 이동평균
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)

        # 크로스오버
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        # ATR (변동성)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 - {order.executed.size}주 @ ${order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 - {order.executed.size}주 @ ${order.executed.price:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 골든 크로스: 매수
            if self.crossover > 0:
                self.order = self.buy()
        else:
            # 데드 크로스: 매도
            if self.crossover < 0:
                self.order = self.close()


def run_backtest(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01',
                 sizer_type='fixed_percent', sizer_params=None):
    """
    백테스트 실행

    Args:
        ticker: 티커 심볼
        start_date: 시작일
        end_date: 종료일
        sizer_type: 포지션 크기 결정 방법
        sizer_params: Sizer 파라미터
    """
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
    cerebro.addstrategy(SimpleStrategy, printlog=False)

    # 데이터 피드 추가
    cerebro.adddata(data_feed)

    # 초기 자금 설정
    cerebro.broker.setcash(10000.0)

    # 수수료 설정
    cerebro.broker.setcommission(commission=0.001)

    # Sizer 설정
    if sizer_type == 'fixed_percent':
        percent = sizer_params.get('percent', 95) if sizer_params else 95
        cerebro.addsizer(bt.sizers.PercentSizer, percents=percent)

    elif sizer_type == 'fixed_risk':
        risk_percent = sizer_params.get('risk_percent', 1.0) if sizer_params else 1.0
        cerebro.addsizer(FixedRiskSizer, risk_percent=risk_percent)

    elif sizer_type == 'kelly':
        win_rate = sizer_params.get('win_rate', 0.55) if sizer_params else 0.55
        reward_risk = sizer_params.get('reward_risk', 1.5) if sizer_params else 1.5
        cerebro.addsizer(KellySizer, win_rate=win_rate, reward_risk_ratio=reward_risk)

    # Analyzers 추가
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                        riskfreerate=0.0, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # 포트폴리오 가치 추적
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='time_return')

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
        print(f"거래 횟수: {total_trades}, 승률: {win_rate:.1f}%")


def visualize_results(results_dict, data, ticker='AAPL'):
    """결과 시각화"""
    fig = plt.figure(figsize=(15, 10))

    # 1. 계좌 가치 변화
    ax1 = plt.subplot(2, 1, 1)

    for method_name, (cerebro, strategy, initial, final, _) in results_dict.items():
        # TimeReturn 분석 결과 가져오기
        time_return = strategy.analyzers.time_return.get_analysis()

        # 날짜와 수익률 추출
        dates = list(time_return.keys())
        returns = list(time_return.values())

        # 누적 수익률 계산 (계좌 가치)
        account_values = [initial]
        for ret in returns:
            account_values.append(account_values[-1] * (1 + ret))

        # 날짜 변환 (datetime 객체를 pandas Timestamp로)
        plot_dates = [data.index[0]] + [pd.Timestamp(d) for d in dates]

        ax1.plot(plot_dates, account_values, label=method_name, linewidth=2, alpha=0.7)

    ax1.set_title(f'{ticker} - Portfolio Value Growth Comparison', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Portfolio Value ($)', fontsize=10)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 2. 성과 비교 바차트
    ax2 = plt.subplot(2, 2, 3)

    methods = []
    returns_list = []
    sharpe_list = []

    for method_name, (cerebro, strategy, initial, final, _) in results_dict.items():
        methods.append(method_name)
        total_return = ((final - initial) / initial) * 100
        returns_list.append(total_return)

        sharpe = strategy.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', 0)
        sharpe_list.append(sharpe_ratio if sharpe_ratio else 0)

    x = np.arange(len(methods))
    width = 0.35

    bars1 = ax2.bar(x - width/2, returns_list, width, label='Total Return (%)', alpha=0.8)

    # 막대 위에 값 표시
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{returns_list[i]:.1f}%',
                ha='center', va='bottom', fontsize=8)

    ax2.set_title('Total Return Comparison', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Return (%)', fontsize=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, rotation=15, ha='right', fontsize=8)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. Sharpe Ratio 비교
    ax3 = plt.subplot(2, 2, 4)

    bars2 = ax3.bar(x, sharpe_list, width*2, label='Sharpe Ratio', alpha=0.8, color='orange')

    # 막대 위에 값 표시
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{sharpe_list[i]:.2f}',
                ha='center', va='bottom', fontsize=8)

    ax3.set_title('Sharpe Ratio Comparison', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Sharpe Ratio', fontsize=9)
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods, rotation=15, ha='right', fontsize=8)
    ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Target (1.0)')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'position_sizing.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Chapter 9: 포지션 크기 결정")
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
    print(f"- 전략: SMA(50/200) 크로스오버")

    print(f"\n{'='*60}")
    print("백테스트 실행 중...")
    print(f"{'='*60}")

    results = {}

    # 1. 고정 비율 (95%)
    print("\n[1/4] 고정 비율 (95%) 전략...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        sizer_type='fixed_percent',
        sizer_params={'percent': 95}
    )
    results['고정 비율 (95%)'] = result
    cerebro1, strategy1, initial1, final1, data = result
    print_performance("고정 비율 (95%)", initial1, final1, strategy1.analyzers)

    # 2. 고정 비율 (50%)
    print("\n[2/4] 고정 비율 (50%) 전략...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        sizer_type='fixed_percent',
        sizer_params={'percent': 50}
    )
    results['고정 비율 (50%)'] = result
    cerebro2, strategy2, initial2, final2, _ = result
    print_performance("고정 비율 (50%)", initial2, final2, strategy2.analyzers)

    # 3. 고정 위험 (1%)
    print("\n[3/4] 고정 위험 (1%) 전략...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        sizer_type='fixed_risk',
        sizer_params={'risk_percent': 1.0}
    )
    results['고정 위험 (1%)'] = result
    cerebro3, strategy3, initial3, final3, _ = result
    print_performance("고정 위험 (1%)", initial3, final3, strategy3.analyzers)

    # 4. 켈리 기준 (Half-Kelly)
    print("\n[4/4] 켈리 기준 (Half-Kelly) 전략...")
    result = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        sizer_type='kelly',
        sizer_params={'win_rate': 0.55, 'reward_risk': 1.5}
    )
    results['Kelly (Half)'] = result
    cerebro4, strategy4, initial4, final4, _ = result
    print_performance("켈리 기준 (Half-Kelly)", initial4, final4, strategy4.analyzers)

    # 비교 요약
    print(f"\n{'='*60}")
    print("=== 포지션 크기 방법 비교 요약 ===")
    print(f"{'='*60}")

    print(f"\n{'방법':<20} {'수익률':>12} {'Sharpe':>10} {'MDD':>10}")
    print("-" * 60)

    for method_name, (_, strategy, initial, final, _) in results.items():
        ret = ((final - initial) / initial) * 100
        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        mdd = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']

        print(f"{method_name:<20} {ret:>11.2f}% {sharpe:>9.2f} {mdd:>9.2f}%")

    # 시각화
    print("\n차트 생성 중...")
    visualize_results(results, data, ticker)

    print(f"\n{'='*60}")
    print("포지션 크기 결정 백테스트 완료!")
    print(f"{'='*60}")

    print("\n주요 인사이트:")
    print("- 고정 비율: 간단하고 복리 효과 발생")
    print("- 고정 위험: 손실 제어에 효과적")
    print("- 켈리 기준: 이론적 최적이지만 실전에서는 보수적 사용")
    print("- 포지션 크기가 위험 관리의 핵심")
    print("- 높은 수익률보다 Sharpe Ratio 중요")
    print("\n다음 챕터에서는 손절매와 익절매를 포함한")
    print("종합적인 리스크 관리 기법을 배워봅시다!")


if __name__ == '__main__':
    main()
