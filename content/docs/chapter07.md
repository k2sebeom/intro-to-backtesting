---
title: "Chapter 7: Bollinger Bands 전략"
weight: 7
bookToc: true
---

# Chapter 7: Bollinger Bands 전략

Bollinger Bands는 John Bollinger가 개발한 변동성 기반 기술적 지표입니다. 가격의 표준편차를 이용해 동적으로 변하는 밴드를 형성하며, 과매수/과매도 판단과 변동성 변화를 감지하는 데 사용됩니다.

## 7.1 Bollinger Bands의 구조

### 7.1.1 Bollinger Bands 계산

Bollinger Bands는 세 개의 라인으로 구성됩니다:

**1. 중간 밴드 (Middle Band)**: 단순 이동평균

$$
\text{MB}_t = \text{SMA}_n(P_t)
$$

**2. 상단 밴드 (Upper Band)**: 중간 밴드 + (표준편차 × k)

$$
\text{UB}_t = \text{MB}_t + k \cdot \sigma_n(P_t)
$$

**3. 하단 밴드 (Lower Band)**: 중간 밴드 - (표준편차 × k)

$$
\text{LB}_t = \text{MB}_t - k \cdot \sigma_n(P_t)
$$

여기서:
- $n$은 기간 (일반적으로 20일)
- $k$는 표준편차 배수 (일반적으로 2)
- $\sigma_n(P_t)$는 $n$ 기간 동안의 가격 표준편차

### 7.1.2 표준편차 계산

$$
\sigma_n(P_t) = \sqrt{\frac{1}{n} \sum_{i=0}^{n-1} (P_{t-i} - \text{MB}_t)^2}
$$

### 7.1.3 Bollinger Bands의 특성

**변동성 측정**:
- 밴드 폭이 넓어짐: 변동성 증가
- 밴드 폭이 좁아짐: 변동성 감소

**가격 포함률**:
- 약 95%의 가격이 ±2σ 밴드 내에 위치 (정규분포 가정)
- 밴드 외부로 가격이 벗어나는 것은 상대적으로 드문 사건

**동적 조정**:
- 시장 변동성에 따라 밴드가 자동으로 확장/축소
- RSI처럼 고정된 임계값(30/70)이 아님

## 7.2 Bollinger Bands 트레이딩 전략

### 7.2.1 밴드 반등 전략 (Mean Reversion)

**기본 개념**: 가격이 밴드 끝에 도달하면 평균으로 회귀한다

**매수 신호**:
- 가격이 하단 밴드에 닿거나 아래로 벗어남
- 과매도 상태로 판단 → 반등 기대

**매도 신호**:
- 가격이 상단 밴드에 닿거나 위로 벗어남
- 과매수 상태로 판단 → 조정 기대

**특징**:
- 횡보장/범위 제한 시장에서 효과적
- 강한 추세에서는 밴드를 따라 계속 움직일 수 있음 (밴드 워킹)

### 7.2.2 밴드 돌파 전략 (Breakout)

**기본 개념**: 변동성 수축 후 확장 시 강한 추세 발생

**매수 신호**:
- 밴드 폭이 좁아진 후 (스퀴즈)
- 가격이 상단 밴드를 상향 돌파
- 상승 추세 시작 신호

**매도 신호**:
- 밴드 폭이 좁아진 후
- 가격이 하단 밴드를 하향 돌파
- 하락 추세 시작 신호

**특징**:
- 추세 시장에서 효과적
- 밴드 워킹(Band Walking) 포착 가능

### 7.2.3 밴드 폭 분석 (Bandwidth)

**Bandwidth 계산**:

$$
\text{Bandwidth}_t = \frac{\text{UB}_t - \text{LB}_t}{\text{MB}_t} \times 100
$$

**해석**:
- 낮은 Bandwidth: 변동성 수축 → 큰 움직임 임박 (스퀴즈)
- 높은 Bandwidth: 변동성 확장 → 추세 진행 중

**스퀴즈 (Squeeze)**:
- Bandwidth가 6개월 최저점에 도달
- 큰 가격 움직임이 곧 발생할 신호
- 방향은 알 수 없음 (돌파 확인 필요)

### 7.2.4 %B 지표

가격의 밴드 내 상대적 위치를 나타냄:

$$
\%B_t = \frac{P_t - \text{LB}_t}{\text{UB}_t - \text{LB}_t}
$$

**해석**:
- %B = 1: 가격이 상단 밴드에 위치
- %B = 0: 가격이 하단 밴드에 위치
- %B = 0.5: 가격이 중간 밴드에 위치
- %B > 1: 가격이 상단 밴드 위에 위치 (매우 강함)
- %B < 0: 가격이 하단 밴드 아래에 위치 (매우 약함)

## 7.3 Bollinger Bands vs. RSI

| 특성 | Bollinger Bands | RSI |
|------|----------------|-----|
| 기반 | 변동성 (표준편차) | 모멘텀 (상승/하락 강도) |
| 임계값 | 동적 (시장 변동성에 따라 변화) | 고정 (30/70) |
| 시장 적응성 | 높음 | 낮음 |
| 추세 포착 | 가능 (밴드 돌파 전략) | 어려움 |
| 변동성 정보 | 제공 (밴드 폭) | 제공 안 함 |
| 사용 난이도 | 상대적으로 복잡 | 단순 |

## 7.4 실전 구현

이번 챕터의 코드에서는 다음을 구현합니다:

1. **밴드 반등 전략**: 하단 밴드 터치 시 매수, 상단 밴드 터치 시 매도
2. **밴드 돌파 전략**: 밴드 스퀴즈 후 돌파 시 추세 추종
3. **%B 기반 전략**: %B 값을 이용한 매매
4. **성과 비교**: Buy & Hold vs. 각 BB 전략

### 7.4.1 Backtrader에서 Bollinger Bands 사용

```python
import backtrader as bt

class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2.0),
    )

    def __init__(self):
        # Bollinger Bands 지표 추가
        self.bband = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

        # 개별 밴드 접근
        self.top_band = self.bband.top
        self.mid_band = self.bband.mid
        self.bot_band = self.bband.bot
```

### 7.4.2 밴드 반등 전략 로직

```python
def next(self):
    if not self.position:
        # 하단 밴드 터치: 매수
        if self.data.close < self.bot_band:
            self.buy()
    else:
        # 상단 밴드 터치: 매도
        if self.data.close > self.top_band:
            self.close()
```

### 7.4.3 밴드 돌파 전략 로직

```python
def next(self):
    # Bandwidth 계산
    bandwidth = (self.top_band - self.bot_band) / self.mid_band

    # 스퀴즈 감지 (낮은 변동성)
    if bandwidth < threshold:
        self.squeeze_detected = True

    if self.squeeze_detected:
        # 상단 밴드 돌파: 매수
        if self.data.close > self.top_band:
            self.buy()
            self.squeeze_detected = False
```

## 7.5 기대 결과

코드를 실행하면 다음을 확인할 수 있습니다:

1. **Bollinger Bands 시각화**: 가격과 함께 상단/중간/하단 밴드 표시
2. **Bandwidth 차트**: 변동성 변화 추이
3. **매매 신호**: 밴드 터치 및 돌파 지점 표시
4. **성과 비교**:
   - Buy & Hold 전략 수익률
   - 밴드 반등 전략 수익률
   - 밴드 돌파 전략 수익률
5. **위험 지표**: Sharpe Ratio, Maximum Drawdown
6. **거래 통계**: 총 거래 횟수, 승률, 평균 손익

## 7.6 분석 포인트

코드를 실행한 후 다음을 분석해보세요:

1. **시장 환경**: 횡보장 vs. 추세 시장에서 어떤 전략이 유리한가?
2. **변동성 변화**: 밴드 폭 변화와 가격 움직임의 관계
3. **거짓 신호**: 밴드 터치 후 반등하지 않는 경우 (밴드 워킹)
4. **돌파 전략**: 스퀴즈 후 돌파가 실제 추세로 이어지는가?
5. **매개변수 민감도**: 기간(20) 및 표준편차 배수(2)에 따른 성과 변화

## 7.7 Bollinger Bands 활용 팁

### 7.7.1 밴드 워킹 (Band Walking)

**현상**: 강한 추세에서 가격이 상단(또는 하단) 밴드를 따라 계속 움직임

**대응**:
- 반등 전략 중단
- 추세 추종 전략으로 전환
- 중간 밴드를 손절 기준으로 사용

### 7.7.2 더블 탑/바텀

- 가격이 상단 밴드를 터치했다가 다시 터치 (더블 탑)
- 두 번째 터치가 첫 번째보다 높지만 밴드를 넘지 못함
- 반전 신호 가능

### 7.7.3 다른 지표와 결합

**추세 확인**:
- Bollinger Bands + 이동평균: 추세 방향 확인
- 중간 밴드가 상승 중이면 상승 추세

**모멘텀 확인**:
- Bollinger Bands + RSI: 신호 신뢰도 증가
- 하단 밴드 터치 + RSI 과매도 → 강한 매수 신호

**거래량 확인**:
- 밴드 돌파 시 거래량 증가하면 신뢰도 상승

## 7.8 개선 방향

Bollinger Bands 전략을 개선할 수 있는 방법:

1. **동적 매개변수**: 시장 변동성에 따라 기간 및 표준편차 배수 조정
2. **스퀴즈 임계값**: 역사적 Bandwidth 분포 분석으로 최적 임계값 결정
3. **포지션 크기**: Bandwidth에 따라 포지션 크기 조절 (낮은 변동성 → 큰 포지션)
4. **손절/익절**: ATR 기반 동적 손절매 설정
5. **다중 시간프레임**: 상위 시간프레임 밴드와 하위 시간프레임 신호 결합

## 다음 단계

다음 챕터에서는 여러 기술적 지표를 결합한 다중 지표 전략을 배웁니다. 이동평균, RSI, Bollinger Bands를 함께 사용하여 신호 신뢰도를 높이는 방법을 다룹니다.

---

**코드 실행:**
```bash
cd codes
uv run chapter07/01_bollinger_bands_strategy.py
```
