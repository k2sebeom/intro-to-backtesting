#!/usr/bin/env python3
"""
Chapter 3: Detailed SMA Backtest with Transaction Costs
거래비용을 고려한 상세 SMA 백테스트

이 스크립트는 거래비용, 슬리피지 등을 고려한 현실적인 백테스트를 수행합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic']
plt.rcParams['axes.unicode_minus'] = False

class SMABacktester:
    def __init__(self, data, short_window, long_window, initial_capital=10000, 
                 commission=0.001, slippage=0.0005):
        """
        SMA 백테스터 초기화
        
        Parameters:
        - data: 주가 데이터
        - short_window: 단기 SMA 기간
        - long_window: 장기 SMA 기간
        - initial_capital: 초기 자본
        - commission: 거래 수수료 (0.1% = 0.001)
        - slippage: 슬리피지 (0.05% = 0.0005)
        """
        self.data = data.copy()
        self.short_window = short_window
        self.long_window = long_window
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.portfolio = pd.DataFrame(index=data.index)
        self.trades = []
        
    def calculate_sma(self):
        """SMA 계산"""
        self.data[f'SMA_{self.short_window}'] = self.data['Close'].rolling(
            window=self.short_window).mean()
        self.data[f'SMA_{self.long_window}'] = self.data['Close'].rolling(
            window=self.long_window).mean()
        
    def generate_signals(self):
        """거래 신호 생성"""
        self.data['Signal'] = 0
        
        # 골든 크로스: 단기 SMA가 장기 SMA를 상향 돌파
        self.data['Signal'] = np.where(
            self.data[f'SMA_{self.short_window}'] > self.data[f'SMA_{self.long_window}'], 1, 0
        )
        
        # 포지션 변화 감지
        self.data['Position'] = self.data['Signal'].diff()
        
    def backtest(self):
        """백테스트 실행"""
        self.calculate_sma()
        self.generate_signals()
        
        # 포트폴리오 초기화
        self.portfolio['Cash'] = self.initial_capital
        self.portfolio['Shares'] = 0
        self.portfolio['Total'] = self.initial_capital
        self.portfolio['Returns'] = 0
        
        current_cash = self.initial_capital
        current_shares = 0
        
        for i in range(len(self.data)):
            date = self.data.index[i]
            price = self.data['Close'].iloc[i]
            position_change = self.data['Position'].iloc[i]
            
            # 거래 실행
            if position_change == 1:  # 매수 신호
                if current_cash > 0:
                    # 슬리피지 적용된 매수 가격
                    buy_price = price * (1 + self.slippage)
                    
                    # 매수 가능한 주식 수 (거래비용 고려)
                    shares_to_buy = int(current_cash / (buy_price * (1 + self.commission)))
                    
                    if shares_to_buy > 0:
                        cost = shares_to_buy * buy_price * (1 + self.commission)
                        current_cash -= cost
                        current_shares += shares_to_buy
                        
                        # 거래 기록
                        self.trades.append({
                            'Date': date,
                            'Type': 'BUY',
                            'Shares': shares_to_buy,
                            'Price': buy_price,
                            'Cost': cost,
                            'Cash_After': current_cash,
                            'Shares_After': current_shares
                        })
                        
            elif position_change == -1:  # 매도 신호
                if current_shares > 0:
                    # 슬리피지 적용된 매도 가격
                    sell_price = price * (1 - self.slippage)
                    
                    # 매도 수익 (거래비용 고려)
                    proceeds = current_shares * sell_price * (1 - self.commission)
                    current_cash += proceeds
                    
                    # 거래 기록
                    self.trades.append({
                        'Date': date,
                        'Type': 'SELL',
                        'Shares': current_shares,
                        'Price': sell_price,
                        'Proceeds': proceeds,
                        'Cash_After': current_cash,
                        'Shares_After': 0
                    })
                    
                    current_shares = 0
            
            # 포트폴리오 가치 업데이트
            self.portfolio.loc[date, 'Cash'] = current_cash
            self.portfolio.loc[date, 'Shares'] = current_shares
            self.portfolio.loc[date, 'Total'] = current_cash + current_shares * price
            
            # 수익률 계산
            if i > 0:
                prev_total = self.portfolio['Total'].iloc[i-1]
                self.portfolio.loc[date, 'Returns'] = (
                    self.portfolio.loc[date, 'Total'] / prev_total - 1
                )
        
        # 누적 수익률 계산
        self.portfolio['Cumulative_Returns'] = (1 + self.portfolio['Returns']).cumprod()
        
    def calculate_metrics(self):
        """성과 지표 계산"""
        total_return = (self.portfolio['Total'].iloc[-1] / self.initial_capital - 1) * 100
        
        # 연간 수익률
        days = (self.data.index[-1] - self.data.index[0]).days
        annual_return = ((self.portfolio['Total'].iloc[-1] / self.initial_capital) ** (365/days) - 1) * 100
        
        # 변동성 (연간화)
        volatility = self.portfolio['Returns'].std() * np.sqrt(252) * 100
        
        # 샤프 비율
        sharpe_ratio = annual_return / volatility if volatility != 0 else 0
        
        # 최대 낙폭
        peak = self.portfolio['Total'].expanding().max()
        drawdown = (self.portfolio['Total'] - peak) / peak
        max_drawdown = drawdown.min() * 100
        
        # 승률
        profitable_trades = 0
        total_trades = len(self.trades) // 2  # 매수-매도 쌍
        
        for i in range(0, len(self.trades), 2):
            if i + 1 < len(self.trades):
                buy_trade = self.trades[i]
                sell_trade = self.trades[i + 1]
                if sell_trade['Proceeds'] > buy_trade['Cost']:
                    profitable_trades += 1
        
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'win_rate': win_rate
        }

def load_nvidia_data():
    """NVIDIA 주식 데이터 로드"""
    data_path = Path(__file__).parent.parent / "data" / "NVDA_1year.csv"
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df.sort_index()
    return df

def main():
    print("=== Chapter 3: Detailed SMA Backtest ===")
    
    # 데이터 로드
    data = load_nvidia_data()
    print(f"데이터 로드 완료: {len(data)}개 데이터 포인트")
    print(f"기간: {data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}")
    
    # 백테스트 설정
    initial_capital = 10000
    commission = 0.001  # 0.1% 거래 수수료
    slippage = 0.0005   # 0.05% 슬리피지
    
    # 다양한 SMA 조합으로 백테스트
    sma_combinations = [
        (5, 20),
        (10, 30),
        (20, 50)
    ]
    
    results = {}
    
    for short, long in sma_combinations:
        print(f"\n=== SMA {short}/{long} 백테스트 ===")
        
        # 백테스터 생성 및 실행
        backtester = SMABacktester(data, short, long, initial_capital, commission, slippage)
        backtester.backtest()
        
        # 성과 지표 계산
        metrics = backtester.calculate_metrics()
        
        results[f"SMA_{short}_{long}"] = {
            'backtester': backtester,
            'metrics': metrics
        }
        
        # 결과 출력
        print(f"총 수익률: {metrics['total_return']:+.2f}%")
        print(f"연간 수익률: {metrics['annual_return']:+.2f}%")
        print(f"변동성: {metrics['volatility']:.2f}%")
        print(f"샤프 비율: {metrics['sharpe_ratio']:.3f}")
        print(f"최대 낙폭: {metrics['max_drawdown']:.2f}%")
        print(f"총 거래 횟수: {metrics['total_trades']}회")
        print(f"승률: {metrics['win_rate']:.1f}%")
        
        # 거래 내역 출력 (처음 5개)
        print(f"\n거래 내역 (처음 5개):")
        for i, trade in enumerate(backtester.trades[:5]):
            print(f"  {i+1}. {trade['Date'].strftime('%Y-%m-%d')} {trade['Type']}: "
                  f"{trade['Shares']}주 @ ${trade['Price']:.2f}")
    
    # Buy & Hold 전략과 비교
    buy_hold_return = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
    print(f"\n매수 후 보유 전략 수익률: {buy_hold_return:+.2f}%")
    
    # 시각화
    fig, axes = plt.subplots(2, 2, figsize=(20, 15))
    
    # 1. 포트폴리오 가치 변화
    ax1 = axes[0, 0]
    for name, result in results.items():
        backtester = result['backtester']
        label = name.replace('_', ' ').replace('SMA', 'SMA ')
        ax1.plot(backtester.portfolio.index, backtester.portfolio['Total'], 
                label=label, linewidth=2)
    
    # Buy & Hold 비교
    buy_hold_value = initial_capital * (data['Close'] / data['Close'].iloc[0])
    ax1.plot(data.index, buy_hold_value, label='Buy & Hold', 
            color='black', linewidth=2, linestyle='--')
    
    ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 누적 수익률
    ax2 = axes[0, 1]
    for name, result in results.items():
        backtester = result['backtester']
        label = name.replace('_', ' ').replace('SMA', 'SMA ')
        cumulative_returns = (backtester.portfolio['Total'] / initial_capital - 1) * 100
        ax2.plot(backtester.portfolio.index, cumulative_returns, label=label, linewidth=2)
    
    buy_hold_cumulative = (buy_hold_value / initial_capital - 1) * 100
    ax2.plot(data.index, buy_hold_cumulative, label='Buy & Hold', 
            color='black', linewidth=2, linestyle='--')
    
    ax2.set_title('Cumulative Returns', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Cumulative Return (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 성과 지표 비교
    ax3 = axes[1, 0]
    strategies = list(results.keys())
    annual_returns = [results[s]['metrics']['annual_return'] for s in strategies]
    
    x_pos = np.arange(len(strategies))
    bars = ax3.bar(x_pos, annual_returns, alpha=0.7, 
                   color=['blue', 'green', 'orange'])
    
    # Buy & Hold 연간 수익률
    days = (data.index[-1] - data.index[0]).days
    buy_hold_annual = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) ** (365/days) - 1) * 100
    ax3.axhline(y=buy_hold_annual, color='red', linestyle='--', linewidth=2, 
               label=f'Buy & Hold: {buy_hold_annual:.1f}%')
    
    ax3.set_title('Annual Returns Comparison', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Strategy')
    ax3.set_ylabel('Annual Return (%)')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([s.replace('_', ' ').replace('SMA', 'SMA ') for s in strategies])
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 거래 빈도 분석
    ax4 = axes[1, 1]
    trade_counts = [results[s]['metrics']['total_trades'] for s in strategies]
    win_rates = [results[s]['metrics']['win_rate'] for s in strategies]
    
    # 이중 y축 사용
    ax4_twin = ax4.twinx()
    
    bars1 = ax4.bar([x - 0.2 for x in x_pos], trade_counts, width=0.4, 
                   alpha=0.7, color='skyblue', label='Total Trades')
    bars2 = ax4_twin.bar([x + 0.2 for x in x_pos], win_rates, width=0.4, 
                        alpha=0.7, color='lightcoral', label='Win Rate (%)')
    
    ax4.set_title('Trading Frequency and Win Rate', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Strategy')
    ax4.set_ylabel('Total Trades', color='blue')
    ax4_twin.set_ylabel('Win Rate (%)', color='red')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([s.replace('_', ' ').replace('SMA', 'SMA ') for s in strategies])
    
    # 범례 결합
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 이미지 저장
    output_path = Path(__file__).parent / "images"
    output_path.mkdir(exist_ok=True)
    plt.savefig(output_path / "sma_detailed_backtest.png", dpi=300, bbox_inches='tight')
    print(f"\n상세 백테스트 차트 저장 완료: {output_path / 'sma_detailed_backtest.png'}")
    
    # 최종 요약
    print("\n" + "="*80)
    print("거래비용 고려 백테스트 최종 요약")
    print("="*80)
    
    best_strategy = max(results.keys(), key=lambda x: results[x]['metrics']['total_return'])
    best_metrics = results[best_strategy]['metrics']
    
    print(f"\n최고 성과 전략: {best_strategy.replace('_', ' ').replace('SMA', 'SMA ')}")
    print(f"총 수익률: {best_metrics['total_return']:+.2f}%")
    print(f"연간 수익률: {best_metrics['annual_return']:+.2f}%")
    print(f"샤프 비율: {best_metrics['sharpe_ratio']:.3f}")
    print(f"최대 낙폭: {best_metrics['max_drawdown']:.2f}%")
    print(f"승률: {best_metrics['win_rate']:.1f}%")
    
    print(f"\n매수 후 보유 대비:")
    excess_return = best_metrics['total_return'] - buy_hold_return
    print(f"초과 수익률: {excess_return:+.2f}%")

if __name__ == "__main__":
    main()