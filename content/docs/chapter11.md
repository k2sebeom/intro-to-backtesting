---
title: "Chapter 11: 포트폴리오 구성과 분산투자"
weight: 11
bookToc: true
---

# Chapter 11: 포트폴리오 구성과 분산투자

"계란을 한 바구니에 담지 마라"는 투자의 가장 기본적인 원칙입니다. 이번 챕터에서는 여러 자산에 분산투자하여 위험을 줄이고 안정적인 수익을 추구하는 포트폴리오 구성 방법을 배웁니다.

## 11.1 분산투자의 원리

### 11.1.1 왜 분산투자가 필요한가?

**단일 자산의 위험**:
```
AAPL만 투자 → AAPL 하락 시 전체 손실
```

**포트폴리오의 위험 감소**:
```
AAPL + MSFT + GOOGL + AMZN
→ 한 종목 하락해도 다른 종목이 보완
```

**수학적 원리**: 상관관계가 낮은 자산 결합

$$
\sigma_p^2 = \sum_{i=1}^{n} w_i^2 \sigma_i^2 + \sum_{i=1}^{n}\sum_{j\neq i}^{n} w_i w_j \rho_{ij} \sigma_i \sigma_j
$$

여기서:
- $\sigma_p$: 포트폴리오 표준편차 (위험)
- $w_i$: 자산 $i$의 비중
- $\sigma_i$: 자산 $i$의 표준편차
- $\rho_{ij}$: 자산 $i$와 $j$의 상관계수

### 11.1.2 상관관계의 중요성

**상관계수 ($\rho$)의 의미**:
- $\rho = +1$: 완전 양의 상관 (함께 움직임) → 분산 효과 없음
- $\rho = 0$: 무상관 (독립적) → 분산 효과 있음
- $\rho = -1$: 완전 음의 상관 (반대로 움직임) → 분산 효과 최대

**예시**:
```
AAPL & MSFT: ρ ≈ 0.7 (같은 기술주 섹터)
AAPL & GOLD: ρ ≈ 0.0 (상관 낮음)
주식 & 채권: ρ ≈ -0.3 (음의 상관)
```

### 11.1.3 최적 분산 개수

**Naive Diversification**: 단순 균등 분산

$$
w_i = \frac{1}{N}
$$

**실증 연구 결과**:
- 15-20개 종목: 대부분의 비체계적 위험 제거
- 30개 이상: 추가 분산 효과 미미
- 너무 많으면: 관리 복잡, 수수료 증가

## 11.2 포트폴리오 배분 전략

### 11.2.1 균등 비중 (Equal Weight)

**방법**: 모든 자산에 동일한 비중 투자

$$
w_i = \frac{1}{N}
$$

**장점**:
- 단순하고 명확
- 시가총액 편향 없음
- 소형주 노출 증가

**단점**:
- 리밸런싱 빈번
- 수수료 증가
- 위험 자산에 과다 노출 가능

### 11.2.2 시가총액 비중 (Market Cap Weight)

**방법**: 시가총액에 비례하여 투자

$$
w_i = \frac{\text{Market Cap}_i}{\sum_{j=1}^{N} \text{Market Cap}_j}
$$

**장점**:
- 시장 대표성
- 리밸런싱 적음
- 지수 추종

**단점**:
- 대형주 편향
- 버블 위험
- 소형주 기회 놓침

### 11.2.3 역변동성 비중 (Inverse Volatility)

**방법**: 변동성에 반비례하여 투자

$$
w_i = \frac{1/\sigma_i}{\sum_{j=1}^{N} 1/\sigma_j}
$$

**장점**:
- 위험 균등 배분
- 안정성 증가
- 변동성 큰 자산 축소

**단점**:
- 수익률 희생 가능
- 변동성 변화 추적 필요

### 11.2.4 리스크 패리티 (Risk Parity)

**방법**: 각 자산의 위험 기여도를 동일하게

**위험 기여도 (Risk Contribution)**:

$$
RC_i = w_i \times \frac{\partial \sigma_p}{\partial w_i}
$$

**목표**: $RC_1 = RC_2 = \cdots = RC_N$

**장점**:
- 진정한 위험 분산
- 상관관계 고려
- 균형잡힌 포트폴리오

**단점**:
- 계산 복잡
- 최적화 필요

### 11.2.5 평균-분산 최적화 (Mean-Variance Optimization)

**Markowitz 모형**: 주어진 위험 수준에서 수익 최대화

$$
\max_{w} \quad \mu^T w - \frac{\lambda}{2} w^T \Sigma w
$$

제약 조건:
$$
\begin{align}
\sum_{i=1}^{N} w_i &= 1 \\
w_i &\geq 0 \quad \forall i
\end{align}
$$

여기서:
- $\mu$: 기대 수익률 벡터
- $\Sigma$: 공분산 행렬
- $\lambda$: 위험 회피 계수

**장점**:
- 이론적으로 최적
- 효율적 프론티어 도출

**단점**:
- 과거 데이터 의존
- 추정 오차 민감
- 극단적 비중 가능

## 11.3 리밸런싱 (Rebalancing)

### 11.3.1 리밸런싱의 필요성

**문제**: 시간이 지나면 비중 변화
```
초기: AAPL 25%, MSFT 25%, GOOGL 25%, AMZN 25%
1년 후: AAPL 35%, MSFT 20%, GOOGL 30%, AMZN 15%
```

**목적**:
- 목표 비중 유지
- 위험 통제
- 차익실현 및 손절

### 11.3.2 리밸런싱 방법

**1. 주기적 리밸런싱 (Time-Based)**
```python
if month == 12:  # 연 1회
    rebalance_to_target_weights()
```

**빈도 옵션**:
- 월간: 빈번, 수수료 높음
- 분기: 균형잡힌 선택
- 연간: 수수료 낮음, 편차 클 수 있음

**2. 임계값 기반 리밸런싱 (Threshold-Based)**
```python
if abs(current_weight - target_weight) > 0.05:  # 5% 편차
    rebalance()
```

**3. 혼합 방식**
```python
# 분기마다 확인하되, 5% 편차 시만 리밸런싱
if quarter_end and abs(current_weight - target_weight) > 0.05:
    rebalance()
```

### 11.3.3 리밸런싱의 효과

**수익 향상 메커니즘**:
1. **Buy Low, Sell High**: 하락한 자산 매수, 상승한 자산 매도
2. **변동성 수익**: 변동성에서 추가 수익 추출
3. **위험 통제**: 극단적 포지션 방지

**예시**:
```
자산 A: 50% → 70% (30% 상승)
자산 B: 50% → 30% (30% 하락)

리밸런싱:
- A 일부 매도 (고점 매도)
- B 일부 매수 (저점 매수)
```

## 11.4 Backtrader에서 다중 자산 백테스팅

### 11.4.1 여러 데이터 피드 추가

```python
# 여러 종목 데이터 다운로드
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

for ticker in tickers:
    data = yf.download(ticker, start, end)
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed, name=ticker)
```

### 11.4.2 포트폴리오 전략 구현

```python
class PortfolioStrategy(bt.Strategy):
    def __init__(self):
        # 각 데이터에 대해 지표 생성
        self.mas = {}
        for data in self.datas:
            self.mas[data._name] = bt.indicators.SMA(data.close, period=50)

    def next(self):
        # 균등 비중 계산
        target_weight = 1.0 / len(self.datas)

        for data in self.datas:
            current_value = self.getposition(data).size * data.close[0]
            portfolio_value = self.broker.getvalue()
            current_weight = current_value / portfolio_value

            # 리밸런싱
            if abs(current_weight - target_weight) > 0.05:
                target_value = portfolio_value * target_weight
                target_shares = target_value / data.close[0]
                self.order_target_size(data=data, target=target_shares)
```

## 11.5 실전 구현

이번 챕터의 코드에서는 다음을 구현합니다:

1. **단일 자산 (AAPL)**: 기준선
2. **균등 비중 포트폴리오**: 4개 기술주 균등 배분
3. **역변동성 포트폴리오**: 변동성 역비례 배분
4. **리밸런싱 효과**: 분기별 리밸런싱 vs. 리밸런싱 없음
5. **상관관계 분석**: 포트폴리오 구성 자산 간 상관관계

## 11.6 기대 결과

코드를 실행하면 다음을 확인할 수 있습니다:

1. **위험 감소 효과**: 단일 자산 vs. 포트폴리오 MDD 비교
2. **상관관계 매트릭스**: 자산 간 상관관계 히트맵
3. **효율적 프론티어**: 위험-수익 그래프
4. **리밸런싱 효과**: 분기별 리밸런싱 수익률 기여
5. **Sharpe Ratio 개선**: 위험 조정 수익 향상

## 11.7 포트폴리오 구성 원칙

### 11.7.1 자산 선택

**1. 상관관계 낮은 자산**:
```
✓ 주식 + 채권
✓ 미국 주식 + 해외 주식
✓ 주식 + 원자재
✗ 애플 + 마이크로소프트 (높은 상관)
```

**2. 다양한 자산군**:
- 주식 (성장)
- 채권 (안정)
- 원자재 (인플레이션 헷지)
- 부동산 (대체 투자)

**3. 유동성 고려**:
- 거래량 충분
- 매수/매도 용이

### 11.7.2 비중 결정

**초보자 권장**:
```
주식 60% + 채권 40%
또는
주식 70% + 채권 30%
```

**공격적 투자자**:
```
주식 80% + 대체자산 20%
```

**보수적 투자자**:
```
주식 40% + 채권 50% + 현금 10%
```

### 11.7.3 리밸런싱 규칙

**권장 방식**: 분기별 + 5% 임계값
```python
if quarter_end:
    for asset in portfolio:
        if abs(current_weight - target_weight) > 0.05:
            rebalance(asset)
```

**수수료 고려**:
- 거래 비용 > 리밸런싱 이익이면 skip
- 큰 편차만 조정

## 11.8 고급 포트폴리오 기법

### 11.8.1 팩터 투자 (Factor Investing)

**팩터**: 수익률을 설명하는 체계적 특성
- **Value**: 저평가 주식
- **Size**: 소형주
- **Momentum**: 추세 주식
- **Quality**: 고품질 기업
- **Low Volatility**: 저변동성 주식

### 11.8.2 All Weather Portfolio (레이 달리오)

**구성**:
```
주식 30%
장기 채권 40%
중기 채권 15%
금 7.5%
원자재 7.5%
```

**특징**: 모든 경제 환경에서 안정적

### 11.8.3 60/40 포트폴리오 (전통적)

**구성**:
```
주식 60%
채권 40%
```

**특징**: 검증된 안정성, 간단한 관리

## 11.9 실전 적용 시 주의사항

### 11.9.1 과거 성과 맹신 금지

**문제**: 과거 최적이 미래 최적 아님

**해결**:
- 다양한 기간 테스트
- Walk-forward 분석
- 스트레스 테스트

### 11.9.2 극단적 비중 회피

**문제**: 평균-분산 최적화 시 극단적 배분
```
자산 A: 95%, 자산 B: 5% ← 위험!
```

**해결**:
- 최소/최대 비중 제약
- 정규화 (Regularization)

### 11.9.3 실시간 모니터링

**필수 지표**:
- 포트폴리오 가치
- 각 자산 비중
- 최대 낙폭
- Sharpe Ratio

## 11.10 개선 방향

포트폴리오 전략을 더욱 개선하는 방법:

1. **동적 자산 배분**: 시장 환경에 따라 비중 조정
2. **Black-Litterman 모델**: 주관적 전망과 시장 균형 결합
3. **위험 버짓팅**: 각 자산에 위험 예산 할당
4. **조건부 상관관계**: VIX 높을 때 상관관계 변화 반영
5. **머신러닝 최적화**: 최적 비중 학습

## 다음 단계

Part 3 (리스크와 포트폴리오 관리)를 완료했습니다! 다음 Part 4에서는 백테스팅 성과를 평가하고 비교하는 방법을 다룹니다:

- Chapter 12: 성과 평가 지표
- Chapter 13: 전략 비교와 최적화

지금까지 **언제** 매매하고 (기술적 분석), **얼마나** 투자하며 (포지션 크기), **어떻게** 위험을 관리하고 (손절매), **무엇에** 분산할지 (포트폴리오)를 배웠습니다. 이제 전략을 **어떻게 평가**할지 배울 차례입니다.

---

**코드 실행:**
```bash
cd codes
uv run chapter11/01_portfolio_diversification.py
```
