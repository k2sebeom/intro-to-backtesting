---
title: "Chapter 15: 머신러닝 기반 전략 (1)"
weight: 15
bookToc: true
---

# Chapter 15: 머신러닝 기반 전략 (Part 1)

## 15.1 소개

전통적인 기술적 분석 전략은 규칙 기반(rule-based)이지만, 머신러닝은 데이터에서 패턴을 자동으로 학습합니다. 이 장에서는 머신러닝을 트레이딩 전략에 적용하는 기초를 학습합니다.

## 15.2 머신러닝과 트레이딩

### 15.2.1 왜 머신러닝인가?

**장점**:
- 복잡한 비선형 패턴 발견
- 다양한 특성(feature) 동시 고려
- 데이터 기반 의사결정
- 자동화된 규칙 생성

**단점**:
- 과적합 위험 높음
- 해석 어려움 (블랙박스)
- 많은 데이터 필요
- 시장 변화에 민감

### 15.2.2 트레이딩 문제의 유형

1. **분류 (Classification)**: 상승/하락 예측
   - 목표: 다음 기간에 가격이 오를지 내릴지 예측
   - 출력: 0 (하락) 또는 1 (상승)

2. **회귀 (Regression)**: 수익률 크기 예측
   - 목표: 다음 기간의 수익률 예측
   - 출력: 연속적인 수익률 값

3. **강화학습 (Reinforcement Learning)**: 최적 행동 학습
   - 목표: 보상을 최대화하는 매매 행동 학습
   - 출력: 매수/매도/보유 행동

이 장에서는 **분류 문제**에 집중합니다.

## 15.3 특성 엔지니어링 (Feature Engineering)

### 15.3.1 기술적 지표를 특성으로

기술적 지표들을 머신러닝 모델의 입력 특성으로 사용합니다:

**가격 기반 특성**:
- 수익률: $R_t = \frac{P_t - P_{t-1}}{P_{t-1}}$
- 이동평균: SMA, EMA
- 상대적 위치: $\frac{P_t - \text{SMA}_t}{\text{SMA}_t}$

**모멘텀 지표**:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- ROC (Rate of Change)

**변동성 지표**:
- Bollinger Bands
- ATR (Average True Range)
- 표준편차

**거래량 지표**:
- 거래량 이동평균
- OBV (On-Balance Volume)
- 거래량 변화율

### 15.3.2 래그 특성 (Lag Features)

과거 값들을 특성으로 사용:

$$X_t = [R_{t-1}, R_{t-2}, \ldots, R_{t-n}]$$

예: 지난 5일간의 수익률을 특성으로 사용

### 15.3.3 타겟 레이블 생성

분류 문제를 위한 레이블 생성:

**이진 분류**:
$$y_t = \begin{cases}
1 & \text{if } R_{t+1} > 0 \\
0 & \text{if } R_{t+1} \leq 0
\end{cases}$$

**임계값 기반**:
$$y_t = \begin{cases}
1 & \text{if } R_{t+1} > \theta \\
0 & \text{if } R_{t+1} \leq \theta
\end{cases}$$

여기서 $\theta$는 임계값(예: 0.01 = 1%)

### 15.3.4 특성 스케일링

머신러닝 모델은 특성의 스케일에 민감합니다:

**표준화 (Standardization)**:
$$X_{\text{scaled}} = \frac{X - \mu}{\sigma}$$

**정규화 (Normalization)**:
$$X_{\text{scaled}} = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$$

**주의**: 훈련 세트의 통계만 사용해야 합니다 (Look-ahead bias 방지)!

## 15.4 시계열 데이터 처리

### 15.4.1 시계열 분할의 특수성

일반적인 K-Fold Cross-Validation은 사용할 수 없습니다!

**잘못된 방법**:
```
[Train][Train][Test][Train][Train]  ← 미래가 과거를 학습
```

**올바른 방법 (Time Series Split)**:
```
[Train][Test]
[Train][Train][Test]
[Train][Train][Train][Test]
```

### 15.4.2 Look-Ahead Bias 방지

**절대 하지 말아야 할 것**:
- 전체 데이터로 스케일링 후 분할
- 미래 데이터로 특성 계산
- 전체 데이터로 특성 선택

**올바른 방법**:
- 훈련 세트로만 스케일러 학습
- 각 시점에서 과거 데이터만 사용
- 훈련 세트로만 특성 선택

## 15.5 머신러닝 모델

### 15.5.1 로지스틱 회귀 (Logistic Regression)

가장 단순한 분류 모델:

$$P(y=1|X) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 X_1 + \ldots + \beta_n X_n)}}$$

**장점**:
- 해석 가능
- 빠른 학습
- 과적합 위험 낮음

**단점**:
- 선형 관계만 모델링
- 복잡한 패턴 포착 어려움

### 15.5.2 랜덤 포레스트 (Random Forest)

여러 결정 트리의 앙상블:

**장점**:
- 비선형 패턴 학습
- Feature importance 제공
- 과적합에 강함
- 하이퍼파라미터에 덜 민감

**단점**:
- 해석 어려움
- 학습 시간 오래 걸림
- 메모리 많이 사용

**주요 하이퍼파라미터**:
- `n_estimators`: 트리 개수 (100-500)
- `max_depth`: 트리 깊이 (5-20)
- `min_samples_split`: 분할 최소 샘플 수 (2-10)

### 15.5.3 그래디언트 부스팅 (Gradient Boosting)

순차적으로 약한 학습기를 결합:

**장점**:
- 높은 예측 정확도
- Feature importance 제공
- 결측치 처리 가능

**단점**:
- 과적합 위험
- 하이퍼파라미터 튜닝 필요
- 학습 시간 김

**라이브러리**:
- XGBoost
- LightGBM
- CatBoost

## 15.6 모델 평가

### 15.6.1 분류 성과 지표

**정확도 (Accuracy)**:
$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

**주의**: 클래스 불균형 시 부적절!

**정밀도 (Precision)**:
$$\text{Precision} = \frac{TP}{TP + FP}$$

**재현율 (Recall)**:
$$\text{Recall} = \frac{TP}{TP + FN}$$

**F1 Score**:
$$F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 15.6.2 ROC 곡선과 AUC

ROC (Receiver Operating Characteristic) 곡선은 임계값에 따른 성능 변화를 보여줍니다.

**AUC (Area Under Curve)**:
- AUC = 0.5: 랜덤 추측
- AUC = 0.6-0.7: 약간 유용
- AUC = 0.7-0.8: 괜찮음
- AUC > 0.8: 좋음

## 15.7 과적합 방지

### 15.7.1 교차 검증

Time Series Split으로 교차 검증:
- 여러 훈련/테스트 기간에서 평가
- 평균 성능으로 모델 선택

### 15.7.2 정규화 (Regularization)

**L1 정규화 (Lasso)**:
$$\text{Loss} = \text{MSE} + \alpha \sum_{i=1}^{n} |\beta_i|$$

**L2 정규화 (Ridge)**:
$$\text{Loss} = \text{MSE} + \alpha \sum_{i=1}^{n} \beta_i^2$$

### 15.7.3 조기 종료 (Early Stopping)

검증 세트 성능이 개선되지 않으면 학습 중단.

## 15.8 실습: ML 기반 트레이딩 전략

### 코드 예제

`codes/chapter15/`에서 다음을 구현합니다:

1. **01_feature_engineering.py**: 기술적 지표를 특성으로 변환
2. **02_logistic_regression_strategy.py**: 로지스틱 회귀 기반 전략
3. **03_random_forest_strategy.py**: 랜덤 포레스트 기반 전략
4. **04_model_evaluation.py**: 모델 성능 평가 및 비교

### 주요 워크플로우

1. **데이터 준비**: OHLCV 데이터 다운로드
2. **특성 생성**: 기술적 지표 계산
3. **레이블 생성**: 다음 기간 수익률로 상승/하락 레이블
4. **데이터 분할**: Time Series Split
5. **특성 스케일링**: 훈련 세트로 학습
6. **모델 학습**: 로지스틱 회귀 / 랜덤 포레스트
7. **예측**: 테스트 세트에서 예측
8. **백테스트**: Backtrader로 실제 성과 측정

## 15.9 요약

이 장에서는 다음을 학습했습니다:

1. **머신러닝과 트레이딩**: 분류 문제로 정식화
2. **특성 엔지니어링**: 기술적 지표를 ML 특성으로 변환
3. **시계열 데이터 처리**: Look-ahead bias 방지
4. **ML 모델**: 로지스틱 회귀, 랜덤 포레스트
5. **모델 평가**: 정확도, 정밀도, 재현율, AUC
6. **과적합 방지**: 교차 검증, 정규화

다음 장에서는 더 고급 머신러닝 기법과 Backtrader 통합을 학습합니다.

## 연습 문제

1. 자신만의 특성을 만들어보세요 (예: 가격/거래량 비율, 변동성 비율 등).
2. 로지스틱 회귀와 랜덤 포레스트의 성능을 비교해보세요.
3. 다른 레이블 생성 방법을 시도해보세요 (예: 2% 이상 상승만 1로 레이블링).
