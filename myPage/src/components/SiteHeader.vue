<template>
    <header ref="headerRef" class="site-header">
        <div class="left">
            <div class="brand">Hank Ku • Portfolio</div>
            <nav class="header-nav">
                <a href="#resume-detail" @click.prevent="scrollTo('resume-detail')">關於我</a>

                <n-dropdown :options="imageOptions" placement="bottom-start" @select="handleNavigate">
                    <a href="#" @click.prevent class="dropdown-link">
                        影像處理 <span class="arrow">▾</span>
                    </a>
                </n-dropdown>

                <n-dropdown :options="nlpOptions" placement="bottom-start" @select="handleNavigate">
                    <a href="#" @click.prevent class="dropdown-link">
                        自然語言處理 <span class="arrow">▾</span>
                    </a>
                </n-dropdown>

                <n-dropdown :options="otherOptions" placement="bottom-start" @select="handleNavigate">
                    <a href="#" @click.prevent class="dropdown-link">
                        其他展示 <span class="arrow">▾</span>
                    </a>
                </n-dropdown>
            </nav>
        </div>
        <div class="right">
            <label>
                <span class="l">{{ isDark ? '深色模式' : '淺色模式' }}</span>
                <n-switch :value="isDark" @update:value="$emit('update:isDark', $event)" size="large">
                    <template #checked-icon><span class="switch-icon">🌙</span></template>
                    <template #unchecked-icon><span class="switch-icon">☀️</span></template>
                </n-switch>
            </label>
            <button
                class="menu-toggle"
                :class="{ open: menuOpen }"
                @click="menuOpen = !menuOpen"
                aria-label="開啟選單"
            >
                <span></span>
            </button>
        </div>

        <!-- 手機版 nav：position: absolute 相對於 fixed header -->
        <Transition name="slide-down">
            <nav v-if="menuOpen" class="mobile-nav">
                <a href="#resume-detail" @click.prevent="mobileScrollTo('resume-detail')">關於我</a>
                <p class="mobile-nav-label">影像處理</p>
                <a v-for="p in imageOptions" :key="p.key" @click="mobileNavigate(p.key)">{{ p.label }}</a>
                <p class="mobile-nav-label">自然語言處理</p>
                <a v-for="p in nlpOptions" :key="p.key" @click="mobileNavigate(p.key)">{{ p.label }}</a>
                <p class="mobile-nav-label">其他展示</p>
                <a v-for="p in otherOptions" :key="p.key" @click="mobileNavigate(p.key)">{{ p.label }}</a>
            </nav>
        </Transition>
    </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { NSwitch, NDropdown } from 'naive-ui';
import { projects } from '../data/projects.js';

defineProps(['isDark']);
defineEmits(['update:isDark']);

const router = useRouter();
const headerRef = ref(null);
const menuOpen = ref(false);
let lastScroll = 0;

const byType = (type) =>
    projects.filter(p => p.type === type).map(p => ({ label: p.name, key: p.id }));

const imageOptions = computed(() => byType('image'));
const nlpOptions   = computed(() => byType('nlp'));
const otherOptions = computed(() => byType('other'));

const handleNavigate = (key) => {
    router.push(`/demo/${key}`);
};

const mobileNavigate = (key) => {
    menuOpen.value = false;
    router.push(`/demo/${key}`);
};

const mobileScrollTo = (id) => {
    menuOpen.value = false;
    scrollTo(id);
};

const handleScroll = () => {
    const currentScroll = window.scrollY;
    if (currentScroll > lastScroll && currentScroll > 50) {
        headerRef.value.style.top = '-64px';
        menuOpen.value = false;
    } else {
        headerRef.value.style.top = '0';
    }
    lastScroll = currentScroll;
};

const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
        const headerOffset = -20;
        const elementPosition = el.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth' // 平滑滾動
        });
    }
};

onMounted(() => window.addEventListener('scroll', handleScroll));
onBeforeUnmount(() => window.removeEventListener('scroll', handleScroll));
</script>

<style scoped>
/* (保留原本的 Header 樣式) */
.site-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    z-index: 60;
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(12px);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s;

    /* 設定優先順序：英數字用 Inter -> Mac 用蘋方 -> Win 用思源黑體 -> 備用系統黑體 */
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;

    /* 讓字體邊緣更平滑銳利 (Mac/iOS 神器) */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.mode-dark .site-header {
    background: rgba(0, 0, 0, 0.4);
    color: #e6eef8;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.left {
    display: flex;
    align-items: center;
    gap: 40px;
}

.brand {
    font-weight: 700;
    font-size: 18px;
}

.header-nav {
    display: flex;
    gap: 24px;
    align-items: center;
}

.header-nav a {
    font-family: Inter, "Noto Sans TC", sans-serif;
    color: inherit;
    text-decoration: none;
    font-weight: 600;
    font-size: 15px;
    transition: color 0.2s;
    cursor: pointer;
}

.header-nav a:hover {
    color: #3b82f6;
}

.mode-dark .header-nav a:hover {
    color: #4ecdc4;
}

.dropdown-link {
    display: flex;
    align-items: center;
    gap: 4px;
}

.arrow {
    font-size: 12px;
    margin-top: 2px;
}

.switch-icon {
    display: inline-block;
    transition: transform 0.5s;
}

.n-switch__button:hover .switch-icon {
    transform: rotate(20deg);
}

.switch-label {
    font-size: 12px;
    margin-right: 10px;
}

.l {
    font-family: 'Inter', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
    font-size: 12px;
    margin-right: 10px;
}

/* ===== 漢堡按鈕 ===== */
.menu-toggle {
    display: none;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 36px;
    height: 36px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    margin-left: 10px;
    color: inherit;
}

.menu-toggle span,
.menu-toggle span::before,
.menu-toggle span::after {
    display: block;
    width: 22px;
    height: 2px;
    background: currentColor;
    border-radius: 2px;
    transition: all 0.3s ease;
    position: relative;
}

.menu-toggle span::before,
.menu-toggle span::after {
    content: '';
    position: absolute;
}

.menu-toggle span::before { top: -7px; }
.menu-toggle span::after  { top:  7px; }

.menu-toggle.open span { background: transparent; }
.menu-toggle.open span::before {
    top: 0;
    transform: rotate(45deg);
}
.menu-toggle.open span::after {
    top: 0;
    transform: rotate(-45deg);
}

/* ===== 手機版 nav ===== */
.mobile-nav {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.97);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    padding: 12px 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    z-index: 59;
}

.mode-dark .mobile-nav {
    background: rgba(2, 6, 23, 0.97);
    border-bottom-color: rgba(255, 255, 255, 0.07);
}

.mobile-nav-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 12px 0 2px 12px;
    padding: 0;
}

.mobile-nav a {
    font-family: 'Inter', 'Noto Sans TC', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: inherit;
    text-decoration: none;
    padding: 9px 14px;
    border-radius: 10px;
    transition: background 0.18s, color 0.18s;
    display: block;
    cursor: pointer;
}

.mobile-nav a:hover,
.mobile-nav a:active {
    background: rgba(59, 130, 246, 0.07);
    color: #3b82f6;
}

.mode-dark .mobile-nav a:hover,
.mode-dark .mobile-nav a:active {
    background: rgba(78, 205, 196, 0.08);
    color: #4ecdc4;
}

/* ===== slide-down 過場 ===== */
.slide-down-enter-active,
.slide-down-leave-active {
    transition: opacity 0.22s ease, transform 0.22s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
    opacity: 0;
    transform: translateY(-8px);
}

/* ===== Tablet & Mobile breakpoints ===== */

/* Tablet：1024px 以下縮減 gap */
@media (max-width: 1023px) {
    .site-header { padding: 0 24px; }
    .left { gap: 24px; }
    .header-nav { gap: 16px; }
}

/* Mobile：768px 以下啟用漢堡選單 */
@media (max-width: 767px) {
    .site-header { padding: 0 16px; }
    .left { gap: 0; }
    .header-nav { display: none; }
    .menu-toggle { display: flex; }
    .l { display: none; }
}
</style>