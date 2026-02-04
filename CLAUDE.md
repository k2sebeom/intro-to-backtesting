# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-powered educational book titled "파이썬으로 배우는 백테스팅 입문" (Introduction to Backtesting with Python). The book teaches quantitative trading fundamentals through hands-on backtesting exercises using Python. It contains both the Hugo documentation site and executable Python code examples that readers run alongside reading the chapters.

**Key characteristics:**
- **Primary language: Korean (한국어)** - All book content, explanations, and user-facing text are written in Korean
- Dual structure: Hugo book content in `content/docs/` + executable Python examples in `codes/`
- English technical terms preserved where appropriate (e.g., "backtesting", "OHLCV", "Sharpe Ratio")
- Educational focus with mathematical explanations (LaTeX math rendering enabled)
- uv package manager for Python environment management

## Commands

### Hugo (Book Site)

```bash
# Start development server
hugo server

# Build static site
hugo

# Output will be in /public/

# Create new content (use this to generate properly structured markdown files)
hugo new content/docs/chapterXX.md

# Check configuration and syntax
hugo config

# Validate content without building
hugo --renderToMemory
```

**AI Usage Note**: When creating new chapters, leverage the `hugo new` command to generate content files with proper frontmatter. Use `hugo server` to preview changes and `hugo config` to verify configuration syntax.

### Python Code Examples

All Python code examples use `uv` as the package manager:

```bash
# Initial setup (from codes/ directory)
cd codes
uv sync

# Run chapter examples
uv run chapter01/01_basic_data_download.py
uv run chapter01/02_matplotlib_basics.py
uv run chapter01/03_first_backtest.py

# Run examples from any chapter
uv run chapter02/01_data_download_multiple_timeframes.py
uv run chapter03/01_sma_calculation.py
```

**Important**: All Python code must be run with `uv run` prefix from the `codes/` directory. The environment is already initialized with uv.

## Architecture

### Repository Structure

```
├── content/docs/          # Hugo book chapters (markdown)
│   ├── chapter01.md       # Chapter content with theory + explanations
│   ├── chapter02.md
│   └── chapter03.md
├── codes/                 # Executable Python examples
│   ├── chapter01/         # Chapter-specific code files
│   ├── chapter02/
│   ├── chapter03/
│   ├── data/              # Downloaded stock data (CSV files)
│   ├── pyproject.toml     # Python dependencies managed by uv
│   └── README.md          # Korean instructions for running code
├── references/            # Library documentation references
│   ├── backtrader.md      # Backtrader framework guide
│   └── yfinance.md        # yfinance API reference
├── hugo.toml              # Hugo configuration
└── themes/hugo-book/      # Hugo Book theme (submodule)
```

### Content-Code Relationship

Each chapter follows a consistent pattern:
1. **Theory in markdown** (`content/docs/chapterXX.md`): Mathematical foundations, explanations, analysis
2. **Implementation in Python** (`codes/chapterXX/`): Working code that demonstrates concepts
3. **Generated outputs**: Charts saved to `codes/chapterXX/images/`, data to `codes/data/`

Example for Chapter 1:
- `content/docs/chapter01.md` explains backtesting concepts, OHLCV data structure, moving averages
- `codes/chapter01/01_basic_data_download.py` downloads NVIDIA data, calculates statistics
- `codes/chapter01/02_matplotlib_basics.py` creates visualizations
- `codes/chapter01/03_first_backtest.py` implements Buy & Hold and SMA strategies

### Python Code Architecture

The `codes/` directory is structured as individual executable scripts per chapter rather than a unified package. Each script:
- Is self-contained and executable with `uv run`
- Uses relative paths based on `__file__` for data directories
- Generates outputs (CSV data, PNG charts) in predictable locations
- Follows consistent naming: `0X_descriptive_name.py`

**Key dependencies** (from `pyproject.toml`):
- `yfinance`: Download stock data from Yahoo Finance
- `pandas`: Data manipulation and analysis
- `matplotlib`: Chart generation and visualization
- `backtrader`: Backtesting framework for trading strategies
- `numpy`: Numerical computations
- `seaborn`: Statistical visualizations

### Hugo Configuration

From `hugo.toml`:
- Theme: `hugo-book` (documentation-focused theme)
- Math rendering enabled via Goldmark extensions (LaTeX support with `$...$` and `$$...$$`)
- Korean language site with English technical terms
- Git info enabled for "last modified" dates
- Table of contents enabled on right side

## Working with This Repository

**Using Hugo CLI**: AI assistants should leverage the `hugo` CLI tool for:
- Creating new content with proper structure (`hugo new`)
- Validating syntax and configuration (`hugo config`, `hugo --renderToMemory`)
- Previewing changes in real-time (`hugo server`)
- Building the final site (`hugo`)

### Adding New Chapters

When creating a new chapter:

1. **Create markdown file using Hugo CLI** (recommended):
   ```bash
   hugo new content/docs/chapterXX.md
   ```
   - Alternatively, create manually: `content/docs/chapterXX.md`
   - Include frontmatter with `title`, `weight`, and `bookToc: true`
   - Write theory with LaTeX math formulas (in Korean, primary language)
   - Reference code files that will be created
   - Include analysis and interpretation of results
   - Use `hugo server` to preview changes in real-time

2. **Create code directory**: `codes/chapterXX/`
   - Create numbered scripts: `01_descriptive_name.py`, `02_next_concept.py`
   - Use relative paths: `os.path.join(os.path.dirname(__file__), "..", "data")`
   - Generate visualizations to `chapterXX/images/` subdirectory
   - Follow existing code patterns from previous chapters

3. **Validate and test**:
   ```bash
   hugo --renderToMemory  # Check for syntax errors
   hugo server            # Preview the site
   ```

4. **Update `codes/README.md`**: Add execution instructions for new chapter (in Korean)

### Code Execution Flow

Typical workflow for code examples:
1. Download data using `yfinance` → Save to `codes/data/`
2. Process data with `pandas` → Calculate indicators, statistics
3. Visualize with `matplotlib` → Save charts to `chapterXX/images/`
4. Run backtests with `backtrader` → Print performance metrics
5. Output is displayed in terminal and saved as files (no GUI)

### Data Management

- Stock data is downloaded to `codes/data/` in CSV format
- Data files are gitignored (users download fresh data when running scripts)
- Scripts check for existing data and reuse when appropriate
- All data paths use relative paths based on script location

### Mathematical Content

The book includes rigorous mathematical explanations:
- Returns: $R_t = \frac{P_t - P_{t-1}}{P_{t-1}}$
- Performance metrics: Sharpe Ratio, Maximum Drawdown, Annualized Return
- Technical indicators: Moving averages, RSI, MACD, Bollinger Bands
- Use LaTeX syntax in markdown with `$` (inline) or `$$` (block)

### Style Considerations

**For markdown chapters (PRIMARY LANGUAGE: KOREAN):**
- **Write ALL explanatory text in Korean (한국어)** - this is the primary language of the book
- Preserve English for technical terms when appropriate (backtesting, OHLCV, Sharpe Ratio, etc.)
- Include practical examples and real data analysis
- Balance theory (mathematical formulas) with practice (code execution)
- Mathematical notation uses standard English symbols (e.g., $R_t$, not localized)

**For Python code:**
- Self-documenting code with clear variable names (English)
- Docstrings in English for functions (standard practice)
- **Print statements and user-facing output in Korean** (matches book language)
- Comments can be in English or Korean, prefer Korean when explaining concepts
- Handle errors gracefully (internet connection, missing data)
- Use type hints where helpful
- Follow patterns from existing chapter code

### References Directory

`references/` contains comprehensive guides for key libraries:
- `backtrader.md`: Full backtrader framework documentation
- `yfinance.md`: Yahoo Finance API usage guide

Consult these when implementing strategies or downloading data.

## Current Progress

**Complete restart in progress - New 18-chapter structure planned**

The book follows a balanced approach covering:
- Technical Analysis Strategies (40%)
- Portfolio Management (25%)
- Machine Learning (20%)
- Foundations & Real-World Application (15%)

See `TABLE_OF_CONTENTS.md` for the complete 18-chapter plan.

Target audience: Readers with basic Python knowledge (variables, loops, functions)

**Status**: Planning phase complete, ready to begin writing chapters
