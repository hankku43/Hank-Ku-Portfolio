<template>
    <section id="about" class="intro-section">
        <div class="bento-grid">

            <!-- ===== 個人簡介 ===== -->
            <div class="bento-box glass bio-box">
                <div class="profile-header">
                    <div class="avatar-wrap">
                        <div class="avatar"></div>
                    </div>
                    <div class="title-group">
                        <h1 class="name">古亦弘</h1>
                        <h2 class="role">AI 全端服務工程師</h2>
                    </div>
                </div>
                <div class="bio-content">
                    <p class="bio-text">
                        臺大森林系碩士畢，具備金融業 B2E 系統 JAVA 全端開發經驗。近期深入 AI
                        領域，以<strong>PyTorch</strong>、<strong>Transformers.js</strong>
                        等工具，從<strong>資料清洗</strong>到<strong>Transformer 模型架構設計及訓練</strong>整合至 Web
                        服務。<strong>熟悉基礎技術</strong>，以紙跟筆就能訓練模型。熱衷於跨領域技術結合，致力以<strong>AI/深度學習</strong>架構開發流暢的智能產品。
                    </p>
                    <div class="bio-action">
                        <span class="sparkle">✨</span> 體驗我的 AI 智慧伴奏服務：
                        <a href="https://accompartner.dev/" rel="noopener noreferrer" target="_blank"
                            class="bio-link">AccomPartner</a>
                    </div>
                </div>
            </div>

            <!-- ===== 其他小型專案 (升級版跑馬燈) ===== -->
            <div class="bento-box glass marquee-box" @mouseenter="pausePlay" @mouseleave="startPlay">

                <div class="marquee-header">
                    <h3>Other Projects / 其他小型專案</h3>
                    <div class="project-filters">
                        <button class="pf-btn" :class="{ active: activeFilter === 'all' }"
                            @click="setFilter('all')">All</button>
                        <button class="pf-btn" :class="{ active: activeFilter === 'image' }"
                            @click="setFilter('image')">影像處理</button>
                        <button class="pf-btn" :class="{ active: activeFilter === 'nlp' }"
                            @click="setFilter('nlp')">自然語言處理</button>
                        <button class="pf-btn" :class="{ active: activeFilter === 'other' }"
                            @click="setFilter('other')">其他展示</button>
                    </div>
                </div>

                <!-- 空白狀態 -->
                <div v-if="filteredProjects.length === 0" class="empty-state">
                    此分類目前暫無專案
                </div>

                <!-- 輪播 -->
                <div v-else class="carousel-viewport">
                    <div class="carousel-track"
                        :class="{ 'fast-return': isReturning }"
                        :style="{ transform: `translateX(calc(-${currentIndex} * (${carouselStep})))` }">

                        <div class="mini-card" v-for="proj in filteredProjects" :key="proj.id" @click="openModal(proj)">
                            <div class="mini-thumb">
                                <img :src="proj.image" :alt="proj.name" />
                                <div class="mini-hover-overlay">
                                    <span>查看詳情 →</span>
                                </div>
                                <span class="mini-badge" :class="proj.type">{{ typeLabel(proj.type) }}</span>
                            </div>
                            <div class="mini-info">
                                <h4 class="mini-name">{{ proj.name }}</h4>
                                <div class="mini-tags-row">
                                    <span v-for="tag in proj.tags.slice(0, 2)" :key="tag">{{ tag }}</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- 箭頭（比可視數量多才顯示） -->
                <div v-if="showArrows" class="custom-arrow">
                    <button type="button" class="arrow-btn left" @click="prev">
                        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2.5"
                            fill="none" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="15 18 9 12 15 6"></polyline>
                        </svg>
                    </button>
                    <button type="button" class="arrow-btn right" @click="next">
                        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2.5"
                            fill="none" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    </button>
                </div>

                <!-- 點點導航 -->
                <div v-if="maxIndex > 0" class="custom-dots">
                    <span v-for="i in (maxIndex + 1)" :key="i" class="dot"
                        :class="{ active: currentIndex === i - 1 }"
                        @mouseenter="goTo(i - 1)">
                    </span>
                </div>

            </div>

            <!-- ===== AccomPartner 主要展示 ===== -->
            <div class="bento-box glass accom-box">
                <div class="video-wrapper"
                     @mouseenter="onVideoEnter"
                     @mouseleave="onVideoLeave">

                    <!-- 靜態封面 -->
                    <img v-show="!videoHovered" src="/images/previews/accompartner.png" alt="Accompartner Video" class="bg-img" />

                    <!-- Hover 時 inline 播放 -->
                    <video v-if="videoHovered"
                        :src="'/videos/demo.mp4'"
                        autoplay muted loop playsinline
                        class="inline-iframe"
                    ></video>

                    <!-- 點擊捕捉層（hover 狀態且尚未點擊） -->
                    <div v-if="videoHovered && !videoClicked" class="iframe-click-catcher" @click="onVideoClick"></div>

                    <!-- 2 秒後出現的點擊提示動畫 -->
                    <Transition name="hint-fade">
                        <div v-if="showClickHint && videoHovered && !videoClicked" class="click-hint">
                            <div class="hint-tap-icon">
                                <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 4.1 12 6" />
                                    <path d="m5.1 8-2.9-.8" />
                                    <path d="m6 12-1.9 2" />
                                    <path d="M7.2 2.2 8 5.1" />
                                    <path d="M9.037 9.69a.498.498 0 0 1 .653-.653l11 4.5a.5.5 0 0 1-.074.949l-4.349 1.041a1 1 0 0 0-.74.739l-1.04 4.35a.5.5 0 0 1-.95.074z" />
                                </svg>
                            </div>
                            <span class="hint-label">點擊查看更多</span>
                        </div>
                    </Transition>

                    <!-- 預設播放按鈕（idle 狀態） -->
                    <div class="video-overlay" v-show="!videoHovered">
                        <div class="play-btn">
                            <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                                <path d="M8 5v14l11-7z" />
                            </svg>
                        </div>
                    </div>

                    <!-- 點擊後顯示的行動按鈕 -->
                    <Transition name="btn-pop">
                        <div v-if="videoClicked" class="video-action-overlay" @click.stop>
                            <button @click="$emit('open-video')" class="action-btn yt-btn">
                                🎬 查看完整DEMO影片
                            </button>
                            <a href="https://accompartner.dev/"
                               target="_blank" rel="noopener noreferrer"
                               class="action-btn create-btn">
                                🎹 立即前往伴伴開始創作
                            </a>
                        </div>
                    </Transition>
                </div>

                <div class="info-wrapper">
                    <div class="info-header">
                        <span class="highlight-tag">🔥 主打專案</span>
                        <div class="title-row">
                            <h3 class="project-title">AccomPartner AI 鋼琴伴奏生成系統</h3>
                            <a href="https://accompartner.dev/" target="_blank" rel="noopener noreferrer" class="try-btn">
                                立即體驗
                                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M5 12h14M12 5l7 7-7 7"/>
                                </svg>
                            </a>
                        </div>
                    </div>
                    <p class="project-desc">
                        定位為 Premium Musical IDE 的混合推論 (Hybrid Inference) 伴奏平台。以 Symusic 與 REMI 構建資料清洗引擎；模型層涵蓋 PyTorch
                        Transformer 的多小節後端生成，以及 Hugging Face BART 搭配 ONNX 的前端 Edge Inference 即時伴奏。並整合 Tone.js 多音發聲與
                        VexFlow 動態五線譜渲染，打造極致的專業音樂創作體驗。
                    </p>
                    <div class="tech-tags">
                        <span>Vue 3 / FastAPI</span>
                        <span>PyTorch</span>
                        <span>BART & ONNX</span>
                        <span>Tone.js</span>
                        <span>VexFlow</span>
                        <span>Symusic</span>
                    </div>
                </div>
            </div>

        </div>

        <!-- ===== 專案詳情 Modal ===== -->
        <Transition name="modal-fade">
            <div v-if="selectedProject" class="proj-modal-overlay" @click.self="closeModal">
                <div class="proj-modal glass">

                    <button class="proj-modal-close" @click="closeModal">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18"
                            height="18">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>

                    <div class="proj-modal-thumb">
                        <img :src="selectedProject.image" :alt="selectedProject.name" />
                        <span class="mini-badge large" :class="selectedProject.type">
                            {{ typeLabel(selectedProject.type) }}
                        </span>
                    </div>

                    <div class="proj-modal-body">
                        <h3 class="proj-modal-title">{{ selectedProject.name }}</h3>
                        <p class="proj-modal-desc">{{ selectedProject.fullDesc }}</p>

                        <div v-if="selectedProject.highlights?.length" class="proj-modal-highlights">
                            <h4>技術亮點</h4>
                            <ul>
                                <li v-for="h in selectedProject.highlights" :key="h">{{ h }}</li>
                            </ul>
                        </div>

                        <div class="tech-tags modal-tags">
                            <span v-for="tag in selectedProject.tags" :key="tag">{{ tag }}</span>
                        </div>

                        <div class="proj-modal-actions">
                            <button class="demo-btn" @click="goToDemo">
                                進入 Demo
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14"
                                    height="14">
                                    <line x1="5" y1="12" x2="19" y2="12" />
                                    <polyline points="12 5 19 12 12 19" />
                                </svg>
                            </button>
                            <a v-if="selectedProject.githubUrl" :href="selectedProject.githubUrl" target="_blank"
                                rel="noopener noreferrer" class="ghost-btn">GitHub</a>
                        </div>
                    </div>

                </div>
            </div>
        </Transition>

    </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { projects } from '../data/projects.js';

// ── 手機偵測 ──────────────────────────────────────────────
const isMobile = ref(false);
const updateMobile = () => { isMobile.value = window.innerWidth < 768; };

const router = useRouter();
defineEmits(['open-video']);

// video hover / click state
const videoHovered = ref(false);
const videoClicked = ref(false);
const showClickHint = ref(false);
let hintTimer = null;

const onVideoEnter = () => {
    videoHovered.value = true;
    hintTimer = setTimeout(() => { showClickHint.value = true; }, 2000);
};
const onVideoLeave = () => {
    videoHovered.value = false;
    videoClicked.value = false;
    showClickHint.value = false;
    clearTimeout(hintTimer);
};
const onVideoClick = () => {
    videoClicked.value = true;
    showClickHint.value = false;
    clearTimeout(hintTimer);
};

// ---- 篩選 ----
const activeFilter = ref('all');

const filteredProjects = computed(() =>
    activeFilter.value === 'all'
        ? projects
        : projects.filter(p => p.type === activeFilter.value)
);

const setFilter = (f) => {
    activeFilter.value = f;
    currentIndex.value = 0;
};

// ---- 輪播 ----
const currentIndex = ref(0);
const isReturning  = ref(false);

// 手機顯示 1 張，桌面顯示 2 張
const visibleCount  = computed(() => isMobile.value ? 1 : 2);
const carouselStep  = computed(() => isMobile.value ? '100% + 12px' : '50% + 6px');
const maxIndex      = computed(() => Math.max(0, filteredProjects.value.length - visibleCount.value));
const showArrows    = computed(() => filteredProjects.value.length > visibleCount.value);

let timer        = null;
let returnTimer  = null;

const next = () => {
    if (filteredProjects.value.length <= visibleCount.value) return;
    if (currentIndex.value >= maxIndex.value) {
        isReturning.value = true;
        currentIndex.value = 0;
        if (returnTimer) clearTimeout(returnTimer);
        returnTimer = setTimeout(() => { isReturning.value = false; }, 300);
    } else {
        currentIndex.value++;
    }
};
const prev = () => {
    if (filteredProjects.value.length <= visibleCount.value) return;
    currentIndex.value = currentIndex.value <= 0 ? maxIndex.value : currentIndex.value - 1;
};
const goTo = (i) => {
    currentIndex.value = i;
};

const pausePlay = () => {
    if (timer) { clearInterval(timer); timer = null; }
};
const startPlay = () => {
    pausePlay();
    if (filteredProjects.value.length > visibleCount.value) {
        timer = setInterval(next, 2800);
    }
};

watch(filteredProjects, () => {
    currentIndex.value = 0;
    startPlay();
});

watch(isMobile, () => {
    currentIndex.value = 0;
    startPlay();
});

onMounted(() => {
    updateMobile();
    window.addEventListener('resize', updateMobile);
    startPlay();
});
onUnmounted(() => {
    window.removeEventListener('resize', updateMobile);
    pausePlay();
    clearTimeout(hintTimer);
    document.body.style.overflow = '';
});

// ---- Modal ----
const selectedProject = ref(null);

const openModal = (p) => {
    selectedProject.value = p;
    document.body.style.overflow = 'hidden';
};
const closeModal = () => {
    selectedProject.value = null;
    document.body.style.overflow = '';
};
const goToDemo = () => {
    if (selectedProject.value) {
        router.push(`/demo/${selectedProject.value.id}`);
        closeModal();
    }
};

// ESC 關閉 modal
const handleKeydown = (e) => { if (e.key === 'Escape') closeModal(); };
onMounted(() => document.addEventListener('keydown', handleKeydown));
onUnmounted(() => document.removeEventListener('keydown', handleKeydown));

const typeMap = { image: '影像處理', nlp: '自然語言處理', other: '其他展示' };
const typeLabel = (t) => typeMap[t] ?? t;
</script>

<style scoped>
.glass,
.bio-content,
.profile-header,
.carousel-track,
.mini-card {
    min-width: 0;
}

.intro-section {
    min-height: calc(100vh - 64px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0px 4vw 0px;
    width: 100%;
    overflow: hidden;      /* 第二道防線：剪裁任何子元素溢出 */
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.bento-grid {
    display: grid;
    width: 100%;
    max-width: 100%;
    min-width: 0;          /* flex 子元素預設 min-width:auto，會撐破容器；強制允許縮到 0 */
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
    grid-template-areas:
        "bio accom"
        "marquee accom";
    gap: 24px;
}

.glass {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(16px);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.8);
    padding: 32px;
    display: flex;
    flex-direction: column;
}

.mode-dark .glass {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

.bio-box {
    grid-area: bio;
    justify-content: center;
}

.accom-box {
    grid-area: accom;
    padding: 24px;
    gap: 24px;
    justify-content: space-evenly;
    height: 100%;
}

/* ================= 個人簡介 ================= */
.profile-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
}

.avatar {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background-image: url("../assets/avatar.jpg");
    background-size: cover;
    background-position: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    transition: transform 0.4s ease, filter 0.4s ease;
}

.avatar:hover {
    transform: scale(1.05);
    filter: brightness(1.1);
}

.name {
    font-family: Inter, "Noto Sans TC", sans-serif;
    font-size: 28px;
    font-weight: 800;
    margin: 0 0 4px 0;
    color: #0f1724;
}

.mode-dark .name {
    color: #ffffff;
}

.role {
    font-size: 15px;
    color: #3b82f6;
    font-weight: 600;
    margin: 0;
}

.mode-dark .role {
    color: #4ecdc4;
}

.bio-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.bio-action {
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    background: rgba(59, 130, 246, 0.05);
    padding: 10px 16px;
    border-radius: 12px;
    border: 1px solid rgba(59, 130, 246, 0.1);
    display: block;
}

.mode-dark .bio-action {
    color: #cbd5e1;
    background: rgba(78, 205, 196, 0.05);
    border-color: rgba(78, 205, 196, 0.1);
}

.bio-link {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 800;
    transition: all 0.2s;
}

.bio-link:hover {
    color: #2563eb;
    text-decoration: underline;
}

.mode-dark .bio-link {
    color: #4ecdc4;
}

.mode-dark .bio-link:hover {
    color: #2dd4bf;
}

.bio-text {
    font-family: Inter, "Noto Sans TC", sans-serif;
    font-size: 15px;
    line-height: 1.8;
    color: #475569;
    text-align: justify;
    margin: 0;
}

.mode-dark .bio-text {
    color: #cbd5e1;
}

/* ================= 跑馬燈區域 ================= */
.marquee-box {
    grid-area: marquee;
    padding: 24px 28px 32px;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 0;
}

.marquee-header {
    width: 100%;
    margin-bottom: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding-left: 4px;
}

.marquee-header h3 {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 2px;
    margin: 0;
    text-transform: uppercase;
}

.mode-dark .marquee-header h3 {
    color: #94a3b8;
}

/* 篩選按鈕 */
.project-filters {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.pf-btn {
    padding: 4px 12px;
    border-radius: 12px;
    border: 1px solid rgba(100, 116, 139, 0.2);
    background: transparent;
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
    letter-spacing: 0.3px;
}

.pf-btn:hover {
    border-color: #3b82f6;
    color: #3b82f6;
}

.pf-btn.active {
    background: #3b82f6;
    border-color: #3b82f6;
    color: white;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.mode-dark .pf-btn {
    border-color: rgba(148, 163, 184, 0.15);
    color: #94a3b8;
}

.mode-dark .pf-btn:hover {
    border-color: #4ecdc4;
    color: #4ecdc4;
}

.mode-dark .pf-btn.active {
    background: #4ecdc4;
    border-color: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 2px 8px rgba(78, 205, 196, 0.3);
}

/* 空白狀態 */
.empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    color: #94a3b8;
    font-weight: 500;
    min-height: 120px;
}

/* 輪播 */
.carousel-viewport {
    width: 100%;
    overflow: hidden;
    padding-bottom: 10px;
    flex: 1;
}

.carousel-track {
    display: flex;
    gap: 12px;
    width: 100%;
    transition: transform 0.8s ease-in-out;
}

.carousel-track.no-transition {
    transition: none;
}

.carousel-track.fast-return {
    transition: transform 0.3s ease-in-out;
}

/* ===== 迷你專案卡片 ===== */
.mini-card {
    flex: 0 0 calc(50% - 6px);
    cursor: pointer;
    border-radius: 16px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.7);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    flex-shrink: 0;
}

.mini-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.18);
}

.mode-dark .mini-card {
    background: rgba(15, 23, 42, 0.55);
    border-color: rgba(255, 255, 255, 0.05);
}

.mode-dark .mini-card:hover {
    box-shadow: 0 8px 24px rgba(78, 205, 196, 0.18);
}

.mini-thumb {
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
    overflow: hidden;
}

.mini-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
}

.mini-card:hover .mini-thumb img {
    transform: scale(1.06);
}

.mini-hover-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.25s ease;
}

.mini-card:hover .mini-hover-overlay {
    opacity: 1;
}

.mini-hover-overlay span {
    color: white;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.mini-badge {
    position: absolute;
    top: 8px;
    left: 8px;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    font-weight: 700;
    backdrop-filter: blur(6px);
    letter-spacing: 0.3px;
}

.mini-badge.image {
    background: rgba(59, 130, 246, 0.9);
    color: #fff;
}

.mini-badge.nlp {
    background: rgba(139, 92, 246, 0.9);
    color: #fff;
}

.mini-badge.other {
    background: rgba(16, 185, 129, 0.9);
    color: #fff;
}

.mini-badge.large {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    top: 12px;
    left: 12px;
}

.mini-info {
    padding: 10px 12px 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.mini-name {
    font-size: 12px;
    font-weight: 700;
    color: #0f1724;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.mode-dark .mini-name {
    color: #e6eef8;
}

.mini-tags-row {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.mini-tags-row span {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    padding: 2px 7px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 600;
}

.mode-dark .mini-tags-row span {
    background: rgba(78, 205, 196, 0.15);
    color: #4ecdc4;
}

/* 箭頭 */
.custom-arrow {
    position: absolute;
    top: 84px;
    bottom: 44px;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    pointer-events: none;
    z-index: 10;
}

.arrow-btn {
    width: 26px;
    height: 48px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.05);
    cursor: pointer;
    pointer-events: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.2s;
}

.arrow-btn.left {
    border-radius: 0 8px 8px 0;
}

.arrow-btn.right {
    border-radius: 8px 0 0 8px;
}

.arrow-btn:hover {
    background: #ffffff;
    color: #3b82f6;
    width: 30px;
}

/* 點點 */
.custom-dots {
    position: absolute;
    bottom: 14px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    gap: 10px;
}

.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.12);
    cursor: pointer;
    transition: background-color 0.3s;
}

.dot.active {
    background-color: #3b82f6;
}

.mode-dark .dot {
    background-color: rgba(255, 255, 255, 0.15);
}

.mode-dark .dot.active {
    background-color: #4ecdc4;
}

/* ================= AccomPartner 展示 ================= */
.video-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.mode-dark .video-wrapper {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.video-wrapper:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2);
}

.bg-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.video-wrapper:hover .bg-img {
    transform: scale(1.03);
}

.video-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.4) 0%, transparent 50%);
    display: flex;
    align-items: center;
    justify-content: center;
}

.play-btn {
    width: 90px;
    height: 90px;
    background: rgba(230, 230, 230, 0.5);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(150, 150, 150, 0.048);
    color: #4C52C7;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    padding-left: 6px;
    transition: all 0.3s ease;
}

.video-wrapper:hover .play-btn {
    background: rgba(59, 130, 246, 0.9);
    border-color: transparent;
    transform: scale(1.1);
}

.inline-iframe {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    border: none;
}

.iframe-click-catcher {
    position: absolute;
    inset: 0;
    z-index: 5;
    cursor: pointer;
}

.video-action-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(6px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 14px;
    z-index: 10;
    border-radius: 16px;
}

.action-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 26px;
    border-radius: 50px;
    font-size: 14px;
    font-weight: 700;
    text-decoration: none;
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    font-family: inherit;
    letter-spacing: 0.3px;
    cursor: pointer;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}

.yt-btn {
    background: linear-gradient(135deg, #1e293b, #334155);
    color: white;
}

.yt-btn:hover {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.5);
}

.create-btn {
    background: linear-gradient(135deg, #3b82f6, #4ecdc4);
    color: white;
}

.create-btn:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 28px rgba(59, 130, 246, 0.45);
}

.click-hint {
    position: absolute;
    inset: 0;
    z-index: 6;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    pointer-events: none;
}

.hint-tap-icon {
    position: relative;
    z-index: 1;
    width: 80px;
    height: 80px;
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    border: 1.5px solid rgba(255, 255, 255, 0.45);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: hint-pulse 1.2s ease-in-out infinite;
}

@keyframes hint-pulse {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.14); }
}

.hint-label {
    font-size: 16px;
    font-weight: 700;
    color: white;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
    background: rgba(0, 0, 0, 0.32);
    padding: 4px 12px;
    border-radius: 20px;
    backdrop-filter: blur(4px);
}

.hint-fade-enter-active { transition: opacity 0.5s ease; }
.hint-fade-leave-active { transition: opacity 0.25s ease; }
.hint-fade-enter-from,
.hint-fade-leave-to     { opacity: 0; }

.btn-pop-enter-active {
    transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.btn-pop-leave-active {
    transition: all 0.2s ease;
}
.btn-pop-enter-from {
    opacity: 0;
    transform: scale(0.88);
}
.btn-pop-leave-to {
    opacity: 0;
    transform: scale(0.95);
}

.info-wrapper {
    padding: 0 8px;
}

.info-header {
    margin-bottom: 12px;
}

.title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.try-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    white-space: nowrap;
    color: #3b82f6;
    border: 1.5px solid #3b82f6;
    background: rgba(59, 130, 246, 0.06);
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.try-btn:hover {
    background: #3b82f6;
    color: white;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
    transform: translateY(-1px);
}

.mode-dark .try-btn {
    color: #4ecdc4;
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.06);
}

.mode-dark .try-btn:hover {
    background: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 4px 14px rgba(78, 205, 196, 0.35);
}

.highlight-tag {
    background: #ef4444d2;
    color: white;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
    display: inline-block;
}

.project-title {
    font-size: 24px;
    font-weight: 800;
    margin: 0;
    color: #0f1724;
}

.mode-dark .project-title {
    color: #e6eef8;
}

.project-desc {
    font-size: 15px;
    line-height: 1.7;
    color: #475569;
    margin: 0 0 20px 0;
    text-align: justify;
}

.mode-dark .project-desc {
    color: #cbd5e1;
}

.tech-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.tech-tags span {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

.mode-dark .tech-tags span {
    background: rgba(78, 205, 196, 0.15);
    color: #4ecdc4;
}

.modal-tags span {
    padding: 3px 10px;
    font-size: 12px;
}

/* ================= Modal ================= */
.proj-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(6px);
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}

.proj-modal {
    position: relative;
    max-width: 560px;
    width: 100%;
    max-height: 85vh;
    overflow-y: auto;
    border-radius: 24px;
    padding: 0;
}

.proj-modal::-webkit-scrollbar {
    width: 4px;
}

.proj-modal::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

.proj-modal-close {
    position: absolute;
    top: 14px;
    right: 14px;
    z-index: 10;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(0, 0, 0, 0.06);
    color: #475569;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.proj-modal-close:hover {
    background: #fff;
    color: #0f1724;
}

.mode-dark .proj-modal-close {
    background: rgba(15, 23, 42, 0.9);
    border-color: rgba(255, 255, 255, 0.08);
    color: #94a3b8;
}

.mode-dark .proj-modal-close:hover {
    color: #e6eef8;
}

.proj-modal-thumb {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    overflow: hidden;
    border-radius: 24px 24px 0 0;
}

.proj-modal-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.proj-modal-body {
    padding: 22px 26px 26px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.proj-modal-title {
    font-size: 20px;
    font-weight: 800;
    color: #0f1724;
    margin: 0;
}

.mode-dark .proj-modal-title {
    color: #e6eef8;
}

.proj-modal-desc {
    font-size: 14px;
    line-height: 1.8;
    color: #475569;
    margin: 0;
    text-align: justify;
}

.mode-dark .proj-modal-desc {
    color: #cbd5e1;
}

.proj-modal-highlights h4 {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #94a3b8;
    text-transform: uppercase;
    margin: 0 0 8px;
}

.proj-modal-highlights ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.proj-modal-highlights li {
    font-size: 13px;
    line-height: 1.6;
    color: #475569;
    padding-left: 16px;
    position: relative;
}

.proj-modal-highlights li::before {
    content: '▸';
    position: absolute;
    left: 0;
    color: #3b82f6;
    font-size: 11px;
    top: 2px;
}

.mode-dark .proj-modal-highlights li {
    color: #cbd5e1;
}

.mode-dark .proj-modal-highlights li::before {
    color: #4ecdc4;
}

.proj-modal-actions {
    display: flex;
    gap: 10px;
    margin-top: 4px;
}

.demo-btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 9px 20px;
    border-radius: 20px;
    background: #3b82f6;
    color: #fff;
    font-size: 13px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    transition: all 0.25s ease;
    font-family: inherit;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.3);
}

.demo-btn:hover {
    background: #2563eb;
    box-shadow: 0 6px 18px rgba(59, 130, 246, 0.4);
    transform: translateY(-1px);
}

.mode-dark .demo-btn {
    background: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 3px 12px rgba(78, 205, 196, 0.3);
}

.mode-dark .demo-btn:hover {
    background: #2dd4bf;
}

.ghost-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 9px 20px;
    border-radius: 20px;
    background: transparent;
    color: #475569;
    font-size: 13px;
    font-weight: 700;
    border: 1px solid rgba(71, 85, 105, 0.2);
    text-decoration: none;
    transition: all 0.25s ease;
}

.ghost-btn:hover {
    color: #0f1724;
    border-color: rgba(15, 23, 42, 0.3);
}

.mode-dark .ghost-btn {
    color: #94a3b8;
    border-color: rgba(148, 163, 184, 0.2);
}

.mode-dark .ghost-btn:hover {
    color: #e6eef8;
    border-color: rgba(230, 238, 248, 0.3);
}

/* Modal Transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.25s ease;
}

.modal-fade-enter-active .proj-modal,
.modal-fade-leave-active .proj-modal {
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.modal-fade-enter-from .proj-modal {
    transform: scale(0.92) translateY(20px);
}

.modal-fade-leave-to .proj-modal {
    transform: scale(0.96);
}

/* ===== RWD ===== */

/* Tablet：1023px 以下切單欄，縮減 padding */
@media (max-width: 1023px) {
    .bento-grid {
        grid-template-columns: 1fr;
        grid-template-areas: "bio" "accom" "marquee";
    }
    .intro-section {
        padding: 24px 4vw 0;
        min-height: auto;
    }
    .glass {
        padding: 24px;
        max-width: 100%;
    }
}

/* Mobile：767px 以下進一步精簡 */
@media (max-width: 767px) {
    .intro-section {
        padding: 16px 14px 0;
    }
    .glass {
        padding: 18px 16px;
        border-radius: 18px;
    }
    .avatar {
        width: 88px;
        height: 88px;
    }
    .name {
        font-size: 22px;
    }
    .role {
        font-size: 13px;
    }
    .bio-text {
        font-size: 14px;
    }
    .project-title {
        font-size: 18px;
    }
    .project-desc {
        font-size: 14px;
    }
    /* Carousel 在手機顯示 1 張（JS 也同步控制 step） */
    .mini-card {
        flex: 0 0 100%;
    }
    .action-btn {
        padding: 10px 18px;
        font-size: 13px;
    }
    .bento-grid {
        gap: 14px;
    }
}
</style>
