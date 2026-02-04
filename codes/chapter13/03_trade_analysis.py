"""
Chapter 13: 백테스트 결과 분석과 시각화
Trade Analysis

이 스크립트는 개별 거래를 분석하고 통계를 시각화합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class TradeAnalyzer(bt.Analyzer):
    """거래 분석기"""

    def __init__(self):
        self.trades = []
        self.entry_price = None
        self.entry_date = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                self.entry_date = self.strategy.data.datetime.date(0)
            elif order.issell() and self.entry_price:
                exit_price = order.executed.price
                exit_date = self.strategy.data.datetime.date(0)

                pnl = exit_price - self.entry_price
                pnl_pct = (exit_price - self.entry_price) / self.entry_price
                duration = (exit_date - self.entry_date).days

                self.trades.append({
                    'entry_date': self.entry_date,
                    'exit_date': exit_date,
                    'entry_price': self.entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'duration': duration,
                    'win': pnl > 0
                })

                self.entry_price = None
                self.entry_date = None

    def get_analysis(self):
        return {'trades': self.trades}


class SMAStrategy(bt.Strategy):
    """이동평균 크로스오버 전략"""

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


def analyze_trades(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01'):
    """거래 분석 및 시각화"""

    # 데이터 다운로드
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return

    # Backtrader 설정
    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(SMAStrategy)
    cerebro.addanalyzer(TradeAnalyzer, _name='trade_analyzer')
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # 백테스트 실행
    print("백테스트 실행 중...")
    strategies = cerebro.run()
    strategy = strategies[0]

    # 거래 데이터 추출
    trade_analysis = strategy.analyzers.trade_analyzer.get_analysis()
    trades = trade_analysis['trades']

    if not trades:
        print("거래가 없습니다.")
        return

    # DataFrame으로 변환
    trades_df = pd.DataFrame(trades)

    # 승패 분리
    winning_trades = trades_df[trades_df['win']]
    losing_trades = trades_df[~trades_df['win']]

    # 통계 계산
    total_trades = len(trades_df)
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

    avg_win = winning_trades['pnl_pct'].mean() if len(winning_trades) > 0 else 0
    avg_loss = losing_trades['pnl_pct'].mean() if len(losing_trades) > 0 else 0

    max_win = trades_df['pnl_pct'].max()
    max_loss = trades_df['pnl_pct'].min()

    avg_duration = trades_df['duration'].mean()
    avg_win_duration = winning_trades['duration'].mean() if len(winning_trades) > 0 else 0
    avg_loss_duration = losing_trades['duration'].mean() if len(losing_trades) > 0 else 0

    # 연속 승패 계산
    consecutive_wins = 0
    consecutive_losses = 0
    max_consecutive_wins = 0
    max_consecutive_losses = 0

    for win in trades_df['win']:
        if win:
            consecutive_wins += 1
            consecutive_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
        else:
            consecutive_losses += 1
            consecutive_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

    # 시각화
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'{symbol} - Trade Analysis', fontsize=16, fontweight='bold')

    # 1. PnL 분포
    ax1 = axes[0, 0]
    trades_df['pnl_pct'].hist(bins=30, ax=ax1, edgecolor='black', alpha=0.7)
    ax1.axvline(0, color='red', linestyle='--', linewidth=2)
    ax1.axvline(avg_win, color='green', linestyle='--', linewidth=1, alpha=0.7, label=f'Avg Win: {avg_win:.2%}')
    ax1.axvline(avg_loss, color='red', linestyle='--', linewidth=1, alpha=0.7, label=f'Avg Loss: {avg_loss:.2%}')
    ax1.set_title('Trade PnL Distribution')
    ax1.set_xlabel('Return (%)')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 승패 비교 박스플롯
    ax2 = axes[0, 1]
    box_data = [winning_trades['pnl_pct'].values * 100, losing_trades['pnl_pct'].values * 100]
    bp = ax2.boxplot(box_data, labels=['Winning', 'Losing'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightgreen')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_title('Win vs Loss Distribution')
    ax2.set_ylabel('Return (%)')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(0, color='red', linestyle='--', linewidth=1)

    # 3. 거래 지속 기간 분포
    ax3 = axes[0, 2]
    trades_df['duration'].hist(bins=30, ax=ax3, edgecolor='black', alpha=0.7, color='blue')
    ax3.axvline(avg_duration, color='red', linestyle='--', linewidth=2, label=f'Avg: {avg_duration:.1f} days')
    ax3.set_title('Trade Duration Distribution')
    ax3.set_xlabel('Days')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. 시간에 따른 거래 수익률
    ax4 = axes[1, 0]
    colors = ['g' if win else 'r' for win in trades_df['win']]
    ax4.scatter(range(len(trades_df)), trades_df['pnl_pct'] * 100, c=colors, alpha=0.6, s=50)
    ax4.axhline(0, color='black', linestyle='-', linewidth=1)
    ax4.set_title('Trade Returns Over Time')
    ax4.set_xlabel('Trade Number')
    ax4.set_ylabel('Return (%)')
    ax4.grid(True, alpha=0.3)

    # 5. 승패별 지속 기간 비교
    ax5 = axes[1, 1]
    duration_data = [winning_trades['duration'].values, losing_trades['duration'].values]
    bp2 = ax5.boxplot(duration_data, labels=['Winning', 'Losing'], patch_artist=True)
    bp2['boxes'][0].set_facecolor('lightgreen')
    bp2['boxes'][1].set_facecolor('lightcoral')
    ax5.set_title('Trade Duration: Win vs Loss')
    ax5.set_ylabel('Days')
    ax5.grid(True, alpha=0.3, axis='y')

    # 6. 통계 테이블
    ax6 = axes[1, 2]
    ax6.axis('off')

    stats_data = [
        ['Total Trades', f'{total_trades}'],
        ['Win Rate', f'{win_rate:.2%}'],
        ['', ''],
        ['Avg Win', f'{avg_win:.2%}'],
        ['Avg Loss', f'{avg_loss:.2%}'],
        ['Max Win', f'{max_win:.2%}'],
        ['Max Loss', f'{max_loss:.2%}'],
        ['', ''],
        ['Avg Duration', f'{avg_duration:.1f} days'],
        ['Win Duration', f'{avg_win_duration:.1f} days'],
        ['Loss Duration', f'{avg_loss_duration:.1f} days'],
        ['', ''],
        ['Max Consecutive Wins', f'{max_consecutive_wins}'],
        ['Max Consecutive Losses', f'{max_consecutive_losses}'],
    ]

    table = ax6.table(cellText=stats_data, cellLoc='left', loc='center', colWidths=[0.6, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    ax6.set_title('Trade Statistics', fontweight='bold', pad=20)

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'trade_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()

    # 상세 통계 출력
    print("\n" + "=" * 60)
    print("거래 통계")
    print("=" * 60)
    print(f"총 거래 횟수: {total_trades}")
    print(f"승리한 거래: {len(winning_trades)} ({win_rate:.2%})")
    print(f"패배한 거래: {len(losing_trades)} ({1-win_rate:.2%})")
    print(f"\n평균 승리: {avg_win:.2%}")
    print(f"평균 손실: {avg_loss:.2%}")
    print(f"손익비 (Avg Win/Avg Loss): {abs(avg_win/avg_loss) if avg_loss != 0 else 0:.2f}")
    print(f"\n최대 승리: {max_win:.2%}")
    print(f"최대 손실: {max_loss:.2%}")
    print(f"\n평균 거래 기간: {avg_duration:.1f} 일")
    print(f"승리 거래 평균 기간: {avg_win_duration:.1f} 일")
    print(f"패배 거래 평균 기간: {avg_loss_duration:.1f} 일")
    print(f"\n최대 연속 승리: {max_consecutive_wins} 회")
    print(f"최대 연속 패배: {max_consecutive_losses} 회")

    # Expectancy 계산
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
    print(f"\n기댓값 (Expectancy): {expectancy:.4f} ({expectancy*100:.2f}%)")

    if expectancy > 0:
        print("  → 양수 기댓값: 장기적으로 수익 가능")
    else:
        print("  → 음수 기댓값: 전략 개선 필요")


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 13: Trade Analysis")
    print("=" * 60)

    analyze_trades(
        symbol='NVDA',
        start_date='2020-01-01',
        end_date='2024-01-01'
    )

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
