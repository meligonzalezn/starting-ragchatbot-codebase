# Frontend Changes

## Feature: Dark / Light Theme Toggle

### Files Modified

#### `frontend/index.html`
- Added a `<button id="themeToggle">` element fixed to the top-right corner of the viewport (inserted directly inside `<body>`, before `.container`).
- The button contains two SVG icons:
  - `.sun-icon` — displayed in dark mode; clicking switches to light theme.
  - `.moon-icon` — displayed in light mode; clicking switches back to dark theme.
- `aria-label` and `title` attributes ensure the button is accessible and keyboard-navigable.

#### `frontend/style.css`
- **Light theme variables** — added `html[data-theme="light"]` block that overrides all CSS custom properties:
  - `--background: #f8fafc` / `--surface: #ffffff` / `--surface-hover: #f1f5f9`
  - `--text-primary: #0f172a` / `--text-secondary: #64748b`
  - `--border-color: #e2e8f0`
  - `--assistant-message: #f1f5f9`
  - `--shadow` reduced opacity for the lighter environment
  - `--welcome-bg: #dbeafe`
- **Smooth transitions** — added `transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease` on all major structural elements (`body`, `.sidebar`, `.chat-messages`, `.message-content`, `.suggested-item`, `#chatInput`, etc.) so theme switches animate smoothly.
- **`.theme-toggle` button styles** — circular, fixed-position button (`2.5rem × 2.5rem`) using CSS variable colors so it adapts to both themes. Includes `:hover` (scale + accent colour) and `:focus` (focus-ring) states.
- **Icon visibility** — `.sun-icon` shown / `.moon-icon` hidden by default (dark mode); selectors under `html[data-theme="light"]` invert that.

#### `frontend/script.js`
- **`initTheme` IIFE** — runs immediately on script load (before `DOMContentLoaded`) to read `localStorage.getItem('theme')` and set `html[data-theme="light"]` if the user previously chose light mode. This prevents a flash of the default dark theme.
- **`toggleTheme()`** — reads the current `data-theme` attribute on `<html>`, toggles it between light and dark, and persists the choice to `localStorage`.
- **`setupEventListeners()`** — wired `document.getElementById('themeToggle').addEventListener('click', toggleTheme)`.
