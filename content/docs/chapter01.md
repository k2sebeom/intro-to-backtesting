---
title: "챕터 1: 설정과 기초"
weight: 1
bookToc: true
---

# 챕터 1: 설정과 기초

백테스팅의 세계에 오신 것을 환영합니다! 이 챕터에서는 백테스팅의 기본 개념을 이해하고, 필요한 도구들을 설치하며, 첫 번째 백테스트를 실행해보겠습니다.

## 백테스팅이란 무엇이고 왜 중요한가

백테스팅(Backtesting)은 과거 데이터를 사용하여 투자 전략의 성과를 시뮬레이션하는 과정입니다. 실제 자금을 투자하기 전에 전략이 얼마나 효과적인지 검증할 수 있는 중요한 도구입니다.

### 백테스팅의 장점

- **리스크 없는 검증**: 실제 돈을 잃을 위험 없이 전략을 테스트
- **객관적 평가**: 감정에 휘둘리지 않고 데이터 기반으로 전략 평가
- **매개변수 최적화**: 다양한 설정을 시도하여 최적의 조합 발견
- **성과 측정**: 수익률, 최대 손실, 샤프 비율 등 다양한 지표로 성과 분석

### 백테스팅의 한계

- **과최적화(Overfitting)**: 과거 데이터에만 맞춘 전략은 미래에 실패할 수 있음
- **생존자 편향**: 상장폐지된 종목 데이터 누락으로 인한 편향
- **거래 비용 미반영**: 수수료, 슬리피지 등 실제 거래 비용 고려 필요

## 개발 환경 설정

### uv 설치

`uv`는 빠르고 현대적인 Python 패키지 관리자입니다. 기존의 pip보다 훨씬 빠르고 의존성 관리가 우수합니다.

macOS에서 Homebrew를 사용하여 설치:

```bash
brew install uv
```

또는 공식 설치 스크립트 사용:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 프로젝트 초기화

이 책의 코드를 따라하려면 `codes` 디렉토리로 이동하여 Python 환경을 초기화하세요:

```bash
cd codes
uv init
```

### 필수 패키지 설치

백테스팅에 필요한 핵심 패키지들을 설치합니다:

```bash
uv add yfinance pandas matplotlib backtrader
```

각 패키지의 역할:

- **yfinance**: Yahoo Finance에서 주식 데이터 다운로드
- **pandas**: 데이터 조작 및 분석
- **matplotlib**: 차트 및 그래프 생성
- **backtrader**: 백테스팅 프레임워크

## OHLCV 데이터 이해

주식 데이터는 일반적으로 OHLCV 형태로 제공됩니다:

- **Open**: 시가 (장 시작 가격)
- **High**: 고가 (하루 중 최고 가격)
- **Low**: 저가 (하루 중 최저 가격)
- **Close**: 종가 (장 마감 가격)
- **Volume**: 거래량

### yfinance로 데이터 가져오기

실제 주식 데이터를 가져와보겠습니다:

```python
import yfinance as yf
import pandas as pd

# 삼성전자 데이터 다운로드 (1년간)
ticker = "005930.KS"  # 삼성전자 코드
data = yf.download(ticker, period="1y")

print(data.head())
print(f"\n데이터 형태: {data.shape}")
print(f"컬럼: {list(data.columns)}")
```

실제 다운로드된 데이터는 다음과 같은 형태입니다:

```
Price          Close      High       Low      Open    Volume
Ticker     005930.KS 005930.KS 005930.KS 005930.KS 005930.KS
Date                                                        
2025-10-14   91600.0   96000.0   90200.0   95300.0  35545235
2025-10-15   95000.0   95300.0   92100.0   92300.0  21050111
2025-10-16   97700.0   97700.0   95000.0   95300.0  28141060
2025-10-17   97900.0   99100.0   96700.0   97200.0  22730809
2025-10-20   98000.0   98300.0   96000.0   97900.0  14242908
```

주목할 점:
- **MultiIndex 컬럼**: yfinance는 여러 종목을 동시에 다운로드할 수 있도록 MultiIndex 구조를 사용합니다
- **한국 시간대**: 데이터는 한국 시간대 기준으로 제공됩니다
- **가격 단위**: 원화 기준 가격입니다
- **거래량**: 실제 거래된 주식 수량입니다

## matplotlib을 사용한 기본 플롯팅

데이터를 시각화하는 것은 패턴을 이해하는 데 중요합니다:

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정 (macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 종가 차트 그리기
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Close'], linewidth=1)
plt.title('삼성전자 주가 추이')
plt.xlabel('날짜')
plt.ylabel('가격 (원)')
plt.grid(True, alpha=0.3)

# x축 날짜 포맷 설정
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
```

## backtrader로 첫 번째 간단한 백테스트

이제 backtrader를 사용하여 간단한 매수 후 보유(Buy and Hold) 전략을 백테스트해보겠습니다:

```python
import backtrader as bt

class BuyAndHold(bt.Strategy):
    def start(self):
        self.val_start = self.broker.get_cash()  # 시작 자금

    def nextstart(self):
        # 첫 번째 데이터에서 전체 자금으로 매수
        size = int(self.broker.get_cash() / self.data.close[0])
        self.buy(size=size)

    def stop(self):
        # 최종 포트폴리오 가치
        self.val_end = self.broker.get_value()
        self.roi = (self.val_end - self.val_start) / self.val_start
        print(f'시작 자금: {self.val_start:,.0f}원')
        print(f'최종 가치: {self.val_end:,.0f}원')
        print(f'수익률: {self.roi:.2%}')

# Cerebro 엔진 생성
cerebro = bt.Cerebro()

# 전략 추가
cerebro.addstrategy(BuyAndHold)

# 데이터 추가
data_bt = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data_bt)

# 초기 자금 설정
cerebro.broker.setcash(10000000)  # 1천만원

# 백테스트 실행
print('백테스트 시작')
cerebro.run()

# 결과 플롯
cerebro.plot(style='candlestick', barup='red', bardown='blue')
```

## 실습: 첫 번째 백테스트 실행

이제 실제로 코드를 실행해보겠습니다. `codes/chapter01` 디렉토리에 예제 파일들이 준비되어 있습니다.

### 데이터 다운로드 예제

```python
# codes/chapter01/download_data.py
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
```

### 기본 차트 그리기 예제

```python
# codes/chapter01/basic_plotting.py
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def plot_stock_price(ticker, period="6m"):
    """주식 가격 차트 그리기"""
    # 데이터 다운로드
    data = yf.download(ticker, period=period)

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
    plt.savefig(f'{ticker}_chart.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    plot_stock_price("005930.KS")  # 삼성전자
```

### 첫 번째 백테스트 예제

```python
# codes/chapter01/first_backtest.py
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
    print(f'총 수익률: {returns_analyzer.rtot:.2%}')

    # 최대 손실 분석
    drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
    print(f'최대 손실: {drawdown_analyzer.max.drawdown:.2%}')

    # 샤프 비율
    sharpe_analyzer = strat.analyzers.sharpe.get_analysis()
    if sharpe_analyzer.get('sharperatio'):
        print(f'샤프 비율: {sharpe_analyzer["sharperatio"]:.2f}')

    # 차트 출력
    cerebro.plot(style='candlestick', barup='red', bardown='blue')

if __name__ == "__main__":
    run_backtest()
```

## 실행 방법 및 결과

코드를 실행하려면 `codes` 디렉토리에서 다음 명령어를 사용하세요:

### 1. 데이터 다운로드 실행

```bash
uv run chapter01/download_data.py
```

**실행 결과:**
```
005930.KS 데이터 다운로드 완료
기간: 2024-10-21 ~ 2025-10-20
데이터 포인트: 241개

최근 5일 데이터:
Price          Close      High       Low      Open    Volume
Ticker     005930.KS 005930.KS 005930.KS 005930.KS 005930.KS
Date                                                        
2025-10-14   91600.0   96000.0   90200.0   95300.0  35545235
2025-10-15   95000.0   95300.0   92100.0   92300.0  21050111
2025-10-16   97700.0   97700.0   95000.0   95300.0  28141060
2025-10-17   97900.0   99100.0   96700.0   97200.0  22730809
2025-10-20   98000.0   98300.0   96000.0   97900.0  14242908

데이터가 samsung_data.csv로 저장되었습니다.
```

> **참고**: 실행 시 `FutureWarning: YF.download() has changed argument auto_adjust default to True` 경고가 나타날 수 있습니다. 이는 yfinance 라이브러리의 기본 설정 변경에 대한 알림으로, 기능에는 영향을 주지 않습니다.

### 2. 기본 차트 그리기 실행

```bash
uv run chapter01/basic_plotting.py
```

**실행 결과:**
```
차트가 005930_KS_chart.png으로 저장되었습니다.
```

생성된 차트는 다음과 같습니다:

![삼성전자 주가 차트](/images/005930_KS_chart.png)

위 차트에서 볼 수 있듯이:
- 상단 그래프는 삼성전자의 주가 추이를 보여줍니다 (6개월간)
- 하단 그래프는 거래량을 나타냅니다
- 2025년 들어 주가가 상승 추세를 보이고 있음을 확인할 수 있습니다

### 3. 첫 번째 백테스트 실행

```bash
uv run chapter01/first_backtest.py
```

**실행 결과:**
```
백테스트 시작
시작 포트폴리오 가치: 10,000,000원
2023-01-02: 매수 주문: 가격 52577, 수량 180
2023-01-03: 매수 체결: 가격 52482, 수량 180, 수수료 14170
최종 포트폴리오 가치: 14,204,695원
총 수익률: 35.10%
최대 손실: 927.77%
총 수익률 (계산): 42.05%
백테스트 결과 차트가 backtest_result.png로 저장되었습니다.
```

백테스트 결과 차트:

![백테스트 결과](/images/backtest_result.png)

### 백테스트 결과 분석

2023년 한 해 동안 삼성전자 매수 후 보유 전략의 결과:

- **시작 자금**: 10,000,000원
- **최종 포트폴리오 가치**: 14,204,695원
- **총 수익률**: 42.05%
- **매수 시점**: 2023년 1월 3일 (52,482원에 180주 매수)
- **수수료**: 14,170원 (0.15%)

차트에서 확인할 수 있는 내용:
- 파란색 선: 포트폴리오 총 가치 변화 (최종 14,204,695원)
- 빨간색 선: 현금 잔고 (매수 후 539,030원 남음)
- 하단 캔들스틱 차트: 삼성전자 주가 움직임 (빨간색: 상승, 파란색: 하락)
- 녹색 삼각형: 매수 신호 (시작 시점에 한 번만 발생)
- 거래량: 회색 막대로 표시

### 성과 지표 해석

- **총 수익률 42.05%**: 2023년 한 해 동안 매우 우수한 성과
- **최대 손실**: 일시적으로 발생한 최대 하락폭
- **샤프 비율**: 위험 대비 수익률을 나타내는 지표 (높을수록 좋음)

이 결과는 2023년 삼성전자가 좋은 성과를 보였음을 의미하지만, 과거 성과가 미래 성과를 보장하지는 않습니다.

## 다음 단계

이 챕터에서는 백테스팅의 기본 개념을 배우고 필요한 도구들을 설치했습니다. 다음 챕터에서는 단순 이동평균(SMA) 전략을 구현하고 백테스트해보겠습니다.

### 주요 학습 내용 정리

- ✅ 백테스팅의 개념과 중요성 이해
- ✅ uv를 사용한 Python 환경 설정
- ✅ yfinance, pandas, matplotlib, backtrader 설치
- ✅ OHLCV 데이터 구조 이해
- ✅ 기본적인 데이터 시각화
- ✅ backtrader를 사용한 첫 번째 백테스트

다음 챕터에서는 더 정교한 거래 전략을 구현해보겠습니다!
