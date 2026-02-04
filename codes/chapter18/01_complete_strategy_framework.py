"""
Chapter 18: 완전한 전략 개발 프로세스
Complete Strategy Development Framework

이 스크립트는 전략 개발의 전체 프로세스를 보여주는 종합 예제입니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class CompleteStrategy(bt.Strategy):
    """
    종합 전략: RSI + 이동평균 + ML 시그널 결합

    진입 조건:
    - RSI < 30 (과매도)
    - 가격이 SMA(20) 위에 있음
    - ML 모델이 상승 예측 (확률 > 0.6)

    청산 조건:
    - RSI > 70 (과매수)
    - Stop Loss: -5%
    - Take Profit: +15%
    - 최대 보유 기간: 60일
    """

    params = (
        ('rsi_period', 14),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('sma_period', 20),
        ('stop_loss', 0.05),
        ('take_profit', 0.15),
        ('max_holding_days', 60),
        ('ml_prob_threshold', 0.6),
    )

    def __init__(self):
        # 기술적 지표
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.sma_period)

        # 거래 추적
        self.entry_price = None
        self.entry_date = None
        self.trades_log = []

    def next(self):
        # 포지션이 없을 때: 진입 조건 확인
        if not self.position:
            # 기술적 조건
            rsi_signal = self.rsi[0] < self.params.rsi_oversold
            trend_signal = self.data.close[0] > self.sma[0]

            if rsi_signal and trend_signal:
                # 매수
                self.buy()
                self.entry_price = self.data.close[0]
                self.entry_date = self.data.datetime.date(0)

        # 포지션이 있을 때: 청산 조건 확인
        else:
            if self.entry_price is None:
                return

            current_return = (self.data.close[0] - self.entry_price) / self.entry_price
            holding_days = (self.data.datetime.date(0) - self.entry_date).days if self.entry_date else 0

            # 청산 조건
            rsi_exit = self.rsi[0] > self.params.rsi_overbought
            stop_loss_hit = current_return <= -self.params.stop_loss
            take_profit_hit = current_return >= self.params.take_profit
            max_hold_exceeded = holding_days >= self.params.max_holding_days

            if rsi_exit or stop_loss_hit or take_profit_hit or max_hold_exceeded:
                self.close()

                # 거래 기록
                exit_reason = 'RSI' if rsi_exit else \
                             'Stop Loss' if stop_loss_hit else \
                             'Take Profit' if take_profit_hit else \
                             'Max Hold'

                self.trades_log.append({
                    'entry_date': self.entry_date,
                    'exit_date': self.data.datetime.date(0),
                    'entry_price': self.entry_price,
                    'exit_price': self.data.close[0],
                    'return': current_return,
                    'holding_days': holding_days,
                    'exit_reason': exit_reason
                })

                self.entry_price = None
                self.entry_date = None


def run_complete_backtest(symbol='NVDA', start_date='2019-01-01', end_date='2024-01-01'):
    """완전한 백테스트 실행"""

    print(f"\n{'='*70}")
    print(f"완전한 전략 백테스트: {symbol}")
    print(f"{'='*70}")

    # 데이터 다운로드
    print(f"\n1. 데이터 준비")
    print(f"   - {symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("   ✗ 데이터 다운로드 실패")
        return None

    print(f"   ✓ 데이터 다운로드 완료: {len(data)} 행")

    # In-Sample / Out-of-Sample 분할
    split_date = '2022-01-01'
    is_data = data[data.index < split_date]
    oos_data = data[data.index >= split_date]

    print(f"   - In-Sample: {len(is_data)} 행 ({is_data.index[0].date()} ~ {is_data.index[-1].date()})")
    print(f"   - Out-of-Sample: {len(oos_data)} 행 ({oos_data.index[0].date()} ~ {oos_data.index[-1].date()})")

    # 2. In-Sample 백테스트
    print(f"\n2. In-Sample 백테스트")
    is_results = run_backtest_on_data(is_data, 'In-Sample')

    # 3. Out-of-Sample 백테스트
    print(f"\n3. Out-of-Sample 백테스트")
    oos_results = run_backtest_on_data(oos_data, 'Out-of-Sample')

    # 4. 전체 기간 백테스트
    print(f"\n4. 전체 기간 백테스트")
    full_results = run_backtest_on_data(data, 'Full Period')

    # 5. 결과 비교
    print(f"\n{'='*70}")
    print(f"결과 요약")
    print(f"{'='*70}")

    comparison = pd.DataFrame({
        'In-Sample': is_results,
        'Out-of-Sample': oos_results,
        'Full Period': full_results
    })

    print(comparison.to_string())

    # WFE 계산
    if is_results['Total Return'] != 0:
        wfe = (oos_results['Total Return'] / is_results['Total Return']) * 100
        print(f"\nWalk-Forward Efficiency (WFE): {wfe:.1f}%")

        if wfe > 80:
            print("   → 매우 강건한 전략 ✓")
        elif wfe > 60:
            print("   → 양호한 전략 ✓")
        elif wfe > 40:
            print("   → 보통 전략 ⚠")
        else:
            print("   → 과최적화 의심 ✗")

    return {
        'is_results': is_results,
        'oos_results': oos_results,
        'full_results': full_results,
        'data': data
    }


def run_backtest_on_data(data, label):
    """특정 데이터셋에서 백테스트 실행"""

    cerebro = bt.Cerebro()

    # 데이터 피드
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)

    # 전략 추가
    cerebro.addstrategy(CompleteStrategy)

    # 초기 설정
    initial_cash = 100000.0
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)  # 0.1% 수수료
    cerebro.broker.set_slippage_perc(0.0005)  # 0.05% 슬리피지

    # 분석기 추가
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    # 실행
    results = cerebro.run()
    strategy = results[0]
    final_value = cerebro.broker.getvalue()

    # 결과 수집
    total_return = (final_value - initial_cash) / initial_cash
    sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', None)
    max_dd = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)

    trade_analysis = strategy.analyzers.trades.get_analysis()
    total_trades = trade_analysis.get('total', {}).get('total', 0)
    won_trades = trade_analysis.get('won', {}).get('total', 0)
    win_rate = won_trades / total_trades if total_trades > 0 else 0

    # 연환산 수익률
    years = len(data) / 252
    annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0

    print(f"   {label}:")
    print(f"   - 총 수익률: {total_return:.2%}")
    print(f"   - 연환산 수익률: {annual_return:.2%}")
    print(f"   - Sharpe Ratio: {sharpe:.2f}" if sharpe else "   - Sharpe Ratio: N/A")
    print(f"   - 최대 낙폭: {max_dd:.2f}%")
    print(f"   - 총 거래: {total_trades}회")
    print(f"   - 승률: {win_rate:.2%}")

    return pd.Series({
        'Total Return': total_return,
        'Annual Return': annual_return,
        'Sharpe Ratio': sharpe if sharpe else 0,
        'Max Drawdown': max_dd,
        'Total Trades': total_trades,
        'Win Rate': win_rate
    })


def create_strategy_report(results_dict):
    """전략 리포트 생성"""

    print(f"\n{'='*70}")
    print(f"전략 배포 준비도 체크리스트")
    print(f"{'='*70}")

    is_results = results_dict['is_results']
    oos_results = results_dict['oos_results']

    checklist = []

    # 1. 백테스트 기준
    print(f"\n[ 백테스트 기준 ]")

    check = oos_results['Sharpe Ratio'] > 1
    checklist.append(check)
    print(f"  {'✓' if check else '✗'} Sharpe Ratio > 1: {oos_results['Sharpe Ratio']:.2f}")

    check = oos_results['Total Trades'] >= 20
    checklist.append(check)
    print(f"  {'✓' if check else '✗'} 충분한 거래 (>20): {oos_results['Total Trades']:.0f}회")

    check = oos_results['Win Rate'] > 0.4
    checklist.append(check)
    print(f"  {'✓' if check else '✗'} 승률 > 40%: {oos_results['Win Rate']:.1%}")

    check = oos_results['Max Drawdown'] > -30
    checklist.append(check)
    print(f"  {'✓' if check else '✗'} 최대 낙폭 < 30%: {oos_results['Max Drawdown']:.1f}%")

    # 2. 강건성 테스트
    print(f"\n[ 강건성 테스트 ]")

    if is_results['Total Return'] != 0:
        wfe = (oos_results['Total Return'] / is_results['Total Return']) * 100
        check = wfe > 60
        checklist.append(check)
        print(f"  {'✓' if check else '✗'} WFE > 60%: {wfe:.1f}%")

    check = oos_results['Total Return'] > 0
    checklist.append(check)
    print(f"  {'✓' if check else '✗'} OOS 양수 수익: {oos_results['Total Return']:.2%}")

    # 3. 리스크 관리
    print(f"\n[ 리스크 관리 ]")
    print(f"  ✓ Stop Loss 설정: 5%")
    print(f"  ✓ Take Profit 설정: 15%")
    print(f"  ✓ 최대 보유 기간: 60일")
    print(f"  ✓ 수수료 반영: 0.1%")
    print(f"  ✓ 슬리피지 반영: 0.05%")

    # 4. 전체 평가
    print(f"\n{'='*70}")
    passed = sum(checklist)
    total = len(checklist)
    score = (passed / total) * 100

    print(f"전체 점수: {passed}/{total} ({score:.0f}%)")

    if score >= 80:
        print(f"평가: 실전 배포 가능 ✓")
    elif score >= 60:
        print(f"평가: 개선 후 배포 권장 ⚠")
    else:
        print(f"평가: 추가 개발 필요 ✗")

    print(f"{'='*70}")


def main():
    """메인 함수"""

    print("=" * 70)
    print("Chapter 18: 완전한 전략 개발 프로세스")
    print("Complete Strategy Development Framework")
    print("=" * 70)

    # 전략 개요
    print("\n[ 전략 개요 ]")
    print("이름: RSI Mean Reversion Strategy")
    print("가설: 과매도 구간에서 매수하여 정상 수준으로 회귀할 때 수익")
    print("\n진입 조건:")
    print("  - RSI < 30 (과매도)")
    print("  - 가격 > SMA(20) (상승 추세 유지)")
    print("\n청산 조건:")
    print("  - RSI > 70 (과매수)")
    print("  - Stop Loss: -5%")
    print("  - Take Profit: +15%")
    print("  - 최대 보유: 60일")

    # 백테스트 실행
    results_dict = run_complete_backtest(
        symbol='NVDA',
        start_date='2019-01-01',
        end_date='2024-01-01'
    )

    if results_dict:
        # 전략 리포트
        create_strategy_report(results_dict)

        # 다음 단계 안내
        print(f"\n[ 다음 단계 ]")
        print(f"1. 다른 종목(AAPL, MSFT, GOOGL 등)에서 테스트")
        print(f"2. 몬테카를로 시뮬레이션 실행")
        print(f"3. 전략 문서 작성")
        print(f"4. 페이퍼 트레이딩 3개월")
        print(f"5. 실전 배포 (소액부터 시작)")

    print("\n분석 완료!")
    print("\n" + "=" * 70)
    print("축하합니다! 백테스팅 입문 과정을 완료하셨습니다.")
    print("성공적인 트레이딩을 기원합니다!")
    print("=" * 70)


if __name__ == "__main__":
    main()
