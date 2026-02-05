#!/usr/bin/env python3
"""
챕터 1: matplotlib 기초 플롯팅
다양한 차트 유형과 시각화 기법을 학습합니다.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없이 이미지 저장
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

# 한글 폰트 설정 (macOS)
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """저장된 NVIDIA 데이터 로드"""
    try:
        data = pd.read_csv('../data/NVDA_1year.csv', index_col=0, parse_dates=True)
        print(f"데이터 로드 완료: {data.shape}")
        return data
    except FileNotFoundError:
        print("데이터 파일을 찾을 수 없습니다. 먼저 01_basic_data_download.py를 실행해주세요.")
        return None

def create_line_plots(data):
    """라인 플롯 기초"""
    print("=== 라인 플롯 생성 ===")
    
    os.makedirs('chapter01/images', exist_ok=True)
    
    # 1. 기본 라인 플롯
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 종가 라인 플롯
    axes[0, 0].plot(data.index, data['Close'], color='blue', linewidth=2)
    axes[0, 0].set_title('종가 추이', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('가격 ($)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 여러 가격 동시 표시
    axes[0, 1].plot(data.index, data['High'], label='고가', color='green', alpha=0.7)
    axes[0, 1].plot(data.index, data['Low'], label='저가', color='red', alpha=0.7)
    axes[0, 1].plot(data.index, data['Close'], label='종가', color='blue', linewidth=2)
    axes[0, 1].set_title('고가/저가/종가 비교', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('가격 ($)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 이동평균 추가
    data['MA_20'] = data['Close'].rolling(window=20).mean()
    data['MA_50'] = data['Close'].rolling(window=50).mean()
    
    axes[1, 0].plot(data.index, data['Close'], label='종가', color='black', linewidth=1)
    axes[1, 0].plot(data.index, data['MA_20'], label='20일 이동평균', color='blue', linewidth=2)
    axes[1, 0].plot(data.index, data['MA_50'], label='50일 이동평균', color='red', linewidth=2)
    axes[1, 0].set_title('이동평균과 종가', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('가격 ($)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 거래량 (로그 스케일)
    axes[1, 1].plot(data.index, data['Volume'], color='orange', alpha=0.7)
    axes[1, 1].set_title('거래량 (로그 스케일)', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('거래량')
    axes[1, 1].set_yscale('log')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/line_plots_basics.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_bar_plots(data):
    """바 플롯과 히스토그램"""
    print("=== 바 플롯 생성 ===")
    
    # 일일 수익률 계산
    data['Daily_Return'] = data['Close'].pct_change()
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. 거래량 바 차트 (최근 30일)
    recent_data = data.tail(30)
    axes[0, 0].bar(range(len(recent_data)), recent_data['Volume'], 
                   color='lightblue', edgecolor='navy', alpha=0.7)
    axes[0, 0].set_title('최근 30일 거래량', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('거래량')
    axes[0, 0].set_xlabel('거래일')
    
    # 2. 일일 수익률 히스토그램
    axes[0, 1].hist(data['Daily_Return'].dropna(), bins=50, 
                    color='green', alpha=0.7, edgecolor='black')
    axes[0, 1].set_title('일일 수익률 분포', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('일일 수익률')
    axes[0, 1].set_ylabel('빈도')
    axes[0, 1].axvline(data['Daily_Return'].mean(), color='red', 
                       linestyle='--', linewidth=2, label='평균')
    axes[0, 1].legend()
    
    # 3. 월별 평균 거래량
    monthly_volume = data.groupby(data.index.to_series('M'))['Volume'].mean()
    axes[1, 0].bar(range(len(monthly_volume)), monthly_volume.values, 
                   color='purple', alpha=0.7)
    axes[1, 0].set_title('월별 평균 거래량', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('평균 거래량')
    axes[1, 0].set_xlabel('월')
    axes[1, 0].set_xticks(range(len(monthly_volume)))
    axes[1, 0].set_xticklabels([str(period) for period in monthly_volume.index], 
                               rotation=45)
    
    # 4. 가격 변동폭 히스토그램
    data['Price_Range'] = data['High'] - data['Low']
    axes[1, 1].hist(data['Price_Range'], bins=30, 
                    color='orange', alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('일일 가격 변동폭 분포', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('가격 변동폭 ($)')
    axes[1, 1].set_ylabel('빈도')
    
    plt.tight_layout()
    plt.savefig('chapter01/images/bar_plots_basics.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_advanced_candlestick(data):
    """고급 캔들스틱 차트"""
    print("=== 고급 캔들스틱 차트 생성 ===")
    
    # 최근 60일 데이터
    recent_data = data.tail(60).copy()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), 
                                   gridspec_kw={'height_ratios': [3, 1]})
    
    # 캔들스틱 차트
    for i, (idx, row) in enumerate(recent_data.iterrows()):
        # 색상 결정
        if row['Close'] >= row['Open']:
            color = 'green'
            alpha = 0.8
        else:
            color = 'red'
            alpha = 0.8
        
        # 몸통 그리기
        body_height = abs(row['Close'] - row['Open'])
        body_bottom = min(row['Open'], row['Close'])
        
        ax1.bar(i, body_height, bottom=body_bottom, width=0.8, 
                color=color, alpha=alpha, edgecolor='black', linewidth=0.5)
        
        # 위아래 꼬리 그리기
        ax1.plot([i, i], [row['Low'], row['High']], 
                 color='black', linewidth=1.5)
    
    # 이동평균선 추가
    ma_20 = recent_data['Close'].rolling(window=20).mean()
    ma_50 = recent_data['Close'].rolling(window=50).mean()
    
    ax1.plot(range(len(recent_data)), ma_20, 
             label='20일 이동평균', color='blue', linewidth=2, alpha=0.8)
    ax1.plot(range(len(recent_data)), ma_50, 
             label='50일 이동평균', color='orange', linewidth=2, alpha=0.8)
    
    ax1.set_title('NVIDIA 캔들스틱 차트 with 이동평균 (최근 60일)', 
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('가격 ($)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 거래량 차트
    colors = ['green' if close >= open_price else 'red' 
              for close, open_price in zip(recent_data['Close'], recent_data['Open'])]
    
    ax2.bar(range(len(recent_data)), recent_data['Volume'], 
            color=colors, alpha=0.7, width=0.8)
    ax2.set_title('거래량', fontsize=12, fontweight='bold')
    ax2.set_ylabel('거래량', fontsize=10)
    ax2.set_xlabel('거래일', fontsize=12)
    
    # x축 레이블 설정
    step = max(1, len(recent_data) // 10)
    ax1.set_xticks(range(0, len(recent_data), step))
    ax1.set_xticklabels([recent_data.index[i].strftime('%m/%d') 
                        for i in range(0, len(recent_data), step)], rotation=45)
    
    ax2.set_xticks(range(0, len(recent_data), step))
    ax2.set_xticklabels([recent_data.index[i].strftime('%m/%d') 
                        for i in range(0, len(recent_data), step)], rotation=45)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/advanced_candlestick.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_subplot_examples(data):
    """서브플롯 활용 예제"""
    print("=== 서브플롯 예제 생성 ===")
    
    # 일일 수익률 계산
    data['Daily_Return'] = data['Close'].pct_change()
    data['Volatility'] = data['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
    
    # 2x3 서브플롯
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. 종가
    axes[0, 0].plot(data.index, data['Close'], color='blue', linewidth=2)
    axes[0, 0].set_title('종가', fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 거래량
    axes[0, 1].plot(data.index, data['Volume'], color='orange', alpha=0.7)
    axes[0, 1].set_title('거래량', fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 일일 수익률
    axes[0, 2].plot(data.index, data['Daily_Return'] * 100, 
                    color='green', alpha=0.7, linewidth=1)
    axes[0, 2].axhline(y=0, color='black', linestyle='-', alpha=0.5)
    axes[0, 2].set_title('일일 수익률 (%)', fontweight='bold')
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. 변동성
    axes[1, 0].plot(data.index, data['Volatility'] * 100, 
                    color='red', linewidth=2)
    axes[1, 0].set_title('연환산 변동성 (%)', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. 가격 vs 거래량 산점도
    axes[1, 1].scatter(data['Volume'], data['Close'], 
                       alpha=0.5, s=10, color='purple')
    axes[1, 1].set_title('가격 vs 거래량', fontweight='bold')
    axes[1, 1].set_xlabel('거래량')
    axes[1, 1].set_ylabel('종가 ($)')
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. 누적 수익률
    cumulative_returns = (1 + data['Daily_Return']).cumprod() - 1
    axes[1, 2].plot(data.index, cumulative_returns * 100, 
                    color='darkgreen', linewidth=2)
    axes[1, 2].set_title('누적 수익률 (%)', fontweight='bold')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/subplot_examples.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_style_examples(data):
    """다양한 스타일 예제"""
    print("=== 스타일 예제 생성 ===")
    
    # 최근 3개월 데이터
    recent_data = data.tail(90)
    
    # 3가지 스타일로 같은 데이터 표현
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 스타일 1: 클래식
    axes[0].plot(recent_data.index, recent_data['Close'], 
                 color='blue', linewidth=2, marker='o', markersize=2)
    axes[0].set_title('클래식 스타일', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('가격 ($)')
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)
    
    # 스타일 2: 모던
    axes[1].fill_between(recent_data.index, recent_data['Close'], 
                         alpha=0.3, color='green')
    axes[1].plot(recent_data.index, recent_data['Close'], 
                 color='darkgreen', linewidth=3)
    axes[1].set_title('모던 스타일', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('가격 ($)')
    axes[1].grid(True, alpha=0.2, linestyle='--')
    axes[1].tick_params(axis='x', rotation=45)
    
    # 스타일 3: 미니멀
    axes[2].plot(recent_data.index, recent_data['Close'], 
                 color='black', linewidth=1.5)
    axes[2].set_title('미니멀 스타일', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('가격 ($)')
    axes[2].spines['top'].set_visible(False)
    axes[2].spines['right'].set_visible(False)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/style_examples.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """메인 함수"""
    print("챕터 1: matplotlib 기초 플롯팅")
    print("=" * 50)
    
    # 데이터 로드
    data = load_data()
    if data is None:
        return
    
    try:
        # 1. 라인 플롯 기초
        create_line_plots(data)
        
        # 2. 바 플롯과 히스토그램
        create_bar_plots(data)
        
        # 3. 고급 캔들스틱 차트
        create_advanced_candlestick(data)
        
        # 4. 서브플롯 예제
        create_subplot_examples(data)
        
        # 5. 스타일 예제
        create_style_examples(data)
        
        print("\n=== 실행 완료 ===")
        print("생성된 차트:")
        print("- line_plots_basics.png: 라인 플롯 기초")
        print("- bar_plots_basics.png: 바 플롯과 히스토그램")
        print("- advanced_candlestick.png: 고급 캔들스틱 차트")
        print("- subplot_examples.png: 서브플롯 활용")
        print("- style_examples.png: 다양한 스타일")
        print("\n다음 단계: uv run chapter01/03_first_backtest.py")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()