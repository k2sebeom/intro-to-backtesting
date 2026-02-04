---
title: "Chapter 12: 성과 지표와 리스크 측정"
weight: 12
bookToc: true
---

# Chapter 12: 성과 지표와 리스크 측정

## 12.1 소개

백테스팅 전략의 성과를 평가하는 것은 매우 중요합니다. 단순히 수익률만 보는 것이 아니라, 얼마나 큰 리스크를 감수했는지, 수익의 일관성은 어떠한지 등을 종합적으로 평가해야 합니다.

이 장에서는 다양한 성과 지표와 리스크 측정 방법을 학습하고, 이를 Python으로 계산하는 방법을 알아봅니다.

## 12.2 수익률 지표

### 12.2.1 총 수익률 (Total Return)

총 수익률은 투자 기간 동안의 전체 수익률을 나타냅니다:

$$TR = \frac{V_{\text{end}} - V_{\text{start}}}{V_{\text{start}}}$$

여기서:
- $V_{\text{end}}$: 기말 포트폴리오 가치
- $V_{\text{start}}$: 기초 포트폴리오 가치

### 12.2.2 연환산 수익률 (Annualized Return)

서로 다른 기간의 전략을 비교하기 위해서는 연환산 수익률을 사용합니다:

$$AR = \left(1 + TR\right)^{\frac{365}{n}} - 1$$

여기서 $n$은 투자 일수입니다.

### 12.2.3 복합 연평균 성장률 (CAGR)

CAGR은 연환산 수익률과 유사하지만, 복리 효과를 고려합니다:

$$CAGR = \left(\frac{V_{\text{end}}}{V_{\text{start}}}\right)^{\frac{1}{T}} - 1$$

여기서 $T$는 투자 연수입니다.

## 12.3 리스크 지표

### 12.3.1 변동성 (Volatility)

변동성은 수익률의 표준편차로 측정됩니다:

$$\sigma = \sqrt{\frac{1}{n-1} \sum_{i=1}^{n} (r_i - \bar{r})^2}$$

연환산 변동성:

$$\sigma_{\text{annual}} = \sigma_{\text{daily}} \times \sqrt{252}$$

### 12.3.2 최대 낙폭 (Maximum Drawdown, MDD)

최대 낙폭은 피크에서 저점까지의 최대 하락폭을 나타냅니다:

$$MDD = \max_{t} \left( \frac{\text{Peak}_t - \text{Valley}_t}{\text{Peak}_t} \right)$$

최대 낙폭은 전략의 최악의 손실 시나리오를 보여줍니다.

### 12.3.3 낙폭 지속 기간 (Drawdown Duration)

최대 낙폭에서 회복하는 데 걸린 시간도 중요한 지표입니다.

## 12.4 리스크 조정 수익률

### 12.4.1 샤프 비율 (Sharpe Ratio)

샤프 비율은 위험 대비 초과 수익률을 측정합니다:

$$\text{Sharpe Ratio} = \frac{E[R_p - R_f]}{\sigma_p}$$

여기서:
- $R_p$: 포트폴리오 수익률
- $R_f$: 무위험 수익률 (일반적으로 국채 수익률)
- $\sigma_p$: 포트폴리오 수익률의 표준편차

**해석**:
- Sharpe Ratio > 1: 양호
- Sharpe Ratio > 2: 매우 좋음
- Sharpe Ratio > 3: 우수

### 12.4.2 소르티노 비율 (Sortino Ratio)

소르티노 비율은 하방 리스크만을 고려합니다:

$$\text{Sortino Ratio} = \frac{E[R_p - R_f]}{\sigma_{\text{downside}}}$$

여기서 $\sigma_{\text{downside}}$는 목표 수익률 이하의 수익률에 대한 표준편차입니다:

$$\sigma_{\text{downside}} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} \min(0, r_i - \text{MAR})^2}$$

MAR (Minimum Acceptable Return)은 보통 0 또는 무위험 수익률을 사용합니다.

### 12.4.3 칼마 비율 (Calmar Ratio)

칼마 비율은 연환산 수익률을 최대 낙폭으로 나눈 값입니다:

$$\text{Calmar Ratio} = \frac{CAGR}{|MDD|}$$

최대 손실 대비 수익률을 평가합니다.

## 12.5 거래 통계

### 12.5.1 승률 (Win Rate)

$$\text{Win Rate} = \frac{\text{Number of Winning Trades}}{\text{Total Number of Trades}}$$

### 12.5.2 Profit Factor

$$\text{Profit Factor} = \frac{\text{Total Profit from Winning Trades}}{|\text{Total Loss from Losing Trades}|}$$

Profit Factor > 1이면 수익성 있는 전략입니다.

### 12.5.3 기댓값 (Expectancy)

거래당 평균 기댓값:

$$E = (P_w \times \text{Avg Win}) - (P_l \times \text{Avg Loss})$$

여기서:
- $P_w$: 승률
- $P_l$: 패율 $(1 - P_w)$

### 12.5.4 평균 거래 수익률

$$\text{Avg Trade Return} = \frac{\sum \text{Trade Returns}}{\text{Total Number of Trades}}$$

## 12.6 벤치마크 대비 성과

### 12.6.1 알파 (Alpha)

알파는 벤치마크 대비 초과 수익률을 나타냅니다:

$$\alpha = R_p - [R_f + \beta \times (R_m - R_f)]$$

여기서:
- $R_m$: 시장 수익률
- $\beta$: 시스템적 리스크

### 12.6.2 베타 (Beta)

베타는 시장 대비 민감도를 나타냅니다:

$$\beta = \frac{\text{Cov}(R_p, R_m)}{\text{Var}(R_m)}$$

## 12.7 실습: 종합 성과 분석 대시보드

이제 실제로 이러한 지표들을 계산하고 분석하는 코드를 작성해보겠습니다.

### 코드 예제

`codes/chapter12/01_performance_metrics.py`에서는 다음을 구현합니다:

1. **기본 수익률 지표**: Total Return, Annualized Return, CAGR
2. **리스크 지표**: Volatility, Maximum Drawdown, Drawdown Duration
3. **리스크 조정 수익률**: Sharpe, Sortino, Calmar Ratio
4. **거래 통계**: Win Rate, Profit Factor, Expectancy
5. **종합 대시보드**: 모든 지표를 한눈에 볼 수 있는 리포트

### 주요 결과 해석

성과 분석 시 주의할 점:

1. **단일 지표에 의존하지 말 것**: 여러 지표를 종합적으로 고려해야 합니다.
2. **샤프 비율의 한계**: 수익률이 정규분포를 따른다고 가정합니다.
3. **최대 낙폭**: 과거 최악의 시나리오가 미래에도 최악의 시나리오는 아닙니다.
4. **승률 vs. 손익비**: 높은 승률보다 높은 Profit Factor가 더 중요할 수 있습니다.

## 12.8 성과 지표 선택 가이드

| 목적 | 추천 지표 |
|------|----------|
| 절대 수익 평가 | CAGR, Total Return |
| 리스크 평가 | Maximum Drawdown, Volatility |
| 리스크 대비 수익 | Sharpe Ratio, Calmar Ratio |
| 하방 리스크 중점 | Sortino Ratio, Maximum Drawdown |
| 거래 효율성 | Win Rate, Profit Factor, Expectancy |
| 시장 대비 성과 | Alpha, Beta, Information Ratio |

## 12.9 요약

이 장에서는 다음을 학습했습니다:

1. **수익률 지표**: 총 수익률, 연환산 수익률, CAGR
2. **리스크 지표**: 변동성, 최대 낙폭, 낙폭 지속 기간
3. **리스크 조정 수익률**: Sharpe, Sortino, Calmar Ratio
4. **거래 통계**: 승률, Profit Factor, 기댓값
5. **벤치마크 대비 성과**: Alpha, Beta

다음 장에서는 이러한 지표들을 시각화하고, 백테스트 결과를 종합적으로 분석하는 방법을 학습합니다.

## 연습 문제

1. 승률이 40%인 전략과 60%인 전략 중 어느 것이 더 나을까요? (힌트: Profit Factor 고려)
2. Sharpe Ratio가 높지만 Maximum Drawdown도 큰 전략과, Sharpe Ratio는 낮지만 MDD도 작은 전략 중 어느 것을 선택하시겠습니까?
3. 실제 주식 전략의 Sharpe Ratio를 계산하고, 1 이상인지 확인해보세요.
