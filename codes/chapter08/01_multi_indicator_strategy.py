"""
Chapter 8: 다중 지표 결합 전략
Multi-Indicator Combined Strategy using Backtrader

이 스크립트는 여러 지표를 결합한 전략들을 구현합니다:
- 전략 1: 추세 확인 + 과매도 진입
- 전략 2: 골든 크로스 + 모멘텀 확인
- 전략 3: 종합 신호 점수
- 단일 지표 전략과 비교
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


class TrendOversoldStrategy(bt.Strategy):
    """
    전략 1: 추세 확인 + 과매도 진입

    상승 추세 중 일시적 조정을 매수 기회로 활용
    """
    params = (
        ('sma_period', 200),
        ('rsi_period', 14),
        ('rsi_lower', 30),
        ('rsi_upper', 70),
        ('bb_period', 20),
        ('bb_dev', 2.0),
        ('printlog', False),
    )

    def __init__(self):
        # 추세 지표
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.sma_period)

        # 모멘텀 지표
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        # 변동성 지표
        self.bband = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_dev
        )

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 - RSI={self.rsi[0]:.1f}')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 - RSI={self.rsi[0]:.1f}')
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 매수 조건: 모두 충족
            uptrend = self.data.close > self.sma  # 상승 추세
            oversold = self.rsi < self.params.rsi_lower  # 과매도
            near_lower = self.data.close < self.bband.lines.mid  # BB 중간 이하

            if uptrend and oversold and near_lower:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 신호 - 추세+과매도+BB')
                self.order = self.buy()

        else:
            # 매도 조건
            overbought = self.rsi > self.params.rsi_upper
            above_upper = self.data.close > self.bband.lines.top

            if overbought or above_upper:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 신호 - 과매수 or BB상단')
                self.order = self.close()


class GoldenCrossMomentumStrategy(bt.Strategy):
    """
    전략 2: 골든 크로스 + 모멘텀 확인

    강한 신호만 선택하여 추세 시작 포착
    """
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
        ('rsi_period', 14),
        ('rsi_threshold', 50),
        ('printlog', False),
    )

    def __init__(self):
        # 이동평균
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)

        # 크로스오버
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        # RSI
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        # Bollinger Bands (변동성 확인용)
        self.bband = bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)
        self.bandwidth = (self.bband.lines.top - self.bband.lines.bot) / self.bband.lines.mid

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 - 골든크로스+모멘텀')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 - 데드크로스')
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # 골든 크로스 + RSI > 50 (상승 모멘텀 확인)
            if self.crossover > 0 and self.rsi > self.params.rsi_threshold:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 골든크로스 + RSI={self.rsi[0]:.1f}')
                self.order = self.buy()

        else:
            # 데드 크로스
            if self.crossover < 0:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 데드크로스')
                self.order = self.close()


class CompositeScoreStrategy(bt.Strategy):
    """
    전략 3: 종합 신호 점수

    여러 지표의 점수를 합산하여 유연한 의사결정
    """
    params = (
        ('sma_period', 200),
        ('rsi_period', 14),
        ('bb_period', 20),
        ('bb_dev', 2.0),
        ('buy_threshold', 3),
        ('sell_threshold', -3),
        ('printlog', False),
    )

    def __init__(self):
        # 지표들
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.sma_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.bband = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_dev
        )

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매수 - Score={self.calculate_score():.0f}')
            else:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: 매도 - Score={self.calculate_score():.0f}')
        self.order = None

    def calculate_score(self):
        """종합 신호 점수 계산"""
        score = 0

        # 추세 점수 (±2)
        if self.data.close > self.sma:
            score += 2
        elif self.data.close < self.sma:
            score -= 2

        # 모멘텀 점수 (±2)
        if self.rsi < 30:
            score += 2
        elif self.rsi > 70:
            score -= 2

        # 변동성 점수 (±1)
        if self.data.close < self.bband.lines.bot:
            score += 1
        elif self.data.close > self.bband.lines.top:
            score -= 1

        return score

    def next(self):
        if self.order:
            return

        score = self.calculate_score()

        if not self.position:
            # 점수가 임계값 이상: 매수
            if score >= self.params.buy_threshold:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: Score={score:.0f} >= {self.params.buy_threshold}')
                self.order = self.buy()

        else:
            # 점수가 임계값 이하: 매도
            if score <= self.params.sell_threshold:
                if self.params.printlog:
                    print(f'{self.data.datetime.date(0)}: Score={score:.0f} <= {self.params.sell_threshold}')
                self.order = self.close()


def run_backtest(ticker='AAPL', start_date='2019-01-01', end_date='2024-01-01',
                 strategy_class=TrendOversoldStrategy):
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
    print(f"=== {strategy_name} ===")
    print(f"{'='*50}")

    # 기본 지표
    total_return = ((final_value - initial_value) / initial_value) * 100
    print(f"\n총 수익률: {total_return:+.2f}%")

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
    else:
        print(f"거래 횟수: 0")


def visualize_indicators(data, ticker='AAPL'):
    """다중 지표 시각화"""
    fig = plt.figure(figsize=(15, 14))

    # 지표 계산
    sma_50 = data['Close'].rolling(window=50).mean()
    sma_200 = data['Close'].rolling(window=200).mean()

    # RSI 계산
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Bollinger Bands 계산
    sma_20 = data['Close'].rolling(window=20).mean()
    std_20 = data['Close'].rolling(window=20).std()
    upper_band = sma_20 + (std_20 * 2)
    lower_band = sma_20 - (std_20 * 2)

    # 1. 가격 + 이동평균
    ax1 = plt.subplot(4, 1, 1)
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, alpha=0.7, color='black')
    ax1.plot(data.index, sma_50, label='SMA(50)', linewidth=1, alpha=0.7, color='blue')
    ax1.plot(data.index, sma_200, label='SMA(200)', linewidth=1, alpha=0.7, color='red')

    # 골든/데드 크로스
    golden_cross = (sma_50 > sma_200) & (sma_50.shift(1) <= sma_200.shift(1))
    death_cross = (sma_50 < sma_200) & (sma_50.shift(1) >= sma_200.shift(1))

    ax1.scatter(data.index[golden_cross], data['Close'][golden_cross],
                marker='^', color='green', s=150, label='Golden Cross', zorder=5)
    ax1.scatter(data.index[death_cross], data['Close'][death_cross],
                marker='v', color='red', s=150, label='Death Cross', zorder=5)

    ax1.set_title(f'{ticker} - Price with Moving Averages', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=10)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 2. RSI
    ax2 = plt.subplot(4, 1, 2)
    ax2.plot(data.index, rsi, label='RSI(14)', linewidth=1.5, color='purple', alpha=0.7)
    ax2.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Overbought (70)')
    ax2.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Oversold (30)')
    ax2.fill_between(data.index, 70, 100, alpha=0.1, color='red')
    ax2.fill_between(data.index, 0, 30, alpha=0.1, color='green')

    ax2.set_title('RSI(14) - Momentum Indicator', fontsize=12, fontweight='bold')
    ax2.set_ylabel('RSI', fontsize=10)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)

    # 3. Bollinger Bands
    ax3 = plt.subplot(4, 1, 3)
    ax3.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, color='black', alpha=0.7)
    ax3.plot(data.index, sma_20, label='Middle Band', linewidth=1, color='blue', alpha=0.7)
    ax3.plot(data.index, upper_band, label='Upper Band', linewidth=1, color='red', linestyle='--', alpha=0.7)
    ax3.plot(data.index, lower_band, label='Lower Band', linewidth=1, color='green', linestyle='--', alpha=0.7)
    ax3.fill_between(data.index, upper_band, lower_band, alpha=0.1, color='gray')

    ax3.set_title('Bollinger Bands - Volatility Indicator', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Price ($)', fontsize=10)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)

    # 4. 종합 신호 점수
    ax4 = plt.subplot(4, 1, 4)

    # 점수 계산
    score = pd.Series(0, index=data.index)

    # 추세 점수
    score += (data['Close'] > sma_200) * 2
    score -= (data['Close'] < sma_200) * 2

    # 모멘텀 점수
    score += (rsi < 30) * 2
    score -= (rsi > 70) * 2

    # 변동성 점수
    score += (data['Close'] < lower_band) * 1
    score -= (data['Close'] > upper_band) * 1

    ax4.plot(data.index, score, label='Composite Score', linewidth=1.5, color='orange', alpha=0.7)
    ax4.axhline(y=3, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Buy Threshold (3)')
    ax4.axhline(y=-3, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Sell Threshold (-3)')
    ax4.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)

    ax4.fill_between(data.index, 3, score.max()+1, alpha=0.1, color='green')
    ax4.fill_between(data.index, -3, score.min()-1, alpha=0.1, color='red')

    ax4.set_title('Composite Signal Score', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Date', fontsize=10)
    ax4.set_ylabel('Score', fontsize=10)
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, 'multi_indicator_strategy.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n차트 저장 완료: {save_path}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Chapter 8: 다중 지표 결합 전략")
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
    print(f"- 수수료: 0.1%")

    print(f"\n{'='*60}")
    print("백테스트 실행 중...")
    print(f"{'='*60}")

    results = {}

    # 1. 추세 확인 + 과매도 진입 전략
    print("\n[1/3] 추세 확인 + 과매도 진입 전략...")
    _, strategy1, initial1, final1, data = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=TrendOversoldStrategy
    )
    results['추세+과매도'] = (final1 - initial1) / initial1 * 100
    print_performance("추세 확인 + 과매도 진입", initial1, final1, strategy1.analyzers)

    # 2. 골든 크로스 + 모멘텀 확인 전략
    print("\n[2/3] 골든 크로스 + 모멘텀 확인 전략...")
    _, strategy2, initial2, final2, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=GoldenCrossMomentumStrategy
    )
    results['골든크로스+모멘텀'] = (final2 - initial2) / initial2 * 100
    print_performance("골든 크로스 + 모멘텀 확인", initial2, final2, strategy2.analyzers)

    # 3. 종합 신호 점수 전략
    print("\n[3/3] 종합 신호 점수 전략...")
    _, strategy3, initial3, final3, _ = run_backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        strategy_class=CompositeScoreStrategy
    )
    results['종합점수'] = (final3 - initial3) / initial3 * 100
    print_performance("종합 신호 점수", initial3, final3, strategy3.analyzers)

    # Buy & Hold 벤치마크
    buy_hold_return = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
    results['Buy & Hold'] = buy_hold_return

    # 비교 요약
    print(f"\n{'='*60}")
    print("=== 전략 비교 요약 ===")
    print(f"{'='*60}")

    print(f"\nBuy & Hold:                     {results['Buy & Hold']:+.2f}%")
    print(f"추세 확인 + 과매도 진입:          {results['추세+과매도']:+.2f}%")
    print(f"골든 크로스 + 모멘텀 확인:        {results['골든크로스+모멘텀']:+.2f}%")
    print(f"종합 신호 점수:                  {results['종합점수']:+.2f}%")

    # 시각화
    print("\n차트 생성 중...")
    visualize_indicators(data, ticker)

    print(f"\n{'='*60}")
    print("다중 지표 결합 전략 백테스트 완료!")
    print(f"{'='*60}")

    print("\n주요 인사이트:")
    print("- 다중 지표 결합으로 신호 신뢰도 향상")
    print("- 추세 필터링으로 거짓 신호 감소")
    print("- 모멘텀 확인으로 진입 타이밍 개선")
    print("- 종합 점수로 유연한 의사결정 가능")
    print("- 과최적화 주의 - 단순함 유지 중요")
    print("\nPart 2 (기술적 분석 전략) 완료!")
    print("다음 Part 3에서는 리스크 관리와")
    print("포트폴리오 구성을 배워봅시다!")


if __name__ == '__main__':
    main()
