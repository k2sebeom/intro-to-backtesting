"""
Chapter 11: 포트폴리오 구성과 분산투자
Portfolio Diversification using Backtrader

이 스크립트는 다양한 포트폴리오 구성 방법을 구현하고 비교합니다:
- 단일 자산 (AAPL)
- 균등 비중 포트폴리오
- 역변동성 포트폴리오
- 리밸런싱 효과
- 상관관계 분석
"""

import os
import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SingleAssetStrategy(bt.Strategy):
    """
    단일 자산 Buy & Hold 전략
    """
    def __init__(self):
        self.order = None

    def next(self):
        if not self.position and len(self) == 1:  # 첫날만 매수
            self.order = self.buy()


class EqualWeightStrategy(bt.Strategy):
    """
    균등 비중 포트폴리오 전략

    모든 자산에 동일한 비중으로 투자
    분기별 리밸런싱
    """
    params = (
        ('rebalance_months', [3, 6, 9, 12]),  # 분기별
        ('printlog', False),
    )

    def __init__(self):
        self.rebalance_flag = False
        self.orders = []

    def prenext(self):
        # 모든 데이터가 준비될 때까지 대기
        pass

    def next(self):
        # 주문 처리 중이면 대기
        if any(self.orders):
            return

        # 리밸런싱 확인
        current_month = self.data.datetime.date(0).month

        if current_month in self.params.rebalance_months:
            if not self.rebalance_flag:
                self.rebalance_flag = True
                self.rebalance_portfolio()
        else:
            self.rebalance_flag = False

    def rebalance_portfolio(self):
        """균등 비중으로 리밸런싱"""
        if self.params.printlog:
            print(f'{self.data.datetime.date(0)}: 리밸런싱 실행')

        portfolio_value = self.broker.getvalue()
        target_weight = 1.0 / len(self.datas)

        for data in self.datas:
            # 목표 가치 계산
            target_value = portfolio_value * target_weight

            # 현재 포지션
            position_value = self.getposition(data).size * data.close[0]

            # 차이 계산
            diff = target_value - position_value

            # 매수/매도 주문
            if abs(diff) > 100:  # 최소 거래 금액
                shares = int(diff / data.close[0])
                if shares != 0:
                    order = self.order_target_size(data=data, target=self.getposition(data).size + shares)
                    self.orders.append(order)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order in self.orders:
                self.orders.remove(order)


class InverseVolatilityStrategy(bt.Strategy):
    """
    역변동성 포트폴리오 전략

    변동성에 반비례하여 투자
    분기별 리밸런싱
    """
    params = (
        ('volatility_period', 60),  # 변동성 계산 기간
        ('rebalance_months', [3, 6, 9, 12]),
        ('printlog', False),
    )

    def __init__(self):
        self.rebalance_flag = False
        self.orders = []

        # 각 데이터의 변동성 계산
        self.stds = {}
        for data in self.datas:
            self.stds[data._name] = bt.indicators.StdDev(
                data.close,
                period=self.params.volatility_period
            )

    def next(self):
        # 주문 처리 중이면 대기
        if any(self.orders):
            return

        # 변동성 계산 기간 대기
        if len(self) < self.params.volatility_period:
            return

        # 리밸런싱 확인
        current_month = self.data.datetime.date(0).month

        if current_month in self.params.rebalance_months:
            if not self.rebalance_flag:
                self.rebalance_flag = True
                self.rebalance_portfolio()
        else:
            self.rebalance_flag = False

    def rebalance_portfolio(self):
        """역변동성 비중으로 리밸런싱"""
        if self.params.printlog:
            print(f'{self.data.datetime.date(0)}: 역변동성 리밸런싱 실행')

        # 각 자산의 변동성 수집
        volatilities = {}
        for data in self.datas:
            vol = self.stds[data._name][0]
            if vol > 0:
                volatilities[data._name] = vol

        if not volatilities:
            return

        # 역변동성 계산
        inv_vols = {name: 1.0/vol for name, vol in volatilities.items()}
        total_inv_vol = sum(inv_vols.values())

        # 비중 계산
        weights = {name: inv_vol/total_inv_vol for name, inv_vol in inv_vols.items()}

        # 포트폴리오 가치
        portfolio_value = self.broker.getvalue()

        # 리밸런싱
        for data in self.datas:
            if data._name in weights:
                target_value = portfolio_value * weights[data._name]
                position_value = self.getposition(data).size * data.close[0]
                diff = target_value - position_value

                if abs(diff) > 100:
                    shares = int(diff / data.close[0])
                    if shares != 0:
                        order = self.order_target_size(data=data, target=self.getposition(data).size + shares)
                        self.orders.append(order)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order in self.orders:
                self.orders.remove(order)


def run_single_asset(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01'):
    """단일 자산 백테스트"""
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(SingleAssetStrategy)
    cerebro.adddata(data_feed, name=ticker)

    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    initial_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    return cerebro, results[0], initial_value, final_value, data


def run_portfolio(tickers, start_date, end_date, strategy_class):
    """포트폴리오 백테스트"""
    # 데이터 다운로드
    all_data = {}
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        all_data[ticker] = data

    # Cerebro 설정
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)

    # 데이터 피드 추가
    for ticker, data in all_data.items():
        data_feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(data_feed, name=ticker)

    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    initial_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    return cerebro, results[0], initial_value, final_value, all_data


def calculate_correlation(tickers, start_date, end_date):
    """상관관계 계산"""
    # 데이터 다운로드
    returns_data = {}
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        # 일별 수익률 계산
        returns = data['Close'].pct_change().dropna()
        returns_data[ticker] = returns

    # DataFrame으로 변환
    returns_df = pd.DataFrame(returns_data)

    # 상관관계 계산
    correlation_matrix = returns_df.corr()

    return correlation_matrix


def print_performance(strategy_name, initial_value, final_value, analyzers):
    """성과 지표 출력"""
    print(f"\n{'='*60}")
    print(f"=== {strategy_name} ===")
    print(f"{'='*60}")

    total_return = ((final_value - initial_value) / initial_value) * 100
    print(f"\n총 수익률: {total_return:+.2f}%")
    print(f"최종 자금: ${final_value:,.2f}")

    sharpe = analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', None)
    if sharpe_ratio is not None:
        print(f"Sharpe Ratio: {sharpe_ratio:.3f}")

    drawdown = analyzers.drawdown.get_analysis()
    print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")


def visualize_results(results_dict, correlation_matrix, tickers):
    """결과 시각화"""
    fig = plt.figure(figsize=(16, 10))

    # 1. 수익률 비교
    ax1 = plt.subplot(2, 3, 1)

    methods = []
    returns_list = []

    for method_name, (_, strategy, initial, final, _) in results_dict.items():
        methods.append(method_name)
        ret = ((final - initial) / initial) * 100
        returns_list.append(ret)

    x = np.arange(len(methods))
    bars = ax1.bar(x, returns_list, alpha=0.8, color='steelblue')

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{returns_list[i]:.1f}%',
                ha='center', va='bottom', fontsize=9)

    ax1.set_title('Total Return Comparison', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Return (%)', fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=15, ha='right', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. Sharpe Ratio 비교
    ax2 = plt.subplot(2, 3, 2)

    sharpe_list = []
    for method_name, (_, strategy, _, _, _) in results_dict.items():
        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        sharpe_list.append(sharpe if sharpe else 0)

    bars2 = ax2.bar(x, sharpe_list, alpha=0.8, color='orange')

    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{sharpe_list[i]:.2f}',
                ha='center', va='bottom', fontsize=9)

    ax2.set_title('Sharpe Ratio Comparison', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Sharpe Ratio', fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, rotation=15, ha='right', fontsize=9)
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. Maximum Drawdown 비교
    ax3 = plt.subplot(2, 3, 3)

    mdd_list = []
    for method_name, (_, strategy, _, _, _) in results_dict.items():
        mdd = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']
        mdd_list.append(mdd)

    bars3 = ax3.bar(x, [-mdd for mdd in mdd_list], alpha=0.8, color='coral')

    for i, bar in enumerate(bars3):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{mdd_list[i]:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

    ax3.set_title('Maximum Drawdown Comparison', fontsize=11, fontweight='bold')
    ax3.set_ylabel('MDD (%)', fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods, rotation=15, ha='right', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. 상관관계 히트맵
    ax4 = plt.subplot(2, 3, 4)

    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, vmin=-1, vmax=1, square=True, ax=ax4,
                cbar_kws={'shrink': 0.8})

    ax4.set_title('Asset Correlation Matrix', fontsize=11, fontweight='bold')

    # 5. 개별 자산 수익률
    ax5 = plt.subplot(2, 3, 5)

    # 각 자산의 수익률 계산 (단일 자산 결과에서)
    single_asset_returns = []
    for ticker in tickers:
        # 임시로 계산
        data = yf.download(ticker, start='2019-01-01', end='2024-01-01', progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        ret = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
        single_asset_returns.append(ret)

    x_assets = np.arange(len(tickers))
    bars5 = ax5.bar(x_assets, single_asset_returns, alpha=0.8, color='lightgreen')

    for i, bar in enumerate(bars5):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{single_asset_returns[i]:.1f}%',
                ha='center', va='bottom', fontsize=9)

    ax5.set_title('Individual Asset Returns', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Return (%)', fontsize=10)
    ax5.set_xticks(x_assets)
    ax5.set_xticklabels(tickers, fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')

    # 6. 위험-수익 산점도
    ax6 = plt.subplot(2, 3, 6)

    for method_name, (_, strategy, initial, final, _) in results_dict.items():
        ret = ((final - initial) / initial) * 100
        mdd = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']

        ax6.scatter(mdd, ret, s=200, alpha=0.6, label=method_name)
        ax6.annotate(method_name, (mdd, ret), fontsize=8, ha='center')

    ax6.set_title('Risk-Return Profile', fontsize=11, fontweight='bold')
    ax6.set_xlabel('Max Drawdown (%)', fontsize=10)
    ax6.set_ylabel('Total Return (%)', fontsize=10)
    ax6.grid(True, alpha=0.3)
    ax6.legend(loc='best', fontsize=8)

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'portfolio_diversification.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Chapter 11: 포트폴리오 구성과 분산투자")
    print("=" * 60)

    # 설정
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    start_date = '2019-01-01'
    end_date = '2024-01-01'
    initial_cash = 10000.0

    print(f"\n=== 백테스트 설정 ===")
    print(f"- 포트폴리오: {', '.join(tickers)}")
    print(f"- 기간: {start_date} ~ {end_date}")
    print(f"- 초기 자금: ${initial_cash:,.2f}")

    print(f"\n{'='*60}")
    print("백테스트 실행 중...")
    print(f"{'='*60}")

    results = {}

    # 1. 단일 자산 (AAPL)
    print("\n[1/3] 단일 자산 (AAPL)...")
    result = run_single_asset('AAPL', start_date, end_date)
    results['단일 자산 (AAPL)'] = result
    _, strategy1, initial1, final1, _ = result
    print_performance("단일 자산 (AAPL)", initial1, final1, strategy1.analyzers)

    # 2. 균등 비중 포트폴리오
    print("\n[2/3] 균등 비중 포트폴리오...")
    result = run_portfolio(tickers, start_date, end_date, EqualWeightStrategy)
    results['균등 비중'] = result
    _, strategy2, initial2, final2, _ = result
    print_performance("균등 비중 포트폴리오", initial2, final2, strategy2.analyzers)

    # 3. 역변동성 포트폴리오
    print("\n[3/3] 역변동성 포트폴리오...")
    result = run_portfolio(tickers, start_date, end_date, InverseVolatilityStrategy)
    results['역변동성'] = result
    _, strategy3, initial3, final3, _ = result
    print_performance("역변동성 포트폴리오", initial3, final3, strategy3.analyzers)

    # 상관관계 계산
    print("\n상관관계 계산 중...")
    correlation_matrix = calculate_correlation(tickers, start_date, end_date)

    print(f"\n{'='*60}")
    print("=== 상관관계 매트릭스 ===")
    print(f"{'='*60}")
    print(correlation_matrix.round(3))

    # 비교 요약
    print(f"\n{'='*60}")
    print("=== 포트폴리오 전략 비교 요약 ===")
    print(f"{'='*60}")

    print(f"\n{'전략':<25} {'수익률':>12} {'Sharpe':>10} {'MDD':>10}")
    print("-" * 60)

    for method_name, (_, strategy, initial, final, _) in results.items():
        ret = ((final - initial) / initial) * 100
        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        mdd = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']

        print(f"{method_name:<25} {ret:>11.2f}% {sharpe:>9.2f} {mdd:>9.2f}%")

    # 시각화
    print("\n차트 생성 중...")
    visualize_results(results, correlation_matrix, tickers)

    print(f"\n{'='*60}")
    print("포트폴리오 분산투자 백테스트 완료!")
    print(f"{'='*60}")

    print("\n주요 인사이트:")
    print("- 분산투자는 위험(MDD)을 감소시킴")
    print("- 균등 비중은 간단하지만 효과적")
    print("- 역변동성은 안정성 증가")
    print("- 상관관계가 낮을수록 분산 효과 큼")
    print("- Sharpe Ratio로 위험 조정 수익 평가")
    print("\nPart 3 (리스크와 포트폴리오 관리) 완료!")
    print("다음 Part에서는 성과 평가 지표와")
    print("전략 최적화를 배워봅시다!")


if __name__ == '__main__':
    main()
