"""
Chapter 6: RSI 및 과매수/과매도 전략
RSI (Relative Strength Index) Strategy using Backtrader

이 스크립트는 RSI 과매수/과매도 전략을 구현합니다:
- 기본 RSI(30/70) 전략
- 보수적 RSI(20/80) 전략
- 추세 필터 추가 RSI 전략
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


class RSIStrategy(bt.Strategy):
    """
    RSI 과매수/과매도 전략

    Parameters:
        rsi_period: RSI 계산 기간 (기본값: 14)
        rsi_lower: 과매도 임계값 (기본값: 30)
        rsi_upper: 과매수 임계값 (기본값: 70)
        use_trend_filter: 추세 필터 사용 여부 (기본값: False)
        trend_period: 추세 필터용 SMA 기간 (기본값: 200)
    """
    params = (
        ('rsi_period', 14),
        ('rsi_lower', 30),
        ('rsi_upper', 70),
        ('use_trend_filter', False),
        ('trend_period', 200),
        ('printlog', False),
    )

    def __init__(self):
        # RSI 지표
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_period
        )

        # 추세 필터 (선택적)
        if self.params.use_trend_filter:
            self.sma = bt.indicators.SMA(
                self.data.close,
                period=self.params.trend_period
            )

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
                          f'RSI: {self.rsi[0]:.2f}')
            else:  # Sell
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 체결 - '
                          f'가격: ${order.executed.price:.2f}, '
                          f'RSI: {self.rsi[0]:.2f}')

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

        # 포지션이 없을 때
        if not self.position:
            # 과매도 영역: 매수 신호
            if self.rsi < self.params.rsi_lower:
                # 추세 필터 사용 시 상승 추세에서만 매수
                if self.params.use_trend_filter:
                    if self.data.close > self.sma:
                        if self.params.printlog:
                            print(f'{self.data.datetime.date(0)}: 과매도 (RSI={self.rsi[0]:.2f}) - 매수')
                        self.order = self.buy()
                else:
                    if self.params.printlog:
                        print(f'{self.data.datetime.date(0)}: 과매도 (RSI={self.rsi[0]:.2f}) - 매수')
                    self.order = self.buy()

        # 포지션이 있을 때
        else:
            # 과매수 영역: 매도 신호
            if self.rsi > self.params.rsi_upper:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 과매수 (RSI={self.rsi[0]:.2f}) - 매도')
                self.order = self.close()


def run_backtest(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01',
                 rsi_lower=30, rsi_upper=70, use_trend_filter=False):
    """
    백테스트 실행

    Args:
        ticker: 티커 심볼
        start_date: 시작일
        end_date: 종료일
        rsi_lower: 과매도 임계값
        rsi_upper: 과매수 임계값
        use_trend_filter: 추세 필터 사용 여부

    Returns:
        cerebro, strategy, initial_value, final_value, data
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
    cerebro.addstrategy(
        RSIStrategy,
        rsi_period=14,
        rsi_lower=rsi_lower,
        rsi_upper=rsi_upper,
        use_trend_filter=use_trend_filter,
        trend_period=200,
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


def calculate_rsi(data, period=14):
    """
    RSI 수동 계산 (시각화용)

    Args:
        data: 가격 데이터 (pandas Series)
        period: RSI 기간

    Returns:
        RSI 값 (pandas Series)
    """
    # 가격 변화
    delta = data.diff()

    # 상승/하락 분리
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Wilder의 평활화 (EMA와 유사)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    # RS 계산
    rs = avg_gain / avg_loss

    # RSI 계산
    rsi = 100 - (100 / (1 + rs))

    return rsi


def visualize_strategy(data, ticker='AAPL'):
    """전략 시각화"""
    fig = plt.figure(figsize=(15, 10))

    # RSI 계산
    rsi = calculate_rsi(data['Close'], period=14)

    # 1. 가격 차트
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, alpha=0.7)

    # 과매수/과매도 신호 표시
    oversold = rsi < 30
    overbought = rsi > 70

    ax1.scatter(data.index[oversold], data['Close'][oversold],
                marker='^', color='green', s=100, label='Oversold (RSI<30)', zorder=5, alpha=0.6)
    ax1.scatter(data.index[overbought], data['Close'][overbought],
                marker='v', color='red', s=100, label='Overbought (RSI>70)', zorder=5, alpha=0.6)

    ax1.set_title(f'{ticker} - Price with RSI Signals', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=10)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 2. RSI 차트
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(data.index, rsi, label='RSI(14)', linewidth=1.5, color='purple', alpha=0.7)

    # 과매수/과매도 기준선
    ax2.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Overbought (70)')
    ax2.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Oversold (30)')
    ax2.axhline(y=50, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)

    # 과매수/과매도 영역 색칠
    ax2.fill_between(data.index, 70, 100, alpha=0.1, color='red')
    ax2.fill_between(data.index, 0, 30, alpha=0.1, color='green')

    ax2.set_title('RSI(14) Indicator', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('RSI', fontsize=10)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'rsi_strategy.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("Chapter 6: RSI 및 과매수/과매도 전략")
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
    print(f"- 전략: RSI(14) 과매수/과매도")

    print(f"\n{'='*50}")
    print("백테스트 실행 중...")
    print(f"{'='*50}")

    # 1. 기본 RSI 전략 (30/70)
    print("\n[1/4] 기본 RSI(30/70) 전략 실행 중...")
    cerebro1, strategy1, initial1, final1, data = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        rsi_lower=30,
        rsi_upper=70,
        use_trend_filter=False
    )
    print_performance("RSI(30/70)", initial1, final1, strategy1.analyzers)

    # 2. 보수적 RSI 전략 (20/80)
    print("\n[2/4] 보수적 RSI(20/80) 전략 실행 중...")
    cerebro2, strategy2, initial2, final2, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        rsi_lower=20,
        rsi_upper=80,
        use_trend_filter=False
    )
    print_performance("RSI(20/80)", initial2, final2, strategy2.analyzers)

    # 3. 추세 필터 RSI 전략
    print("\n[3/4] 추세 필터 RSI(30/70) 전략 실행 중...")
    cerebro3, strategy3, initial3, final3, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        rsi_lower=30,
        rsi_upper=70,
        use_trend_filter=True
    )
    print_performance("RSI(30/70) + SMA(200) 필터", initial3, final3, strategy3.analyzers)

    # 4. Buy & Hold 벤치마크
    print("\n[4/4] Buy & Hold 벤치마크 계산 중...")
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

    rsi1_return = ((final1 - initial1) / initial1) * 100
    rsi2_return = ((final2 - initial2) / initial2) * 100
    rsi3_return = ((final3 - initial3) / initial3) * 100

    print(f"\nBuy & Hold:              {buy_hold_return:+.2f}%")
    print(f"RSI(30/70):              {rsi1_return:+.2f}%")
    print(f"RSI(20/80):              {rsi2_return:+.2f}%")
    print(f"RSI(30/70) + 추세 필터:   {rsi3_return:+.2f}%")

    print(f"\nBuy & Hold 대비:")
    print(f"- RSI(30/70) 초과 수익:         {rsi1_return - buy_hold_return:+.2f}%")
    print(f"- RSI(20/80) 초과 수익:         {rsi2_return - buy_hold_return:+.2f}%")
    print(f"- RSI(30/70)+필터 초과 수익:    {rsi3_return - buy_hold_return:+.2f}%")

    # 시각화
    print("\n차트 생성 중...")
    visualize_strategy(data, ticker)

    print(f"\n{'='*50}")
    print("RSI 전략 백테스트 완료!")
    print(f"{'='*50}")

    print("\n주요 인사이트:")
    print("- RSI는 역추세(mean reversion) 전략")
    print("- 과매도/과매수 영역에서 반전을 포착")
    print("- 횡보장에서 효과적, 강한 추세에서는 손실 가능")
    print("- 추세 필터를 추가하면 거짓 신호 감소")
    print("- 임계값(30/70 vs 20/80)에 따라 거래 빈도 차이")
    print("\n다음 챕터에서는 Bollinger Bands를 사용한")
    print("변동성 기반 전략을 배워봅시다!")


if __name__ == '__main__':
    main()
