#!/usr/bin/env python3
"""
Chapter 2: 데이터 준비 - NVIDIA 주식 데이터 다운로드
Multiple timeframes data download script
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def download_nvidia_data():
    """Download NVIDIA stock data for multiple timeframes"""
    
    # Create data directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Define timeframes
    timeframes = {
        "1year": 365,
        "5years": 365 * 5,
        "10years": 365 * 10
    }
    
    # NVIDIA ticker
    ticker = "NVDA"
    
    print(f"NVIDIA 주식 데이터 다운로드 시작...")
    print(f"티커: {ticker}")
    print("-" * 50)
    
    for period_name, days in timeframes.items():
        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            print(f"\n{period_name} 데이터 다운로드 중...")
            print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
            
            # Download data
            nvda = yf.Ticker(ticker)
            data = nvda.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"❌ {period_name} 데이터를 가져올 수 없습니다.")
                continue
            
            # Save to CSV
            filename = f"{data_dir}/NVDA_{period_name}.csv"
            data.to_csv(filename)
            
            print(f"✅ {period_name} 데이터 저장 완료: {filename}")
            print(f"   데이터 포인트 수: {len(data)}")
            print(f"   날짜 범위: {data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"   컬럼: {list(data.columns)}")
            
            # Display basic statistics
            print(f"   가격 범위: ${data['Close'].min():.2f} ~ ${data['Close'].max():.2f}")
            print(f"   평균 거래량: {data['Volume'].mean():,.0f}")
            
        except Exception as e:
            print(f"❌ {period_name} 데이터 다운로드 실패: {str(e)}")
    
    print("\n" + "=" * 50)
    print("데이터 다운로드 완료!")
    
    # List all downloaded files
    print("\n다운로드된 파일 목록:")
    for file in os.listdir(data_dir):
        if file.startswith("NVDA_") and file.endswith(".csv"):
            filepath = os.path.join(data_dir, file)
            size = os.path.getsize(filepath)
            print(f"  📁 {file} ({size:,} bytes)")

if __name__ == "__main__":
    download_nvidia_data()