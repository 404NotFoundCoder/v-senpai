# v-senpai-3.1

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

## PWA（可安裝、離線殼層）

使用 [vite-plugin-pwa](https://vite-pwa-org.netlify.app/)：`npm run build` 後會產生 `manifest.webmanifest`、`sw.js`，並自動註冊 Service Worker（`registerType: 'autoUpdate'`）。

- **安裝**：部署到 **HTTPS**（如 Vercel）後，瀏覽器可「加入主畫面／安裝應用程式」。
- **離線**：已快取的靜態資源可離線開啟；動態資料（Firebase 等）仍須連線。
- **本機測 Service Worker**：在 `vite.config.ts` 將 `devOptions.enabled` 改為 `true` 後再 `npm run dev`（用完建議改回 `false`）。
- **圖示**：使用 `public/logo.png`；若更換圖檔請維持路徑或一併更新 `manifest.icons`。
