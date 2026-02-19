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

## Code Quality Tooling Added

### Prettier Formatting
All frontend files have been formatted with [Prettier](https://prettier.io/) for consistent style.

**Files formatted:**
- `frontend/index.html`
- `frontend/style.css`
- `frontend/script.js`

**Config:** `.prettierrc` at project root
```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": false,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "htmlWhitespaceSensitivity": "css",
  "endOfLine": "lf"
}
```

### ESLint Setup
ESLint flat config added for `frontend/script.js`.

**Config:** `eslint.config.js` at project root
- Target: `frontend/**/*.js`
- Globals: `window`, `document`, `fetch`, `console`, `marked`
- Rules: `no-unused-vars` (warn), `no-undef` (error), `eqeqeq` (error), `prefer-const` (warn)

### npm Scripts
`package.json` added with frontend-specific scripts:
```
npm run format        # prettier --write frontend/
npm run format:check  # prettier --check frontend/
npm run lint          # eslint frontend/script.js
```

## Development Scripts

Three shell scripts added under `scripts/`:

| Script | Purpose |
|---|---|
| `scripts/format.sh` | Auto-format all Python + frontend code |
| `scripts/lint.sh` | Check all code without modifying (CI-safe) |
| `scripts/quality.sh` | Run format then lint (full quality pass) |

Run from project root:
```bash
bash scripts/format.sh   # fix all formatting
bash scripts/lint.sh     # check only (exits 1 on failure)
bash scripts/quality.sh  # format + check
```
