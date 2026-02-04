---
title: "Chapter 5: 이동평균 전략"
weight: 5
bookToc: true
---

# Chapter 5: 이동평균 전략

이동평균(Moving Average)은 가장 기본적이면서도 널리 사용되는 기술적 지표입니다. 이번 챕터에서는 이동평균의 원리를 이해하고, 골든 크로스(Golden Cross)와 데드 크로스(Death Cross) 전략을 구현해봅니다.

## 5.1 이동평균의 종류

### 5.1.1 단순 이동평균 (Simple Moving Average, SMA)

단순 이동평균은 일정 기간 동안의 가격을 산술 평균한 값입니다:

$$
\text{SMA}_n(t) = \frac{1}{n} \sum_{i=0}^{n-1} P_{t-i}
$$

여기서:
- $n$은 기간 (예: 20일, 50일, 200일)
- $P_t$는 시점 $t$의 종가
- $t$는 현재 시점

**특징:**
- 모든 데이터에 동일한 가중치 부여
- 계산이 간단하고 해석이 쉬움
- 오래된 데이터가 갑자기 평균에서 빠지면서 "계단 효과" 발생 가능

### 5.1.2 지수 이동평균 (Exponential Moving Average, EMA)

지수 이동평균은 최근 데이터에 더 큰 가중치를 부여합니다:

$$
\text{EMA}_n(t) = \alpha \cdot P_t + (1 - \alpha) \cdot \text{EMA}_n(t-1)
$$

여기서 평활 계수(smoothing factor) $\alpha$는:

$$
\alpha = \frac{2}{n + 1}
$$

**특징:**
- 최근 데이터에 더 민감하게 반응
- 계단 효과가 없어 부드러운 곡선
- 트렌드 변화를 빠르게 포착

## 5.2 골든 크로스와 데드 크로스

### 5.2.1 골든 크로스 (Golden Cross)

**매수 신호**: 단기 이동평균이 장기 이동평균을 상향 돌파

일반적으로 사용되는 조합:
- 50일 SMA가 200일 SMA를 상향 돌파
- 50일 EMA가 200일 EMA를 상향 돌파

**의미**: 단기 추세가 장기 추세보다 강해지고 있으며, 상승 추세가 시작될 가능성

### 5.2.2 데드 크로스 (Death Cross)

**매도 신호**: 단기 이동평균이 장기 이동평균을 하향 돌파

**의미**: 단기 추세가 장기 추세보다 약해지고 있으며, 하락 추세가 시작될 가능성

### 5.2.3 전략의 장단점

**장점:**
- 명확한 진입/청산 신호
- 주요 트렌드를 따라가는 추세 추종 전략
- 구현이 간단하고 이해하기 쉬움
- 장기적으로 큰 수익 기회 포착 가능

**단점:**
- 횡보장(sideways market)에서 빈번한 거짓 신호(whipsaw)
- 신호 지연(lag): 트렌드가 이미 상당히 진행된 후 신호 발생
- 진입/청산 시점이 늦어 초기 이익 놓치거나 손실 확대 가능

## 5.3 실전 구현

이번 챕터의 코드에서는 다음을 구현합니다:

1. **SMA 크로스오버 전략**: 50일/200일 SMA를 사용한 골든/데드 크로스
2. **EMA 크로스오버 전략**: 50일/200일 EMA를 사용한 크로스오버
3. **성과 비교**: Buy & Hold vs. SMA 전략 vs. EMA 전략

### 5.3.1 Backtrader에서 이동평균 사용

```python
import backtrader as bt

class MovingAverageCrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 50),
        ('slow_period', 200),
    )

    def __init__(self):
        # SMA 계산
        self.fast_ma = bt.indicators.SMA(
            self.data.close,
            period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SMA(
            self.data.close,
            period=self.params.slow_period
        )

        # 크로스오버 신호
        self.crossover = bt.indicators.CrossOver(
            self.fast_ma,
            self.slow_ma
        )
```

### 5.3.2 거래 로직

```python
def next(self):
    if self.crossover > 0:  # 골든 크로스
        if not self.position:
            self.buy()
    elif self.crossover < 0:  # 데드 크로스
        if self.position:
            self.close()
```

## 5.4 기대 결과

코드를 실행하면 다음을 확인할 수 있습니다:

1. **이동평균 시각화**: 가격과 함께 50일/200일 이동평균 표시
2. **매매 신호**: 골든 크로스와 데드 크로스 지점 표시
3. **성과 비교**:
   - Buy & Hold 전략 수익률
   - SMA 크로스오버 전략 수익률
   - EMA 크로스오버 전략 수익률
4. **위험 지표**: Sharpe Ratio, Maximum Drawdown
5. **거래 통계**: 총 거래 횟수, 승률, 평균 수익/손실

## 5.5 분석 포인트

코드를 실행한 후 다음을 분석해보세요:

1. **트렌드 추종 효과**: 강한 상승/하락 추세에서 전략이 얼마나 효과적인가?
2. **횡보장 손실**: 가격이 이동평균 주변에서 횡보할 때 손실이 얼마나 발생하는가?
3. **신호 지연**: 실제 트렌드 전환과 매매 신호 사이의 시간 차이
4. **SMA vs. EMA**: 어떤 이동평균이 더 나은 성과를 보이는가?
5. **거래 빈도**: 거래가 얼마나 자주 발생하며, 수수료 영향은?

## 5.6 개선 방향

이동평균 전략을 개선할 수 있는 방법:

1. **기간 최적화**: 50/200일이 아닌 다른 기간 조합 테스트
2. **필터 추가**: 거래량, 변동성 등 추가 조건으로 거짓 신호 필터링
3. **포지션 크기 조절**: 신호 강도에 따라 매수 비중 조절
4. **손절/익절**: 고정 비율 손절매와 익절매 설정
5. **다중 시간프레임**: 상위 시간프레임 트렌드 확인 후 진입

## 다음 단계

다음 챕터에서는 RSI(Relative Strength Index)를 활용한 과매수/과매도 전략을 배웁니다. 이동평균이 추세 추종 전략이라면, RSI는 역추세(mean reversion) 전략의 대표적인 예입니다.

---

**코드 실행:**
```bash
cd codes
uv run chapter05/01_moving_average_strategy.py
```
