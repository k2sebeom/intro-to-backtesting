---
title: "Chapter 9: 포지션 크기 결정"
weight: 9
bookToc: true
---

# Chapter 9: 포지션 크기 결정

아무리 좋은 전략이라도 포지션 크기를 잘못 결정하면 큰 손실을 입거나 기회를 놓칠 수 있습니다. 이번 챕터에서는 계좌 크기와 위험 허용도에 맞게 포지션 크기를 결정하는 다양한 방법을 배웁니다.

## 9.1 포지션 크기의 중요성

### 9.1.1 포지션 크기가 중요한 이유

**1. 위험 관리의 핵심**
- 너무 큰 포지션: 한 번의 손실로 계좌 파산 가능
- 너무 작은 포지션: 수익 기회 미활용

**2. 복리 효과**
- 일정한 포지션 크기 유지 시 복리 효과 극대화
- 계좌 크기에 비례하여 포지션 조정

**3. 심리적 안정**
- 적절한 포지션 크기로 감정적 의사결정 방지
- 손실을 견딜 수 있는 수준 유지

### 9.1.2 포지션 크기의 기본 원칙

**원칙 1: 한 번의 거래로 전체 계좌의 1-2% 이상 위험에 노출하지 않기**
```
예: 계좌 $10,000
→ 거래당 최대 위험: $100-$200
```

**원칙 2: 계좌 크기에 비례하여 포지션 조정**
```
계좌 $10,000 → 포지션 $9,500
계좌 $20,000 → 포지션 $19,000
```

**원칙 3: 변동성에 따라 포지션 크기 조정**
```
고변동성 자산 → 작은 포지션
저변동성 자산 → 큰 포지션
```

## 9.2 포지션 크기 결정 방법

### 9.2.1 고정 금액 (Fixed Amount)

**방법**: 매번 동일한 금액 투자

```python
position_size = fixed_amount  # 예: $5,000
shares = position_size / current_price
```

**장점**:
- 단순하고 이해하기 쉬움
- 구현 간단

**단점**:
- 계좌 크기 변화 무시
- 복리 효과 없음
- 위험 관리 어려움

**적용 사례**: 초보자, 소액 계좌

### 9.2.2 고정 비율 (Fixed Percentage)

**방법**: 계좌 크기의 일정 비율 투자

```python
position_size = account_value * percentage  # 예: 95%
shares = position_size / current_price
```

**장점**:
- 계좌 크기에 비례하여 자동 조정
- 복리 효과 발생
- 구현 간단

**단점**:
- 변동성 고려 없음
- 연속 손실 시 빠른 계좌 감소

**적용 사례**: 가장 일반적인 방법, 장기 투자

### 9.2.3 고정 위험 (Fixed Risk)

**방법**: 거래당 위험을 계좌의 일정 비율로 제한

$$
\text{Position Size} = \frac{\text{Account Value} \times \text{Risk \%}}{\text{Entry Price} - \text{Stop Loss Price}}
$$

**예시**:
```
계좌: $10,000
위험 허용: 1% → $100
진입가: $100
손절가: $95
손실폭: $5

포지션 크기 = $100 / $5 = 20주
투자금액 = 20주 × $100 = $2,000
```

**장점**:
- 명확한 위험 관리
- 손실을 정확히 제어
- 변동성 자동 반영

**단점**:
- 손절매 필수
- 계산 복잡

**적용 사례**: 전문 트레이더, 단기 매매

### 9.2.4 켈리 기준 (Kelly Criterion)

**방법**: 최적 성장률을 위한 수학적 공식

$$
f^* = \frac{p \cdot (b + 1) - 1}{b}
$$

또는 더 간단하게:

$$
f^* = \frac{W - (1 - W)}{R}
$$

여기서:
- $f^*$: 투자할 자본 비율
- $W$: 승률 (Win Rate)
- $R$: 평균 승리/평균 손실 비율 (Reward/Risk Ratio)
- $p$: 승률
- $b$: 배당률 (net odds)

**예시**:
```
승률 (W) = 60% = 0.6
평균 수익 = $300
평균 손실 = $150
R = $300 / $150 = 2

Kelly % = (0.6 - (1-0.6)) / 2 = (0.6 - 0.4) / 2 = 0.1 = 10%
```

**장점**:
- 이론적으로 최적의 성장률
- 장기적으로 복리 최대화

**단점**:
- 실전에서는 너무 공격적
- 승률과 손익비 정확한 추정 필요
- 변동성이 큼

**개선: Half-Kelly 또는 Quarter-Kelly**
```python
kelly_percentage = (win_rate - (1 - win_rate)) / reward_risk_ratio
safe_percentage = kelly_percentage * 0.5  # Half-Kelly
```

**적용 사례**: 경험 많은 트레이더, 안정적인 전략

### 9.2.5 변동성 기반 (Volatility-Based)

**방법**: ATR(Average True Range)를 사용한 변동성 고려

$$
\text{Position Size} = \frac{\text{Account Value} \times \text{Risk \%}}{\text{ATR} \times \text{ATR Multiplier}}
$$

**예시**:
```
계좌: $10,000
위험 허용: 1% → $100
ATR(14) = $5
ATR 배수 = 2 (손절매 = 진입가 - 2×ATR)

포지션 크기 = $100 / ($5 × 2) = 10주
```

**장점**:
- 시장 변동성 자동 반영
- 동적 위험 조정
- 다양한 자산 비교 가능

**단점**:
- ATR 계산 필요
- 구현 복잡

**적용 사례**: 다양한 자산 거래, 변동성 큰 시장

## 9.3 Backtrader에서 포지션 크기 관리

### 9.3.1 Sizer 클래스

Backtrader는 `Sizer` 클래스를 통해 포지션 크기를 관리합니다:

```python
# 고정 비율
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

# 고정 수량
cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# 고정 위험 (커스텀 구현 필요)
cerebro.addsizer(FixedRiskSizer, risk_percent=1.0)
```

### 9.3.2 커스텀 Sizer 구현

```python
class FixedRiskSizer(bt.Sizer):
    params = (
        ('risk_percent', 1.0),  # 위험 비율 (%)
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            # 계좌 크기
            account_value = self.broker.getvalue()

            # 위험 금액
            risk_amount = account_value * (self.params.risk_percent / 100)

            # 진입가와 손절가 (전략에서 설정)
            entry_price = data.close[0]
            stop_loss = self.strategy.stop_loss_price

            # 주당 위험
            risk_per_share = entry_price - stop_loss

            if risk_per_share > 0:
                # 포지션 크기 계산
                position_size = risk_amount / risk_per_share
                return int(position_size)

        return 0
```

## 9.4 실전 구현

이번 챕터의 코드에서는 다음을 구현합니다:

1. **고정 비율 전략**: 95% 투자
2. **고정 위험 전략**: 거래당 1% 위험
3. **켈리 기준 전략**: Half-Kelly 방법
4. **변동성 기반 전략**: ATR 기반 포지션 크기
5. **성과 비교**: 각 방법의 수익률, 위험, Sharpe Ratio

## 9.5 기대 결과

코드를 실행하면 다음을 확인할 수 있습니다:

1. **계좌 성장 곡선**: 각 포지션 크기 방법별 계좌 가치 변화
2. **포지션 크기 변화**: 시간에 따른 포지션 크기 조정
3. **위험 지표**:
   - 최대 낙폭 (Maximum Drawdown)
   - 변동성 (Volatility)
   - Sharpe Ratio
4. **거래 통계**: 평균 포지션 크기, 최대/최소 포지션
5. **비교 분석**: 어떤 방법이 가장 안정적이고 수익성이 높은가?

## 9.6 분석 포인트

코드를 실행한 후 다음을 분석해보세요:

1. **위험 조정 수익**: 높은 수익률보다 Sharpe Ratio가 중요
2. **최대 낙폭**: 감내할 수 있는 수준인가?
3. **계좌 성장 안정성**: 부드러운 성장 vs. 급등락
4. **포지션 크기 변화**: 시장 변동성에 적절히 반응하는가?
5. **복리 효과**: 고정 비율 방법의 복리 효과 확인

## 9.7 포지션 크기 결정 시 주의사항

### 9.7.1 과도한 레버리지 피하기

**문제**: 켈리 기준이 20%를 제안해도 너무 공격적

**해결책**: Half-Kelly 또는 Quarter-Kelly 사용
```python
kelly = 0.20
safe_kelly = kelly * 0.5  # 10%
```

### 9.7.2 연속 손실 대비

**문제**: 연속 손실 시 계좌 급감

**해결책**: 최대 손실 제한 설정
```python
if consecutive_losses >= 3:
    position_size *= 0.5  # 포지션 크기 절반으로 축소
```

### 9.7.3 승률과 손익비 변화

**문제**: 과거 데이터 기반 켈리 계산이 미래에 맞지 않음

**해결책**:
- 보수적 추정 사용
- 주기적으로 재계산
- 실시간 성과 모니터링

### 9.7.4 유동성 고려

**문제**: 계산된 포지션 크기가 시장 유동성 초과

**해결책**:
```python
daily_volume = data.volume[0]
max_position = daily_volume * 0.01  # 일일 거래량의 1%
position_size = min(calculated_size, max_position)
```

## 9.8 실전 적용 가이드

### 9.8.1 초보자 권장 설정

```python
# 보수적 접근
position_size = account_value * 0.50  # 50% 투자
risk_per_trade = account_value * 0.01  # 1% 위험
```

### 9.8.2 중급자 권장 설정

```python
# 균형 잡힌 접근
position_size = account_value * 0.80  # 80% 투자
risk_per_trade = account_value * 0.015  # 1.5% 위험
```

### 9.8.3 전문가 권장 설정

```python
# 공격적 접근 (Half-Kelly)
kelly = (win_rate - (1 - win_rate)) / reward_risk_ratio
position_size = account_value * kelly * 0.5
risk_per_trade = account_value * 0.02  # 2% 위험
```

## 9.9 포지션 크기 최적화

### 9.9.1 백테스팅을 통한 최적화

다양한 포지션 크기로 백테스트:
```python
for position_percent in [0.25, 0.50, 0.75, 0.95]:
    # 백테스트 실행
    # Sharpe Ratio 및 Max Drawdown 비교
```

**최적화 목표**:
- 최대 Sharpe Ratio
- 최소 Drawdown
- 목표 수익률 달성

### 9.9.2 동적 포지션 조정

시장 환경에 따라 포지션 크기 조정:
```python
if market_volatility > threshold:
    position_size *= 0.7  # 변동성 높을 때 축소
else:
    position_size *= 1.0  # 정상
```

## 9.10 개선 방향

포지션 크기 전략을 더욱 개선하는 방법:

1. **다중 자산 포트폴리오**: 자산별 최적 포지션 배분
2. **상관관계 고려**: 상관관계 높은 자산은 합산 위험 계산
3. **시장 체제 인식**: 상승장/하락장/횡보장별 다른 설정
4. **머신러닝 통합**: 최적 포지션 크기 학습
5. **실시간 조정**: 실시간 변동성 및 위험에 따라 동적 조정

## 다음 단계

다음 챕터에서는 손절매(Stop Loss)와 익절매(Take Profit)를 포함한 종합적인 리스크 관리 기법을 배웁니다. 포지션 크기 결정만큼이나 중요한 것이 언제 손실을 확정하고 이익을 실현할 것인가입니다.

---

**코드 실행:**
```bash
cd codes
uv run chapter09/01_position_sizing.py
```
