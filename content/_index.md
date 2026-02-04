---
title: "파이썬으로 배우는 백테스팅 입문"
type: docs
---

# 파이썬으로 배우는 백테스팅 입문

**Introduction to Backtesting with Python**

백테스팅을 통해 트레이딩 전략을 체계적으로 검증하고 최적화하는 방법을 배워봅시다.

## 책 소개

이 책은 Python을 사용하여 금융 데이터를 분석하고, 트레이딩 전략을 백테스팅하는 방법을 다룹니다. 기초부터 시작하여 점진적으로 고급 기법까지 학습합니다.

### 주요 특징

- **실용적 접근**: 모든 장에 실행 가능한 Python 코드 포함
- **균형 잡힌 커버리지**: 기술적 분석, 머신러닝, 포트폴리오 관리
- **한국어로 작성**: 명확한 설명과 예제
- **무료 도구 사용**: yfinance, backtrader, matplotlib 등 오픈소스 라이브러리

## 학습 대상

- 기본적인 Python 지식을 가진 학습자
- 트레이딩 전략을 체계적으로 검증하고 싶은 분
- 데이터 분석과 금융을 결합하고 싶은 개발자
- 퀀트 트레이딩에 관심 있는 모든 분

## 책의 구성

**총 18개 챕터** - 기초부터 실전 적용까지

### Part 1: 기초와 데이터 (Chapters 1-4)
- Chapter 1: 백테스팅 시작하기 ✅
- Chapter 2: 금융 데이터 다운로드와 이해
- Chapter 3: 데이터 전처리와 수익률
- Chapter 4: Backtrader 프레임워크 기초

### Part 2: 기술적 분석 전략 (Chapters 5-8)
- Chapter 5: 이동평균 전략
- Chapter 6: 모멘텀과 변동성 지표
- Chapter 7: 추세 추종과 평균 회귀
- Chapter 8: 다중 지표 결합 전략

### Part 3: 리스크와 포트폴리오 관리 (Chapters 9-11)
- Chapter 9: 리스크 관리
- Chapter 10: 포트폴리오 구성과 리밸런싱
- Chapter 11: 포트폴리오 최적화

### Part 4: 성과 분석 (Chapters 12-13)
- Chapter 12: 성과 지표와 리스크 측정
- Chapter 13: 백테스트 결과 분석과 시각화

### Part 5: 고급 기법 (Chapters 14-16)
- Chapter 14: 과최적화 방지와 검증
- Chapter 15: 머신러닝 기반 전략 (Part 1)
- Chapter 16: 머신러닝 기반 전략 (Part 2)

### Part 6: 실전 적용 (Chapters 17-18)
- Chapter 17: 실전 트레이딩 고려사항
- Chapter 18: 완전한 전략 개발 프로세스

## 시작하기

### 환경 설정

```bash
# uv 패키지 관리자 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 디렉토리로 이동
cd codes

# 의존성 설치
uv sync
```

### 첫 스크립트 실행

```bash
# Chapter 1의 Hello Trading 스크립트 실행
uv run chapter01/01_hello_trading.py
```

## 사전 요구사항

**필요한 것:**
- 기본적인 Python 지식 (변수, 함수, 반복문)
- 금융 시장에 대한 기초적 이해

**필요하지 않은 것:**
- 고급 수학이나 통계학 지식
- 이전 트레이딩 경험
- 유료 소프트웨어나 데이터 구독

## 학습 방법

1. **순서대로 진행**: Chapter 1부터 시작하여 순차적으로 학습
2. **코드 실행**: 각 장의 Python 스크립트를 직접 실행
3. **실험**: 파라미터를 변경하며 결과 관찰
4. **연습 문제**: 각 장 끝의 과제 수행

---

**현재 진행 상황**: Chapter 1 완료 - 백테스팅의 기초를 배웠습니다!

시작할 준비가 되셨나요? [Chapter 1: 백테스팅 시작하기](/docs/chapter01)로 이동하세요.
