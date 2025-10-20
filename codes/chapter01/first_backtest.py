import backtrader as bt
import yfinance as yf

class BuyAndHoldStrategy(bt.Strategy):
    """매수 후 보유 전략"""
    
    def log(self, txt, dt=None):
        """로그 출력"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'매수 체결: 가격 {order.executed.price:.0f}, '
                        f'수량 {order.executed.size}, '
                        f'수수료 {order.executed.comm:.0f}')
            elif order.issell():
                self.log(f'매도 체결: 가격 {order.executed.price:.0f}, '
                        f'수량 {order.executed.size}, '
                        f'수수료 {order.executed.comm:.0f}')
                        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('주문 취소/거부/마진콜')
            
        self.order = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
            
        self.log(f'거래 완료: 손익 {trade.pnl:.0f}, 순손익 {trade.pnlcomm:.0f}')
    
    def next(self):
        # 현재 포지션이 없고 주문이 없으면 매수
        if not self.position and not self.order:
            # 사용 가능한 현금의 95%로 매수
            size = int((self.broker.get_cash() * 0.95) / self.dataclose[0])
            self.log(f'매수 주문: 가격 {self.dataclose[0]:.0f}, 수량 {size}')
            self.order = self.buy(size=size)

def run_backtest():
    """백테스트 실행"""
    # Cerebro 엔진 생성
    cerebro = bt.Cerebro()
    
    # 전략 추가
    cerebro.addstrategy(BuyAndHoldStrategy)
    
    # 데이터 다운로드 및 추가
    data = yf.download('005930.KS', start='2023-01-01', end='2024-01-01')
    
    # MultiIndex 컬럼을 단순화 (backtrader 호환성)
    data.columns = data.columns.droplevel(1)
    
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    
    # 초기 설정
    cerebro.broker.setcash(10000000)  # 1천만원
    cerebro.broker.setcommission(commission=0.0015)  # 0.15% 수수료
    
    # 분석기 추가
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    
    print('백테스트 시작')
    print(f'시작 포트폴리오 가치: {cerebro.broker.getvalue():,.0f}원')
    
    # 백테스트 실행
    results = cerebro.run()
    
    print(f'최종 포트폴리오 가치: {cerebro.broker.getvalue():,.0f}원')
    
    # 결과 분석
    strat = results[0]
    
    # 수익률 분석
    returns_analyzer = strat.analyzers.returns.get_analysis()
    if 'rtot' in returns_analyzer:
        print(f'총 수익률: {returns_analyzer["rtot"]:.2%}')
    
    # 최대 손실 분석
    drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
    if 'max' in drawdown_analyzer:
        print(f'최대 손실: {drawdown_analyzer["max"]["drawdown"]:.2%}')
    
    # 샤프 비율
    sharpe_analyzer = strat.analyzers.sharpe.get_analysis()
    if 'sharperatio' in sharpe_analyzer and sharpe_analyzer['sharperatio']:
        print(f'샤프 비율: {sharpe_analyzer["sharperatio"]:.2f}')
    
    # 간단한 수익률 계산
    start_value = 10000000
    end_value = cerebro.broker.getvalue()
    total_return = (end_value - start_value) / start_value
    print(f'총 수익률 (계산): {total_return:.2%}')
    
    # 차트 저장
    import matplotlib.pyplot as plt
    figs = cerebro.plot(style='candlestick', barup='red', bardown='blue', returnfig=True)
    if figs:
        figs[0][0].savefig('backtest_result.png', dpi=300, bbox_inches='tight')
        print("백테스트 결과 차트가 backtest_result.png로 저장되었습니다.")
        plt.close('all')

if __name__ == "__main__":
    run_backtest()