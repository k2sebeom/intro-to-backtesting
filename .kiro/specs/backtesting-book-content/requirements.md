# Requirements Document

## Introduction

This feature will systematically generate comprehensive content for a Korean backtesting book, covering 22 chapters (0-21) with trading strategies and algorithms. Each chapter will include both executable Python code examples and detailed written content explaining the concepts, implementation, and results.

## Requirements

### Requirement 1

**User Story:** As a book author, I want to generate executable Python code examples for each trading strategy chapter, so that readers can follow along with practical implementations.

#### Acceptance Criteria

1. WHEN a chapter code generation task is executed THEN the system SHALL create a dedicated folder under `./codes/chapter{XX}` for that chapter
2. WHEN generating code THEN the system SHALL implement the specific trading algorithm described in the chapter outline
3. WHEN creating code examples THEN the system SHALL use the existing NVIDIA stock data from `codes/data/NVDA_1year.csv`
4. WHEN implementing algorithms THEN the system SHALL include proper data loading, strategy implementation, backtesting, and visualization components
5. WHEN generating visualizations THEN the system SHALL save plots as PNG files without using popup displays (no `plt.show()` or `cv2.imshow()`)
6. WHEN creating code THEN the system SHALL ensure all code is executable via `uv run chapter{XX}/filename.py` from the codes directory
7. WHEN implementing strategies THEN the system SHALL use appropriate libraries (yfinance, matplotlib, backtrader, pandas, numpy)
8. WHEN generating outputs THEN the system SHALL create both console outputs and image files that demonstrate the strategy results

### Requirement 2

**User Story:** As a book author, I want to generate comprehensive chapter content in Korean, so that readers can understand the theory, implementation, and results of each trading strategy.

#### Acceptance Criteria

1. WHEN a chapter writing task is executed THEN the system SHALL create a markdown file at `content/docs/chapter{XX}.md`
2. WHEN writing chapter content THEN the system SHALL start with detailed algorithm explanations including mathematical formulas
3. WHEN explaining algorithms THEN the system SHALL provide step-by-step implementation guidance with code snippets
4. WHEN including code examples THEN the system SHALL reference the actual generated code files and explain their execution
5. WHEN showing results THEN the system SHALL include actual outputs (console output and images) from running the generated code
6. WHEN adding images THEN the system SHALL move generated images to `static/images/chapter{XX}/` and reference them properly in markdown
7. WHEN writing content THEN the system SHALL use Korean language throughout the chapter
8. WHEN structuring content THEN the system SHALL follow the established format: algorithm theory → implementation guide → code execution → results analysis
9. WHEN completing a chapter THEN the system SHALL ensure the content is compatible with Hugo static site generator and hugo-book theme

### Requirement 3

**User Story:** As a book author, I want to maintain consistency across all chapters, so that the book provides a cohesive learning experience.

#### Acceptance Criteria

1. WHEN generating any chapter content THEN the system SHALL follow the established project structure and naming conventions
2. WHEN creating code examples THEN the system SHALL use consistent coding style and documentation patterns across all chapters
3. WHEN writing chapters THEN the system SHALL maintain consistent Korean writing style and technical terminology
4. WHEN implementing strategies THEN the system SHALL use the same base data source (NVIDIA stock data) for comparability
5. WHEN generating visualizations THEN the system SHALL use consistent chart styling and formatting across chapters
6. WHEN completing chapters THEN the system SHALL ensure each chapter builds upon concepts from previous chapters appropriately

### Requirement 4

**User Story:** As a book author, I want to validate that all generated content works correctly, so that readers can successfully follow the examples.

#### Acceptance Criteria

1. WHEN code is generated THEN the system SHALL execute the code to verify it runs without errors
2. WHEN images are generated THEN the system SHALL verify the image files are created and readable
3. WHEN chapters are written THEN the system SHALL verify that Hugo can build the site successfully
4. WHEN referencing code outputs THEN the system SHALL include actual execution results rather than placeholder content
5. WHEN completing a chapter THEN the system SHALL verify all image references and code snippets are accurate and functional