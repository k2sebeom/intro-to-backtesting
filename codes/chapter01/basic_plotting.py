import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def plot_stock_price(ticker, period="6mo"):
    """주식 가격 차트 그리기"""
    # 데이터 다운로드
    data = yf.download(ticker, period=period)
    
    # MultiIndex 컬럼 처리
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    # 차트 생성
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                   gridspec_kw={'height_ratios': [3, 1]})
    
    # 가격 차트
    ax1.plot(data.index, data['Close'], linewidth=1.5, color='blue')
    ax1.set_title(f'{ticker} 주가 차트', fontsize=16)
    ax1.set_ylabel('가격 (원)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 거래량 차트
    ax2.bar(data.index, data['Volume'], alpha=0.7, color='gray')
    ax2.set_ylabel('거래량', fontsize=12)
    ax2.set_xlabel('날짜', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # 날짜 포맷 설정
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    filename = f'{ticker.replace(".", "_")}_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"차트가 {filename}으로 저장되었습니다.")
    plt.close()  # 메모리 절약을 위해 figure 닫기

if __name__ == "__main__":
    plot_stock_price("005930.KS")  # 삼성전자