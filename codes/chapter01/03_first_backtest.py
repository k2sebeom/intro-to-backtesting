#!/usr/bin/env python3
"""
챕터 1: 첫 번째 백테스트
backtrader를 사용한 간단한 매수 후 보유 전략 백테스트
"""

import backtrader as bt
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없이 이미지 저장
import matplotlib.pyplot as plt
import os
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

class BuyAndHoldStrategy(bt.Strategy):
    """
    매수 후 보유 전략 (Buy and Hold)
    - 첫 거래일에 매수
    - 마지막 거래일까지 보유
    """
    
    def __init__(self):
        """전략 초기화"""
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 로그 출력용
        self.log_data = []
        
    def log(self, txt, dt=None):
        """로그 출력 함수"""
        dt = dt or self.datas[0].datetime.date(0)
        log_entry = f'{dt.isoformat()}: {txt}'
        print(log_entry)
        self.log_data.append(log_entry)
        
    def notify_order(self, order):
        """주문 상태 변경 알림"""
        if order.status in [order.Submitted, order.Accepted]:
            # 주문이 제출되거나 접수된 상태
            return
            
        # 주문이 완료된 경우
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'매수 체결: 가격 {order.executed.price:.2f}, '
                        f'수수료 {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'매도 체결: 가격 {order.executed.price:.2f}, '
                        f'수수료 {order.executed.comm:.2f}')
                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('주문 취소/거부됨')
            
        # 주문 완료 후 초기화
        self.order = None
        
    def notify_trade(self, trade):
        """거래 완료 알림"""
        if not trade.isclosed:
            return
            
        self.log(f'거래 완료: 수익 {trade.pnl:.2f}, 순수익 {trade.pnlcomm:.2f}')
        
    def next(self):
        """매 거래일마다 실행되는 함수"""
        # 현재 포지션 확인
        if not self.position:
            # 포지션이 없으면 매수 (첫 거래일에만)
            if len(self.data) == 1:  # 첫 번째 데이터 포인트
                self.log(f'매수 주문: 가격 {self.dataclose[0]:.2f}')
                self.order = self.buy()
                
    def stop(self):
        """백테스트 종료 시 실행"""
        self.log(f'전략 종료: 최종 포트폴리오 가치 {self.broker.getvalue():.2f}')

class SimpleMovingAverageStrategy(bt.Strategy):
    """
    간단한 이동평균 전략
    - 20일 이동평균 위에서 매수
    - 20일 이동평균 아래에서 매도
    """
    
    params = (
        ('ma_period', 20),  # 이동평균 기간
        ('printlog', True), # 로그 출력 여부
    )
    
    def __init__(self):
        """전략 초기화"""
        self.dataclose = self.datas[0].close
        self.order = None
        
        # 20일 단순 이동평균 계산
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.ma_period)
        
        # 로그 출력용
        self.log_data = []
        
    def log(self, txt, dt=None):
        """로그 출력 함수"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            log_entry = f'{dt.isoformat()}: {txt}'
            print(log_entry)
            self.log_data.append(log_entry)
            
    def notify_order(self, order):
        """주문 상태 변경 알림"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'매수 체결: 가격 {order.executed.price:.2f}')
            else:
                self.log(f'매도 체결: 가격 {order.executed.price:.2f}')
                
        self.order = None
        
    def next(self):
        """매 거래일마다 실행되는 함수"""
        # 현재 가격과 이동평균 로그
        self.log(f'종가: {self.dataclose[0]:.2f}, SMA: {self.sma[0]:.2f}')
        
        # 대기 중인 주문이 있으면 리턴
        if self.order:
            return
            
        # 포지션이 없는 경우 (매수 신호 확인)
        if not self.position:
            # 종가가 이동평균 위에 있으면 매수
            if self.dataclose[0] > self.sma[0]:
                self.log('매수 신호 발생')
                self.order = self.buy()
                
        else:
            # 포지션이 있는 경우 (매도 신호 확인)
            # 종가가 이동평균 아래에 있으면 매도
            if self.dataclose[0] < self.sma[0]:
                self.log('매도 신호 발생')
                self.order = self.sell()

def load_data_for_backtrader():
    """backtrader용 데이터 로드"""
    try:
        # CSV 파일에서 데이터 로드
        df = pd.read_csv('../data/NVDA_1year.csv', index_col=0, parse_dates=True)
        
        # backtrader 데이터 피드 생성
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 인덱스를 datetime으로 사용
            open='Open',
            high='High', 
            low='Low',
            close='Close',
            volume='Volume',
            openinterest=None
        )
        
        print(f"데이터 로드 완료: {len(df)}개 거래일")
        print(f"기간: {df.index[0].date()} ~ {df.index[-1].date()}")
        
        return data, df
        
    except FileNotFoundError:
        print("데이터 파일을 찾을 수 없습니다. 먼저 01_basic_data_download.py를 실행해주세요.")
        return None, None

def run_buy_and_hold_backtest():
    """매수 후 보유 전략 백테스트"""
    print("=== 매수 후 보유 전략 백테스트 ===")
    
    # Cerebro 엔진 생성
    cerebro = bt.Cerebro()
    
    # 데이터 로드
    data, df = load_data_for_backtrader()
    if data is None:
        return None
        
    # 데이터 추가
    cerebro.adddata(data)
    
    # 전략 추가
    cerebro.addstrategy(BuyAndHoldStrategy)
    
    # 초기 자금 설정
    initial_cash = 10000.0
    cerebro.broker.setcash(initial_cash)
    
    # 수수료 설정 (0.1%)
    cerebro.broker.setcommission(commission=0.001)
    
    # 백테스트 실행 전 포트폴리오 가치
    print(f'초기 포트폴리오 가치: ${cerebro.broker.getvalue():.2f}')
    
    # 백테스트 실행
    results = cerebro.run()
    
    # 백테스트 실행 후 포트폴리오 가치
    final_value = cerebro.broker.getvalue()
    print(f'최종 포트폴리오 가치: ${final_value:.2f}')
    
    # 수익률 계산
    total_return = (final_value - initial_cash) / initial_cash * 100
    print(f'총 수익률: {total_return:.2f}%')
    
    # 벤치마크 수익률 (단순 매수 후 보유)
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    benchmark_return = (end_price - start_price) / start_price * 100
    print(f'벤치마크 수익률: {benchmark_return:.2f}%')
    
    return cerebro, results[0]

def run_sma_backtest():
    """이동평균 전략 백테스트"""
    print("\n=== 이동평균 전략 백테스트 ===")
    
    # Cerebro 엔진 생성
    cerebro = bt.Cerebro()
    
    # 데이터 로드
    data, df = load_data_for_backtrader()
    if data is None:
        return None
        
    # 데이터 추가
    cerebro.adddata(data)
    
    # 전략 추가
    cerebro.addstrategy(SimpleMovingAverageStrategy, printlog=False)
    
    # 초기 자금 설정
    initial_cash = 10000.0
    cerebro.broker.setcash(initial_cash)
    
    # 수수료 설정 (0.1%)
    cerebro.broker.setcommission(commission=0.001)
    
    # 백테스트 실행 전 포트폴리오 가치
    print(f'초기 포트폴리오 가치: ${cerebro.broker.getvalue():.2f}')
    
    # 백테스트 실행
    results = cerebro.run()
    
    # 백테스트 실행 후 포트폴리오 가치
    final_value = cerebro.broker.getvalue()
    print(f'최종 포트폴리오 가치: ${final_value:.2f}')
    
    # 수익률 계산
    total_return = (final_value - initial_cash) / initial_cash * 100
    print(f'총 수익률: {total_return:.2f}%')
    
    return cerebro, results[0]

def save_backtest_plots(cerebro, strategy_name):
    """백테스트 결과 플롯 저장"""
    print(f"=== {strategy_name} 차트 저장 ===")
    
    # 이미지 저장 디렉토리 생성
    os.makedirs('chapter01/images', exist_ok=True)
    
    try:
        # 플롯 생성 (GUI 없이)
        figs = cerebro.plot(iplot=False, volume=True, style='candlestick')
        
        # figs가 리스트인지 확인
        if not isinstance(figs, list):
            figs = [figs]
        
        # 이미지 저장
        for i, fig in enumerate(figs):
            if len(figs) > 1:
                filename = f'chapter01/images/{strategy_name.lower().replace(" ", "_")}_backtest_{i+1}.png'
            else:
                filename = f'chapter01/images/{strategy_name.lower().replace(" ", "_")}_backtest.png'
            
            fig.savefig(filename, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            print(f"차트 저장: {filename}")
            
    except Exception as e:
        print(f"차트 저장 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def compare_strategies():
    """전략 비교 분석"""
    print("\n=== 전략 비교 분석 ===")
    
    # 데이터 로드
    data, df = load_data_for_backtrader()
    if data is None:
        return
    
    strategies = {
        'Buy and Hold': BuyAndHoldStrategy,
        'SMA Strategy': SimpleMovingAverageStrategy
    }
    
    results = {}
    initial_cash = 10000.0
    
    for strategy_name, strategy_class in strategies.items():
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        
        # BuyAndHoldStrategy는 printlog 매개변수가 없음
        if strategy_class == BuyAndHoldStrategy:
            cerebro.addstrategy(strategy_class)
        else:
            cerebro.addstrategy(strategy_class, printlog=False)
            
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        
        # 백테스트 실행
        result = cerebro.run()
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_cash) / initial_cash * 100
        
        results[strategy_name] = {
            'final_value': final_value,
            'total_return': total_return,
            'cerebro': cerebro
        }
        
        print(f"{strategy_name}: 최종 가치 ${final_value:.2f}, 수익률 {total_return:.2f}%")
    
    # 벤치마크 계산
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    benchmark_return = (end_price - start_price) / start_price * 100
    print(f"벤치마크 (NVDA): 수익률 {benchmark_return:.2f}%")
    
    return results

def create_performance_comparison():
    """성과 비교 차트 생성"""
    print("\n=== 성과 비교 차트 생성 ===")
    
    # 데이터 로드
    _, df = load_data_for_backtrader()
    if df is None:
        return
    
    # 벤치마크 수익률 계산 (NVDA 매수 후 보유)
    df['Benchmark_Return'] = df['Close'] / df['Close'].iloc[0]
    
    # 간단한 이동평균 전략 시뮬레이션
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['Position'] = 0
    df['Signal'] = 0
    
    # 신호 생성
    df.loc[df['Close'] > df['SMA_20'], 'Signal'] = 1
    df.loc[df['Close'] < df['SMA_20'], 'Signal'] = -1
    
    # 포지션 계산 (신호 변화 시점에서만 거래)
    df['Position'] = df['Signal'].shift(1)
    df['Position'].fillna(0, inplace=True)
    
    # 전략 수익률 계산
    df['Daily_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Position'] * df['Daily_Return']
    df['Strategy_Cumulative'] = (1 + df['Strategy_Return']).cumprod()
    
    # 차트 생성
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 가격 차트와 이동평균
    ax1.plot(df.index, df['Close'], label='NVDA 종가', color='black', linewidth=2)
    ax1.plot(df.index, df['SMA_20'], label='20일 이동평균', color='blue', linewidth=2)
    ax1.set_title('NVIDIA 주가와 20일 이동평균', fontsize=14, fontweight='bold')
    ax1.set_ylabel('가격 ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 누적 수익률 비교
    ax2.plot(df.index, df['Benchmark_Return'], label='매수 후 보유', 
             color='green', linewidth=2)
    ax2.plot(df.index, df['Strategy_Cumulative'], label='이동평균 전략', 
             color='red', linewidth=2)
    ax2.set_title('전략별 누적 수익률 비교', fontsize=14, fontweight='bold')
    ax2.set_ylabel('누적 수익률 (배수)')
    ax2.set_xlabel('날짜')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chapter01/images/strategy_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("전략 비교 차트 저장: chapter01/images/strategy_comparison.png")

def main():
    """메인 함수"""
    print("챕터 1: 첫 번째 백테스트")
    print("=" * 50)
    
    try:
        # 1. 매수 후 보유 전략 백테스트
        cerebro1, strategy1 = run_buy_and_hold_backtest()
        if cerebro1:
            save_backtest_plots(cerebro1, "Buy and Hold")
        
        # 2. 이동평균 전략 백테스트
        cerebro2, strategy2 = run_sma_backtest()
        if cerebro2:
            save_backtest_plots(cerebro2, "SMA Strategy")
        
        # 3. 전략 비교
        compare_strategies()
        
        # 4. 성과 비교 차트
        create_performance_comparison()
        
        print("\n=== 실행 완료 ===")
        print("생성된 파일:")
        print("- buy_and_hold_backtest.png: 매수 후 보유 전략 차트")
        print("- sma_strategy_backtest.png: 이동평균 전략 차트")
        print("- strategy_comparison.png: 전략 비교 차트")
        print("\n챕터 1 완료! 다음은 챕터 2로 진행하세요.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()