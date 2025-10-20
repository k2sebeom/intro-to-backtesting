#!/usr/bin/env python3
"""
Chapter 2: 데이터 전처리 및 정제
Data preprocessing and cleaning script
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_and_preprocess_data(filename):
    """Load and preprocess NVIDIA data"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        return None
    
    print(f"📊 데이터 로딩: {filename}")
    
    # Load data
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    print(f"원본 데이터 크기: {df.shape}")
    print(f"날짜 범위: {df.index[0]} ~ {df.index[-1]}")
    
    # Check for missing values
    missing_values = df.isnull().sum()
    print(f"\n결측값 확인:")
    for col, missing in missing_values.items():
        if missing > 0:
            print(f"  {col}: {missing}개 ({missing/len(df)*100:.2f}%)")
        else:
            print(f"  {col}: 결측값 없음")
    
    # Remove rows with missing values
    original_length = len(df)
    df = df.dropna()
    removed_rows = original_length - len(df)
    
    if removed_rows > 0:
        print(f"\n🧹 {removed_rows}개 행 제거 (결측값 포함)")
    
    # Check for duplicate dates
    duplicates = df.index.duplicated().sum()
    if duplicates > 0:
        print(f"🔍 중복 날짜 발견: {duplicates}개")
        df = df[~df.index.duplicated(keep='first')]
        print(f"   중복 제거 후 크기: {df.shape}")
    else:
        print("🔍 중복 날짜 없음")
    
    # Sort by date
    df = df.sort_index()
    
    # Add technical indicators for data validation
    df['Daily_Return'] = df['Close'].pct_change()
    df['Price_Range'] = df['High'] - df['Low']
    df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
    
    # Data quality checks
    print(f"\n📈 데이터 품질 검사:")
    
    # Check for unrealistic price movements (>50% in one day)
    extreme_moves = abs(df['Daily_Return']) > 0.5
    extreme_count = extreme_moves.sum()
    print(f"  극단적 가격 변동 (>50%): {extreme_count}개")
    
    if extreme_count > 0:
        extreme_dates = df[extreme_moves].index
        for date in extreme_dates:
            return_val = df.loc[date, 'Daily_Return']
            print(f"    {date.strftime('%Y-%m-%d')}: {return_val:.2%}")
    
    # Check for zero volume days
    zero_volume = (df['Volume'] == 0).sum()
    print(f"  거래량 0인 날: {zero_volume}개")
    
    # Check price consistency (High >= Close >= Low, High >= Open >= Low)
    price_inconsistency = (
        (df['High'] < df['Close']) | 
        (df['High'] < df['Open']) | 
        (df['Low'] > df['Close']) | 
        (df['Low'] > df['Open'])
    ).sum()
    print(f"  가격 일관성 오류: {price_inconsistency}개")
    
    # Basic statistics
    print(f"\n📊 기본 통계:")
    print(f"  평균 종가: ${df['Close'].mean():.2f}")
    print(f"  최고가: ${df['High'].max():.2f}")
    print(f"  최저가: ${df['Low'].min():.2f}")
    print(f"  평균 거래량: {df['Volume'].mean():,.0f}")
    print(f"  일일 수익률 표준편차: {df['Daily_Return'].std():.4f}")
    
    # Save preprocessed data
    processed_filename = filename.replace('.csv', '_processed.csv')
    processed_filepath = os.path.join(data_dir, processed_filename)
    df.to_csv(processed_filepath)
    
    print(f"\n✅ 전처리된 데이터 저장: {processed_filename}")
    print(f"최종 데이터 크기: {df.shape}")
    
    return df

def preprocess_all_timeframes():
    """Preprocess all downloaded NVIDIA data files"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    
    # Find all NVIDIA CSV files
    nvda_files = [f for f in os.listdir(data_dir) 
                  if f.startswith("NVDA_") and f.endswith(".csv") and "_processed" not in f]
    
    if not nvda_files:
        print("❌ NVDA 데이터 파일을 찾을 수 없습니다.")
        print("먼저 01_data_download_multiple_timeframes.py를 실행하세요.")
        return
    
    print("🔄 모든 타임프레임 데이터 전처리 시작")
    print("=" * 50)
    
    processed_data = {}
    
    for filename in sorted(nvda_files):
        print(f"\n처리 중: {filename}")
        print("-" * 30)
        
        df = load_and_preprocess_data(filename)
        if df is not None:
            timeframe = filename.replace("NVDA_", "").replace(".csv", "")
            processed_data[timeframe] = df
    
    print("\n" + "=" * 50)
    print("🎉 모든 데이터 전처리 완료!")
    
    # Summary comparison
    print(f"\n📋 타임프레임별 요약:")
    for timeframe, df in processed_data.items():
        print(f"  {timeframe}:")
        print(f"    기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"    데이터 포인트: {len(df):,}개")
        print(f"    평균 종가: ${df['Close'].mean():.2f}")
        print(f"    변동성: {df['Daily_Return'].std():.4f}")

if __name__ == "__main__":
    preprocess_all_timeframes()