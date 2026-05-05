<template>
    <n-config-provider :theme="isDark ? darkTheme : null">
        <div :class="{ 'mode-dark': isDark }">

            <SiteHeader v-model:isDark="isDark" />

            <main class="main-content">

                <IntroSection @open-video="handleVideoModal" />

                <ResumeSection />

                <SiteFooter />
            </main>

            <VideoModal v-model:show="showModal" />

        </div>
    </n-config-provider>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { NConfigProvider, darkTheme } from 'naive-ui';

import SiteHeader from '../components/SiteHeader.vue';
import IntroSection from '../components/IntroSection.vue';
import ResumeSection from '../components/ResumeSection.vue';
import SiteFooter from '../components/SiteFooter.vue';
import VideoModal from '../components/VideoModal.vue';

const isDark = ref(false);
const showModal = ref(false);
const handleVideoModal = () => { showModal.value = true; };

onMounted(() => {
    isDark.value = localStorage.getItem('mypage-theme-dark') === 'true';
});

watch(isDark, (val) => {
    localStorage.setItem('mypage-theme-dark', val);
});

</script>

<style scoped>
/* 這裡保留背景與光暈效果即可 */
.mode-dark {
    background-color: #020617;
    color: #e6eef8;
}

.main-content {
    width: 100%;
    margin: 0;
    padding-top: var(--header-height, 64px);
    background: linear-gradient(180deg, #f3f6fb, #ffffff);
    transition: color 0.5s, background 0.5s;
    position: relative;
    z-index: 1;
}

/* 保持全螢幕的動態光暈效果 */
.main-content::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 20% 30%, rgba(120, 161, 255, 0.45), transparent 65%),
        radial-gradient(circle at 80% 70%, rgba(200, 160, 255, 0.4), transparent 80%);
    z-index: -1;
    animation: subtleGlow-light 8s ease-in-out infinite alternate;
}

.mode-dark .main-content {
    background: linear-gradient(180deg, #1a1c2e, #0f172a, #1e1b4b);
}

.mode-dark .main-content::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 20%, rgba(56, 189, 248, 0.4), transparent 70%), radial-gradient(circle at 70% 80%, rgba(168, 85, 247, 0.2), transparent 75%);
    mix-blend-mode: screen;
    z-index: -1;
    animation: subtleGlow 12s ease-in-out infinite alternate;
}

@keyframes subtleGlow-light {
    0% {
        opacity: 0.4;
    }

    100% {
        opacity: 0.9;
    }
}

@keyframes subtleGlow {
    0% {
        opacity: 0.5;
    }

    100% {
        opacity: 0.95;
    }
}

@media (max-width: 767px) {
    .main-content {
        padding-left: 0;
        padding-right: 0;
    }
}
</style>