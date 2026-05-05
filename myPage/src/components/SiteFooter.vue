<template>
    <footer class="site-footer">
        <div>
            © 2026 古亦弘 •
            <span class="social-icon">💼</span>
            <a href="https://pda.104.com.tw/profile/share/eVHTjap6lkYwZJnYR0BQEZLmNB29r05D" target="_blank">104
                Resume</a> •
            <a href="https://accompartner.dev" target="_blank">Accompartner.dev</a> •
            <a href="mailto:hank.ku43@gmail.com">Email Me</a>
        </div>
    </footer>
</template>

<style scoped>
.site-footer {
    margin-top: 80px;
    padding: 40px 0;
    text-align: center;
    font-size: 14px;
    color: #475569;
    border-top: 1px solid rgba(0, 0, 0, 0.05);

    /* 設定優先順序：英數字用 Inter -> Mac 用蘋方 -> Win 用思源黑體 -> 備用系統黑體 */
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;

    /* 讓字體邊緣更平滑銳利 (Mac/iOS 神器) */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.mode-dark .site-footer {
    color: #e6eef8;
    border-top-color: rgba(255, 255, 255, 0.05);
}

.social-icon {
    margin-right: 4px;
}

a {
    color: inherit;
    text-decoration: none;
}

a:hover {
    color: #3b82f6;
}

/* ===== RWD ===== */
@media (max-width: 1023px) {
    .site-footer {
        margin-top: 60px;
        padding: 32px 0;
    }
}

@media (max-width: 767px) {
    .site-footer {
        margin-top: 36px;
        padding: 24px 16px;
        font-size: 13px;
        line-height: 1.8;
    }
}
</style>