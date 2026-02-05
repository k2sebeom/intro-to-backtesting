"""
Chapter 1: 백테스팅 시작하기
첫 번째 스크립트 - Hello Trading

이 스크립트는 다음을 수행합니다:
1. 개발 환경 검증 (필수 라이브러리 확인)
2. 간단한 수익률 계산
3. 기본 통계 분석
4. 시각화 생성
"""

import sys
import os
from pathlib import Path

# 환경 검증을 위한 import
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI 없이 차트 생성
import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt

plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def print_header():
    """프로그램 헤더 출력"""
    print("=" * 42)
    print("   파이썬으로 배우는 백테스팅 입문")
    print("   Chapter 1: 백테스팅 시작하기")
    print("=" * 42)
    print()


def verify_environment():
    """개발 환경 검증 - 모든 필수 라이브러리 확인"""
    print("환경 검증 중...")

    # Python 버전
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✓ Python {python_version}")

    # 라이브러리 버전
    print(f"✓ pandas {pd.__version__}")
    print(f"✓ numpy {np.__version__}")
    print(f"✓ matplotlib {matplotlib.__version__}")
    print(f"✓ yfinance {yf.__version__}")
    print(f"✓ backtrader {bt.__version__}")

    print("\n모든 라이브러리가 정상적으로 설치되었습니다!\n")


def calculate_simple_returns():
    """간단한 수익률 계산 예제"""
    print("=" * 42)
    print("간단한 수익률 계산 예제")
    print("=" * 42)
    print()

    # 가상의 주가 데이터
    prices = np.array([100.0, 105.0, 103.0, 108.0, 112.0])

    print("가상의 주가 데이터:")
    print(f"Day 1: ${prices[0]:.2f}")

    # 일일 수익률 계산
    returns = np.diff(prices) / prices[:-1]

    for i, (price, ret) in enumerate(zip(prices[1:], returns), start=2):
        print(f"Day {i}: ${price:.2f} (수익률: {ret:+.2%})")

    return prices, returns


def calculate_statistics(returns):
    """기본 통계 계산"""
    print("\n" + "=" * 42)
    print("통계 분석")
    print("=" * 42)

    mean_return = np.mean(returns)
    std_return = np.std(returns)
    max_return = np.max(returns)
    min_return = np.min(returns)

    print(f"평균 일일 수익률: {mean_return:.2%}")
    print(f"수익률 표준편차: {std_return:.2%}")
    print(f"최대 일일 수익률: {max_return:+.2%}")
    print(f"최소 일일 수익률: {min_return:+.2%}")

    # 누적 수익률 계산
    cumulative_return = np.prod(1 + returns) - 1
    print(f"총 누적 수익률: {cumulative_return:.2%}")

    return mean_return, std_return, max_return, min_return, cumulative_return


def create_visualization(prices, returns):
    """시각화 생성"""
    # 한글 폰트 설정 (matplotlib에서 한글 표시)
    plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # 누적 수익률 계산
    cumulative_returns = np.cumprod(1 + returns) - 1
    cumulative_returns = np.insert(cumulative_returns, 0, 0)  # 첫날은 0%

    # 그림 생성
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Chapter 1: Hello Trading - Analysis', fontsize=16, fontweight='bold')

    days = np.arange(1, len(prices) + 1)

    # 1. 주가 추이
    axes[0].plot(days, prices, marker='o', linewidth=2, markersize=8, color='#2E86AB')
    axes[0].set_title('Price Trend', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Day')
    axes[0].set_ylabel('Price ($)')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xticks(days)

    # 2. 일일 수익률
    colors = ['green' if r >= 0 else 'red' for r in returns]
    axes[1].bar(days[1:], returns * 100, color=colors, alpha=0.7, edgecolor='black')
    axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1].set_title('Daily Returns', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Day')
    axes[1].set_ylabel('Return (%)')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].set_xticks(days[1:])

    # 3. 누적 수익률
    axes[2].plot(days, cumulative_returns * 100, marker='o', linewidth=2,
                 markersize=8, color='#A23B72')
    axes[2].fill_between(days, 0, cumulative_returns * 100, alpha=0.3, color='#A23B72')
    axes[2].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
    axes[2].set_title('Cumulative Returns', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Day')
    axes[2].set_ylabel('Cumulative Return (%)')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xticks(days)

    plt.tight_layout()

    # 이미지 저장
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    images_dir.mkdir(exist_ok=True)

    output_path = images_dir / "hello_trading.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return output_path


def main():
    """메인 함수"""
    # 헤더 출력
    print_header()

    # 1. 환경 검증
    verify_environment()

    # 2. 수익률 계산
    prices, returns = calculate_simple_returns()

    # 3. 통계 분석
    calculate_statistics(returns)

    # 4. 시각화
    output_path = create_visualization(prices, returns)
    print(f"\n차트가 저장되었습니다: {output_path.relative_to(Path.cwd())}")

    # 완료 메시지
    print("\n" + "=" * 42)
    print("축하합니다! 첫 번째 스크립트 실행 완료!")
    print("=" * 42)


if __name__ == "__main__":
    main()
