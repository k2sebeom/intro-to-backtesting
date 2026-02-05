"""
Chapter 4: Backtrader 프레임워크 기초
Buy & Hold 전략 백테스트

이 스크립트는 다음을 수행합니다:
1. Backtrader로 Buy & Hold 전략 구현
2. 초기 자금, 수수료 설정
3. Analyzers를 사용한 성과 분석
4. 벤치마크 (SPY) 비교
5. 포트폴리오 가치 시각화
"""

import sys
import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import backtrader as bt
import yfinance as yf


def print_header():
    """프로그램 헤더 출력"""
    print("=" * 42)
    print("Chapter 4: Backtrader 프레임워크 기초")
    print("=" * 42)
    print()


class BuyAndHoldStrategy(bt.Strategy):
    """
    Buy & Hold 전략
    첫 거래일에 매수하고 끝까지 보유
    """

    def __init__(self):
        """초기화"""
        self.order = None
        self.buy_price = None
        self.buy_comm = None

    def log(self, txt, dt=None):
        """로그 출력"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')

    def next(self):
        """매 바마다 실행"""
        # 이미 주문이 있으면 대기
        if self.order:
            return

        # 포지션이 없으면 매수
        if not self.position:
            # 사용 가능한 모든 자금으로 매수
            self.order = self.buy()
            self.log('매수 주문 실행')

    def notify_order(self, order):
        """주문 상태 변경 알림"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                self.log(f'매수 체결: 가격 ${order.executed.price:.2f}, '
                        f'비용 ${order.executed.value:.2f}, '
                        f'수수료 ${order.executed.comm:.2f}')

            elif order.issell():
                self.log(f'매도 체결: 가격 ${order.executed.price:.2f}, '
                        f'비용 ${order.executed.value:.2f}, '
                        f'수수료 ${order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('주문 취소/거부')

        self.order = None

    def notify_trade(self, trade):
        """거래 완료 알림"""
        if not trade.isclosed:
            return

        self.log(f'거래 종료: 총손익 ${trade.pnl:.2f}, '
                f'순손익 ${trade.pnlcomm:.2f}')

    def stop(self):
        """백테스트 종료 시 호출"""
        self.log(f'최종 포트폴리오 가치: ${self.broker.getvalue():.2f}')


def load_data(data_dir):
    """데이터 로드"""
    data_file = data_dir / "AAPL_5y.csv"

    if not data_file.exists():
        print(f"데이터 파일이 없습니다: {data_file}")
        print("Chapter 2를 먼저 실행하여 데이터를 다운로드하세요.")
        sys.exit(1)

    df = pd.read_csv(data_file, index_col='Date', parse_dates=True)

    # Backtrader 데이터 피드 생성
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 인덱스 사용
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=-1  # 없음
    )

    return data, df


def run_backtest(data, initial_cash=10000.0, commission=0.001):
    """백테스트 실행"""
    print("=== Buy & Hold 전략 백테스트 ===\n")

    # Cerebro 생성
    cerebro = bt.Cerebro()

    # 전략 추가
    cerebro.addstrategy(BuyAndHoldStrategy)

    # 데이터 추가
    cerebro.adddata(data)

    # 브로커 설정
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)

    # 사이저 추가: 사용 가능한 현금의 95%로 매수
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    # Analyzers 추가
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                       riskfreerate=0.01)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    print(f"초기 설정:")
    print(f"- 초기 자금: ${initial_cash:,.2f}")
    print(f"- 수수료: {commission*100:.2f}%")
    print(f"- 데이터: AAPL\n")

    # 백테스트 실행
    print("백테스트 실행 중...\n")
    start_value = cerebro.broker.getvalue()
    results = cerebro.run()
    end_value = cerebro.broker.getvalue()

    return results[0], start_value, end_value


def analyze_results(strategy, start_value, end_value):
    """결과 분석"""
    print("\n" + "=" * 42)
    print("=== 성과 분석 ===")
    print("=" * 42)

    # 기본 지표
    total_return = (end_value - start_value) / start_value * 100
    print("\n기본 지표:")
    print(f"- 초기 자금: ${start_value:,.2f}")
    print(f"- 최종 자금: ${end_value:,.2f}")
    print(f"- 총 수익률: {total_return:+.2f}%")

    # Sharpe Ratio
    sharpe_analysis = strategy.analyzers.sharpe.get_analysis()
    sharpe = sharpe_analysis.get('sharperatio', None)
    if sharpe is not None:
        print(f"\nSharpe Ratio: {sharpe:.3f}")
    else:
        print("\nSharpe Ratio: N/A")

    # Drawdown
    dd_analysis = strategy.analyzers.drawdown.get_analysis()
    print(f"\n최대 낙폭:")
    print(f"- Max Drawdown: {dd_analysis.max.drawdown:.2f}%")
    if dd_analysis.max.len > 0:
        print(f"- DD Duration: {dd_analysis.max.len} days")

    # Returns
    returns_analysis = strategy.analyzers.returns.get_analysis()
    print(f"\n수익률:")
    if 'rtot' in returns_analysis:
        print(f"- Total Return: {returns_analysis['rtot']*100:+.2f}%")
    if 'rnorm' in returns_analysis:
        print(f"- Annualized Return: {returns_analysis['rnorm']*100:+.2f}%")

    # Trades
    trades_analysis = strategy.analyzers.trades.get_analysis()
    print(f"\n거래 통계:")
    if 'total' in trades_analysis and 'total' in trades_analysis['total']:
        total_trades = trades_analysis['total']['total']
        print(f"- 총 거래: {total_trades}")

        if total_trades > 0:
            won = trades_analysis['won']['total'] if 'won' in trades_analysis else 0
            lost = trades_analysis['lost']['total'] if 'lost' in trades_analysis else 0
            win_rate = (won / total_trades * 100) if total_trades > 0 else 0
            print(f"- 승: {won}, 패: {lost}")
            print(f"- 승률: {win_rate:.1f}%")
    else:
        print("- 거래 없음 (현재 포지션 보유 중)")

    print()


def compare_with_benchmark(df, start_value, end_value):
    """벤치마크 비교"""
    print("=" * 42)
    print("=== 벤치마크 비교 (vs SPY) ===")
    print("=" * 42)

    # SPY 데이터 다운로드
    start_date = df.index[0]
    end_date = df.index[-1]

    spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)

    # Handle potential multi-index
    if isinstance(spy_data.columns, pd.MultiIndex):
        spy_close = spy_data[('Close', 'SPY')]
    else:
        spy_close = spy_data['Close']

    # 수익률 계산
    strategy_return = (end_value - start_value) / start_value * 100
    spy_return = (spy_close.iloc[-1] / spy_close.iloc[0] - 1) * 100
    excess_return = strategy_return - spy_return

    print(f"AAPL Buy & Hold: {strategy_return:+.2f}%")
    print(f"SPY: {spy_return:+.2f}%")
    print(f"초과 수익: {excess_return:+.2f}%")
    print()


def create_visualization(df, start_value, end_value):
    """시각화 생성"""
    print("차트 생성 중...")

    plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('Chapter 4: Buy & Hold Strategy Results', fontsize=16, fontweight='bold')

    # 1. 가격 차트
    ax1 = axes[0]
    ax1.plot(df.index, df['Close'], linewidth=2, color='#2E86AB', label='AAPL Price')
    ax1.set_title('AAPL Stock Price', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # 첫 매수 포인트 표시
    ax1.scatter([df.index[0]], [df['Close'].iloc[0]],
               color='green', s=200, marker='^', zorder=5, label='Buy')
    ax1.legend()

    # 2. 포트폴리오 가치 (시뮬레이션)
    ax2 = axes[1]

    # 간단한 포트폴리오 가치 계산
    initial_shares = start_value / df['Close'].iloc[0]
    portfolio_value = initial_shares * df['Close']

    ax2.plot(df.index, portfolio_value, linewidth=2, color='#A23B72', label='Portfolio Value')
    ax2.axhline(y=start_value, color='gray', linestyle='--', linewidth=1, label='Initial Capital')
    ax2.set_title('Portfolio Value Over Time', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Value ($)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 수익률 텍스트
    total_return = (end_value - start_value) / start_value * 100
    ax2.text(0.02, 0.98, f'Total Return: {total_return:+.2f}%',
            transform=ax2.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    # 저장
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    images_dir.mkdir(exist_ok=True)

    output_path = images_dir / "buy_and_hold.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def main():
    """메인 함수"""
    # 헤더
    print_header()

    # 데이터 디렉토리
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    # 1. 데이터 로드
    data, df = load_data(data_dir)

    # 2. 백테스트 실행
    strategy, start_value, end_value = run_backtest(data)

    # 3. 결과 분석
    analyze_results(strategy, start_value, end_value)

    # 4. 벤치마크 비교
    compare_with_benchmark(df, start_value, end_value)

    # 5. 시각화
    output_path = create_visualization(df, start_value, end_value)
    print(f"차트 저장 완료: {output_path.relative_to(Path.cwd())}")

    # 완료 메시지
    print("\n" + "=" * 42)
    print("Buy & Hold 백테스트 완료!")
    print("=" * 42)
    print("\n주요 인사이트:")
    print("- Backtrader 프레임워크 사용법")
    print("- Buy & Hold 벤치마크 전략")
    print("- Analyzers를 통한 성과 분석")
    print("- 전략 vs. 벤치마크 비교")
    print("\n다음 챕터에서는 이동평균 전략을")
    print("구현하고 최적화해봅시다!")


if __name__ == "__main__":
    main()
