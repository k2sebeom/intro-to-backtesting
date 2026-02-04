"""
Chapter 12: 성과 지표와 리스크 측정
Performance Metrics and Risk Measurement

이 스크립트는 백테스팅 전략의 다양한 성과 지표를 계산합니다:
- 수익률 지표: Total Return, Annualized Return, CAGR
- 리스크 지표: Volatility, Maximum Drawdown
- 리스크 조정 수익률: Sharpe Ratio, Sortino Ratio, Calmar Ratio
- 거래 통계: Win Rate, Profit Factor, Expectancy
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
import backtrader as bt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class PerformanceMetrics:
    """성과 지표 계산 클래스"""

    def __init__(self, returns, equity_curve, trades=None, rf_rate=0.02):
        """
        Parameters:
        -----------
        returns : pd.Series
            일별 수익률
        equity_curve : pd.Series
            자산 곡선
        trades : list
            개별 거래 수익률 리스트 (선택)
        rf_rate : float
            무위험 수익률 (연율)
        """
        self.returns = returns
        self.equity_curve = equity_curve
        self.trades = trades if trades is not None else []
        self.rf_rate = rf_rate
        self.daily_rf_rate = (1 + rf_rate) ** (1/252) - 1

    def total_return(self):
        """총 수익률"""
        return (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) - 1

    def annualized_return(self):
        """연환산 수익률"""
        total_days = len(self.returns)
        total_ret = self.total_return()
        years = total_days / 252
        return (1 + total_ret) ** (1/years) - 1

    def cagr(self):
        """복합 연평균 성장률"""
        return self.annualized_return()

    def volatility(self, annualize=True):
        """변동성 (표준편차)"""
        vol = self.returns.std()
        if annualize:
            vol = vol * np.sqrt(252)
        return vol

    def maximum_drawdown(self):
        """최대 낙폭"""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()

    def drawdown_duration(self):
        """최대 낙폭 지속 기간 (일)"""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max

        # 낙폭 구간 찾기
        is_drawdown = drawdown < 0
        drawdown_periods = []
        start = None

        for i, in_dd in enumerate(is_drawdown):
            if in_dd and start is None:
                start = i
            elif not in_dd and start is not None:
                drawdown_periods.append(i - start)
                start = None

        if start is not None:  # 아직 회복 중
            drawdown_periods.append(len(is_drawdown) - start)

        return max(drawdown_periods) if drawdown_periods else 0

    def sharpe_ratio(self):
        """샤프 비율"""
        excess_returns = self.returns - self.daily_rf_rate
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def sortino_ratio(self, mar=0):
        """소르티노 비율"""
        excess_returns = self.returns - self.daily_rf_rate
        downside_returns = excess_returns[excess_returns < mar]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0

        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    def calmar_ratio(self):
        """칼마 비율"""
        mdd = abs(self.maximum_drawdown())
        if mdd == 0:
            return 0
        return self.cagr() / mdd

    def win_rate(self):
        """승률"""
        if len(self.trades) == 0:
            return 0
        winning_trades = sum(1 for t in self.trades if t > 0)
        return winning_trades / len(self.trades)

    def profit_factor(self):
        """Profit Factor"""
        if len(self.trades) == 0:
            return 0

        wins = sum(t for t in self.trades if t > 0)
        losses = abs(sum(t for t in self.trades if t < 0))

        if losses == 0:
            return float('inf') if wins > 0 else 0

        return wins / losses

    def expectancy(self):
        """거래당 기댓값"""
        if len(self.trades) == 0:
            return 0

        winning_trades = [t for t in self.trades if t > 0]
        losing_trades = [t for t in self.trades if t < 0]

        if not winning_trades:
            avg_win = 0
        else:
            avg_win = np.mean(winning_trades)

        if not losing_trades:
            avg_loss = 0
        else:
            avg_loss = abs(np.mean(losing_trades))

        win_rate = self.win_rate()

        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    def get_all_metrics(self):
        """모든 지표를 딕셔너리로 반환"""
        return {
            '총 수익률': f"{self.total_return():.2%}",
            '연환산 수익률': f"{self.annualized_return():.2%}",
            'CAGR': f"{self.cagr():.2%}",
            '변동성 (연율)': f"{self.volatility():.2%}",
            '최대 낙폭': f"{self.maximum_drawdown():.2%}",
            '낙폭 지속 기간': f"{self.drawdown_duration()} 일",
            'Sharpe Ratio': f"{self.sharpe_ratio():.2f}",
            'Sortino Ratio': f"{self.sortino_ratio():.2f}",
            'Calmar Ratio': f"{self.calmar_ratio():.2f}",
            '승률': f"{self.win_rate():.2%}",
            'Profit Factor': f"{self.profit_factor():.2f}",
            '기댓값': f"{self.expectancy():.4f}",
            '총 거래 횟수': len(self.trades)
        }


class SMAStrategy(bt.Strategy):
    """이동평균 크로스오버 전략 (성과 측정용)"""

    params = (
        ('fast_period', 50),
        ('slow_period', 200),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.trade_returns = []
        self.entry_price = None

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
                self.entry_price = self.data.close[0]
        else:
            if self.crossover < 0:
                exit_price = self.data.close[0]
                if self.entry_price:
                    trade_return = (exit_price - self.entry_price) / self.entry_price
                    self.trade_returns.append(trade_return)
                self.close()
                self.entry_price = None


def run_backtest_with_metrics(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01'):
    """백테스트 실행 및 성과 지표 계산"""

    # 데이터 다운로드
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return

    # Backtrader 설정
    cerebro = bt.Cerebro()

    # 데이터 피드 생성
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)

    # 전략 추가
    cerebro.addstrategy(SMAStrategy)

    # 초기 자본
    cerebro.broker.setcash(100000.0)

    # 수수료 설정
    cerebro.broker.setcommission(commission=0.001)

    print(f'초기 자본: ${cerebro.broker.getvalue():,.2f}')

    # 백테스트 실행
    strategies = cerebro.run()
    strategy = strategies[0]

    final_value = cerebro.broker.getvalue()
    print(f'최종 자본: ${final_value:,.2f}')

    # 성과 지표 계산을 위한 데이터 준비
    # 일별 수익률 계산
    portfolio_values = []

    # Backtrader로 포트폴리오 값 추출
    for i in range(len(data)):
        cerebro.broker.setcash(100000.0)  # 초기화
        temp_cerebro = bt.Cerebro()
        temp_data = bt.feeds.PandasData(dataname=data.iloc[:i+1])
        temp_cerebro.adddata(temp_data)
        temp_cerebro.addstrategy(SMAStrategy)
        temp_cerebro.broker.setcommission(commission=0.001)
        temp_cerebro.run()
        portfolio_values.append(temp_cerebro.broker.getvalue())

    # 자산 곡선 생성
    equity_curve = pd.Series(portfolio_values, index=data.index)

    # 일별 수익률
    returns = equity_curve.pct_change().dropna()

    # 거래 수익률
    trade_returns = strategy.trade_returns

    # 성과 지표 계산
    metrics = PerformanceMetrics(returns, equity_curve, trade_returns)

    return metrics, equity_curve, data


def plot_performance_dashboard(metrics, equity_curve, price_data, symbol):
    """성과 대시보드 시각화"""

    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(f'{symbol} Strategy Performance Dashboard', fontsize=16, fontweight='bold')

    # 1. Equity Curve
    ax1 = axes[0, 0]
    equity_curve.plot(ax=ax1, label='Strategy', linewidth=2)
    ax1.set_title('Equity Curve')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Drawdown
    ax2 = axes[0, 1]
    returns = equity_curve.pct_change().dropna()
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    drawdown.plot(ax=ax2, color='red', linewidth=2)
    ax2.fill_between(drawdown.index, 0, drawdown, color='red', alpha=0.3)
    ax2.set_title('Drawdown')
    ax2.set_ylabel('Drawdown (%)')
    ax2.grid(True, alpha=0.3)

    # 3. Monthly Returns
    ax3 = axes[1, 0]
    monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
    monthly_returns.plot(kind='bar', ax=ax3, color=['g' if x > 0 else 'r' for x in monthly_returns])
    ax3.set_title('Monthly Returns')
    ax3.set_ylabel('Return (%)')
    ax3.set_xlabel('Month')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # 4. Returns Distribution
    ax4 = axes[1, 1]
    returns.hist(bins=50, ax=ax4, edgecolor='black', alpha=0.7)
    ax4.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.4f}')
    ax4.set_title('Returns Distribution')
    ax4.set_xlabel('Daily Return')
    ax4.set_ylabel('Frequency')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 5. Cumulative Returns
    ax5 = axes[2, 0]
    strategy_cumret = (1 + returns).cumprod() - 1
    buy_hold_ret = price_data['Close'].pct_change().dropna()
    buy_hold_cumret = (1 + buy_hold_ret).cumprod() - 1

    strategy_cumret.plot(ax=ax5, label='Strategy', linewidth=2)
    buy_hold_cumret.plot(ax=ax5, label='Buy & Hold', linewidth=2, linestyle='--')
    ax5.set_title('Cumulative Returns Comparison')
    ax5.set_ylabel('Cumulative Return')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 6. Performance Metrics Table
    ax6 = axes[2, 1]
    ax6.axis('off')

    metrics_dict = metrics.get_all_metrics()

    # 테이블 데이터 준비
    table_data = []
    for key, value in metrics_dict.items():
        table_data.append([key, value])

    # 테이블 생성
    table = ax6.table(cellText=table_data,
                      colLabels=['Metric', 'Value'],
                      cellLoc='left',
                      loc='center',
                      colWidths=[0.6, 0.4])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # 헤더 스타일
    for i in range(2):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # 행 색상 교체
    for i in range(1, len(table_data) + 1):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    ax6.set_title('Performance Metrics', fontweight='bold', pad=20)

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)

    output_path = os.path.join(images_dir, 'performance_dashboard.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n대시보드 저장됨: {output_path}")

    plt.show()


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 12: 성과 지표와 리스크 측정")
    print("Performance Metrics and Risk Measurement")
    print("=" * 60)

    # 백테스트 실행
    metrics, equity_curve, price_data = run_backtest_with_metrics(
        symbol='NVDA',
        start_date='2020-01-01',
        end_date='2024-01-01'
    )

    # 성과 지표 출력
    print("\n" + "=" * 60)
    print("성과 지표 (Performance Metrics)")
    print("=" * 60)

    metrics_dict = metrics.get_all_metrics()
    for key, value in metrics_dict.items():
        print(f"{key:20s}: {value}")

    # 지표 해석
    print("\n" + "=" * 60)
    print("지표 해석 (Interpretation)")
    print("=" * 60)

    sharpe = metrics.sharpe_ratio()
    if sharpe > 2:
        sharpe_rating = "매우 좋음 (Excellent)"
    elif sharpe > 1:
        sharpe_rating = "양호 (Good)"
    elif sharpe > 0:
        sharpe_rating = "보통 (Fair)"
    else:
        sharpe_rating = "나쁨 (Poor)"

    print(f"Sharpe Ratio {sharpe:.2f}: {sharpe_rating}")

    profit_factor = metrics.profit_factor()
    if profit_factor > 2:
        pf_rating = "우수 (Excellent)"
    elif profit_factor > 1.5:
        pf_rating = "좋음 (Good)"
    elif profit_factor > 1:
        pf_rating = "수익성 있음 (Profitable)"
    else:
        pf_rating = "손실 (Losing)"

    print(f"Profit Factor {profit_factor:.2f}: {pf_rating}")

    mdd = metrics.maximum_drawdown()
    if mdd > -0.1:
        mdd_rating = "낮은 리스크 (Low Risk)"
    elif mdd > -0.2:
        mdd_rating = "중간 리스크 (Medium Risk)"
    else:
        mdd_rating = "높은 리스크 (High Risk)"

    print(f"Maximum Drawdown {mdd:.2%}: {mdd_rating}")

    # 대시보드 시각화
    plot_performance_dashboard(metrics, equity_curve, price_data, 'NVDA')

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
