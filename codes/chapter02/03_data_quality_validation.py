#!/usr/bin/env python3
"""
Chapter 2: 데이터 품질 검증 및 시각화
Data quality validation and visualization script
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime
import seaborn as sns

# Set Korean font for matplotlib
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

def validate_data_quality(df, timeframe_name):
    """Comprehensive data quality validation"""
    
    print(f"🔍 {timeframe_name} 데이터 품질 검증")
    print("-" * 40)
    
    validation_results = {}
    
    # 1. Completeness check
    total_days = (df.index[-1] - df.index[0]).days
    trading_days = len(df)
    completeness = trading_days / (total_days * 5/7)  # Approximate trading days
    
    print(f"📅 완전성 검사:")
    print(f"  전체 기간: {total_days}일")
    print(f"  거래일 수: {trading_days}일")
    print(f"  완전성 비율: {completeness:.2%}")
    
    validation_results['completeness'] = completeness
    
    # 2. Data consistency checks
    print(f"\n🔧 일관성 검사:")
    
    # Price consistency
    high_low_consistent = (df['High'] >= df['Low']).all()
    high_close_consistent = (df['High'] >= df['Close']).all()
    high_open_consistent = (df['High'] >= df['Open']).all()
    low_close_consistent = (df['Low'] <= df['Close']).all()
    low_open_consistent = (df['Low'] <= df['Open']).all()
    
    price_consistent = all([high_low_consistent, high_close_consistent, 
                           high_open_consistent, low_close_consistent, low_open_consistent])
    
    print(f"  가격 일관성: {'✅ 통과' if price_consistent else '❌ 실패'}")
    
    # Volume consistency
    positive_volume = (df['Volume'] >= 0).all()
    print(f"  거래량 일관성: {'✅ 통과' if positive_volume else '❌ 실패'}")
    
    validation_results['price_consistency'] = price_consistent
    validation_results['volume_consistency'] = positive_volume
    
    # 3. Outlier detection
    print(f"\n📊 이상치 검사:")
    
    # Price outliers (using IQR method)
    Q1 = df['Close'].quantile(0.25)
    Q3 = df['Close'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    price_outliers = ((df['Close'] < lower_bound) | (df['Close'] > upper_bound)).sum()
    print(f"  가격 이상치: {price_outliers}개 ({price_outliers/len(df)*100:.2f}%)")
    
    # Return outliers (>3 standard deviations)
    returns = df['Close'].pct_change().dropna()
    return_std = returns.std()
    return_outliers = (abs(returns) > 3 * return_std).sum()
    print(f"  수익률 이상치: {return_outliers}개 ({return_outliers/len(returns)*100:.2f}%)")
    
    validation_results['price_outliers'] = price_outliers
    validation_results['return_outliers'] = return_outliers
    
    # 4. Missing data patterns
    print(f"\n🕳️ 결측값 패턴:")
    missing_data = df.isnull().sum()
    total_missing = missing_data.sum()
    print(f"  총 결측값: {total_missing}개")
    
    if total_missing > 0:
        for col, missing in missing_data.items():
            if missing > 0:
                print(f"    {col}: {missing}개")
    else:
        print("  결측값 없음 ✅")
    
    validation_results['missing_data'] = total_missing
    
    # 5. Data distribution analysis
    print(f"\n📈 분포 분석:")
    print(f"  가격 범위: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
    print(f"  가격 변화율: {((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100:.2f}%")
    print(f"  평균 일일 변동성: {returns.std():.4f}")
    print(f"  최대 일일 상승: {returns.max():.4f} ({returns.max()*100:.2f}%)")
    print(f"  최대 일일 하락: {returns.min():.4f} ({returns.min()*100:.2f}%)")
    
    validation_results['price_range'] = (df['Close'].min(), df['Close'].max())
    validation_results['total_return'] = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1)
    validation_results['volatility'] = returns.std()
    
    return validation_results

def create_quality_visualizations(timeframes_data):
    """Create comprehensive data quality visualizations"""
    
    print("\n🎨 데이터 품질 시각화 생성 중...")
    
    # Create images directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 1. Price comparison across timeframes
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('NVIDIA 주식 데이터 품질 분석', fontsize=16, fontweight='bold')
    
    # Plot 1: Price trends
    ax1 = axes[0, 0]
    colors = ['blue', 'green', 'red']
    
    for i, (timeframe, df) in enumerate(timeframes_data.items()):
        # Normalize to show relative performance
        normalized_price = df['Close'] / df['Close'].iloc[0] * 100
        ax1.plot(df.index, normalized_price, label=f'{timeframe}', 
                color=colors[i % len(colors)], alpha=0.8)
    
    ax1.set_title('정규화된 가격 추이 비교')
    ax1.set_ylabel('정규화된 가격 (시작점=100)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Volume comparison
    ax2 = axes[0, 1]
    
    for i, (timeframe, df) in enumerate(timeframes_data.items()):
        # Show recent volume (last 252 trading days for comparison)
        recent_data = df.tail(min(252, len(df)))
        ax2.plot(recent_data.index, recent_data['Volume'], 
                label=f'{timeframe}', color=colors[i % len(colors)], alpha=0.7)
    
    ax2.set_title('최근 거래량 비교')
    ax2.set_ylabel('거래량')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Return distribution
    ax3 = axes[1, 0]
    
    for i, (timeframe, df) in enumerate(timeframes_data.items()):
        returns = df['Close'].pct_change().dropna()
        ax3.hist(returns, bins=50, alpha=0.6, label=f'{timeframe}', 
                color=colors[i % len(colors)], density=True)
    
    ax3.set_title('일일 수익률 분포')
    ax3.set_xlabel('일일 수익률')
    ax3.set_ylabel('밀도')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Data quality summary
    ax4 = axes[1, 1]
    
    quality_metrics = []
    timeframe_names = []
    
    for timeframe, df in timeframes_data.items():
        returns = df['Close'].pct_change().dropna()
        
        # Calculate quality score (0-100)
        completeness_score = min(len(df) / 252, 1.0) * 25  # Max 25 points
        consistency_score = 25  # Assume good consistency
        outlier_score = max(0, 25 - (abs(returns) > 3 * returns.std()).sum())  # Max 25 points
        missing_score = 25 if df.isnull().sum().sum() == 0 else 0  # Max 25 points
        
        total_score = completeness_score + consistency_score + outlier_score + missing_score
        quality_metrics.append(total_score)
        timeframe_names.append(timeframe)
    
    bars = ax4.bar(timeframe_names, quality_metrics, color=colors[:len(timeframe_names)])
    ax4.set_title('데이터 품질 점수')
    ax4.set_ylabel('품질 점수 (0-100)')
    ax4.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, score in zip(bars, quality_metrics):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{score:.1f}', ha='center', va='bottom')
    
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{images_dir}/data_quality_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Individual timeframe analysis
    for timeframe, df in timeframes_data.items():
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'NVIDIA {timeframe} 데이터 상세 분석', fontsize=14, fontweight='bold')
        
        # Candlestick-style price chart
        ax1 = axes[0, 0]
        
        # Sample data for better visualization (every 10th point for long timeframes)
        sample_freq = max(1, len(df) // 500)
        sampled_df = df.iloc[::sample_freq]
        
        for i in range(len(sampled_df)):
            date = sampled_df.index[i]
            open_price = sampled_df['Open'].iloc[i]
            close_price = sampled_df['Close'].iloc[i]
            high_price = sampled_df['High'].iloc[i]
            low_price = sampled_df['Low'].iloc[i]
            
            color = 'green' if close_price >= open_price else 'red'
            
            # High-low line
            ax1.plot([date, date], [low_price, high_price], color='black', linewidth=0.5)
            # Open-close rectangle
            ax1.plot([date, date], [open_price, close_price], color=color, linewidth=2)
        
        ax1.set_title(f'{timeframe} 가격 차트')
        ax1.set_ylabel('가격 ($)')
        ax1.grid(True, alpha=0.3)
        
        # Volume chart
        ax2 = axes[0, 1]
        ax2.bar(sampled_df.index, sampled_df['Volume'], alpha=0.7, color='blue')
        ax2.set_title(f'{timeframe} 거래량')
        ax2.set_ylabel('거래량')
        ax2.grid(True, alpha=0.3)
        
        # Returns distribution
        ax3 = axes[1, 0]
        returns = df['Close'].pct_change().dropna()
        ax3.hist(returns, bins=50, alpha=0.7, color='purple', edgecolor='black')
        ax3.axvline(returns.mean(), color='red', linestyle='--', label=f'평균: {returns.mean():.4f}')
        ax3.axvline(returns.mean() + returns.std(), color='orange', linestyle='--', alpha=0.7)
        ax3.axvline(returns.mean() - returns.std(), color='orange', linestyle='--', alpha=0.7)
        ax3.set_title('일일 수익률 분포')
        ax3.set_xlabel('일일 수익률')
        ax3.set_ylabel('빈도')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Rolling volatility
        ax4 = axes[1, 1]
        rolling_vol = returns.rolling(window=20).std()
        ax4.plot(rolling_vol.index, rolling_vol, color='red', alpha=0.8)
        ax4.set_title('20일 롤링 변동성')
        ax4.set_ylabel('변동성')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{images_dir}/nvidia_{timeframe}_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"✅ 시각화 완료! 이미지 저장 위치: {images_dir}/")

def main():
    """Main data quality validation function"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    # Find processed data files
    processed_files = [f for f in os.listdir(data_dir) 
                      if f.startswith("NVDA_") and f.endswith("_processed.csv")]
    
    if not processed_files:
        print("❌ 전처리된 데이터 파일을 찾을 수 없습니다.")
        print("먼저 02_data_preprocessing.py를 실행하세요.")
        return
    
    print("🔍 NVIDIA 데이터 품질 검증 시작")
    print("=" * 50)
    
    timeframes_data = {}
    validation_summary = {}
    
    # Load and validate each timeframe
    for filename in sorted(processed_files):
        timeframe = filename.replace("NVDA_", "").replace("_processed.csv", "")
        
        filepath = os.path.join(data_dir, filename)
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        
        timeframes_data[timeframe] = df
        validation_results = validate_data_quality(df, timeframe)
        validation_summary[timeframe] = validation_results
        
        print()
    
    # Create visualizations
    create_quality_visualizations(timeframes_data)
    
    # Final summary
    print("=" * 50)
    print("📋 최종 검증 요약")
    print("=" * 50)
    
    for timeframe, results in validation_summary.items():
        print(f"\n{timeframe.upper()}:")
        print(f"  완전성: {results['completeness']:.2%}")
        print(f"  가격 일관성: {'✅' if results['price_consistency'] else '❌'}")
        print(f"  거래량 일관성: {'✅' if results['volume_consistency'] else '❌'}")
        print(f"  가격 이상치: {results['price_outliers']}개")
        print(f"  수익률 이상치: {results['return_outliers']}개")
        print(f"  결측값: {results['missing_data']}개")
        print(f"  총 수익률: {results['total_return']:.2%}")
        print(f"  변동성: {results['volatility']:.4f}")
    
    print(f"\n🎉 데이터 품질 검증 완료!")
    print(f"📊 생성된 시각화 파일:")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, "images")
    for file in os.listdir(images_dir):
        if file.endswith('.png'):
            print(f"  📈 {file}")

if __name__ == "__main__":
    main()