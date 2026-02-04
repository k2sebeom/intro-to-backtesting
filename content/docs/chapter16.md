---
title: "Chapter 16: 머신러닝 기반 전략 (2)"
weight: 16
bookToc: true
---

# Chapter 16: 머신러닝 기반 전략 (Part 2)

## 16.1 소개

이전 장에서는 기본적인 머신러닝 모델을 학습했습니다. 이 장에서는 더 고급 기법과 Backtrader와의 통합, 그리고 실전 적용 방법을 학습합니다.

## 16.2 Feature Importance 분석

### 16.2.1 트리 기반 모델의 Feature Importance

랜덤 포레스트와 그래디언트 부스팅은 각 특성의 중요도를 제공합니다:

$$\text{Importance}_i = \frac{\sum_{t \in T} \Delta \text{Gini}_i(t)}{|T|}$$

여기서:
- $T$: 모든 트리 집합
- $\Delta \text{Gini}_i(t)$: 노드 $t$에서 특성 $i$에 의한 불순도 감소

**활용**:
- 중요하지 않은 특성 제거
- 전략 해석
- 새로운 특성 아이디어 발굴

### 16.2.2 Permutation Importance

특성을 무작위로 섞었을 때 성능 하락 정도로 중요도 측정:

1. 기본 모델 성능 측정
2. 특성 하나를 무작위로 섞기
3. 성능 재측정
4. 성능 차이가 중요도

**장점**:
- 모델에 독립적
- 실제 예측 성능 반영

## 16.3 앙상블 기법

### 16.3.1 투표 (Voting)

여러 모델의 예측을 결합:

**하드 투표 (Hard Voting)**:
$$\hat{y} = \text{mode}(h_1(x), h_2(x), \ldots, h_n(x))$$

**소프트 투표 (Soft Voting)**:
$$\hat{y} = \arg\max_c \sum_{i=1}^{n} P_i(y=c|x)$$

### 16.3.2 스태킹 (Stacking)

여러 모델의 예측을 입력으로 하는 메타 모델:

1. 베이스 모델들 학습 (로지스틱 회귀, 랜덤 포레스트, XGBoost)
2. 각 모델의 예측을 새로운 특성으로 사용
3. 메타 모델 학습 (간단한 로지스틱 회귀)

## 16.4 Backtrader와 ML 통합

### 16.4.1 ML Strategy 구조

```python
class MLStrategy(bt.Strategy):
    def __init__(self):
        # 모델 로드
        self.model = load_model('model.pkl')
        self.scaler = load_scaler('scaler.pkl')

    def next(self):
        # 특성 계산
        features = self.calculate_features()

        # 예측
        prediction = self.model.predict(features)

        # 거래 실행
        if prediction == 1 and not self.position:
            self.buy()
        elif prediction == 0 and self.position:
            self.close()
```

### 16.4.2 온라인 학습 vs. 오프라인 학습

**오프라인 학습**:
- 전체 훈련 데이터로 한 번 학습
- 모델 저장 후 백테스트에서 로드
- 간단하지만 적응력 부족

**온라인 학습**:
- 백테스트 중 주기적으로 재학습
- 시장 변화에 적응
- 계산 비용 높음

### 16.4.3 재학습 전략

**고정 윈도우 (Fixed Window)**:
- 항상 최근 N일 데이터로 학습
- 예: 최근 252일(1년)

**확장 윈도우 (Expanding Window)**:
- 처음부터 현재까지 모든 데이터
- 데이터 누적

**재학습 주기**:
- 매일: 계산 비용 높음, 최신 정보 반영
- 매주/매월: 현실적인 선택
- 분기별: 장기 전략

## 16.5 신호 필터링

### 16.5.1 확률 임계값

단순히 클래스를 예측하는 대신 확률을 사용:

```python
prob = model.predict_proba(features)[:, 1]

if prob > 0.6:  # 60% 이상 확신할 때만 매수
    self.buy()
```

**장점**:
- 확신도 기반 거래
- 거래 빈도 조절
- 리스크 관리

### 16.5.2 다중 시그널 결합

여러 모델의 예측을 결합:

```python
lr_prob = lr_model.predict_proba(features)[:, 1]
rf_prob = rf_model.predict_proba(features)[:, 1]

# 평균 확률
avg_prob = (lr_prob + rf_prob) / 2

if avg_prob > 0.6:
    self.buy()
```

## 16.6 리스크 관리와 포지션 사이징

### 16.6.1 Kelly Criterion with ML

ML 모델의 승률과 손익비를 사용한 Kelly Criterion:

$$f^* = \frac{p \times b - q}{b}$$

여기서:
- $p$: 모델의 예상 승률
- $q = 1 - p$
- $b$: 평균 승리 / 평균 손실

### 16.6.2 확률 기반 포지션 사이징

확률에 따라 포지션 크기 조절:

$$\text{Position Size} = \text{Base Size} \times (2 \times \text{Probability} - 1)$$

예: 확률 70% → 포지션 크기 = Base × 0.4

## 16.7 모델 모니터링

### 16.7.1 성능 추적

시간에 따른 모델 성능 변화 모니터링:
- 예측 정확도
- Precision/Recall
- Calibration (예측 확률과 실제 빈도)

### 16.7.2 데이터 드리프트 감지

특성 분포가 훈련 시와 다르게 변하는지 확인:

**통계적 검정**:
- Kolmogorov-Smirnov Test
- Population Stability Index (PSI)

$$PSI = \sum_{i=1}^{n} (\text{Actual}_i - \text{Expected}_i) \times \ln\left(\frac{\text{Actual}_i}{\text{Expected}_i}\right)$$

**해석**:
- PSI < 0.1: 안정적
- PSI 0.1-0.25: 약간 변화
- PSI > 0.25: 재학습 필요

## 16.8 실습: 고급 ML 전략

### 코드 예제

`codes/chapter16/`에서 다음을 구현합니다:

1. **01_feature_importance.py**: Feature importance 분석
2. **02_ensemble_models.py**: 앙상블 기법 (Voting, Stacking)
3. **03_backtrader_ml_integration.py**: Backtrader와 ML 통합
4. **04_online_learning.py**: 재학습 전략 구현

### 주요 워크플로우

1. **모델 학습**: 여러 ML 모델 학습 및 Feature importance 분석
2. **앙상블**: 모델 결합으로 성능 향상
3. **백테스트 통합**: Backtrader에서 ML 모델 사용
4. **재학습**: 주기적 모델 업데이트
5. **성능 모니터링**: 시간에 따른 성능 추적

## 16.9 실전 고려사항

### 16.9.1 과적합 재검토

ML 전략은 과적합 위험이 높습니다:
- **Walk-forward 분석 필수**
- **Out-of-sample 성능 확인**
- **여러 종목/시장에서 테스트**

### 16.9.2 계산 비용

- **훈련 시간**: 재학습 시 얼마나 걸리는가?
- **예측 시간**: 실시간으로 충분히 빠른가?
- **메모리**: 모델 크기가 적절한가?

### 16.9.3 모델 해석 가능성

- **규제 요구사항**: 금융 규제에서 모델 설명 필요할 수 있음
- **리스크 관리**: 모델이 왜 그런 결정을 했는지 이해
- **디버깅**: 문제 발생 시 원인 파악

## 16.10 ML 전략 체크리스트

- [ ] Look-ahead bias 방지 (Time Series Split)
- [ ] 특성 스케일링 (훈련 세트로만)
- [ ] Feature importance 분석
- [ ] Walk-forward 검증
- [ ] 앙상블 기법 고려
- [ ] 확률 임계값 설정
- [ ] 재학습 전략 설계
- [ ] 성능 모니터링 구현
- [ ] 여러 종목/시장에서 테스트
- [ ] 거래 비용 고려

## 16.11 요약

이 장에서는 다음을 학습했습니다:

1. **Feature Importance**: 중요한 특성 식별
2. **앙상블 기법**: Voting, Stacking
3. **Backtrader 통합**: ML 모델을 백테스트에 적용
4. **온라인 학습**: 주기적 재학습
5. **신호 필터링**: 확률 기반 거래
6. **모델 모니터링**: 성능 추적 및 드리프트 감지

다음 장에서는 실전 트레이딩의 현실적인 고려사항을 학습합니다.

## 연습 문제

1. Feature importance를 분석하고, 하위 50% 특성을 제거했을 때 성능 변화를 확인해보세요.
2. 3개 이상의 모델로 앙상블을 구성하고, 단일 모델 대비 성능을 비교해보세요.
3. 재학습 주기를 변경하며 (매주, 매월, 분기) 성능 차이를 분석해보세요.
