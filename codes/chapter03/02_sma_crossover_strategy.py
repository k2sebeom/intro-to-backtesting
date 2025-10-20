#!/usr/bin/env python3
"""
Chapter 3: SMA Crossover Strategy Implementation
SMA 교차 전략 구현

이 스크립트는 SMA 교차 신호를 기반으로 한 트레이딩 전략을 구현합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic']
plt.rcParams['axes.unicode_minus'] = False

def load_nvidia_data():
    """NVIDIA 주식 데이터 로드"""
    data_path = Path(__file__).parent.parent / "data" / "NVDA_1year.csv"
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    return df

def calculate_sma(prices, window):
    """단순 이동평균 계산"""
    return prices.rolling(window=window).mean()

def generate_signals(df, short_window, long_window):
    """SMA 교차 신호 생성"""
    df = df.copy()
    
    # SMA 계산
    df[f'SMA_{short_window}'] = calculate_sma(df['Close'], short_window)
    df[f'SMA_{long_window}'] = calculate_sma(df['Close'], long_window)
    
    # 신호 생성
    df['Signal'] = 0
    df['Signal'][short_window:] = np.where(
        df[f'SMA_{short_window}'][short_window:] > df[f'SMA_{long_window}'][short_window:], 1, 0
    )
    
    # 포지션 변화 감지
    df['Position'] = df['Signal'].diff()
    
    return df

def calculate_strategy_returns(df, initial_capital=10000):
    """전략 수익률 계산"""
    df = df.copy()
    
    # 일일 수익률 계산
    df['Daily_Return'] = df['Close'].pct_change()
    
    # 전략 수익률 (신호에 따른)
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Daily_Return']
    
    # 누적 수익률
    df['Cumulative_Market_Return'] = (1 + df['Daily_Return']).cumprod()
    df['Cumulative_Strategy_Return'] = (1 + df['Strategy_Return']).cumprod()
    
    # 포트폴리오 가치
    df['Market_Value'] = initial_capital * df['Cumulative_Market_Return']
    df['Strategy_Value'] = initial_capital * df['Cumulative_Strategy_Return']
    
    return df

def analyze_performance(df):
    """성과 분석"""
    # 전체 수익률
    total_market_return = (df['Cumulative_Market_Return'].iloc[-1] - 1) * 100
    total_strategy_return = (df['Cumulative_Strategy_Return'].iloc[-1] - 1) * 100
    
    # 연간 수익률 (252 거래일 기준)
    trading_days = len(df)
    annual_market_return = ((df['Cumulative_Market_Return'].iloc[-1]) ** (252/trading_days) - 1) * 100
    annual_strategy_return = ((df['Cumulative_Strategy_Return'].iloc[-1]) ** (252/trading_days) - 1) * 100
    
    # 변동성 (연간화)
    market_volatility = df['Daily_Return'].std() * np.sqrt(252) * 100
    strategy_volatility = df['Strategy_Return'].std() * np.sqrt(252) * 100
    
    # 샤프 비율 (무위험 수익률 0% 가정)
    market_sharpe = annual_market_return / market_volatility if market_volatility != 0 else 0
    strategy_sharpe = annual_strategy_return / strategy_volatility if strategy_volatility != 0 else 0
    
    # 최대 낙폭 (Maximum Drawdown)
    market_peak = df['Cumulative_Market_Return'].expanding().max()
    market_drawdown = (df['Cumulative_Market_Return'] - market_peak) / market_peak
    max_market_drawdown = market_drawdown.min() * 100
    
    strategy_peak = df['Cumulative_Strategy_Return'].expanding().max()
    strategy_drawdown = (df['Cumulative_Strategy_Return'] - strategy_peak) / strategy_peak
    max_strategy_drawdown = strategy_drawdown.min() * 100
    
    return {
        'total_market_return': total_market_return,
        'total_strategy_return': total_strategy_return,
        'annual_market_return': annual_market_return,
        'annual_strategy_return': annual_strategy_return,
        'market_volatility': market_volatility,
        'strategy_volatility': strategy_volatility,
        'market_sharpe': market_sharpe,
        'strategy_sharpe': strategy_sharpe,
        'max_market_drawdown': max_market_drawdown,
        'max_strategy_drawdown': max_strategy_drawdown
    }

def main():
    print("=== Chapter 3: SMA Crossover Strategy ===")
    
    # 데이터 로드
    df = load_nvidia_data()
    print(f"데이터 로드 완료: {len(df)}개 데이터 포인트")
    
    # 다양한 SMA 조합 테스트
    sma_combinations = [
        (5, 20),   # 단기: 5일, 장기: 20일
        (10, 30),  # 단기: 10일, 장기: 30일
        (20, 50),  # 단기: 20일, 장기: 50일
    ]
    
    results = {}
    
    for short, long in sma_combinations:
        print(f"\n=== SMA {short}/{long} 전략 분석 ===")
        
        # 신호 생성
        strategy_df = generate_signals(df, short, long)
        
        # 수익률 계산
        strategy_df = calculate_strategy_returns(strategy_df)
        
        # 성과 분석
        performance = analyze_performance(strategy_df)
        results[f"SMA_{short}_{long}"] = {
            'df': strategy_df,
            'performance': performance
        }
        
        # 거래 신호 분석
        buy_signals = strategy_df[strategy_df['Position'] == 1]
        sell_signals = strategy_df[strategy_df['Position'] == -1]
        
        print(f"매수 신호: {len(buy_signals)}회")
        print(f"매도 신호: {len(sell_signals)}회")
        print(f"총 수익률: {performance['total_strategy_return']:.2f}% (vs 시장: {performance['total_market_return']:.2f}%)")
        print(f"연간 수익률: {performance['annual_strategy_return']:.2f}% (vs 시장: {performance['annual_market_return']:.2f}%)")
        print(f"변동성: {performance['strategy_volatility']:.2f}% (vs 시장: {performance['market_volatility']:.2f}%)")
        print(f"샤프 비율: {performance['strategy_sharpe']:.3f} (vs 시장: {performance['market_sharpe']:.3f})")
        print(f"최대 낙폭: {performance['max_strategy_drawdown']:.2f}% (vs 시장: {performance['max_market_drawdown']:.2f}%)")
    
    # 시각화
    fig, axes = plt.subplots(2, 2, figsize=(20, 15))
    
    # 1. SMA 20/50 전략의 가격 차트와 신호
    best_strategy = results['SMA_20_50']['df']
    ax1 = axes[0, 0]
    ax1.plot(best_strategy['Date'], best_strategy['Close'], label='NVDA Price', color='black', linewidth=2)
    ax1.plot(best_strategy['Date'], best_strategy['SMA_20'], label='SMA 20', color='blue', linewidth=1.5)
    ax1.plot(best_strategy['Date'], best_strategy['SMA_50'], label='SMA 50', color='red', linewidth=1.5)
    
    # 매수/매도 신호 표시
    buy_signals = best_strategy[best_strategy['Position'] == 1]
    sell_signals = best_strategy[best_strategy['Position'] == -1]
    
    ax1.scatter(buy_signals['Date'], buy_signals['Close'], color='green', marker='^', 
               s=100, label=f'Buy Signal ({len(buy_signals)})', zorder=5)
    ax1.scatter(sell_signals['Date'], sell_signals['Close'], color='red', marker='v', 
               s=100, label=f'Sell Signal ({len(sell_signals)})', zorder=5)
    
    ax1.set_title('SMA 20/50 Crossover Strategy Signals', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 누적 수익률 비교
    ax2 = axes[0, 1]
    for name, result in results.items():
        strategy_df = result['df']
        label = name.replace('_', ' ').replace('SMA', 'SMA ')
        ax2.plot(strategy_df['Date'], (strategy_df['Cumulative_Strategy_Return'] - 1) * 100, 
                label=label, linewidth=2)
    
    ax2.plot(df['Date'], (results['SMA_20_50']['df']['Cumulative_Market_Return'] - 1) * 100, 
            label='Buy & Hold', color='black', linewidth=2, linestyle='--')
    
    ax2.set_title('Cumulative Returns Comparison', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Cumulative Return (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 성과 지표 비교 (막대 차트)
    ax3 = axes[1, 0]
    strategies = list(results.keys())
    annual_returns = [results[s]['performance']['annual_strategy_return'] for s in strategies]
    market_return = results['SMA_20_50']['performance']['annual_market_return']
    
    x_pos = np.arange(len(strategies))
    bars = ax3.bar(x_pos, annual_returns, alpha=0.7, color=['blue', 'green', 'orange'])
    ax3.axhline(y=market_return, color='red', linestyle='--', linewidth=2, label=f'Market: {market_return:.1f}%')
    
    ax3.set_title('Annual Returns Comparison', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Strategy')
    ax3.set_ylabel('Annual Return (%)')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([s.replace('_', ' ').replace('SMA', 'SMA ') for s in strategies])
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 막대 위에 값 표시
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 4. 리스크-수익률 산점도
    ax4 = axes[1, 1]
    for name, result in results.items():
        perf = result['performance']
        label = name.replace('_', ' ').replace('SMA', 'SMA ')
        ax4.scatter(perf['strategy_volatility'], perf['annual_strategy_return'], 
                   s=100, label=label, alpha=0.7)
    
    # 시장 성과 추가
    market_perf = results['SMA_20_50']['performance']
    ax4.scatter(market_perf['market_volatility'], market_perf['annual_market_return'], 
               s=100, color='red', marker='s', label='Market (Buy & Hold)')
    
    ax4.set_title('Risk-Return Profile', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Volatility (%)')
    ax4.set_ylabel('Annual Return (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 이미지 저장
    output_path = Path(__file__).parent / "images"
    output_path.mkdir(exist_ok=True)
    plt.savefig(output_path / "sma_crossover_strategy.png", dpi=300, bbox_inches='tight')
    print(f"\n전략 분석 차트 저장 완료: {output_path / 'sma_crossover_strategy.png'}")
    
    # 최종 성과 요약
    print("\n" + "="*60)
    print("최종 성과 요약")
    print("="*60)
    
    for name, result in results.items():
        perf = result['performance']
        strategy_name = name.replace('_', ' ').replace('SMA', 'SMA ')
        print(f"\n{strategy_name}:")
        print(f"  총 수익률: {perf['total_strategy_return']:+.2f}%")
        print(f"  연간 수익률: {perf['annual_strategy_return']:+.2f}%")
        print(f"  변동성: {perf['strategy_volatility']:.2f}%")
        print(f"  샤프 비율: {perf['strategy_sharpe']:.3f}")
        print(f"  최대 낙폭: {perf['max_strategy_drawdown']:.2f}%")

if __name__ == "__main__":
    main()