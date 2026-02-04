---
title: "Chapter 10: 리스크 관리와 손절매"
weight: 10
bookToc: true
---

# Chapter 10: 리스크 관리와 손절매

성공적인 트레이딩의 핵심은 수익을 극대화하는 것이 아니라 손실을 최소화하는 것입니다. 이번 챕터에서는 손절매(Stop Loss)와 익절매(Take Profit)를 활용한 체계적인 리스크 관리 기법을 배웁니다.

## 10.1 리스크 관리의 중요성

### 10.1.1 왜 리스크 관리가 중요한가?

**손실의 비대칭성**:
```
10% 손실 → 11.1% 수익 필요 (회복)
20% 손실 → 25% 수익 필요
50% 손실 → 100% 수익 필요!
```

**복리 효과의 역**:
- 작은 손실도 누적되면 계좌 파괴
- 일관된 소액 손실 제어가 핵심

**감정적 의사결정 방지**:
- 큰 손실 → 패닉 매도 또는 복수 매매
- 명확한 규칙으로 감정 제어

### 10.1.2 리스크 관리의 기본 원칙

**원칙 1: 거래 전에 손절매 지점 결정**
```
진입 전 → 손절매 가격 설정
진입 후 → 절대 변경하지 않음
```

**원칙 2: 손익비(Risk-Reward Ratio) 최소 1:2**
```
손실 위험: $100
목표 수익: $200 이상

손익비 = 목표 수익 / 위험 손실 = 2:1
```

**원칙 3: 연속 손실 대비 계획**
```
3회 연속 손실 시 → 휴식 또는 포지션 축소
시스템 재검토 필요
```

## 10.2 손절매 (Stop Loss) 유형

### 10.2.1 고정 비율 손절매 (Percentage Stop)

**방법**: 진입가에서 고정 비율만큼 떨어지면 청산

```python
entry_price = 100
stop_loss_percent = 0.02  # 2%
stop_loss_price = entry_price * (1 - stop_loss_percent)  # $98
```

**장점**:
- 단순하고 명확
- 계산 쉬움
- 일관된 위험 관리

**단점**:
- 변동성 무시
- 시장 구조 무시
- 거짓 손절 가능

**적용 사례**: 초보자, 단기 매매

### 10.2.2 ATR 기반 손절매 (ATR Stop)

**방법**: ATR(Average True Range) 배수로 손절매 설정

$$
\text{Stop Loss} = \text{Entry Price} - (n \times \text{ATR})
$$

```python
entry_price = 100
atr = 5
multiplier = 2
stop_loss_price = entry_price - (atr * multiplier)  # $90
```

**장점**:
- 변동성 자동 반영
- 시장 적응적
- 거짓 손절 감소

**단점**:
- ATR 계산 필요
- 시장별 최적 배수 다름

**적용 사례**: 경험자, 변동성 큰 시장

**ATR 배수 가이드**:
- 단기 (Scalping): 1-1.5 × ATR
- 중기 (Swing): 2-3 × ATR
- 장기 (Position): 3-5 × ATR

### 10.2.3 지지선/저항선 기반 손절매

**방법**: 주요 가격 수준 아래/위에 손절매 설정

```
매수 시: 최근 저점 아래
매도 시: 최근 고점 위
```

**장점**:
- 시장 구조 반영
- 논리적 위치
- 심리적 안정

**단점**:
- 주관적 판단 필요
- 명확한 지지/저항 없을 수 있음

**적용 사례**: 기술적 분석 중심 트레이더

### 10.2.4 추적 손절매 (Trailing Stop)

**방법**: 가격이 유리하게 움직이면 손절매도 함께 이동

$$
\text{Trailing Stop} = \max(\text{Current Stop}, \text{Highest Price} - \text{Trail Amount})
$$

```python
# 초기 손절매
stop_loss = entry_price * 0.98  # 2% 아래

# 가격 상승 시
if current_price > entry_price:
    new_stop = current_price * 0.98
    stop_loss = max(stop_loss, new_stop)  # 위로만 이동
```

**장점**:
- 수익 보호
- 큰 추세 포착
- 감정 제어

**단점**:
- 조기 청산 가능
- 횡보장에서 불리

**적용 사례**: 추세 추종 전략, 큰 수익 추구

### 10.2.5 시간 기반 손절매 (Time Stop)

**방법**: 일정 기간 후 무조건 청산

```python
entry_date = datetime(2024, 1, 1)
max_holding_days = 10

if current_date - entry_date >= timedelta(days=max_holding_days):
    close_position()
```

**장점**:
- 자본 효율
- 기회비용 감소
- 시스템 단순화

**단점**:
- 가격 무시
- 추세 놓칠 수 있음

**적용 사례**: 단기 매매, 옵션 거래

## 10.3 익절매 (Take Profit) 전략

### 10.3.1 고정 목표 익절매

**방법**: 손익비에 따른 목표가 도달 시 청산

```python
entry_price = 100
stop_loss = 95
risk = entry_price - stop_loss  # $5

reward_risk_ratio = 2
take_profit = entry_price + (risk * reward_risk_ratio)  # $110
```

**장점**:
- 명확한 목표
- 손익비 준수
- 감정 제거

**단점**:
- 큰 추세 놓칠 수 있음
- 목표가 임의적일 수 있음

### 10.3.2 부분 익절 (Partial Profit Taking)

**방법**: 여러 단계로 나눠 익절

```python
entry_price = 100
position_size = 100

# 첫 번째 목표 (+5%)
if price >= 105:
    close_shares(50)  # 50% 청산

# 두 번째 목표 (+10%)
if price >= 110:
    close_shares(30)  # 추가 30% 청산

# 나머지는 추적 손절매
```

**장점**:
- 위험 감소
- 큰 추세도 포착
- 심리적 안정

**단점**:
- 복잡성 증가
- 수수료 증가

### 10.3.3 추적 익절 (Trailing Take Profit)

**방법**: 가격이 유리하게 움직일 때만 추적

```python
# 일정 수익 이상 달성 후 추적 시작
if profit >= initial_target:
    trailing_stop_active = True

if trailing_stop_active:
    trail_stop = highest_price * 0.95  # 5% 아래 추적
```

## 10.4 손익비와 승률의 관계

### 10.4.1 손익비 (Risk-Reward Ratio)

$$
\text{Risk-Reward Ratio} = \frac{\text{Average Win}}{\text{Average Loss}}
$$

### 10.4.2 기대값 (Expected Value)

$$
\text{EV} = (W \times \text{AvgWin}) - ((1 - W) \times \text{AvgLoss})
$$

여기서 $W$는 승률 (Win Rate)

**예시**:
```
승률 40%, 평균 수익 $300, 평균 손실 $100

EV = (0.4 × 300) - (0.6 × 100)
   = 120 - 60
   = $60 (양수 → 수익성 있음!)
```

### 10.4.3 손익비-승률 조합

| 승률 | 필요한 최소 손익비 | 비고 |
|-----|------------------|------|
| 30% | 2.33:1 | 낮은 승률, 높은 손익비 |
| 40% | 1.50:1 | 균형 잡힌 조합 |
| 50% | 1.00:1 | 가장 쉬움 |
| 60% | 0.67:1 | 높은 승률, 낮은 손익비 가능 |

**교훈**: 낮은 승률도 높은 손익비로 수익 가능!

## 10.5 Backtrader에서 손절매/익절매 구현

### 10.5.1 고정 손절매/익절매

```python
class StopLossStrategy(bt.Strategy):
    params = (
        ('stop_loss_percent', 0.02),  # 2% 손절
        ('take_profit_percent', 0.04),  # 4% 익절
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                # 손절매/익절매 주문 생성
                stop_price = order.executed.price * (1 - self.params.stop_loss_percent)
                limit_price = order.executed.price * (1 + self.params.take_profit_percent)

                self.sell(exectype=bt.Order.Stop, price=stop_price)
                self.sell(exectype=bt.Order.Limit, price=limit_price)
```

### 10.5.2 ATR 기반 손절매

```python
def next(self):
    if not self.position:
        if buy_signal:
            self.buy()
    else:
        # ATR 손절매
        atr = self.atr[0]
        stop_price = self.position.price - (atr * 2)

        if self.data.close[0] < stop_price:
            self.close()
```

### 10.5.3 추적 손절매

```python
class TrailingStopStrategy(bt.Strategy):
    def __init__(self):
        self.highest_price = 0
        self.trail_percent = 0.05  # 5%

    def next(self):
        if self.position:
            # 최고가 업데이트
            if self.data.close[0] > self.highest_price:
                self.highest_price = self.data.close[0]

            # 추적 손절매 확인
            trail_stop = self.highest_price * (1 - self.trail_percent)

            if self.data.close[0] < trail_stop:
                self.close()
```

## 10.6 실전 구현

이번 챕터의 코드에서는 다음을 구현합니다:

1. **고정 비율 손절매/익절매**: 2% 손절, 4% 익절
2. **ATR 기반 손절매**: 2×ATR 손절매
3. **추적 손절매**: 고점에서 5% 아래 추적
4. **손절매 없는 전략과 비교**
5. **성과 분석**: 승률, 손익비, 최대 낙폭

## 10.7 기대 결과

코드를 실행하면 다음을 확인할 수 있습니다:

1. **손절매 효과**: 최대 낙폭 감소 확인
2. **승률과 손익비**: 각 방법의 승률과 평균 손익
3. **거래 빈도**: 손절매 사용 시 거래 증가
4. **위험 조정 수익**: Sharpe Ratio 개선 여부
5. **손절매 히트맵**: 어느 구간에서 손절이 많이 발생하는가?

## 10.8 리스크 관리 체크리스트

### 10.8.1 거래 전

- [ ] 손절매 가격 결정
- [ ] 익절매 목표 설정
- [ ] 손익비 확인 (최소 1:2)
- [ ] 포지션 크기 계산
- [ ] 최대 손실 금액 확인

### 10.8.2 거래 중

- [ ] 손절매 주문 즉시 설정
- [ ] 감정적 판단 배제
- [ ] 손절매 임의 변경 금지
- [ ] 추적 손절매 업데이트 (해당 시)

### 10.8.3 거래 후

- [ ] 거래 기록 및 분석
- [ ] 손절매 적절성 평가
- [ ] 손익비 달성 여부 확인
- [ ] 개선점 도출

## 10.9 흔한 실수와 대응

### 10.9.1 손절매 이동하기

**문제**: "조금만 더 기다리면..." → 큰 손실

**해결책**:
- 자동 주문 시스템 사용
- 원칙 준수 강조
- 거래 일지 작성

### 10.9.2 너무 가까운 손절매

**문제**: 정상 변동으로 손절 → 거짓 손절

**해결책**:
- ATR 기반 거리 사용
- 변동성 고려
- 백테스팅으로 최적화

### 10.9.3 손절매 없이 거래

**문제**: "이번엔 괜찮아" → 계좌 파산

**해결책**:
- 손절매 필수 규칙화
- 최악의 시나리오 시뮬레이션
- 작은 계좌로 연습

## 10.10 개선 방향

리스크 관리를 더욱 개선하는 방법:

1. **동적 손절매**: 변동성에 따라 손절매 거리 조정
2. **상관관계 고려**: 여러 포지션의 합산 위험 관리
3. **최대 일일 손실**: 하루 최대 손실 도달 시 거래 중단
4. **월간 손실 제한**: 월 손실 한도 설정
5. **심리적 준비**: 손실 시뮬레이션 및 대응 훈련

## 다음 단계

다음 챕터에서는 여러 자산에 분산투자하는 포트폴리오 구성 방법을 배웁니다. 단일 자산 리스크를 넘어 포트폴리오 전체의 위험을 관리하는 방법을 다룹니다.

---

**코드 실행:**
```bash
cd codes
uv run chapter10/01_risk_management.py
```
