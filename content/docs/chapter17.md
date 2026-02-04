---
title: "Chapter 17: 실전 트레이딩 고려사항"
weight: 17
bookToc: true
---

# Chapter 17: 실전 트레이딩 고려사항

## 17.1 소개

백테스트에서 좋은 성과를 보인 전략이 실전에서 실패하는 경우가 많습니다. 이 장에서는 백테스트와 실전 사이의 간극을 줄이기 위한 현실적인 고려사항들을 학습합니다.

## 17.2 슬리피지 (Slippage)

### 17.2.1 슬리피지란?

슬리피지는 예상 체결 가격과 실제 체결 가격의 차이입니다:

$$\text{Slippage} = \text{Actual Fill Price} - \text{Expected Price}$$

**발생 원인**:
- 호가 스프레드 (Bid-Ask Spread)
- 시장 영향 (Market Impact)
- 주문 지연 (Order Latency)
- 부분 체결 (Partial Fills)

### 17.2.2 슬리피지 모델링

**고정 슬리피지**:
- 모든 거래에 고정 금액 또는 비율 적용
- 예: 0.05% 슬리피지

$$\text{Buy Price} = \text{Close Price} \times (1 + 0.0005)$$
$$\text{Sell Price} = \text{Close Price} \times (1 - 0.0005)$$

**변동 슬리피지**:
- 거래량, 변동성, 호가 스프레드에 비례

$$\text{Slippage} = k \times \frac{\text{ATR}}{\text{Price}} \times \frac{\text{Order Size}}{\text{Avg Volume}}$$

여기서 $k$는 조정 상수입니다.

### 17.2.3 Backtrader에서 슬리피지 설정

```python
cerebro.broker.set_slippage_perc(0.0005)  # 0.05% 슬리피지
```

또는 커스텀 슬리피지:

```python
cerebro.broker.set_slippage_fixed(0.05)  # 고정 $0.05
```

## 17.3 거래 비용

### 17.3.1 수수료 (Commission)

**유형**:
- **고정 수수료**: 거래당 고정 금액
- **비율 수수료**: 거래 금액의 일정 비율
- **티어 수수료**: 거래량에 따라 차등 적용

**일반적인 수수료율**:
- 주식: 0.1% - 0.3%
- 선물: $2 - $5 per contract
- 암호화폐: 0.1% - 0.5%

### 17.3.2 세금

**한국 주식**:
- 매도 시 증권거래세: 0.23% (2023년 기준)
- 양도소득세: 대주주 또는 해외주식

**미국 주식**:
- 양도소득세: 매년 또는 매도 시 정산

### 17.3.3 기타 비용

- **데이터 피드 비용**: 실시간 데이터
- **플랫폼 이용료**: 거래 플랫폼 월 사용료
- **대여 비용**: 공매도 시 주식 대여 비용
- **금융 비용**: 신용거래 시 이자

## 17.4 시장 영향 (Market Impact)

### 17.4.1 개념

대량 주문은 시장 가격을 움직입니다:

**영향 정도**:
$$\text{Impact} = \lambda \times \left(\frac{\text{Order Size}}{\text{Daily Volume}}\right)^{\alpha}$$

일반적으로 $\alpha \approx 0.5$ ~ $0.6$

### 17.4.2 영향 최소화 전략

**주문 분할**:
- 대량 주문을 여러 개의 작은 주문으로 분할
- TWAP (Time-Weighted Average Price)
- VWAP (Volume-Weighted Average Price)

**유동성 고려**:
- 거래량이 충분한 종목 선택
- 주문 크기를 일평균 거래량의 1-5% 이내로 제한

## 17.5 주문 유형

### 17.5.1 Market Order (시장가 주문)

즉시 체결되지만 슬리피지 위험 높음.

**장점**: 확실한 체결
**단점**: 불리한 가격에 체결 가능

### 17.5.2 Limit Order (지정가 주문)

특정 가격 이하/이상에서만 체결.

**장점**: 가격 통제
**단점**: 미체결 위험

$$\text{Buy}: \text{Price} \leq \text{Limit Price}$$
$$\text{Sell}: \text{Price} \geq \text{Limit Price}$$

### 17.5.3 Stop Order (손절 주문)

특정 가격에 도달하면 시장가로 전환.

**Stop Loss**:
$$\text{Trigger Price} = \text{Entry Price} \times (1 - \text{Stop Loss \%})$$

### 17.5.4 Stop-Limit Order

Stop 트리거 후 지정가 주문 실행.

**장점**: 가격 통제
**단점**: 갭 발생 시 미체결 위험

## 17.6 체결 가능성 (Fill Probability)

### 17.6.1 체결 지연

백테스트는 즉시 체결을 가정하지만, 실전에서는:
- 주문 전송 지연
- 거래소 매칭 지연
- 네트워크 지연

**모델링**:
```python
# 다음 봉에서 체결
self.buy()  # 현재 close 가격이 아닌 다음 open 가격에 체결
```

### 17.6.2 부분 체결

유동성 부족 시 주문이 부분적으로만 체결될 수 있습니다.

**모델링**:
- 주문 크기를 일평균 거래량의 일정 비율로 제한
- 체결률을 확률적으로 모델링

## 17.7 시장 체제 (Market Regime)

### 17.7.1 체제 유형

**추세 시장 (Trending Market)**:
- 명확한 상승/하락 추세
- 추세 추종 전략 유리

**횡보 시장 (Range-bound Market)**:
- 일정 범위 내 등락
- 평균 회귀 전략 유리

**고변동성 시장 (High Volatility Market)**:
- 급격한 가격 변동
- 리스크 관리 중요

### 17.7.2 체제 감지

**변동성 기반**:
$$\text{Regime} = \begin{cases}
\text{High Volatility} & \text{if } \sigma_t > \mu_\sigma + k \cdot \text{std}(\sigma) \\
\text{Low Volatility} & \text{otherwise}
\end{cases}$$

**추세 강도 기반**:
- ADX (Average Directional Index)
- ADX > 25: 강한 추세
- ADX < 20: 약한 추세 (횡보)

### 17.7.3 적응형 전략

시장 체제에 따라 전략 또는 파라미터를 조정:

```python
if market_regime == 'trending':
    use_trend_following_strategy()
elif market_regime == 'range_bound':
    use_mean_reversion_strategy()
```

## 17.8 실습: 현실적인 백테스트

### 코드 예제

`codes/chapter17/`에서 다음을 구현합니다:

1. **01_slippage_commission.py**: 슬리피지와 수수료 영향 분석
2. **02_order_types.py**: 다양한 주문 유형 비교
3. **03_market_regime.py**: 시장 체제 감지 및 적응형 전략
4. **04_realistic_simulation.py**: 모든 요소를 고려한 현실적 시뮬레이션

### 주요 결과

일반적으로:
- 수수료 0.1% 추가 시 연수익률 2-5% 감소
- 슬리피지 0.05% 추가 시 연수익률 1-3% 감소
- 체결 지연 모델링 시 승률 5-10% 감소

## 17.9 백테스트 vs. 실전 체크리스트

**백테스트에 반영해야 할 요소**:
- [ ] 수수료 (최소 0.1%)
- [ ] 슬리피지 (최소 0.05%)
- [ ] 체결 지연 (다음 봉 open 가격)
- [ ] 주문 크기 제한 (일평균 거래량의 5% 이내)
- [ ] 세금 (해당 시)
- [ ] 갭 (Gap) 고려

**실전에서 추가로 고려**:
- [ ] 시스템 다운타임
- [ ] API 속도 제한
- [ ] 계좌 잔고 부족
- [ ] 규제 변경
- [ ] 거래소 점검

## 17.10 페이퍼 트레이딩

실전 배포 전에 페이퍼 트레이딩(모의 거래) 필수:

**기간**: 최소 3개월
**목적**:
- 시스템 안정성 확인
- 슬리피지 실측
- 심리적 적응

## 17.11 요약

이 장에서는 다음을 학습했습니다:

1. **슬리피지**: 원인, 모델링, 영향
2. **거래 비용**: 수수료, 세금, 기타 비용
3. **시장 영향**: 대량 주문의 가격 영향
4. **주문 유형**: Market, Limit, Stop Order
5. **체결 가능성**: 지연, 부분 체결
6. **시장 체제**: 감지 및 적응형 전략
7. **현실적 시뮬레이션**: 모든 요소를 고려한 백테스트

다음 장에서는 완전한 전략 개발 프로세스를 종합적으로 학습합니다.

## 연습 문제

1. 자신의 전략에 슬리피지 0.05%와 수수료 0.1%를 추가하고, 성과 변화를 측정해보세요.
2. 시장 체제 감지 알고리즘을 구현하고, 체제별 전략 성과를 비교해보세요.
3. 다양한 주문 유형(Market, Limit)을 사용했을 때 체결률과 성과를 비교해보세요.
