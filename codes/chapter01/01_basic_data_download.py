#!/usr/bin/env python3
"""
챕터 1: 기본 데이터 다운로드 예제
NVIDIA 주식 데이터를 yfinance로 다운로드하고 기본 정보를 확인합니다.
"""

import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없이 이미지 저장
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def download_nvidia_data():
    """NVIDIA 주식 데이터 다운로드"""
    print("=== NVIDIA 주식 데이터 다운로드 ===")
    
    # NVIDIA 티커 생성
    nvda = yf.Ticker("NVDA")
    
    # 기본 회사 정보 출력
    info = nvda.info
    print(f"회사명: {info.get('longName', 'N/A')}")
    print(f"섹터: {info.get('sector', 'N/A')}")
    print(f"산업: {info.get('industry', 'N/A')}")
    print(f"시가총액: ${info.get('marketCap', 0):,}")
    print(f"통화: {info.get('currency', 'N/A')}")
    print()
    
    # 최근 1년 데이터 다운로드
    print("최근 1년 데이터 다운로드 중...")
    data = nvda.history(period="1y")
    
    print(f"데이터 기간: {data.index[0].date()} ~ {data.index[-1].date()}")
    print(f"총 데이터 포인트: {len(data)}개")
    print()
    
    # 데이터 구조 확인
    print("=== 데이터 구조 ===")
    print(f"컬럼: {list(data.columns)}")
    print(f"인덱스 타입: {type(data.index)}")
    print(f"데이터 타입:")
    print(data.dtypes)
    print()
    
    # 기본 통계 정보
    print("=== 기본 통계 정보 ===")
    print(data.describe())
    print()
    
    # 최근 5일 데이터 출력
    print("=== 최근 5일 데이터 ===")
    print(data.tail())
    print()
    
    return data

def analyze_ohlcv_structure(data):
    """OHLCV 데이터 구조 분석"""
    print("=== OHLCV 데이터 분석 ===")
    
    # 일일 수익률 계산
    data['Daily_Return'] = data['Close'].pct_change()
    
    # 일일 변동성 (True Range) 계산
    data['Prev_Close'] = data['Close'].shift(1)
    data['True_Range'] = data[['High', 'Low', 'Prev_Close']].apply(
        lambda x: max(
            x['High'] - x['Low'],
            abs(x['High'] - x['Prev_Close']) if pd.notna(x['Prev_Close']) else 0,
            abs(x['Low'] - x['Prev_Close']) if pd.notna(x['Prev_Close']) else 0
        ), axis=1
    )
    
    # 캔들스틱 분석
    data['Body_Size'] = abs(data['Close'] - data['Open'])
    data['Upper_Shadow'] = data['High'] - data[['Open', 'Close']].max(axis=1)
    data['Lower_Shadow'] = data[['Open', 'Close']].min(axis=1) - data['Low']
    data['Is_Bullish'] = data['Close'] > data['Open']
    
    print(f"평균 일일 수익률: {data['Daily_Return'].mean():.4f} ({data['Daily_Return'].mean()*100:.2f}%)")
    print(f"일일 수익률 표준편차: {data['Daily_Return'].std():.4f} ({data['Daily_Return'].std()*100:.2f}%)")
    print(f"최대 일일 수익률: {data['Daily_Return'].max():.4f} ({data['Daily_Return'].max()*100:.2f}%)")
    print(f"최소 일일 수익률: {data['Daily_Return'].min():.4f} ({data['Daily_Return'].min()*100:.2f}%)")
    print()
    
    print(f"평균 True Range: ${data['True_Range'].mean():.2f}")
    print(f"평균 몸통 크기: ${data['Body_Size'].mean():.2f}")
    print(f"상승 캔들 비율: {data['Is_Bullish'].mean():.2%}")
    print()
    
    return data

def create_basic_plots(data):
    """기본 차트 생성"""
    print("=== 차트 생성 중 ===")
    
    # 이미지 저장 디렉토리 생성
    os.makedirs('chapter01/images', exist_ok=True)
    
    # 1. 가격 차트
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 종가 차트
    ax1.plot(data.index, data['Close'], linewidth=2, color='blue', label='종가')
    ax1.set_title('NVIDIA 주가 추이 (최근 1년)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('가격 ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 거래량 차트
    ax2.bar(data.index, data['Volume'], alpha=0.7, color='orange', label='거래량')
    ax2.set_title('NVIDIA 거래량', fontsize=14, fontweight='bold')
    ax2.set_ylabel('거래량', fontsize=12)
    ax2.set_xlabel('날짜', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('chapter01/images/nvda_price_volume.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. 캔들스틱 차트 (최근 30일)
    recent_data = data.tail(30)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 상승/하락 캔들 구분
    up_days = recent_data['Close'] >= recent_data['Open']
    down_days = recent_data['Close'] < recent_data['Open']
    
    # 캔들스틱 그리기
    for i, (idx, row) in enumerate(recent_data.iterrows()):
        color = 'green' if row['Close'] >= row['Open'] else 'red'
        
        # 몸통
        body_height = abs(row['Close'] - row['Open'])
        body_bottom = min(row['Open'], row['Close'])
        ax.bar(i, body_height, bottom=body_bottom, width=0.6, 
               color=color, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # 위아래 꼬리
        ax.plot([i, i], [row['Low'], row['High']], color='black', linewidth=1)
    
    ax.set_title('NVIDIA 캔들스틱 차트 (최근 30일)', fontsize=14, fontweight='bold')
    ax.set_ylabel('가격 ($)', fontsize=12)
    ax.set_xlabel('거래일', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # x축 레이블 설정
    ax.set_xticks(range(0, len(recent_data), 5))
    ax.set_xticklabels([recent_data.index[i].strftime('%m/%d') 
                       for i in range(0, len(recent_data), 5)], rotation=45)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/nvda_candlestick.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. 수익률 분포
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 일일 수익률 히스토그램
    ax1.hist(data['Daily_Return'].dropna(), bins=50, alpha=0.7, color='blue', edgecolor='black')
    ax1.set_title('일일 수익률 분포', fontsize=14, fontweight='bold')
    ax1.set_xlabel('일일 수익률', fontsize=12)
    ax1.set_ylabel('빈도', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.axvline(data['Daily_Return'].mean(), color='red', linestyle='--', 
                label=f'평균: {data["Daily_Return"].mean():.4f}')
    ax1.legend()
    
    # 누적 수익률
    cumulative_returns = (1 + data['Daily_Return']).cumprod() - 1
    ax2.plot(data.index, cumulative_returns * 100, linewidth=2, color='green')
    ax2.set_title('누적 수익률', fontsize=14, fontweight='bold')
    ax2.set_xlabel('날짜', fontsize=12)
    ax2.set_ylabel('누적 수익률 (%)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/nvda_returns.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("차트가 chapter01/images/ 디렉토리에 저장되었습니다.")
    print("- nvda_price_volume.png: 가격 및 거래량 차트")
    print("- nvda_candlestick.png: 캔들스틱 차트")
    print("- nvda_returns.png: 수익률 분석 차트")

def save_data_to_csv(data):
    """데이터를 CSV 파일로 저장"""
    # 데이터 디렉토리 생성
    file_dir = os.path.dirname(__file__)
    dest_dir = os.path.join(file_dir, '../data')
    os.makedirs(dest_dir, exist_ok=True)
    
    # 기본 OHLCV 데이터만 저장
    ohlcv_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    # CSV 파일로 저장
    filename = os.path.join(dest_dir, 'NVDA_1year.csv')
    ohlcv_data.to_csv(filename)
    
    print(f"데이터가 {filename}에 저장되었습니다.")
    print(f"저장된 데이터 크기: {ohlcv_data.shape}")

def main():
    """메인 함수"""
    print("챕터 1: NVIDIA 주식 데이터 분석")
    print("=" * 50)
    
    try:
        # 1. 데이터 다운로드
        data = download_nvidia_data()
        
        # 2. 데이터 구조 분석
        analyzed_data = analyze_ohlcv_structure(data)
        
        # 3. 차트 생성
        create_basic_plots(analyzed_data)
        
        # 4. 데이터 저장
        save_data_to_csv(data)
        
        print("\n=== 실행 완료 ===")
        print("다음 단계: uv run chapter01/02_matplotlib_basics.py")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("인터넷 연결을 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main()