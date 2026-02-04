"""
Chapter 15: 머신러닝 기반 전략 (Part 1)
Feature Engineering

이 스크립트는 기술적 지표를 머신러닝 특성으로 변환합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn as sns

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def create_features(data):
    """기술적 지표 특성 생성"""

    df = data.copy()

    # 1. 가격 기반 특성
    # 수익률
    df['returns'] = df['Close'].pct_change()

    # 이동평균
    for period in [5, 10, 20, 50, 200]:
        df[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
        df[f'price_to_sma_{period}'] = df['Close'] / df[f'sma_{period}'] - 1

    # 지수 이동평균
    for period in [12, 26]:
        df[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

    # 2. 모멘텀 지표
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_diff'] = df['macd'] - df['macd_signal']

    # ROC (Rate of Change)
    for period in [5, 10, 20]:
        df[f'roc_{period}'] = (df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)

    # 3. 변동성 지표
    # Bollinger Bands
    df['bb_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # ATR (Average True Range)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()
    df['atr_ratio'] = df['atr'] / df['Close']

    # 표준편차 (변동성)
    for period in [5, 10, 20]:
        df[f'volatility_{period}'] = df['returns'].rolling(window=period).std()

    # 4. 거래량 지표
    # 거래량 이동평균
    for period in [5, 10, 20]:
        df[f'volume_sma_{period}'] = df['Volume'].rolling(window=period).mean()
        df[f'volume_ratio_{period}'] = df['Volume'] / df[f'volume_sma_{period}']

    # OBV (On-Balance Volume)
    df['obv'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
    df['obv_sma'] = df['obv'].rolling(window=20).mean()

    # 5. 래그 특성 (과거 값)
    for lag in [1, 2, 3, 5, 10]:
        df[f'returns_lag_{lag}'] = df['returns'].shift(lag)
        df[f'volume_lag_{lag}'] = df['Volume'].shift(lag)

    # 6. 타겟 레이블 생성
    # 다음 기간 수익률
    df['future_return'] = df['returns'].shift(-1)

    # 이진 분류 레이블 (상승=1, 하락=0)
    df['target'] = (df['future_return'] > 0).astype(int)

    # 임계값 기반 레이블 (1% 이상 상승만 1)
    threshold = 0.01
    df['target_threshold'] = (df['future_return'] > threshold).astype(int)

    return df


def analyze_features(df):
    """특성 분석 및 시각화"""

    # 결측치 제거
    df_clean = df.dropna()

    # 특성 컬럼 선택
    feature_cols = [col for col in df_clean.columns if col not in
                    ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
                     'future_return', 'target', 'target_threshold']]

    # 기본 통계
    print("\n특성 기본 통계:")
    print(df_clean[feature_cols].describe())

    # 타겟 분포
    print("\n타겟 레이블 분포:")
    print(df_clean['target'].value_counts())
    print(f"상승 비율: {df_clean['target'].mean():.2%}")

    # 시각화
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Feature Engineering Analysis', fontsize=16, fontweight='bold')

    # 1. 타겟 분포
    ax1 = axes[0, 0]
    df_clean['target'].value_counts().plot(kind='bar', ax=ax1, color=['red', 'green'])
    ax1.set_title('Target Distribution')
    ax1.set_xlabel('Class (0=Down, 1=Up)')
    ax1.set_ylabel('Count')
    ax1.set_xticklabels(['Down', 'Up'], rotation=0)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. 주요 특성 상관관계
    ax2 = axes[0, 1]
    important_features = ['returns', 'rsi', 'macd_diff', 'bb_position',
                          'atr_ratio', 'volume_ratio_5', 'target']
    corr = df_clean[important_features].corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                ax=ax2, cbar_kws={'label': 'Correlation'})
    ax2.set_title('Feature Correlation Matrix')

    # 3. RSI와 타겟 관계
    ax3 = axes[1, 0]
    df_clean.boxplot(column='rsi', by='target', ax=ax3)
    ax3.set_title('RSI Distribution by Target')
    ax3.set_xlabel('Target (0=Down, 1=Up)')
    ax3.set_ylabel('RSI')
    plt.sca(ax3)
    plt.xticks([1, 2], ['Down', 'Up'])

    # 4. 특성 중요도 (상관관계 절댓값)
    ax4 = axes[1, 1]
    target_corr = df_clean[feature_cols].corrwith(df_clean['target']).abs().sort_values(ascending=False)
    top_10 = target_corr.head(10)
    top_10.plot(kind='barh', ax=ax4, color='skyblue')
    ax4.set_title('Top 10 Features by Correlation with Target')
    ax4.set_xlabel('|Correlation|')
    ax4.invert_yaxis()
    ax4.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'feature_engineering_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()

    return feature_cols


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 15: Feature Engineering for ML Trading")
    print("=" * 60)

    # 데이터 다운로드
    symbol = 'NVDA'
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start='2020-01-01', end='2024-01-01', progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return

    print(f"데이터 크기: {len(data)} 행")

    # 특성 생성
    print("\n특성 생성 중...")
    df = create_features(data)

    # 결측치 정보
    missing_before = df.isnull().sum().sum()
    df_clean = df.dropna()
    missing_removed = len(df) - len(df_clean)

    print(f"결측치 제거 전: {len(df)} 행")
    print(f"결측치 제거 후: {len(df_clean)} 행")
    print(f"제거된 행: {missing_removed}")

    # 생성된 특성 목록
    feature_cols = [col for col in df_clean.columns if col not in
                    ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
                     'future_return', 'target', 'target_threshold']]

    print(f"\n생성된 특성 개수: {len(feature_cols)}")
    print("\n특성 카테고리:")
    print("  - 가격 기반 특성")
    print("  - 모멘텀 지표 (RSI, MACD, ROC)")
    print("  - 변동성 지표 (Bollinger Bands, ATR)")
    print("  - 거래량 지표")
    print("  - 래그 특성")

    # 특성 분석
    analyze_features(df)

    # 데이터 저장
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    output_file = os.path.join(data_dir, f'{symbol}_ml_features.csv')
    df_clean.to_csv(output_file)
    print(f"\n특성 데이터 저장됨: {output_file}")

    # 타겟 상관관계 분석
    print("\n" + "=" * 60)
    print("타겟 상관관계 분석")
    print("=" * 60)

    target_corr = df_clean[feature_cols].corrwith(df_clean['target']).sort_values(ascending=False)
    print("\n타겟과 가장 높은 상관관계를 가진 특성 (Top 10):")
    print(target_corr.head(10))

    print("\n타겟과 가장 낮은 상관관계를 가진 특성 (Bottom 10):")
    print(target_corr.tail(10))

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
