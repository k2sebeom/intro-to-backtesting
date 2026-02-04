"""
Chapter 16: 머신러닝 기반 전략 (Part 2)
ML and Backtrader Integration

이 스크립트는 머신러닝 모델을 Backtrader와 통합하여 백테스트합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import backtrader as bt
import pickle

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class MLStrategy(bt.Strategy):
    """머신러닝 기반 트레이딩 전략"""

    params = (
        ('model', None),
        ('scaler', None),
        ('feature_cols', None),
        ('prob_threshold', 0.6),
    )

    def __init__(self):
        # 특성 계산을 위한 지표들
        self.sma_5 = bt.indicators.SMA(self.data.close, period=5)
        self.sma_20 = bt.indicators.SMA(self.data.close, period=20)
        self.sma_50 = bt.indicators.SMA(self.data.close, period=50)

        self.ema_12 = bt.indicators.EMA(self.data.close, period=12)
        self.ema_26 = bt.indicators.EMA(self.data.close, period=26)

        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        self.macd = bt.indicators.MACD(self.data.close)

        self.bbands = bt.indicators.BollingerBands(self.data.close, period=20)

    def next(self):
        # 충분한 데이터가 쌓일 때까지 대기
        if len(self.data) < 200:
            return

        # 특성 계산
        features = self.calculate_features()

        if features is None:
            return

        # 모델 예측
        features_scaled = self.params.scaler.transform([features])
        prob = self.params.model.predict_proba(features_scaled)[0, 1]

        # 확률 기반 거래
        if not self.position:
            if prob > self.params.prob_threshold:
                self.buy()
        else:
            if prob < (1 - self.params.prob_threshold):
                self.close()

    def calculate_features(self):
        """현재 시점의 특성 계산"""

        try:
            # 수익률
            returns = (self.data.close[0] - self.data.close[-1]) / self.data.close[-1]

            # 가격 대비 SMA
            price_to_sma_20 = self.data.close[0] / self.sma_20[0] - 1

            # RSI
            rsi = self.rsi[0]

            # MACD
            macd_diff = self.macd.macd[0] - self.macd.signal[0]

            # Bollinger Bands 위치
            bb_position = (self.data.close[0] - self.bbands.lines.bot[0]) / \
                          (self.bbands.lines.top[0] - self.bbands.lines.bot[0])

            # 변동성 (최근 20일)
            recent_returns = [(self.data.close[-i] - self.data.close[-i-1]) / self.data.close[-i-1]
                             for i in range(1, min(21, len(self.data)))]
            volatility = np.std(recent_returns) if len(recent_returns) > 0 else 0

            # 거래량 비율
            volume_sma_5 = np.mean([self.data.volume[-i] for i in range(min(5, len(self.data)))])
            volume_ratio = self.data.volume[0] / volume_sma_5 if volume_sma_5 > 0 else 1

            # 래그 특성
            returns_lag_1 = (self.data.close[-1] - self.data.close[-2]) / self.data.close[-2] if len(self.data) > 2 else 0
            returns_lag_2 = (self.data.close[-2] - self.data.close[-3]) / self.data.close[-3] if len(self.data) > 3 else 0
            returns_lag_3 = (self.data.close[-3] - self.data.close[-4]) / self.data.close[-4] if len(self.data) > 4 else 0
            returns_lag_5 = (self.data.close[-5] - self.data.close[-6]) / self.data.close[-6] if len(self.data) > 6 else 0

            features = [
                returns, price_to_sma_20, rsi, macd_diff, bb_position,
                volatility, volume_ratio, returns_lag_1, returns_lag_2,
                returns_lag_3, returns_lag_5
            ]

            return features

        except Exception as e:
            return None


def prepare_ml_model(data, feature_cols):
    """ML 모델 학습"""

    print("\nML 모델 학습 중...")

    # 특성 생성
    df = data.copy()
    df['returns'] = df['Close'].pct_change()
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['price_to_sma_20'] = df['Close'] / df['sma_20'] - 1

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()
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

    # 결측치 제거
    df = df.dropna()

    # 훈련 데이터 (처음 70%)
    split_idx = int(len(df) * 0.7)
    train_df = df.iloc[:split_idx]

    X_train = train_df[feature_cols]
    y_train = train_df['target']

    # 스케일링
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # 모델 학습
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    print(f"훈련 데이터: {len(train_df)} 행")
    print(f"특성 개수: {len(feature_cols)}")
    print("모델 학습 완료!")

    return model, scaler


def run_ml_backtest(symbol='NVDA', start_date='2020-01-01', end_date='2024-01-01',
                    prob_threshold=0.6):
    """ML 전략 백테스트"""

    # 데이터 다운로드
    print(f"\n{symbol} 데이터 다운로드 중...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if data.empty:
        print("데이터 다운로드 실패")
        return None

    # 특성 컬럼
    feature_cols = ['returns', 'price_to_sma_20', 'rsi', 'macd_diff', 'bb_position',
                    'volatility', 'volume_ratio', 'returns_lag_1', 'returns_lag_2',
                    'returns_lag_3', 'returns_lag_5']

    # 모델 학습
    model, scaler = prepare_ml_model(data, feature_cols)

    # Backtrader 설정
    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)

    # ML 전략 추가
    cerebro.addstrategy(MLStrategy,
                       model=model,
                       scaler=scaler,
                       feature_cols=feature_cols,
                       prob_threshold=prob_threshold)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # 분석기 추가
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    # 백테스트 실행
    print(f"\n백테스트 실행 중 (확률 임계값: {prob_threshold})...")
    initial_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    # 결과 분석
    strategy = results[0]

    total_return = (final_value - initial_value) / initial_value
    sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
    max_dd = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)

    print(f"\n{'='*60}")
    print(f"백테스트 결과 (ML Strategy)")
    print(f"{'='*60}")
    print(f"초기 자본: ${initial_value:,.2f}")
    print(f"최종 자본: ${final_value:,.2f}")
    print(f"총 수익률: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"최대 낙폭: {max_dd:.2f}%")

    return {
        'total_return': total_return,
        'sharpe': sharpe,
        'max_dd': max_dd
    }


def main():
    """메인 함수"""

    print("=" * 60)
    print("Chapter 16: ML and Backtrader Integration")
    print("=" * 60)

    # 다양한 확률 임계값으로 테스트
    thresholds = [0.5, 0.55, 0.6, 0.65, 0.7]

    results = []
    for threshold in thresholds:
        print(f"\n\n{'#'*60}")
        print(f"확률 임계값: {threshold}")
        print(f"{'#'*60}")

        result = run_ml_backtest(
            symbol='NVDA',
            start_date='2020-01-01',
            end_date='2024-01-01',
            prob_threshold=threshold
        )

        if result:
            result['threshold'] = threshold
            results.append(result)

    # 결과 비교
    if results:
        print("\n\n" + "=" * 60)
        print("확률 임계값 비교")
        print("=" * 60)

        results_df = pd.DataFrame(results)
        print(results_df.to_string(index=False))

        # 최적 임계값
        best_idx = results_df['sharpe'].idxmax()
        best_threshold = results_df.loc[best_idx, 'threshold']
        best_sharpe = results_df.loc[best_idx, 'sharpe']

        print(f"\n최적 확률 임계값: {best_threshold} (Sharpe Ratio: {best_sharpe:.2f})")

    print("\n분석 완료!")


if __name__ == "__main__":
    main()
