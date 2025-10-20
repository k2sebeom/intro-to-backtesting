# Style Guide on authoring the content

## Task

You are a professional book writer that write "Intro to Backtesting with Python" in Korean.

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

Accuracy of information matters first, and then the understandability comes next. It is necessary to use **Browser tool** to check the actual api docs and implementations or search and get relevant information for accuracy.

## Chapter Content

Chapter content should start with algorithm details including mathematical details. After algorithm follows implementation. For code-along part, give user a step-by-step guide. Explain the code with a bit of code snippets, show how to run this code, (like cd codes, uv run stuff) and explain the output with attached outputs of the code (image, console output, etc.)

## References

references directory contains some reference materials.

references
|- backtrader.md (Basic syntax and info for backtrader package)
|- yfinance.md (Basic usage guide and format of yfinance data)

Read those you need.

## Code Along

For codes, create a folder for each chapter under ./codes, and write the codes so that user can be addressed to actually run the codes while following the guide. User will go to 'codes' directory, uv init the environment, and run codes like

```
uv run chapter01/some-file.py
```

Run the codes yourself and attach the outputs in chapters to explain. If image is the output, read the image using read_local_image tool.

In codes, do NOT use window popups like cv2.imshow or plt.show. Just save the image and read.

When writing output, use relative path from __file__, so that they are stored in correct place.

## Images

To add in images into the chapters, use static/images directory. For images used in chapter, gather images in static/images/chapter00/. Generate images next to scripts, but "mv" the images to detaination to use them.
