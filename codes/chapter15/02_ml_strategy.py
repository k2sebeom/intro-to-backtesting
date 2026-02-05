"""
Chapter 15: 머신러닝 기반 전략 (Part 1)
ML-Based Trading Strategy

이 스크립트는 로지스틱 회귀와 랜덤 포레스트를 사용한 트레이딩 전략을 구현합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import backtrader as bt

plt.rcParams['font.family'] = ['Nanum Gothic', 'Malgun Gothic', 'AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_features(data):
    """특성 생성 (Chapter 15-01과 동일)"""

    df = data.copy()

    # 수익률
    df['returns'] = df['Close'].pct_change()

    # 이동평균
    df['sma_5'] = df['Close'].rolling(window=5).mean()
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['sma_50'] = df['Close'].rolling(window=50).mean()
    df['price_to_sma_20'] = df['Close'] / df['sma_20'] - 1

    # EMA
    df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()

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

    # Bollinger Bands
    df['bb_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # 변동성
    df['volatility'] = df['returns'].rolling(window=20).std()

    # 거래량
    df['volume_sma_5'] = df['Volume'].rolling(window=5).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma_5']

    # 래그 특성
    for lag in [1, 2, 3, 5]:
        df[f'returns_lag_{lag}'] = df['returns'].shift(lag)

    # 타겟
    df['future_return'] = df['returns'].shift(-1)
    df['target'] = (df['future_return'] > 0).astype(int)

    return df


def train_ml_models(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01'):
    """머신러닝 모델 학습 및 평가"""

    # 데이터 다운로드
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    
    # yfinance multi-level columns handling
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if data.empty:
        print("데이터 다운로드 실패")
        return None

    # 특성 생성
    print("특성 생성 중...")
    df = create_features(data)
    df = df.dropna()

    # 특성과 타겟 분리
    feature_cols = ['returns', 'price_to_sma_20', 'rsi', 'macd_diff', 'bb_position',
                    'volatility', 'volume_ratio', 'returns_lag_1', 'returns_lag_2',
                    'returns_lag_3', 'returns_lag_5']

    X = df[feature_cols]
    y = df['target']

    print(f"데이터 크기: {len(df)} 행, {len(feature_cols)} 특성")
    print(f"타겟 분포: 상승={y.sum()}, 하락={len(y)-y.sum()}, 상승 비율={y.mean():.2%}")

    # 시계열 분할
    tscv = TimeSeriesSplit(n_splits=5)

    results = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        print(f"\n{'='*60}")
        print(f"Fold {fold + 1}/5")
        print(f"{'='*60}")

        # 데이터 분할
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        print(f"훈련 세트: {len(X_train)} 행")
        print(f"테스트 세트: {len(X_test)} 행")

        # 특성 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 1. 로지스틱 회귀
        print("\n로지스틱 회귀 학습 중...")
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train_scaled, y_train)
        lr_pred = lr_model.predict(X_test_scaled)
        lr_prob = lr_model.predict_proba(X_test_scaled)[:, 1]

        lr_metrics = {
            'model': 'Logistic Regression',
            'fold': fold + 1,
            'accuracy': accuracy_score(y_test, lr_pred),
            'precision': precision_score(y_test, lr_pred, zero_division=0),
            'recall': recall_score(y_test, lr_pred, zero_division=0),
            'f1': f1_score(y_test, lr_pred, zero_division=0),
            'auc': roc_auc_score(y_test, lr_prob)
        }

        print(f"정확도: {lr_metrics['accuracy']:.4f}")
        print(f"정밀도: {lr_metrics['precision']:.4f}")
        print(f"재현율: {lr_metrics['recall']:.4f}")
        print(f"F1 점수: {lr_metrics['f1']:.4f}")
        print(f"AUC: {lr_metrics['auc']:.4f}")

        results.append(lr_metrics)

        # 2. 랜덤 포레스트
        print("\n랜덤 포레스트 학습 중...")
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=10,
                                          random_state=42, n_jobs=-1)
        rf_model.fit(X_train_scaled, y_train)
        rf_pred = rf_model.predict(X_test_scaled)
        rf_prob = rf_model.predict_proba(X_test_scaled)[:, 1]

        rf_metrics = {
            'model': 'Random Forest',
            'fold': fold + 1,
            'accuracy': accuracy_score(y_test, rf_pred),
            'precision': precision_score(y_test, rf_pred, zero_division=0),
            'recall': recall_score(y_test, rf_pred, zero_division=0),
            'f1': f1_score(y_test, rf_pred, zero_division=0),
            'auc': roc_auc_score(y_test, rf_prob)
        }

        print(f"정확도: {rf_metrics['accuracy']:.4f}")
        print(f"정밀도: {rf_metrics['precision']:.4f}")
        print(f"재현율: {rf_metrics['recall']:.4f}")
        print(f"F1 점수: {rf_metrics['f1']:.4f}")
        print(f"AUC: {rf_metrics['auc']:.4f}")

        results.append(rf_metrics)

    results_df = pd.DataFrame(results)

    # 결과 시각화
    plot_model_comparison(results_df, symbol)

    return results_df


def plot_model_comparison(results_df, symbol):
    """모델 비교 시각화"""

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'{symbol} - ML Model Comparison', fontsize=16, fontweight='bold')

    metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc']
    titles = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC']

    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx // 3, idx % 3]

        # 모델별 평균
        lr_data = results_df[results_df['model'] == 'Logistic Regression'][metric]
        rf_data = results_df[results_df['model'] == 'Random Forest'][metric]

        ax.bar(['Logistic\nRegression', 'Random\nForest'],
               [lr_data.mean(), rf_data.mean()],
               color=['skyblue', 'lightgreen'],
               alpha=0.7, edgecolor='black')

        # 에러 바 (표준편차)
        ax.errorbar(['Logistic\nRegression', 'Random\nForest'],
                   [lr_data.mean(), rf_data.mean()],
                   yerr=[lr_data.std(), rf_data.std()],
                   fmt='none', ecolor='black', capsize=5)

        ax.set_title(title)
        ax.set_ylabel('Score')
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')

        # 값 표시
        ax.text(0, lr_data.mean() + 0.05, f'{lr_data.mean():.3f}',
                ha='center', fontsize=10)
        ax.text(1, rf_data.mean() + 0.05, f'{rf_data.mean():.3f}',
                ha='center', fontsize=10)

    # 6번째 서브플롯: 평균 지표 테이블
    ax6 = axes[1, 2]
    ax6.axis('off')

    summary_data = []
    for model in ['Logistic Regression', 'Random Forest']:
        model_data = results_df[results_df['model'] == model]
        summary_data.append([
            model.replace(' ', '\n'),
            f"{model_data['accuracy'].mean():.3f}",
            f"{model_data['precision'].mean():.3f}",
            f"{model_data['recall'].mean():.3f}",
            f"{model_data['f1'].mean():.3f}",
            f"{model_data['auc'].mean():.3f}"
        ])

    table = ax6.table(cellText=summary_data,
                      colLabels=['Model', 'Acc', 'Prec', 'Rec', 'F1', 'AUC'],
                      cellLoc='center', loc='center',
                      colWidths=[0.3, 0.14, 0.14, 0.14, 0.14, 0.14])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # 헤더 스타일
    for i in range(6):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    ax6.set_title('Average Metrics', fontweight='bold', pad=20)

    plt.tight_layout()

    # 이미지 저장
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, 'ml_model_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n차트 저장됨: {output_path}")

    plt.show()


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 15: ML-Based Trading Strategy")
    print("=" * 60)

    # 모델 학습 및 평가
    results = train_ml_models(
        symbol='NVDA',
        start_date='2020-01-01',
        end_date='2024-01-01'
    )

    if results is not None:
        print("\n" + "=" * 60)
        print("전체 평균 성과")
        print("=" * 60)

        for model in ['Logistic Regression', 'Random Forest']:
            model_data = results[results['model'] == model]
            print(f"\n{model}:")
            print(f"  정확도: {model_data['accuracy'].mean():.4f} ± {model_data['accuracy'].std():.4f}")
            print(f"  정밀도: {model_data['precision'].mean():.4f} ± {model_data['precision'].std():.4f}")
            print(f"  재현율: {model_data['recall'].mean():.4f} ± {model_data['recall'].std():.4f}")
            print(f"  F1 점수: {model_data['f1'].mean():.4f} ± {model_data['f1'].std():.4f}")
            print(f"  AUC: {model_data['auc'].mean():.4f} ± {model_data['auc'].std():.4f}")

        # 해석
        print("\n" + "=" * 60)
        print("결과 해석")
        print("=" * 60)

        lr_auc = results[results['model'] == 'Logistic Regression']['auc'].mean()
        rf_auc = results[results['model'] == 'Random Forest']['auc'].mean()

        print(f"\nAUC 비교:")
        print(f"  로지스틱 회귀: {lr_auc:.4f}")
        print(f"  랜덤 포레스트: {rf_auc:.4f}")

        if rf_auc > lr_auc + 0.02:
            print("\n  → 랜덤 포레스트가 더 우수한 성능")
        elif lr_auc > rf_auc + 0.02:
            print("\n  → 로지스틱 회귀가 더 우수한 성능")
        else:
            print("\n  → 두 모델의 성능이 유사함")

        if max(lr_auc, rf_auc) > 0.6:
            print("\n모델이 예측력을 가지고 있음 (AUC > 0.6)")
        else:
            print("\n모델의 예측력이 약함 (AUC < 0.6)")

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
