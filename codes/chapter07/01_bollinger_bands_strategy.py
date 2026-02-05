"""
Chapter 7: Bollinger Bands 전략
Bollinger Bands Strategy using Backtrader

이 스크립트는 Bollinger Bands 기반 전략들을 구현합니다:
- 밴드 반등(Mean Reversion) 전략
- 밴드 돌파(Breakout) 전략
- %B 기반 전략
- Buy & Hold 벤치마크 비교
"""

import os
import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic',
                                'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BollingerBandsMeanReversionStrategy(bt.Strategy):
    """
    Bollinger Bands 밴드 반등 전략 (Mean Reversion)

    하단 밴드 터치 시 매수, 상단 밴드 터치 시 매도
    """
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('printlog', False),
    )

    def __init__(self):
        # Bollinger Bands 지표
        self.bband = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 체결 - ${order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 체결 - ${order.executed.price:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 하단 밴드 터치 또는 돌파: 매수
            if self.data.close[0] <= self.bband.lines.bot[0]:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 하단 밴드 터치 - 매수')
                self.order = self.buy()

        else:
            # 상단 밴드 터치 또는 돌파: 매도
            if self.data.close[0] >= self.bband.lines.top[0]:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 상단 밴드 터치 - 매도')
                self.order = self.close()


class BollingerBandsBreakoutStrategy(bt.Strategy):
    """
    Bollinger Bands 밴드 돌파 전략 (Breakout)

    밴드 스퀴즈 후 상단 밴드 돌파 시 매수
    """
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('squeeze_threshold', 0.05),  # Bandwidth 임계값
        ('printlog', False),
    )

    def __init__(self):
        self.bband = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

        # Bandwidth 계산
        self.bandwidth = (self.bband.lines.top - self.bband.lines.bot) / self.bband.lines.mid

        self.order = None
        self.squeeze_detected = False

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 체결 - ${order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 체결 - ${order.executed.price:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        # 스퀴즈 감지 (낮은 변동성)
        if self.bandwidth[0] < self.params.squeeze_threshold:
            self.squeeze_detected = True

        if not self.position:
            # 스퀴즈 후 상단 밴드 돌파: 매수
            if self.squeeze_detected and self.data.close[0] > self.bband.lines.top[0]:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 스퀴즈 후 상단 밴드 돌파 - 매수')
                self.order = self.buy()
                self.squeeze_detected = False

        else:
            # 중간 밴드 아래로 떨어지면 청산
            if self.data.close[0] < self.bband.lines.mid[0]:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 중간 밴드 이탈 - 매도')
                self.order = self.close()


class BollingerBandsPercentBStrategy(bt.Strategy):
    """
    Bollinger Bands %B 기반 전략

    %B < 0.2: 과매도 → 매수
    %B > 0.8: 과매수 → 매도
    """
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('buy_threshold', 0.2),
        ('sell_threshold', 0.8),
        ('printlog', False),
    )

    def __init__(self):
        self.bband = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

        # %B 계산
        self.percent_b = (self.data.close - self.bband.lines.bot) / \
                        (self.bband.lines.top - self.bband.lines.bot)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 체결 - ${order.executed.price:.2f}, %B={self.percent_b[0]:.2f}')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 체결 - ${order.executed.price:.2f}, %B={self.percent_b[0]:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # %B < 0.2: 매수
            if self.percent_b[0] < self.params.buy_threshold:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: %B={self.percent_b[0]:.2f} < 0.2 - 매수')
                self.order = self.buy()

        else:
            # %B > 0.8: 매도
            if self.percent_b[0] > self.params.sell_threshold:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: %B={self.percent_b[0]:.2f} > 0.8 - 매도')
                self.order = self.close()


def run_backtest(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01',
                 strategy_class=BollingerBandsMeanReversionStrategy):
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


def visualize_strategy(data, ticker='AAPL'):
    """전략 시각화"""
    fig = plt.figure(figsize=(15, 12))

    # Bollinger Bands 계산
    sma_20 = data['Close'].rolling(window=20).mean()
    std_20 = data['Close'].rolling(window=20).std()
    upper_band = sma_20 + (std_20 * 2)
    lower_band = sma_20 - (std_20 * 2)
    bandwidth = (upper_band - lower_band) / sma_20

    # 1. 가격 + Bollinger Bands
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, color='black', alpha=0.7)
    ax1.plot(data.index, sma_20, label='Middle Band (SMA 20)', linewidth=1, color='blue', alpha=0.7)
    ax1.plot(data.index, upper_band, label='Upper Band (+2σ)', linewidth=1, color='red', linestyle='--', alpha=0.7)
    ax1.plot(data.index, lower_band, label='Lower Band (-2σ)', linewidth=1, color='green', linestyle='--', alpha=0.7)

    # 밴드 사이 영역 색칠
    ax1.fill_between(data.index, upper_band, lower_band, alpha=0.1, color='gray')

    # 밴드 터치 신호
    lower_touch = data['Close'] <= lower_band
    upper_touch = data['Close'] >= upper_band

    ax1.scatter(data.index[lower_touch], data['Close'][lower_touch],
                marker='^', color='green', s=50, label='Lower Band Touch', zorder=5, alpha=0.6)
    ax1.scatter(data.index[upper_touch], data['Close'][upper_touch],
                marker='v', color='red', s=50, label='Upper Band Touch', zorder=5, alpha=0.6)

    ax1.set_title(f'{ticker} - Bollinger Bands (20, 2)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=10)
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)

    # 2. Bandwidth (변동성)
    ax2 = plt.subplot(3, 1, 2)
    ax2.plot(data.index, bandwidth, label='Bandwidth', linewidth=1.5, color='purple', alpha=0.7)
    ax2.axhline(y=0.05, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Squeeze Threshold')

    # 스퀴즈 영역 표시
    squeeze = bandwidth < 0.05
    ax2.fill_between(data.index, 0, bandwidth, where=squeeze, alpha=0.3, color='red', label='Squeeze Zone')

    ax2.set_title('Bandwidth (Volatility Indicator)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Bandwidth', fontsize=10)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)

    # 3. %B 지표
    ax3 = plt.subplot(3, 1, 3)
    percent_b = (data['Close'] - lower_band) / (upper_band - lower_band)
    ax3.plot(data.index, percent_b, label='%B', linewidth=1.5, color='orange', alpha=0.7)

    # 임계값 선
    ax3.axhline(y=1.0, color='red', linestyle='-', linewidth=0.5, alpha=0.5)
    ax3.axhline(y=0.8, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Overbought (0.8)')
    ax3.axhline(y=0.5, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    ax3.axhline(y=0.2, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Oversold (0.2)')
    ax3.axhline(y=0.0, color='green', linestyle='-', linewidth=0.5, alpha=0.5)

    # 과매수/과매도 영역 색칠
    ax3.fill_between(data.index, 0.8, 1.2, alpha=0.1, color='red')
    ax3.fill_between(data.index, -0.2, 0.2, alpha=0.1, color='green')

    ax3.set_title('%B Indicator (Position within Bands)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Date', fontsize=10)
    ax3.set_ylabel('%B', fontsize=10)
    ax3.set_ylim(-0.2, 1.2)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'bollinger_bands_strategy.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("Chapter 7: Bollinger Bands 전략")
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
    print(f"- Bollinger Bands: 기간=20, 표준편차=2")

    print(f"\n{'='*50}")
    print("백테스트 실행 중...")
    print(f"{'='*50}")

    # 1. 밴드 반등 전략
    print("\n[1/4] 밴드 반등(Mean Reversion) 전략 실행 중...")
    cerebro1, strategy1, initial1, final1, data = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=BollingerBandsMeanReversionStrategy
    )
    print_performance("밴드 반등 전략", initial1, final1, strategy1.analyzers)

    # 2. 밴드 돌파 전략
    print("\n[2/4] 밴드 돌파(Breakout) 전략 실행 중...")
    cerebro2, strategy2, initial2, final2, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=BollingerBandsBreakoutStrategy
    )
    print_performance("밴드 돌파 전략", initial2, final2, strategy2.analyzers)

    # 3. %B 기반 전략
    print("\n[3/4] %B 기반 전략 실행 중...")
    cerebro3, strategy3, initial3, final3, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=BollingerBandsPercentBStrategy
    )
    print_performance("%B 기반 전략", initial3, final3, strategy3.analyzers)

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

    bb1_return = ((final1 - initial1) / initial1) * 100
    bb2_return = ((final2 - initial2) / initial2) * 100
    bb3_return = ((final3 - initial3) / initial3) * 100

    print(f"\nBuy & Hold:          {buy_hold_return:+.2f}%")
    print(f"밴드 반등 전략:       {bb1_return:+.2f}%")
    print(f"밴드 돌파 전략:       {bb2_return:+.2f}%")
    print(f"%B 기반 전략:         {bb3_return:+.2f}%")

    print(f"\nBuy & Hold 대비:")
    print(f"- 밴드 반등 초과 수익:   {bb1_return - buy_hold_return:+.2f}%")
    print(f"- 밴드 돌파 초과 수익:   {bb2_return - buy_hold_return:+.2f}%")
    print(f"- %B 기반 초과 수익:     {bb3_return - buy_hold_return:+.2f}%")

    # 시각화
    print("\n차트 생성 중...")
    visualize_strategy(data, ticker)

    print(f"\n{'='*50}")
    print("Bollinger Bands 전략 백테스트 완료!")
    print(f"{'='*50}")

    print("\n주요 인사이트:")
    print("- Bollinger Bands는 동적 변동성 기반 지표")
    print("- 밴드 반등: 횡보장에서 효과적")
    print("- 밴드 돌파: 추세 시장에서 효과적")
    print("- Bandwidth: 변동성 수축/확장 감지")
    print("- %B: 밴드 내 가격 위치 정량화")
    print("\n다음 챕터에서는 여러 지표를 결합한")
    print("다중 지표 전략을 배워봅시다!")


if __name__ == '__main__':
    main()
