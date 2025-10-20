---
title: "Configuration"
weight: 10
---

# Configuration

This page covers advanced configuration options.

## Theme Configuration

You can customize the theme by modifying your `hugo.toml` file:

```toml
[params]
  BookTheme = 'auto'  # light, dark, or auto
  BookToC = true      # Show table of contents
  BookSearch = true   # Enable search
```

## Custom Styling

Create `assets/_custom.scss` to add custom styles:

```scss
.book-brand {
  color: #007acc;
}
```