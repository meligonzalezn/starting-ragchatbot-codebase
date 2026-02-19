# Frontend Changes

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
