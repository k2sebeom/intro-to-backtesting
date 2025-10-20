# Backtrader: Complete Guide for Programmers

Backtrader is a Python library for backtesting trading strategies. It provides a comprehensive framework for developing, testing, and analyzing algorithmic trading strategies with ease of use as its primary objective.

## Table of Contents

1. [Installation and Basic Setup](#installation-and-basic-setup)
2. [Core Concepts](#core-concepts)
3. [Quick Start Example](#quick-start-example)
4. [Data Feeds](#data-feeds)
5. [Strategies](#strategies)
6. [Indicators](#indicators)
7. [Orders and Trading](#orders-and-trading)
8. [Broker Configuration](#broker-configuration)
9. [Analyzers and Performance Metrics](#analyzers-and-performance-metrics)
10. [Plotting](#plotting)
11. [Optimization](#optimization)
12. [Advanced Features](#advanced-features)

## Installation and Basic Setup

```bash
pip install backtrader
```

For plotting capabilities:
```bash
pip install backtrader[plotting]
# or
pip install matplotlib
```

## Core Concepts

### Lines and Index 0 Approach

Backtrader uses a unique "Index 0" approach where:
- Current value is accessed with index `[0]`
- Previous value is accessed with index `[-1]`
- Earlier values with `[-2]`, `[-3]`, etc.

```python
# In a strategy
current_close = self.data.close[0]
previous_close = self.data.close[-1]
```

### Main Components

1. **Cerebro**: The main engine that orchestrates everything
2. **Data Feeds**: Market data sources (CSV, live feeds, etc.)
3. **Strategies**: Your trading logic
4. **Indicators**: Technical analysis tools
5. **Broker**: Simulates order execution and portfolio management
6. **Analyzers**: Performance analysis tools

## Quick Start Example

Here's a complete minimal example:

```python
import backtrader as bt
import datetime

class TestStrategy(bt.Strategy):
    def __init__(self):
        # Keep reference to close price
        self.dataclose = self.datas[0].close
        
    def next(self):
        # Log the closing price
        print(f'Close: {self.dataclose[0]:.2f}')
        
        # Simple strategy: buy if we don't have a position
        if not self.position:
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    # Buy signal: 2 consecutive down days
                    self.buy()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # Add strategy
    cerebro.addstrategy(TestStrategy)
    
    # Create data feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname='data.csv',
        fromdate=datetime.datetime(2020, 1, 1),
        todate=datetime.datetime(2021, 1, 1)
    )
    
    # Add data to cerebro
    cerebro.adddata(data)
    
    # Set initial cash
    cerebro.broker.setcash(10000.0)
    
    # Run backtest
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
```

## Data Feeds

### Common Data Feed Types

```python
import backtrader.feeds as btfeeds

# Yahoo Finance CSV
data = btfeeds.YahooFinanceCSVData(
    dataname='AAPL.csv',
    fromdate=datetime.datetime(2020, 1, 1),
    todate=datetime.datetime(2021, 1, 1)
)

# Generic CSV
data = btfeeds.GenericCSVData(
    dataname='mydata.csv',
    datetime=0,    # Column with datetime
    open=1,        # Column with open price
    high=2,        # Column with high price
    low=3,         # Column with low price
    close=4,       # Column with close price
    volume=5,      # Column with volume
    openinterest=-1  # No open interest column
)

# Pandas DataFrame
import pandas as pd
df = pd.read_csv('data.csv', parse_dates=True, index_col=0)
data = bt.feeds.PandasData(dataname=df)
```

### Data Feed Parameters

```python
data = btfeeds.YahooFinanceCSVData(
    dataname='data.csv',
    name='AAPL',  # Name for plotting
    fromdate=datetime.datetime(2020, 1, 1),
    todate=datetime.datetime(2021, 1, 1),
    timeframe=bt.TimeFrame.Days,
    compression=1,
    sessionstart=datetime.time(9, 30),
    sessionend=datetime.time(16, 0)
)
```

## Strategies

### Strategy Lifecycle

```python
class MyStrategy(bt.Strategy):
    def __init__(self):
        """Called during strategy initialization"""
        # Create indicators here
        self.sma = bt.indicators.SimpleMovingAverage(period=20)
        
    def start(self):
        """Called when backtesting starts"""
        print("Backtesting started")
        
    def prenext(self):
        """Called before minimum period is met"""
        pass
        
    def nextstart(self):
        """Called exactly once when minimum period is met"""
        pass
        
    def next(self):
        """Called for each bar after minimum period"""
        # Main trading logic goes here
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()
            
    def stop(self):
        """Called when backtesting ends"""
        print("Backtesting finished")
```

### Strategy Parameters

```python
class ParameterizedStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('stake', 100),
        ('printlog', False),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.params.period)
        
    def next(self):
        if self.params.printlog:
            print(f'Close: {self.data.close[0]:.2f}')

# Add strategy with custom parameters
cerebro.addstrategy(ParameterizedStrategy, period=30, stake=200)
```

### Notifications

```python
class NotificationStrategy(bt.Strategy):
    def notify_order(self, order):
        """Called when order status changes"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED: Price {order.executed.price:.2f}')
            else:
                print(f'SELL EXECUTED: Price {order.executed.price:.2f}')
                
    def notify_trade(self, trade):
        """Called when trade is closed"""
        if trade.isclosed:
            print(f'TRADE PROFIT: {trade.pnl:.2f}')
            
    def notify_cashvalue(self, cash, value):
        """Called with current cash and portfolio value"""
        print(f'Cash: {cash:.2f}, Portfolio: {value:.2f}')
```

## Indicators

### Built-in Indicators

```python
class IndicatorStrategy(bt.Strategy):
    def __init__(self):
        # Moving averages
        self.sma = bt.indicators.SimpleMovingAverage(period=20)
        self.ema = bt.indicators.ExponentialMovingAverage(period=20)
        
        # Oscillators
        self.rsi = bt.indicators.RSI(period=14)
        self.macd = bt.indicators.MACD()
        self.stoch = bt.indicators.Stochastic()
        
        # Bollinger Bands
        self.bbands = bt.indicators.BollingerBands(period=20, devfactor=2)
        
        # Volume indicators
        self.volume_sma = bt.indicators.SMA(self.data.volume, period=20)
        
    def next(self):
        # Use indicators in trading logic
        if self.rsi[0] < 30 and self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.rsi[0] > 70:
            self.sell()
```

### Custom Indicators

```python
class MyCustomIndicator(bt.Indicator):
    lines = ('signal',)
    params = (('period', 20),)
    
    def __init__(self):
        self.addminperiod(self.params.period)
        
    def next(self):
        # Custom calculation
        data_slice = self.data.get(ago=0, size=self.params.period)
        self.lines.signal[0] = sum(data_slice) / len(data_slice)

# Use in strategy
class CustomIndicatorStrategy(bt.Strategy):
    def __init__(self):
        self.custom = MyCustomIndicator(period=10)
```

## Orders and Trading

### Basic Order Types

```python
class OrderStrategy(bt.Strategy):
    def next(self):
        # Market orders
        self.buy()  # Buy with default size
        self.sell() # Sell with default size
        
        # Specify size
        self.buy(size=100)
        self.sell(size=50)
        
        # Limit orders
        self.buy(price=100.0, exectype=bt.Order.Limit)
        self.sell(price=110.0, exectype=bt.Order.Limit)
        
        # Stop orders
        self.sell(price=95.0, exectype=bt.Order.Stop)
        
        # Stop-limit orders
        self.sell(price=95.0, plimit=94.0, exectype=bt.Order.StopLimit)
        
        # Close position
        self.close()
```

### Order Management

```python
class OrderManagementStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        
    def next(self):
        # Check if order is pending
        if self.order:
            return
            
        # Check if we're in the market
        if not self.position:
            # Buy signal
            if self.data.close[0] > self.data.close[-1]:
                self.order = self.buy()
        else:
            # Sell signal
            if self.data.close[0] < self.data.close[-1]:
                self.order = self.sell()
                
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None
```

### Position Sizing

```python
# Fixed size sizer
cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# Percentage sizer
cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

# Custom sizer
class CustomSizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        # Custom sizing logic
        return int(cash * 0.1 / data.close[0])

cerebro.addsizer(CustomSizer)
```

## Broker Configuration

### Basic Broker Settings

```python
# Set initial cash
cerebro.broker.setcash(100000.0)

# Set commission
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# Set slippage
cerebro.broker.set_slippage_perc(perc=0.01)  # 1%
```

### Commission Schemes

```python
# Stock-like commission
cerebro.broker.setcommission(
    commission=0.001,  # 0.1%
    mult=1.0,
    margin=None
)

# Futures-like commission
cerebro.broker.setcommission(
    commission=2.0,    # $2 per contract
    mult=10,           # Multiplier
    margin=2000.0      # Margin per contract
)
```

## Analyzers and Performance Metrics

### Built-in Analyzers

```python
# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

# Run backtest
results = cerebro.run()
strat = results[0]

# Get analyzer results
print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
print(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
print(f"Total Return: {strat.analyzers.returns.get_analysis()['rtot']:.2f}%")

trade_analysis = strat.analyzers.trades.get_analysis()
print(f"Total Trades: {trade_analysis['total']['total']}")
print(f"Win Rate: {trade_analysis['won']['total'] / trade_analysis['total']['total'] * 100:.1f}%")
```

### Custom Analyzer

```python
class CustomAnalyzer(bt.Analyzer):
    def __init__(self):
        self.trades = []
        
    def notify_trade(self, trade):
        if trade.isclosed:
            self.trades.append(trade.pnl)
            
    def get_analysis(self):
        return {
            'total_trades': len(self.trades),
            'avg_profit': sum(self.trades) / len(self.trades) if self.trades else 0,
            'max_profit': max(self.trades) if self.trades else 0,
            'min_profit': min(self.trades) if self.trades else 0
        }

# Add custom analyzer
cerebro.addanalyzer(CustomAnalyzer, _name='custom')
```

## Plotting

### Basic Plotting

```python
# Run backtest
cerebro.run()

# Plot results (shows popup window)
cerebro.plot()

# Plot with custom settings
cerebro.plot(
    style='candlestick',
    barup='green',
    bardown='red',
    volume=True
)
```

### Silent Plot Saving (No Popup Windows)

```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Run backtest
cerebro.run()

# Plot and save silently
figs = cerebro.plot(iplot=False)  # iplot=False prevents inline plotting
for i, fig in enumerate(figs):
    fig.savefig(f'backtest_plot_{i}.png', dpi=300, bbox_inches='tight')
    plt.close(fig)  # Close figure to free memory
```

### Advanced Silent Plotting with Custom Settings

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime

class SilentPlotter:
    def __init__(self, output_dir='plots'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def save_plot(self, cerebro, filename=None, **plot_kwargs):
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'backtest_{timestamp}'
            
        # Default plot settings for better images
        plot_settings = {
            'iplot': False,
            'volume': True,
            'style': 'candlestick',
            'barup': 'green',
            'bardown': 'red'
        }
        plot_settings.update(plot_kwargs)
        
        figs = cerebro.plot(**plot_settings)
        
        saved_files = []
        for i, fig in enumerate(figs):
            if len(figs) > 1:
                filepath = os.path.join(self.output_dir, f'{filename}_{i+1}.png')
            else:
                filepath = os.path.join(self.output_dir, f'{filename}.png')
                
            fig.savefig(filepath, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            saved_files.append(filepath)
            
        return saved_files

# Usage
plotter = SilentPlotter('my_plots')
cerebro.run()
saved_files = plotter.save_plot(cerebro, 'my_strategy_results')
print(f"Plots saved: {saved_files}")
```

### Plotting with Custom Schemes

```python
import backtrader as bt

# Custom plot scheme
class MyPlotScheme(bt.PlotScheme):
    def __init__(self):
        super().__init__()
        self.style = 'candlestick'
        self.barup = '#26a69a'      # Teal for bullish
        self.bardown = '#ef5350'    # Red for bearish
        self.volup = '#26a69a'      # Volume colors
        self.voldown = '#ef5350'
        self.grid = True
        self.subtxtsize = 10

# Use custom scheme
cerebro.run()
figs = cerebro.plot(plotter=MyPlotScheme(), iplot=False)
```

### Plotting Individual Indicators

```python
class PlottingStrategy(bt.Strategy):
    def __init__(self):
        # These will be plotted automatically
        self.sma = bt.indicators.SMA(period=20)
        self.ema = bt.indicators.EMA(period=20)
        
        # Plot on separate subplot
        self.rsi = bt.indicators.RSI(period=14)
        self.rsi.plotinfo.subplot = True
        
        # Don't plot this indicator
        self.hidden = bt.indicators.SMA(period=10)
        self.hidden.plotinfo.plot = False
        
        # Custom indicator plotting
        self.macd = bt.indicators.MACD()
        self.macd.plotinfo.plotname = 'My MACD'
        
        # Bollinger Bands with custom colors
        self.bbands = bt.indicators.BollingerBands()
        self.bbands.plotlines.top._plotskip = False
        self.bbands.plotlines.bot._plotskip = False
        self.bbands.plotlines.mid.ls = '--'  # Dashed line style
```

### Plot Customization Options

```python
class CustomPlotStrategy(bt.Strategy):
    def __init__(self):
        # Moving average with custom plot settings
        self.sma = bt.indicators.SMA(period=20)
        self.sma.plotinfo.plotname = 'SMA-20'
        self.sma.plotlines.sma.color = 'blue'
        self.sma.plotlines.sma.linewidth = 2
        
        # RSI with horizontal lines
        self.rsi = bt.indicators.RSI()
        self.rsi.plotinfo.subplot = True
        self.rsi.plotinfo.plothlines = [30, 70]  # Overbought/oversold lines
        
        # Stochastic with custom names
        self.stoch = bt.indicators.Stochastic()
        self.stoch.plotinfo.subplot = True
        self.stoch.plotlines.percK._name = '%K'
        self.stoch.plotlines.percD._name = '%D'
        self.stoch.plotlines.percD.ls = '--'  # Dashed line
```

### Batch Plot Generation

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def generate_strategy_plots(strategies, data, output_dir='strategy_plots'):
    """Generate plots for multiple strategies"""
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    
    for strategy_name, strategy_class in strategies.items():
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class)
        cerebro.broker.setcash(10000)
        
        # Run backtest
        result = cerebro.run()
        
        # Generate plot
        figs = cerebro.plot(iplot=False, volume=False)  # Disable volume for cleaner plots
        
        # Save plot
        for i, fig in enumerate(figs):
            filename = f'{strategy_name}_{i+1}.png' if len(figs) > 1 else f'{strategy_name}.png'
            filepath = os.path.join(output_dir, filename)
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
        results[strategy_name] = {
            'final_value': cerebro.broker.getvalue(),
            'plot_files': [os.path.join(output_dir, f'{strategy_name}.png')]
        }
    
    return results

# Usage
strategies = {
    'SMA_Strategy': MySMAStrategy,
    'RSI_Strategy': MyRSIStrategy,
    'MACD_Strategy': MyMACDStrategy
}

results = generate_strategy_plots(strategies, data)
for name, result in results.items():
    print(f"{name}: Final Value = {result['final_value']:.2f}")
```

### Jupyter Notebook Plotting

```python
# For Jupyter notebooks - inline plotting
%matplotlib inline

# Run and plot inline
cerebro.run()
cerebro.plot(iplot=True)  # iplot=True for inline display

# Save from notebook
figs = cerebro.plot(iplot=False)
for i, fig in enumerate(figs):
    fig.savefig(f'notebook_plot_{i}.png', dpi=150, bbox_inches='tight')
```

### Plot Configuration for Different Use Cases

```python
# High-quality plots for reports
def plot_for_report(cerebro, filename):
    figs = cerebro.plot(
        iplot=False,
        style='candlestick',
        volume=True,
        grid=True,
        barup='#2E8B57',      # Sea green
        bardown='#DC143C',    # Crimson
        volup='#90EE90',      # Light green
        voldown='#FFB6C1'     # Light pink
    )
    
    for i, fig in enumerate(figs):
        fig.set_size_inches(16, 10)  # Large size for reports
        fig.savefig(f'{filename}_{i}.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)

# Quick plots for analysis
def plot_for_analysis(cerebro, filename):
    figs = cerebro.plot(
        iplot=False,
        style='line',
        volume=False,
        grid=False
    )
    
    for i, fig in enumerate(figs):
        fig.savefig(f'{filename}_{i}.png', dpi=150, bbox_inches='tight')
        plt.close(fig)
```

## Optimization

### Parameter Optimization

```python
class OptimizableStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('threshold', 0.02),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.params.period)
        
    def next(self):
        if self.data.close[0] / self.sma[0] - 1 > self.params.threshold:
            self.buy()
        elif self.data.close[0] / self.sma[0] - 1 < -self.params.threshold:
            self.sell()
            
    def stop(self):
        print(f'Period: {self.params.period}, Threshold: {self.params.threshold:.3f}, '
              f'Final Value: {self.broker.getvalue():.2f}')

# Optimize parameters
cerebro.optstrategy(
    OptimizableStrategy,
    period=range(10, 31),
    threshold=[0.01, 0.02, 0.03]
)

# Run optimization
results = cerebro.run(maxcpus=1)
```

## Advanced Features

### Multiple Data Feeds

```python
class MultiDataStrategy(bt.Strategy):
    def __init__(self):
        # Access different data feeds
        self.data0_sma = bt.indicators.SMA(self.datas[0], period=20)
        self.data1_sma = bt.indicators.SMA(self.datas[1], period=20)
        
    def next(self):
        # Trade based on multiple instruments
        if self.datas[0].close[0] > self.data0_sma[0] and \
           self.datas[1].close[0] > self.data1_sma[0]:
            self.buy(data=self.datas[0])

# Add multiple data feeds
cerebro.adddata(data1, name='AAPL')
cerebro.adddata(data2, name='MSFT')
```

### Data Resampling

```python
# Resample daily data to weekly
data_weekly = cerebro.resampledata(
    data,
    timeframe=bt.TimeFrame.Weeks,
    compression=1
)
```

### Live Trading Integration

```python
# Example with Interactive Brokers (requires ib_insync)
import backtrader as bt

class LiveStrategy(bt.Strategy):
    def next(self):
        # Same strategy logic works for live trading
        if not self.position:
            self.buy()

# Configure for live trading
cerebro = bt.Cerebro()
cerebro.addstrategy(LiveStrategy)

# Add live data feed (implementation depends on broker)
# data = bt.feeds.IBData(dataname='AAPL', timeframe=bt.TimeFrame.Minutes)
# cerebro.adddata(data)
```

### Custom Data Feeds

```python
class CustomDataFeed(bt.feeds.GenericCSVData):
    params = (
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
    )

# Use custom data feed
data = CustomDataFeed(dataname='custom_data.csv')
cerebro.adddata(data)
```

## Best Practices

### 1. Strategy Development

```python
class WellStructuredStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('printlog', False),
    )
    
    def log(self, txt, dt=None):
        """Centralized logging"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
    
    def __init__(self):
        # Initialize indicators
        self.sma = bt.indicators.SMA(period=self.params.period)
        
        # Track orders and positions
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
                
        self.order = None
        
    def next(self):
        self.log(f'Close: {self.dataclose[0]:.2f}')
        
        if self.order:
            return
            
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE')
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE')
                self.order = self.sell()
```

### 2. Performance Considerations

```python
# Use memory-efficient settings for large datasets
cerebro = bt.Cerebro(stdstats=False)  # Disable default observers
cerebro.broker.set_coc(True)  # Cheat-on-close for faster execution
```

### 3. Error Handling

```python
class RobustStrategy(bt.Strategy):
    def next(self):
        try:
            # Your trading logic here
            if self.data.close[0] > self.sma[0]:
                self.buy()
        except Exception as e:
            print(f"Error in strategy: {e}")
            # Handle error appropriately
```

This guide covers the essential aspects of backtrader for programmers. The library's strength lies in its simplicity and extensibility, allowing you to focus on strategy development rather than infrastructure concerns.
