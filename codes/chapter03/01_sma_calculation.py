#!/usr/bin/env python3
"""
Chapter 3: Simple Moving Average (SMA) Calculation
단순 이동평균 계산 및 시각화

이 스크립트는 NVIDIA 주식 데이터를 사용하여 다양한 기간의 SMA를 계산하고 시각화합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import os

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

def main():
    print("=== Chapter 3: Simple Moving Average (SMA) 계산 ===")
    
    # 데이터 로드
    df = load_nvidia_data()
    print(f"데이터 로드 완료: {len(df)}개 데이터 포인트")
    print(f"기간: {df['Date'].min().strftime('%Y-%m-%d')} ~ {df['Date'].max().strftime('%Y-%m-%d')}")
    
    # 다양한 SMA 기간 설정
    sma_periods = [5, 10, 20, 50, 100]
    
    # SMA 계산
    for period in sma_periods:
        df[f'SMA_{period}'] = calculate_sma(df['Close'], period)
        print(f"SMA {period}일 계산 완료")
    
    # 기본 통계 출력
    print("\n=== 최근 10일 데이터 ===")
    columns_to_show = ['Date', 'Close'] + [f'SMA_{p}' for p in sma_periods]
    print(df[columns_to_show].tail(10).to_string(index=False))
    
    # 시각화
    plt.figure(figsize=(15, 10))
    
    # 가격과 SMA 플롯
    plt.plot(df['Date'], df['Close'], label='NVDA Close Price', linewidth=2, color='black')
    
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i, period in enumerate(sma_periods):
        plt.plot(df['Date'], df[f'SMA_{period}'], 
                label=f'SMA {period}', linewidth=1.5, color=colors[i])
    
    plt.title('NVIDIA Stock Price with Simple Moving Averages', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # x축 날짜 포맷 설정
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # 이미지 저장
    output_path = Path(__file__).parent / "images"
    output_path.mkdir(exist_ok=True)
    plt.savefig(output_path / "sma_calculation.png", dpi=300, bbox_inches='tight')
    print(f"\n차트 저장 완료: {output_path / 'sma_calculation.png'}")
    
    # SMA 교차점 분석
    print("\n=== SMA 교차점 분석 ===")
    
    # SMA 20과 SMA 50의 교차점 찾기
    df['SMA_20_above_50'] = df['SMA_20'] > df['SMA_50']
    df['SMA_20_above_50_prev'] = df['SMA_20_above_50'].shift(1)
    
    # 골든 크로스 (상승 신호)
    golden_cross = df[(df['SMA_20_above_50'] == True) & (df['SMA_20_above_50_prev'] == False)]
    
    # 데드 크로스 (하락 신호)
    death_cross = df[(df['SMA_20_above_50'] == False) & (df['SMA_20_above_50_prev'] == True)]
    
    print(f"골든 크로스 (SMA 20 > SMA 50) 발생 횟수: {len(golden_cross)}")
    if len(golden_cross) > 0:
        print("골든 크로스 발생일:")
        for _, row in golden_cross.iterrows():
            print(f"  - {row['Date'].strftime('%Y-%m-%d')}: ${row['Close']:.2f}")
    
    print(f"\n데드 크로스 (SMA 20 < SMA 50) 발생 횟수: {len(death_cross)}")
    if len(death_cross) > 0:
        print("데드 크로스 발생일:")
        for _, row in death_cross.iterrows():
            print(f"  - {row['Date'].strftime('%Y-%m-%d')}: ${row['Close']:.2f}")
    
    # 현재 SMA 상태
    latest = df.iloc[-1]
    print(f"\n=== 현재 SMA 상태 ({latest['Date'].strftime('%Y-%m-%d')}) ===")
    print(f"현재가: ${latest['Close']:.2f}")
    for period in sma_periods:
        sma_value = latest[f'SMA_{period}']
        if not pd.isna(sma_value):
            diff = ((latest['Close'] - sma_value) / sma_value) * 100
            print(f"SMA {period}: ${sma_value:.2f} (현재가 대비 {diff:+.2f}%)")

if __name__ == "__main__":
    main()