"""
Chapter 2: 금융 데이터 다운로드와 이해
실제 주식 데이터 다운로드 및 탐색

이 스크립트는 다음을 수행합니다:
1. Apple (AAPL) 주식 데이터 다운로드
2. OHLCV 기본 통계 분석
3. 캔들스틱 패턴 분석
4. 다중 종목 비교
5. 다중 타임프레임 분석
6. 시각화 생성
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf


def print_header():
    """프로그램 헤더 출력"""
    print("=" * 42)
    print("Chapter 2: 금융 데이터 다운로드와 이해")
    print("=" * 42)
    print()


def download_single_stock(ticker_symbol="AAPL", years=5):
    """
    단일 종목 데이터 다운로드

    Parameters:
    -----------
    ticker_symbol : str
        종목 심볼
    years : int
        다운로드할 데이터 기간 (년)

    Returns:
    --------
    pd.DataFrame, yf.Ticker
        OHLCV 데이터, 티커 객체
    """
    print(f"=== {ticker_symbol} 데이터 다운로드 ===")

    # 날짜 계산
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} ({years}년)")

    # 티커 객체 생성
    ticker = yf.Ticker(ticker_symbol)

    # 데이터 다운로드
    data = ticker.history(start=start_date, end=end_date)

    print(f"총 데이터 포인트: {len(data)}개")

    # 회사 정보 출력
    try:
        info = ticker.info
        print(f"\n회사 정보:")
        print(f"- 이름: {info.get('longName', 'N/A')}")
        print(f"- 섹터: {info.get('sector', 'N/A')}")
        print(f"- 시가총액: ${info.get('marketCap', 0):,}")
    except:
        print("회사 정보를 가져올 수 없습니다.")

    return data, ticker


def analyze_ohlcv(data):
    """OHLCV 기본 통계 분석"""
    print("\n" + "=" * 42)
    print("=== OHLCV 기본 통계 ===")
    print("=" * 42)

    # 종가 통계
    print(f"평균 종가: ${data['Close'].mean():.2f}")
    print(f"최고가: ${data['High'].max():.2f} ({data['High'].idxmax().strftime('%Y-%m-%d')})")
    print(f"최저가: ${data['Low'].min():.2f} ({data['Low'].idxmin().strftime('%Y-%m-%d')})")

    # 일일 변동폭
    data['Range'] = data['High'] - data['Low']
    data['Range_Pct'] = (data['Range'] / data['Close']) * 100

    print(f"\n일일 변동폭 (High-Low):")
    print(f"- 평균: ${data['Range'].mean():.2f} ({data['Range_Pct'].mean():.2f}%)")
    print(f"- 최대: ${data['Range'].max():.2f} ({data.loc[data['Range'].idxmax(), 'Range_Pct']:.2f}%)")

    return data


def analyze_candlestick_patterns(data):
    """캔들스틱 패턴 분석"""
    print("\n" + "=" * 42)
    print("=== 캔들스틱 패턴 분석 ===")
    print("=" * 42)

    # 몸통 크기
    data['Body'] = abs(data['Close'] - data['Open'])

    # 위/아래 꼬리
    data['Upper_Shadow'] = data['High'] - data[['Open', 'Close']].max(axis=1)
    data['Lower_Shadow'] = data[['Open', 'Close']].min(axis=1) - data['Low']

    # 상승/하락 캔들 카운트
    bullish = (data['Close'] > data['Open']).sum()
    bearish = (data['Close'] <= data['Open']).sum()

    print(f"상승 캔들: {bullish}개 ({bullish/len(data)*100:.1f}%)")
    print(f"하락 캔들: {bearish}개 ({bearish/len(data)*100:.1f}%)")

    print(f"\n평균 몸통 크기: ${data['Body'].mean():.2f}")
    print(f"평균 위 꼬리: ${data['Upper_Shadow'].mean():.2f}")
    print(f"평균 아래 꼬리: ${data['Lower_Shadow'].mean():.2f}")

    return data


def compare_multiple_tickers(tickers=["AAPL", "MSFT", "GOOGL", "NVDA"], period="1y"):
    """다중 종목 비교"""
    print("\n" + "=" * 42)
    print(f"=== 다중 종목 비교 (최근 {period}) ===")
    print("=" * 42)

    # 데이터 다운로드
    data = yf.download(tickers, period=period, progress=False)

    # 수익률 계산
    returns = {}
    for ticker in tickers:
        if len(tickers) == 1:
            close = data['Close']
        else:
            close = data['Close'][ticker]

        ret = (close.iloc[-1] / close.iloc[0] - 1) * 100
        returns[ticker] = ret

        # 특별히 높은 수익률에 이모지 추가
        emoji = " 🚀" if ret > 100 else ""
        print(f"{ticker}: {ret:+.1f}%{emoji}")

    return data, returns


def compare_timeframes(ticker_symbol="SPY"):
    """다중 타임프레임 비교"""
    print("\n" + "=" * 42)
    print(f"=== {ticker_symbol} 타임프레임 비교 ===")
    print("=" * 42)

    ticker = yf.Ticker(ticker_symbol)

    # 여러 타임프레임 다운로드
    daily = ticker.history(period="1y", interval="1d")
    weekly = ticker.history(period="2y", interval="1wk")
    monthly = ticker.history(period="5y", interval="1mo")

    timeframes = {
        "일봉 (1년)": daily,
        "주봉 (2년)": weekly,
        "월봉 (5년)": monthly
    }

    for name, df in timeframes.items():
        ret = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        volatility = df['Close'].pct_change().std() * 100
        print(f"{name}:")
        print(f"  데이터 포인트: {len(df)}개")
        print(f"  수익률: {ret:+.1f}%")
        print(f"  변동성 (일일): {volatility:.2f}%")

    return daily, weekly, monthly


def create_visualizations(data, multi_ticker_data, daily, weekly, monthly, ticker_symbol="AAPL"):
    """종합 시각화 생성"""
    print("\n차트 생성 중...")

    # 한글 폰트 설정
    plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False

    # 그림 생성 (2x2 레이아웃)
    fig = plt.figure(figsize=(16, 12))

    # 1. 종가와 거래량
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(data.index, data['Close'], linewidth=2, color='#2E86AB')
    ax1.set_title(f'{ticker_symbol} Price Trend (5 Years)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.grid(True, alpha=0.3)

    ax1_volume = ax1.twinx()
    ax1_volume.bar(data.index, data['Volume'], alpha=0.3, color='gray', label='Volume')
    ax1_volume.set_ylabel('Volume')

    # 2. 캔들스틱 차트 (최근 60일)
    ax2 = plt.subplot(2, 2, 2)
    recent_data = data.tail(60)

    for idx, (date, row) in enumerate(recent_data.iterrows()):
        color = 'green' if row['Close'] >= row['Open'] else 'red'

        # 몸통
        body_height = abs(row['Close'] - row['Open'])
        body_bottom = min(row['Open'], row['Close'])
        ax2.bar(idx, body_height, bottom=body_bottom, width=0.6,
                color=color, alpha=0.8, edgecolor='black')

        # 위아래 꼬리
        ax2.plot([idx, idx], [row['Low'], row['High']], color='black', linewidth=1)

    ax2.set_title('Candlestick Chart (Last 60 Days)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Price ($)')
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. 다중 종목 비교 (정규화)
    ax3 = plt.subplot(2, 2, 3)
    if isinstance(multi_ticker_data, pd.DataFrame) and 'Close' in multi_ticker_data.columns:
        close_data = multi_ticker_data['Close']
        if isinstance(close_data, pd.DataFrame):
            # 정규화 (첫날 = 100)
            normalized = (close_data / close_data.iloc[0]) * 100
            for ticker in normalized.columns:
                ax3.plot(normalized.index, normalized[ticker], linewidth=2, label=ticker)

        ax3.set_title('Multi-Ticker Comparison (Normalized)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Normalized Price (Start = 100)')
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)

    # 4. 타임프레임 비교
    ax4 = plt.subplot(2, 2, 4)

    # 각 타임프레임 정규화
    daily_norm = (daily['Close'] / daily['Close'].iloc[0]) * 100
    weekly_norm = (weekly['Close'] / weekly['Close'].iloc[0]) * 100
    monthly_norm = (monthly['Close'] / monthly['Close'].iloc[0]) * 100

    ax4.plot(daily_norm.index, daily_norm, linewidth=2, label='Daily (1Y)', alpha=0.7)
    ax4.plot(weekly_norm.index, weekly_norm, linewidth=2, label='Weekly (2Y)', alpha=0.7)
    ax4.plot(monthly_norm.index, monthly_norm, linewidth=2, label='Monthly (5Y)', alpha=0.7)

    ax4.set_title('Timeframe Comparison (SPY)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Normalized Price (Start = 100)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # 저장
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    images_dir.mkdir(exist_ok=True)

    output_path = images_dir / "data_exploration.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def save_data_to_cache(data, ticker_symbol, data_dir):
    """데이터를 CSV로 저장"""
    cache_file = data_dir / f"{ticker_symbol}_5y.csv"
    data.to_csv(cache_file)
    print(f"\n데이터 캐시 저장: {cache_file}")


def main():
    """메인 함수"""
    # 헤더
    print_header()

    # 데이터 디렉토리 설정
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # 1. 단일 종목 다운로드 (Apple, 5년)
    data, ticker = download_single_stock("AAPL", years=5)

    # 2. OHLCV 분석
    data = analyze_ohlcv(data)

    # 3. 캔들스틱 패턴 분석
    data = analyze_candlestick_patterns(data)

    # 4. 다중 종목 비교
    multi_ticker_data, returns = compare_multiple_tickers(
        tickers=["AAPL", "MSFT", "GOOGL", "NVDA"],
        period="1y"
    )

    # 5. 타임프레임 비교
    daily, weekly, monthly = compare_timeframes("SPY")

    # 6. 시각화
    output_path = create_visualizations(
        data, multi_ticker_data, daily, weekly, monthly, "AAPL"
    )
    print(f"차트 저장 완료: {output_path.relative_to(Path.cwd())}")

    # 7. 데이터 캐싱
    save_data_to_cache(data, "AAPL", data_dir)

    # 완료 메시지
    print("\n" + "=" * 42)
    print("데이터 탐색 완료!")
    print("=" * 42)
    print("\n주요 인사이트:")
    print("- OHLCV 데이터 구조 이해")
    print("- 캔들스틱 패턴 분석 방법")
    print("- 다중 종목 및 타임프레임 비교")
    print("- yfinance 활용 방법")
    print("\n다음 챕터에서는 데이터 전처리와")
    print("수익률 계산 방법을 배워봅시다!")


if __name__ == "__main__":
    main()
