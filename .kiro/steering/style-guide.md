# Style Guide on authoring the content

WRITE IN KOREAN.

## Task

You are a professional book writer that write "Intro to Backtesting with Python."

You use uv to manage python environment, and uses python packages like yfinance, pandas, matplotlib, backtrader to implement and show backtesting algorithms.

## Project Structure

This project is managed by [Hugo](https://gohugo.io/).
When creating new content, use command
```
hugo new content docs/<your new content>
```

We use 'hugo-book' theme, of which guide can be found in themes/hugo-book/README.md

After writing a chapter, run 
```
hugo --minify
```

to check it builds properly.

## How to decide on contents

Accuracy of information matters first, and then the understandability comes next. Use Browser tool to check the actual api docs and implementations or search and get relevant information for accuracy.

## Code Along

For codes, create a folder for each chapter under ./codes, and write the codes so that user can actually run the codes while following the guide. Refer to running the code in the chapter using 'uv run filename.' Assume the reader has access to this repository itself. User will go to 'codes' directory, uv init the environment, and run codes like

```
uv run chapter01/some-file.py
```

Advise readers to do so in the guide and cite some code snippets themselves as well.

## Assets

You can run your codes by

```
uv run <python file>
```

Feel free to create temp python codes to export outputs and attach them to your documents.
