<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+TC:wght@400;500;600;700;900&display=swap');

/*
 * =============================================
 * 全站統一 RWD Breakpoints（桌面優先）
 * Desktop  : ≥ 1024px  → 預設樣式（無 media query）
 * Tablet   : 768–1023px → @media (max-width: 1023px)
 * Mobile   : < 768px   → @media (max-width: 767px)
 * =============================================
 */

:root {
  --bg-light: #f1f5f9;
  --text-light: #0f1724;
  --subtext-light: #475569;
  --card-bg-light: #ffffff;

  --bg-dark: #020617;
  --text-dark: #e6eef8;
  --subtext-dark: #cbd5e1;
  --card-bg-dark: #071226;

  --header-height: 64px;
}

* {
  box-sizing: border-box;
}

body,
html,
#app {
  height: 100%;
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
  background-color: var(--bg-light);
  color: var(--text-light);
  transition: background 0.5s, color 0.5s;
}

/* --- 保留你原本的 Loading Overlay 樣式 --- */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
  transition: opacity 0.3s ease;
}

.mode-dark .loading-overlay {
  background: rgba(0, 0, 0, 0.6);
}

.spinner {
  width: 60px;
  height: 60px;
  border: 6px solid rgba(0, 0, 0, 0.1);
  border-top: 6px solid #3eaf7c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.mode-dark .spinner {
  border: 6px solid rgba(255, 255, 255, 0.1);
  border-top: 6px solid #4ecdc4;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  font-family: Inter, "Noto Sans TC", sans-serif;
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
  letter-spacing: 1px;
}

@media (max-width: 767px) {
  .spinner {
    width: 44px;
    height: 44px;
  }
  .loading-overlay p {
    font-size: 0.95rem;
  }
}

.mode-dark .loading-overlay p {
  color: #eee;
}

#app-container, body {
  /* 科技感與易讀性的完美組合 */
  font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
  
  /* 讓字體渲染更細膩的設定 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  
  /* 預設字體顏色，讓整體質感更高級 (避開全黑) */
  color: #1e293b;
}

/* 如果有深色模式，也要在這邊統一處理 */
.mode-dark #app-container, .mode-dark body {
  color: #f8fafc;
}

/* 移除預設的 margin，確保滿版效果 */
body {
  margin: 0;
  padding: 0;
}
</style>