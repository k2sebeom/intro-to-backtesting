import yfinance as yf
import pandas as pd

def download_stock_data(ticker, period="1y"):
    """주식 데이터 다운로드"""
    try:
        data = yf.download(ticker, period=period)
        print(f"{ticker} 데이터 다운로드 완료")
        print(f"기간: {data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"데이터 포인트: {len(data)}개")
        return data
    except Exception as e:
        print(f"데이터 다운로드 실패: {e}")
        return None

if __name__ == "__main__":
    # 삼성전자 데이터 다운로드
    samsung = download_stock_data("005930.KS")
    
    if samsung is not None:
        print("\n최근 5일 데이터:")
        print(samsung.tail())
        
        # CSV로 저장
        samsung.to_csv("samsung_data.csv")
        print("\n데이터가 samsung_data.csv로 저장되었습니다.")