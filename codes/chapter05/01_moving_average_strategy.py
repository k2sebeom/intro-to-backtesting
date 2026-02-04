"""
Chapter 5: 이동평균 전략
Moving Average Crossover Strategy using Backtrader

이 스크립트는 골든 크로스/데드 크로스 전략을 구현합니다:
- SMA(50/200) 크로스오버 전략
- EMA(50/200) 크로스오버 전략
- Buy & Hold 벤치마크 비교
"""

import os
import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class MovingAverageCrossStrategy(bt.Strategy):
    """
    이동평균 크로스오버 전략

    Parameters:
        fast_period: 단기 이동평균 기간 (기본값: 50)
        slow_period: 장기 이동평균 기간 (기본값: 200)
        ma_type: 이동평균 타입 ('sma' 또는 'ema')
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('ma_type', 'sma'),  # 'sma' or 'ema'
        ('printlog', False),
    )

    def __init__(self):
        # 이동평균 선택
        if self.params.ma_type == 'sma':
            self.fast_ma = bt.indicators.SMA(
                self.data.close,
                period=self.params.fast_period
            )
            self.slow_ma = bt.indicators.SMA(
                self.data.close,
                period=self.params.slow_period
            )
        else:  # ema
            self.fast_ma = bt.indicators.EMA(
                self.data.close,
                period=self.params.fast_period
            )
            self.slow_ma = bt.indicators.EMA(
                self.data.close,
                period=self.params.slow_period
            )

        # 크로스오버 신호
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        # 매매 기록
        self.order = None
        self.buy_price = None
        self.buy_comm = None

    def notify_order(self, order):
        """주문 상태 변경 알림"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 체결 - '
                          f'가격: ${order.executed.price:.2f}, '
                          f'수수료: ${order.executed.comm:.2f}')
            else:  # Sell
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 체결 - '
                          f'가격: ${order.executed.price:.2f}, '
                          f'수수료: ${order.executed.comm:.2f}')

        self.order = None

    def notify_trade(self, trade):
        """거래 완료 알림"""
        if not trade.isclosed:
            return

        if self.params.printlog:
            print(f'{self.data.datetime.date(0)}: 거래 손익 - '
                  f'총손익: ${trade.pnl:.2f}, '
                  f'순손익: ${trade.pnlcomm:.2f}')

    def next(self):
        """매 봉마다 실행되는 로직"""
        # 이미 주문이 진행 중이면 대기
        if self.order:
            return

        # 골든 크로스: 매수
        if self.crossover > 0:
            if not self.position:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 골든 크로스 - 매수 신호')
                self.order = self.buy()

        # 데드 크로스: 매도
        elif self.crossover < 0:
            if self.position:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 데드 크로스 - 매도 신호')
                self.order = self.close()


def run_backtest(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01',
                 ma_type='sma', fast=50, slow=200):
    """
    백테스트 실행

    Args:
        ticker: 티커 심볼
        start_date: 시작일
        end_date: 종료일
        ma_type: 이동평균 타입 ('sma' 또는 'ema')
        fast: 단기 이동평균 기간
        slow: 장기 이동평균 기간

    Returns:
        cerebro: Backtrader Cerebro 인스턴스
    """
    # 데이터 다운로드
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Multi-index 컬럼 처리 (yfinance가 multi-index를 반환하는 경우)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    # Backtrader 데이터 피드 생성
    data_feed = bt.feeds.PandasData(dataname=data)

    # Cerebro 엔진 초기화
    cerebro = bt.Cerebro()

    # 전략 추가
    cerebro.addstrategy(
        MovingAverageCrossStrategy,
        fast_period=fast,
        slow_period=slow,
        ma_type=ma_type,
        printlog=False
    )

    # 데이터 피드 추가
    cerebro.adddata(data_feed)

    # 초기 자금 설정
    cerebro.broker.setcash(10000.0)

    # 수수료 설정
    cerebro.broker.setcommission(commission=0.001)

    # 포지션 크기 설정 (95% 투자)
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
    print(f"\n{'='*50}")
    print(f"=== {strategy_name} 성과 ===")
    print(f"{'='*50}")

    # 기본 지표
    total_return = ((final_value - initial_value) / initial_value) * 100
    print(f"\n기본 지표:")
    print(f"- 초기 자금: ${initial_value:,.2f}")
    print(f"- 최종 자금: ${final_value:,.2f}")
    print(f"- 총 수익률: {total_return:+.2f}%")

    # Sharpe Ratio
    sharpe = analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', None)
    if sharpe_ratio is not None:
        print(f"\nSharpe Ratio: {sharpe_ratio:.3f}")

    # Drawdown
    drawdown = analyzers.drawdown.get_analysis()
    print(f"\n최대 낙폭:")
    print(f"- Max Drawdown: {drawdown['max']['drawdown']:.2f}%")
    if drawdown['max']['len'] > 0:
        print(f"- DD Duration: {drawdown['max']['len']} days")

    # Returns
    returns = analyzers.returns.get_analysis()
    print(f"\n수익률:")
    print(f"- Total Return: {returns['rtot']*100:+.2f}%")
    print(f"- Annualized Return: {returns['rnorm100']:.2f}%")

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
    else:
        print(f"\n거래 통계:")
        print(f"- 총 거래: 0")
        print(f"- 매매 신호가 발생하지 않았습니다.")


def visualize_strategy(data, cerebro_sma, cerebro_ema, ticker='AAPL'):
    """전략 시각화"""
    fig = plt.figure(figsize=(15, 12))

    # 1. SMA 전략
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, alpha=0.7)

    # SMA 계산 및 플롯
    sma_50 = data['Close'].rolling(window=50).mean()
    sma_200 = data['Close'].rolling(window=200).mean()
    ax1.plot(data.index, sma_50, label='SMA(50)', linewidth=1, alpha=0.8)
    ax1.plot(data.index, sma_200, label='SMA(200)', linewidth=1, alpha=0.8)

    # 골든/데드 크로스 표시
    golden_cross = (sma_50 > sma_200) & (sma_50.shift(1) <= sma_200.shift(1))
    death_cross = (sma_50 < sma_200) & (sma_50.shift(1) >= sma_200.shift(1))

    ax1.scatter(data.index[golden_cross], data['Close'][golden_cross],
                marker='^', color='green', s=100, label='Golden Cross', zorder=5)
    ax1.scatter(data.index[death_cross], data['Close'][death_cross],
                marker='v', color='red', s=100, label='Death Cross', zorder=5)

    ax1.set_title(f'{ticker} - SMA(50/200) Crossover Strategy', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=10)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 2. EMA 전략
    ax2 = plt.subplot(3, 1, 2)
    ax2.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, alpha=0.7)

    # EMA 계산 및 플롯
    ema_50 = data['Close'].ewm(span=50, adjust=False).mean()
    ema_200 = data['Close'].ewm(span=200, adjust=False).mean()
    ax2.plot(data.index, ema_50, label='EMA(50)', linewidth=1, alpha=0.8)
    ax2.plot(data.index, ema_200, label='EMA(200)', linewidth=1, alpha=0.8)

    # 골든/데드 크로스 표시
    golden_cross_ema = (ema_50 > ema_200) & (ema_50.shift(1) <= ema_200.shift(1))
    death_cross_ema = (ema_50 < ema_200) & (ema_50.shift(1) >= ema_200.shift(1))

    ax2.scatter(data.index[golden_cross_ema], data['Close'][golden_cross_ema],
                marker='^', color='green', s=100, label='Golden Cross', zorder=5)
    ax2.scatter(data.index[death_cross_ema], data['Close'][death_cross_ema],
                marker='v', color='red', s=100, label='Death Cross', zorder=5)

    ax2.set_title(f'{ticker} - EMA(50/200) Crossover Strategy', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Price ($)', fontsize=10)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)

    # 3. 성과 비교 (포트폴리오 가치)
    ax3 = plt.subplot(3, 1, 3)

    # Buy & Hold 수익률 계산
    buy_hold_returns = (data['Close'] / data['Close'].iloc[0]) * 10000

    ax3.plot(data.index, buy_hold_returns, label='Buy & Hold',
             linewidth=2, alpha=0.7)

    # 참고: Backtrader의 포트폴리오 가치는 cerebro.plot()으로 확인
    # 여기서는 Buy & Hold와 전략 비교를 위한 시각화만 제공

    ax3.set_title('Strategy Performance Comparison', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Date', fontsize=10)
    ax3.set_ylabel('Portfolio Value ($)', fontsize=10)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'moving_average_strategy.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("Chapter 5: 이동평균 전략")
    print("=" * 50)

    # 설정
    ticker = 'AAPL'
    start_date = '2019-01-01'
    end_date = '2024-01-01'
    initial_cash = 10000.0

    print(f"\n=== 백테스트 설정 ===")
    print(f"- 티커: {ticker}")
    print(f"- 기간: {start_date} ~ {end_date}")
    print(f"- 초기 자금: ${initial_cash:,.2f}")
    print(f"- 수수료: 0.1%")
    print(f"- 전략: SMA(50/200), EMA(50/200) 크로스오버")

    print(f"\n{'='*50}")
    print("백테스트 실행 중...")
    print(f"{'='*50}")

    # 1. SMA 전략
    print("\n[1/3] SMA 전략 실행 중...")
    cerebro_sma, strategy_sma, initial_sma, final_sma, data = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        ma_type='sma',
        fast=50,
        slow=200
    )
    print_performance("SMA(50/200) 크로스오버", initial_sma, final_sma, strategy_sma.analyzers)

    # 2. EMA 전략
    print("\n[2/3] EMA 전략 실행 중...")
    cerebro_ema, strategy_ema, initial_ema, final_ema, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        ma_type='ema',
        fast=50,
        slow=200
    )
    print_performance("EMA(50/200) 크로스오버", initial_ema, final_ema, strategy_ema.analyzers)

    # 3. Buy & Hold 벤치마크
    print("\n[3/3] Buy & Hold 벤치마크 계산 중...")
    buy_hold_return = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
    buy_hold_final = initial_cash * (1 + buy_hold_return / 100)

    print(f"\n{'='*50}")
    print(f"=== Buy & Hold 벤치마크 ===")
    print(f"{'='*50}")
    print(f"- 초기 자금: ${initial_cash:,.2f}")
    print(f"- 최종 자금: ${buy_hold_final:,.2f}")
    print(f"- 총 수익률: {buy_hold_return:+.2f}%")

    # 비교 요약
    print(f"\n{'='*50}")
    print("=== 전략 비교 요약 ===")
    print(f"{'='*50}")

    sma_return = ((final_sma - initial_sma) / initial_sma) * 100
    ema_return = ((final_ema - initial_ema) / initial_ema) * 100

    print(f"\nBuy & Hold:     {buy_hold_return:+.2f}%")
    print(f"SMA(50/200):    {sma_return:+.2f}%")
    print(f"EMA(50/200):    {ema_return:+.2f}%")

    print(f"\nBuy & Hold 대비:")
    print(f"- SMA 초과 수익: {sma_return - buy_hold_return:+.2f}%")
    print(f"- EMA 초과 수익: {ema_return - buy_hold_return:+.2f}%")

    # 시각화
    print("\n차트 생성 중...")
    visualize_strategy(data, cerebro_sma, cerebro_ema, ticker)

    print(f"\n{'='*50}")
    print("이동평균 전략 백테스트 완료!")
    print(f"{'='*50}")

    print("\n주요 인사이트:")
    print("- 이동평균 크로스오버는 추세 추종 전략")
    print("- 강한 트렌드에서 효과적, 횡보장에서는 손실 발생 가능")
    print("- EMA가 SMA보다 최근 가격에 민감하게 반응")
    print("- 신호 지연(lag)으로 인해 진입/청산 시점 늦어질 수 있음")
    print("\n다음 챕터에서는 RSI를 사용한")
    print("과매수/과매도 전략을 배워봅시다!")


if __name__ == '__main__':
    main()
