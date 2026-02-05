---
title: "Chapter 4: Backtrader 프레임워크 기초"
weight: 4
bookToc: true
---

# Chapter 4: Backtrader 프레임워크 기초

이 챕터에서는 Python의 대표적인 백테스팅 프레임워크인 **Backtrader**를 본격적으로 사용합니다. Backtrader의 아키텍처를 이해하고, 첫 번째 실전 전략인 Buy & Hold를 구현하며, 기본적인 성과 분석 방법을 배웁니다.

## 4.1 Backtrader란?

### Backtrader 소개

**Backtrader**는 Python으로 작성된 오픈소스 백테스팅 프레임워크입니다.

**주요 특징**:
- ✅ 완전한 기능: Strategy, Indicators, Analyzers, Observers 등
- ✅ 유연성: 다양한 전략과 지표를 쉽게 구현
- ✅ 성능: 효율적인 데이터 처리
- ✅ 시각화: 내장 플로팅 기능
- ✅ 활발한 커뮤니티: 풍부한 문서와 예제

**공식 사이트**: https://www.backtrader.com/

### 왜 Backtrader인가?

다른 백테스팅 라이브러리와 비교:

| 라이브러리 | 장점 | 단점 |
|-----------|------|------|
| **Backtrader** | 완전한 기능, 유연성 | 학습 곡선 |
| Zipline | Quantopian 출신, 강력 | 유지보수 중단 |
| Backtesting.py | 간단함, 빠름 | 제한적 기능 |
| VectorBT | 빠른 속도, 벡터화 | 복잡한 전략 어려움 |

Backtrader는 **기능의 완전성**과 **유연성**에서 최고의 선택입니다.

## 4.2 Backtrader 아키텍처

### 핵심 구성 요소

Backtrader는 다음 4가지 핵심 요소로 구성됩니다:

```
┌─────────────────────────────────────┐
│           Cerebro (엔진)             │
│  ┌───────────────────────────────┐  │
│  │        Strategy (전략)         │  │
│  │  - __init__: 초기화            │  │
│  │  - next: 매 바마다 실행        │  │
│  │  - notify_order: 주문 알림     │  │
│  │  - notify_trade: 거래 알림     │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │      Data Feeds (데이터)       │  │
│  │  - CSV, Pandas, Yahoo, 등     │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │     Analyzers (분석기)         │  │
│  │  - Sharpe, Drawdown, Returns  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### 1. Cerebro (대뇌)

**역할**: 전체 백테스팅 엔진의 중앙 컨트롤러

```python
import backtrader as bt

cerebro = bt.Cerebro()  # Cerebro 인스턴스 생성

# 설정
cerebro.addstrategy(MyStrategy)  # 전략 추가
cerebro.adddata(data)             # 데이터 추가
cerebro.broker.setcash(10000)     # 초기 자본금
cerebro.broker.setcommission(0.001)  # 수수료 0.1%

# 실행
results = cerebro.run()
```

#### 2. Strategy (전략)

**역할**: 트레이딩 로직을 정의하는 클래스

```python
class MyStrategy(bt.Strategy):
    def __init__(self):
        """초기화: 지표 계산 등"""
        self.sma = bt.indicators.SMA(self.data.close, period=20)

    def next(self):
        """매 바(일)마다 실행되는 메인 로직"""
        if not self.position:  # 포지션이 없으면
            if self.data.close[0] > self.sma[0]:
                self.buy()  # 매수
        else:  # 포지션이 있으면
            if self.data.close[0] < self.sma[0]:
                self.sell()  # 매도
```

**주요 메서드**:
- `__init__()`: 전략 초기화, 지표 생성
- `next()`: 매 바마다 실행 (핵심 로직)
- `notify_order()`: 주문 상태 변경 알림
- `notify_trade()`: 거래 완료 알림
- `stop()`: 백테스트 종료 시 호출

#### 3. Data Feeds (데이터 피드)

**역할**: 전략에 시장 데이터 제공

```python
# Pandas DataFrame에서 데이터 로드
data = bt.feeds.PandasData(dataname=df)

# CSV 파일에서 데이터 로드
data = bt.feeds.GenericCSVData(
    dataname='AAPL_5y.csv',
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5
)

cerebro.adddata(data)
```

#### 4. Analyzers (분석기)

**역할**: 백테스트 성과 분석

```python
# Analyzer 추가
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

# 실행 후 결과 확인
results = cerebro.run()
strat = results[0]

print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.3f}")
print(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
```

## 4.3 데이터 접근 방법

### 인덱싱 규칙

Backtrader는 **0-based indexing**을 사용하지만 **역순**입니다:

```python
self.data.close[0]   # 현재 종가
self.data.close[-1]  # 이전 종가
self.data.close[-2]  # 2일 전 종가

self.data.high[0]    # 현재 고가
self.data.low[0]     # 현재 저가
self.data.volume[0]  # 현재 거래량
```

**주의**: `[0]`이 **현재**, `[-1]`이 **과거**입니다!

### Lines 개념

Backtrader는 **Lines** 개념을 사용합니다:

```python
# OHLCV는 기본 Lines
self.data.close  # Close line
self.data.open   # Open line
self.data.high   # High line
self.data.low    # Low line
self.data.volume # Volume line

# 지표도 Lines
self.sma = bt.indicators.SMA(period=20)
self.sma[0]  # 현재 SMA 값
```

## 4.4 주문 실행

### 기본 주문 메서드

```python
# 매수
self.buy()                    # 시장가 전량 매수
self.buy(size=100)           # 100주 매수
self.buy(price=150.0)        # 지정가 매수

# 매도
self.sell()                   # 포지션 전량 매도
self.sell(size=50)           # 50주 매도
self.close()                  # 포지션 청산 (매도와 동일)
```

### 주문 추적

```python
class MyStrategy(bt.Strategy):
    def __init__(self):
        self.order = None

    def next(self):
        # 대기 중인 주문이 있으면 건너뛰기
        if self.order:
            return

        if not self.position:
            self.order = self.buy()

    def notify_order(self, order):
        """주문 상태 변경 알림"""
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'매수 체결: {order.executed.price:.2f}')
            elif order.issell():
                print(f'매도 체결: {order.executed.price:.2f}')

            self.order = None  # 주문 완료, 초기화

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('주문 취소/거부')
            self.order = None
```

### 포지션 관리

```python
# 현재 포지션 확인
if self.position:
    print(f'보유 주식: {self.position.size}주')
    print(f'평균 매수가: {self.position.price:.2f}')

# 포지션 여부
if not self.position:  # 포지션 없음
    self.buy()

if self.position:      # 포지션 있음
    self.sell()
```

## 4.5 첫 번째 전략: Buy & Hold

### Buy & Hold 전략이란?

**Buy & Hold (매수 후 보유)**는 가장 간단한 투자 전략입니다:

1. 백테스트 시작 시점에 매수
2. 끝까지 보유
3. 종료 시점에 매도

이 전략은 **벤치마크**로 자주 사용됩니다.

### 전략 구현

```python
class BuyAndHoldStrategy(bt.Strategy):
    """
    Buy & Hold 전략
    첫 거래일에 매수하고 끝까지 보유
    """

    def __init__(self):
        """초기화"""
        self.order = None
        self.buy_price = None
        self.buy_comm = None

    def next(self):
        """매 바마다 실행"""
        # 이미 주문이 있으면 대기
        if self.order:
            return

        # 포지션이 없으면 매수
        if not self.position:
            # 사용 가능한 모든 자금으로 매수
            self.order = self.buy()
            print(f'{self.data.datetime.date(0)}: 매수 주문 실행')

    def notify_order(self, order):
        """주문 상태 변경 알림"""
        if order.status in [order.Submitted, order.Accepted]:
            # 주문 제출/접수 - 아무것도 하지 않음
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                print(f'매수 체결: 가격 ${order.executed.price:.2f}, '
                      f'수수료 ${order.executed.comm:.2f}')

        self.order = None

    def notify_trade(self, trade):
        """거래 완료 알림"""
        if trade.isclosed:
            print(f'거래 종료: 손익 ${trade.pnl:.2f}')

    def stop(self):
        """백테스트 종료 시 호출"""
        print(f'\n최종 포트폴리오 가치: ${self.broker.getvalue():.2f}')
```

## 4.6 실습: Buy & Hold 백테스트

이제 실제로 Buy & Hold 전략을 백테스트해봅시다.

### 코드 실행

```bash
cd codes
uv run chapter04/01_buy_and_hold.py
```

### 스크립트 개요

이 스크립트는 다음을 수행합니다:

1. **데이터 로드**: Chapter 2에서 저장한 AAPL 데이터
2. **Cerebro 설정**: 초기 자금, 수수료 설정
3. **전략 실행**: Buy & Hold 전략 백테스트
4. **성과 분석**: Analyzers를 사용한 상세 분석
5. **시각화**: 포트폴리오 가치, 거래 기록 차트

### 실행 결과 분석

실제 스크립트를 실행한 결과입니다:

```
==========================================
Chapter 4: Backtrader 프레임워크 기초
==========================================

=== Buy & Hold 전략 백테스트 ===

초기 설정:
- 초기 자금: $10,000.00
- 수수료: 0.10%
- 데이터: AAPL

백테스트 실행 중...

2021-02-08: 매수 주문 실행
2021-02-09: 매수 체결: 가격 $133.19, 비용 $9479.88, 수수료 $9.48
2026-02-04: 최종 포트폴리오 가치: $20189.72

==========================================
=== 성과 분석 ===
==========================================

기본 지표:
- 초기 자금: $10,000.00
- 최종 자금: $20,189.72
- 총 수익률: +101.90%

Sharpe Ratio: 0.603

최대 낙폭:
- Max Drawdown: 32.46%
- DD Duration: 354 days

수익률:
- Total Return: +70.26%
- Annualized Return: +15.16%

거래 통계:
- 총 거래: 1
- 승: 0, 패: 0
- 승률: 0.0%

==========================================
=== 벤치마크 비교 (vs SPY) ===
==========================================
AAPL Buy & Hold: +101.90%
SPY: +89.15%
초과 수익: +12.74%

차트 저장 완료: chapter04/images/buy_and_hold.png
```

![Buy & Hold 백테스트 결과](/images/chapter04/buy_and_hold.png)

### 결과 해석

#### 차트 분석

**상단 패널: AAPL 주가 차트**
- **녹색 삼각형 (▲)**: 매수 시점 (2021-02-09, $133.19)
- 5년간 주가는 $133 → $248로 약 86% 상승
- 두 차례 큰 조정 구간:
  - **2022년 하반기**: $170 → $123 (-27.6%)
  - **2024년 말**: $250 → $174 (-30.4%)
- 최종 주가: $248 (2026-02-04)

**하단 패널: 포트폴리오 가치**
- **보라색 실선**: 백테스트 포트폴리오 가치
- **점선**: 초기 자금 $10,000
- 주가 움직임과 정확히 일치하는 모습
- 최종 가치: $20,189.72 (약 2배)

#### 성과 지표 분석

**1. 총 수익률: +101.90%**
- 초기 $10,000 → 최종 $20,189.72
- 5년간 약 2배 수익
- 복리 효과를 포함한 실제 수익률

**2. 연간 수익률: +15.16%**
- 5년간 평균 연 15.16% 수익
- S&P 500 장기 평균 (약 10%)보다 높은 수치
- 계산: $(20189.72 / 10000)^{1/5} - 1 = 0.1516$

**3. Sharpe Ratio: 0.603**
- 위험 대비 수익률 측정
- 일반적 해석:
  - < 1.0: 보통
  - 1.0~2.0: 좋음
  - > 2.0: 매우 좋음
- **0.603은 보통 수준**: 수익은 있지만 변동성도 상당함

**4. Maximum Drawdown: -32.46%**
- 고점 대비 최대 낙폭
- 2024년 말 조정 시 발생 ($250 → $174)
- **의미**: 최악의 경우 자산이 32% 하락할 수 있음
- 투자자는 이 정도의 손실을 견딜 수 있어야 함

**5. Drawdown Duration: 354일**
- 고점 회복에 걸린 최장 기간
- 약 1년간 손실 상태 지속
- **심리적 압박**: 장기간 손실 상태는 투자자의 인내심을 시험

#### 벤치마크 비교

**AAPL vs SPY**:
- AAPL: +101.90%
- SPY: +89.15%
- 초과 수익: +12.74%

**해석**:
- AAPL이 시장(SPY)을 13% 초과 달성
- 하지만 개별 주식은 더 높은 리스크(변동성)를 동반
- Sharpe Ratio로 비교하면 리스크 조정 후 차이는 더 작을 것

#### 거래 비용 영향

**수수료 분석**:
- 매수 비용: $9,479.88
- 수수료: $9.48 (0.1%)
- 수수료 비율: 전체 수익의 약 0.05%

**인사이트**:
- Buy & Hold는 거래가 1회뿐이므로 수수료 영향 최소
- 빈번한 거래 전략은 수수료가 수익률에 큰 영향
- 다음 챕터에서 다룰 이동평균 전략에서 이를 확인할 예정

#### 실전 적용 고려사항

**장점**:
- ✅ 간단한 전략 (매수 후 보유만)
- ✅ 거래 비용 최소화
- ✅ 장기적으로 시장 상승 추세 활용
- ✅ 감정적 결정 배제

**단점**:
- ❌ 큰 낙폭 (-32%) 견뎌야 함
- ❌ 조정 구간에서 손실 축소 불가
- ❌ 하락장에서 무력함
- ❌ 타이밍의 중요성 (매수 시점)

**누가 사용해야 하는가?**
- 장기 투자자 (5년 이상)
- 높은 변동성을 견딜 수 있는 투자자
- 시장 타이밍을 잡기 어렵다고 생각하는 투자자
- 적극적 관리 시간이 없는 투자자

### 백테스팅의 가치

이 간단한 Buy & Hold 백테스트를 통해 우리는:

1. **실제 성과 확인**: 5년간 +101.9% 수익 (이론이 아닌 실제)
2. **리스크 파악**: 최대 -32% 하락 가능성 인지
3. **심리적 준비**: 1년간 손실 상태를 견뎌야 할 수도 있음
4. **벤치마크 비교**: SPY 대비 +13% 초과 수익 확인
5. **전략 개선 방향**: 조정 구간에서 손실을 줄일 방법 필요

### 수익성의 진실: Buy & Hold가 이기기 어려운 벤치마크다

**⚠️ 가장 중요한 수익성 교훈**: 이 단순한 Buy & Hold 결과가 바로 당신이 개발할 모든 복잡한 전략이 넘어야 할 **최소 기준**입니다.

```
Buy & Hold 성과:
- 총 수익률: +101.90%
- 연간 수익률: +15.16%
- Sharpe Ratio: 0.603
- 최대 낙폭: -32.46%
- 거래 횟수: 1회
- 거래 비용: $9.48
```

**현실 체크: Chapter 5의 이동평균 전략 미리보기**

다음 챕터에서 배울 SMA(50/200) 골든크로스 전략의 실제 결과:

```
SMA 전략 성과:
- 총 수익률: +11.07%  ← Buy & Hold보다 -90.8% 낮음!
- Sharpe Ratio: 0.266  ← Buy & Hold의 절반도 안 됨
- 최대 낙폭: -14.41%  ← 이것만 더 나음
- 거래 횟수: 2회
- 거래 비용: ~$30-40
```

**충격적인 사실**: 복잡한 이동평균 전략이 단순히 사서 보유하는 것보다 **90% 이상 낮은** 수익을 냈습니다!

**왜 이런 일이 발생하는가?**

1. **강세장에서는 계속 보유가 최선**
   - 2021-2026년 AAPL은 강한 상승 추세
   - 매도 신호로 현금 전환 시 상승 놓침
   - 재진입 시점은 이미 가격이 올라간 후

2. **신호 지연 (Signal Lag)**
   - 이동평균은 과거 데이터 기반
   - 200일 이동평균은 200일 전 ~ 오늘까지의 평균
   - 트렌드가 이미 진행된 후에야 신호 발생

3. **거래 비용 누적**
   - Buy & Hold: 1회 거래, $9.48 수수료
   - SMA 전략: 2회 거래, $30-40 수수료
   - 거래가 많을수록 수수료가 수익 잠식

4. **타이밍 불일치**
   - 매도 신호: 종종 너무 늦음 (이미 많이 하락한 후)
   - 매수 신호: 종종 너무 늦음 (이미 많이 상승한 후)

**그렇다면 왜 복잡한 전략을 배우는가?**

이것이 이 책의 핵심 질문입니다. 답은:

✅ **시장 환경이 다를 때를 대비**
- 2008 금융위기: -50% 하락 (Buy & Hold 참담)
- 2000 닷컴 버블: -80% 하락 (Buy & Hold 파멸)
- 횡보장: 10년간 제자리 (Buy & Hold 무의미)

✅ **리스크 조정 후 더 나을 수 있음**
- SMA는 최대 낙폭 -14% (vs -32%)
- 심리적으로 견디기 쉬움
- 일부 투자자는 높은 수익보다 낮은 변동성 선호

✅ **여러 전략 조합**
- 강세장: Buy & Hold 비중 높임
- 약세장: 방어적 전략 비중 높임
- **시장 체제 감지**가 핵심

**수익성 체크리스트: 전략 평가 시 필수 질문**

| 질문 | Buy & Hold | 당신의 전략 |
|------|------------|------------|
| 절대 수익률이 더 높은가? | 101.90% | ? |
| 리스크 조정 수익률(Sharpe)이 더 높은가? | 0.603 | ? |
| 최대 낙폭이 더 낮은가? | -32.46% | ? |
| 거래 비용을 고려했는가? | $9.48 | ? |
| 다양한 시장 환경에서 테스트했는가? | 강세장만 | ? |

**모든 칸에서 "Yes"가 아니면, 그 전략은 실전에서 실패할 가능성이 높습니다.**

**실용적 조언**:
1. 먼저 Buy & Hold 백테스트를 항상 실행하세요
2. 새 전략은 반드시 Buy & Hold와 비교하세요
3. 수익률만 보지 말고 Sharpe Ratio, Max DD도 비교하세요
4. 강세장에서 이기지 못해도 괜찮습니다 - 약세장에서 방어가 목표일 수 있습니다
5. "이기기" 위해 필요한 것: 더 높은 Sharpe Ratio 또는 더 낮은 Max DD

다음 챕터에서는 이동평균을 활용하여 조정 구간에서 현금으로 전환하는 전략을 배워봅시다! (단, 현실적인 기대치를 가지고 접근합니다)

## 4.7 Analyzers를 사용한 성과 분석

### 주요 Analyzers

Backtrader는 다양한 내장 Analyzers를 제공합니다:

**1. SharpeRatio (샤프 비율)**

위험 대비 수익률:

$$\text{Sharpe Ratio} = \frac{E[R - R_f]}{\sigma}$$

```python
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                    riskfreerate=0.01)  # 무위험 이자율 1%

sharpe = results[0].analyzers.sharpe.get_analysis()
print(f"Sharpe Ratio: {sharpe['sharperatio']:.3f}")
```

**2. DrawDown (낙폭)**

최대 손실폭:

$$\text{MDD} = \max_{t}\left(\frac{Peak - Trough}{Peak}\right)$$

```python
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

dd = results[0].analyzers.drawdown.get_analysis()
print(f"Max Drawdown: {dd['max']['drawdown']:.2f}%")
print(f"DD Duration: {dd['max']['len']} days")
```

**3. Returns (수익률)**

```python
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

rets = results[0].analyzers.returns.get_analysis()
print(f"Total Return: {rets['rtot']:.2%}")
print(f"Average Return: {rets['ravg']:.2%}")
```

**4. TradeAnalyzer (거래 분석)**

```python
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

trades = results[0].analyzers.trades.get_analysis()
print(f"Total Trades: {trades['total']['total']}")
print(f"Won: {trades['won']['total']}")
print(f"Lost: {trades['lost']['total']}")
```

### 커스텀 Analyzer

필요하면 직접 Analyzer를 만들 수 있습니다:

```python
class MyAnalyzer(bt.Analyzer):
    def __init__(self):
        self.rets = []

    def notify_cashvalue(self, cash, value):
        """포트폴리오 가치 변경 시 호출"""
        self.rets.append(value)

    def get_analysis(self):
        """분석 결과 반환"""
        return {
            'final_value': self.rets[-1],
            'max_value': max(self.rets),
            'min_value': min(self.rets)
        }
```

## 4.8 브로커 설정

### 초기 자본금

```python
cerebro.broker.setcash(100000)  # $100,000
```

### 수수료

```python
# 비율 기반 (0.1%)
cerebro.broker.setcommission(commission=0.001)

# 주당 고정 ($0.01/주)
cerebro.broker.setcommission(commission=0.01, commtype=bt.CommInfoBase.COMM_FIXED)
```

### 슬리피지 (Slippage)

```python
# 고정 슬리피지
cerebro.broker.set_slippage_fixed(0.05, slip_open=True, slip_out=True)

# 비율 슬리피지
cerebro.broker.set_slippage_perc(0.001)  # 0.1%
```

### 포지션 사이징

```python
# 전략에서 크기 지정
self.buy(size=100)  # 100주

# 브로커에서 기본 크기 설정
cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# 자금 비율 기반
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)  # 95% 투자
```

## 4.9 다음 단계

### 이 챕터에서 배운 것

✅ **Backtrader 아키텍처**: Cerebro, Strategy, Data Feeds, Analyzers
✅ **전략 구현**: `__init__()`, `next()`, `notify_order()` 메서드
✅ **주문 실행**: `buy()`, `sell()`, `close()` 메서드
✅ **Buy & Hold 전략**: 가장 기본적인 벤치마크 전략
✅ **성과 분석**: Analyzers를 사용한 상세 분석
✅ **브로커 설정**: 자본금, 수수료, 슬리피지

### 실습 과제

1. **다른 종목**: Tesla (TSLA) 또는 Microsoft (MSFT)로 Buy & Hold를 실행해보세요.

2. **초기 자금 변경**: $50,000, $100,000으로 변경하여 결과를 비교해보세요.

3. **수수료 영향**: 수수료를 0%, 0.05%, 0.2%로 변경하여 영향을 분석해보세요.

4. **기간 변경**: 1년, 3년, 10년 데이터로 백테스트해보세요.

### 다음 챕터 미리보기

**Chapter 5: 이동평균 전략 (Part 2 시작!)**에서는:
- 단순 이동평균 (SMA)과 지수 이동평균 (EMA)
- Golden Cross / Death Cross 크로스오버 전략
- 파라미터 최적화
- 실전 이동평균 전략 백테스팅

---

**💡 핵심 메시지: 수익성 벤치마크의 설정**

Backtrader는 강력하고 유연한 백테스팅 프레임워크입니다. Cerebro, Strategy, Data Feeds, Analyzers의 4가지 핵심 요소를 이해하면, 어떤 복잡한 전략도 구현할 수 있습니다.

**하지만 기술보다 더 중요한 것**: Buy & Hold (+101.90%, Sharpe 0.603, Max DD -32%)는 가장 간단한 전략이지만, **모든 커스텀 전략이 넘어야 할 최소 기준**입니다.

**명심하세요**:
- 복잡한 전략 ≠ 더 높은 수익
- 90% 이상의 기술적 지표 전략은 강세장에서 Buy & Hold를 이기지 못함
- 전략의 가치는 "다른 시장 환경에서의 방어력"에 있습니다
- Sharpe Ratio와 Max DD를 함께 봐야 진정한 성과를 알 수 있습니다

다음 챕터부터는 Part 2로 진입하여 실전 기술적 분석 전략들을 하나씩 구현해봅시다! (그리고 대부분이 Buy & Hold를 이기지 못한다는 냉혹한 현실도 함께 배웁니다)
