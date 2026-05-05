<template>
    <section id="projects" class="showcase-section">
        <div class="section-header">
            <span class="section-label">PORTFOLIO</span>
            <h2 class="section-title">Projects / 專案展示</h2>
            <p class="section-sub">每個專案都是一次技術探索與解題過程</p>
        </div>

        <!-- 篩選標籤 -->
        <div class="filter-bar">
            <button
                v-for="f in filters"
                :key="f.key"
                class="filter-btn"
                :class="{ active: activeFilter === f.key }"
                @click="activeFilter = f.key"
            >
                {{ f.label }}
            </button>
        </div>

        <!-- 專案卡片網格 -->
        <div class="projects-grid">
            <div
                v-for="project in filteredProjects"
                :key="project.id"
                class="project-card glass"
                @click="openDetail(project)"
            >
                <!-- 縮圖 -->
                <div class="card-thumbnail">
                    <img v-if="project.image" :src="project.image" :alt="project.name" />
                    <div v-else class="placeholder-img">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
                            <rect x="3" y="3" width="18" height="18" rx="3" />
                            <path d="M3 9h18M9 21V9" />
                        </svg>
                    </div>
                    <span class="type-badge" :class="project.type">{{ typeLabel(project.type) }}</span>
                </div>

                <!-- 卡片內容 -->
                <div class="card-content">
                    <h3 class="card-title">{{ project.name }}</h3>
                    <p class="card-desc">{{ project.desc }}</p>

                    <div class="tech-tags">
                        <span v-for="tag in project.tags" :key="tag">{{ tag }}</span>
                    </div>

                    <div class="card-actions">
                        <a
                            v-if="project.demoUrl"
                            :href="project.demoUrl"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="action-btn primary"
                            @click.stop
                        >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                                <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
                            </svg>
                            Live Demo
                        </a>
                        <a
                            v-if="project.githubUrl"
                            :href="project.githubUrl"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="action-btn ghost"
                            @click.stop
                        >
                            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
                            </svg>
                            GitHub
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- 詳細介紹 Modal -->
        <Transition name="modal-fade">
            <div v-if="selectedProject" class="modal-overlay" @click.self="closeDetail">
                <div class="modal-card glass">
                    <button class="modal-close" @click="closeDetail">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20">
                            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>

                    <div class="modal-thumbnail">
                        <img v-if="selectedProject.image" :src="selectedProject.image" :alt="selectedProject.name" />
                        <div v-else class="placeholder-img large">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="60" height="60">
                                <rect x="3" y="3" width="18" height="18" rx="3" /><path d="M3 9h18M9 21V9" />
                            </svg>
                        </div>
                        <span class="type-badge" :class="selectedProject.type">{{ typeLabel(selectedProject.type) }}</span>
                    </div>

                    <div class="modal-body">
                        <h2 class="modal-title">{{ selectedProject.name }}</h2>
                        <p class="modal-desc">{{ selectedProject.fullDesc || selectedProject.desc }}</p>

                        <div class="modal-section" v-if="selectedProject.highlights?.length">
                            <h4 class="modal-section-title">技術亮點</h4>
                            <ul class="highlight-list">
                                <li v-for="h in selectedProject.highlights" :key="h">{{ h }}</li>
                            </ul>
                        </div>

                        <div class="modal-section">
                            <h4 class="modal-section-title">技術棧</h4>
                            <div class="tech-tags">
                                <span v-for="tag in selectedProject.tags" :key="tag">{{ tag }}</span>
                            </div>
                        </div>

                        <div class="modal-actions">
                            <a v-if="selectedProject.demoUrl" :href="selectedProject.demoUrl" target="_blank" rel="noopener noreferrer" class="action-btn primary large">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                                    <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
                                </svg>
                                Live Demo
                            </a>
                            <a v-if="selectedProject.githubUrl" :href="selectedProject.githubUrl" target="_blank" rel="noopener noreferrer" class="action-btn ghost large">
                                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
                                </svg>
                                GitHub
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>
    </section>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    projects: {
        type: Array,
        default: () => [
            {
                id: 1,
                name: '交通法規 RAG 系統',
                desc: '以 LangChain 與向量資料庫建構的法規問答系統，支援自然語言查詢交通法規條文。',
                fullDesc: '整合 LangChain、ChromaDB 向量資料庫與 GPT-4 API，針對交通法規文件進行 RAG（Retrieval-Augmented Generation）問答。支援模糊查詢、條文溯源與多輪對話，並提供完整的 REST API 介面供前端串接。',
                type: 'backend',
                tags: ['Python', 'LangChain', 'ChromaDB', 'FastAPI', 'GPT-4'],
                image: 'https://picsum.photos/id/36/800/450',
                highlights: [
                    '使用 ChromaDB 進行語意向量搜尋，Top-K 精準召回',
                    '自製法規文本切割器，確保條文邊界完整',
                    'FastAPI + Docker 容器化部署，RESTful 接口設計',
                ],
                demoUrl: '',
                githubUrl: '',
            },
            {
                id: 2,
                name: '車輛辨識系統',
                desc: '基於 YOLOv8 的即時車輛型號與車牌辨識，整合至 Web Dashboard 做可視化呈現。',
                fullDesc: '訓練 YOLOv8 模型識別多種車輛類型與車牌號碼，使用 OpenCV 串流處理影像，並透過 WebSocket 將辨識結果即時推送至 Vue 3 前端 Dashboard，支援多鏡頭同時監控。',
                type: 'fullstack',
                tags: ['Python', 'YOLOv8', 'OpenCV', 'FastAPI', 'Vue 3', 'WebSocket'],
                image: 'https://picsum.photos/id/180/800/450',
                highlights: [
                    'YOLOv8 自訓練模型，mAP@0.5 達 0.87',
                    'WebSocket 即時推流，延遲 < 100ms',
                    'Vue 3 前端 Dashboard 含歷史紀錄與統計圖表',
                ],
                demoUrl: '',
                githubUrl: '',
            },
            {
                id: 3,
                name: '古文語言模型',
                desc: '以 GPT-2 為基底，在文言文語料上進行 Fine-tuning，用於古典詩詞生成與翻譯。',
                fullDesc: '收集並清洗唐詩、宋詞、文言文語料共約 80 萬字，對 GPT-2 進行 LoRA 微調。支援現代文輸入、輸出對應文言文，並提供詩詞生成（五言、七言絕句）功能，透過 Gradio 介面提供互動展示。',
                type: 'backend',
                tags: ['Python', 'PyTorch', 'Transformers', 'LoRA', 'Gradio', 'NLP'],
                image: 'https://picsum.photos/id/119/800/450',
                highlights: [
                    'LoRA 微調節省 90% GPU 記憶體，訓練效率大幅提升',
                    'BLEU score 相較 base model 提升 23%',
                    'Gradio 互動介面，即時生成詩詞',
                ],
                demoUrl: '',
                githubUrl: '',
            },
            {
                id: 4,
                name: 'AccomPartner 前端播放器',
                desc: '整合 Tone.js 多音合成與 VexFlow 動態五線譜渲染的 Web 音樂播放器元件。',
                fullDesc: '以 Vue 3 封裝的音樂播放器核心模組，使用 Tone.js 實現鋼琴音色合成與 MIDI 時序控制，搭配 VexFlow 將 MIDI 資料即時渲染為可視化五線譜。支援 Edge Inference（ONNX）即時伴奏生成，無需後端。',
                type: 'frontend',
                tags: ['Vue 3', 'Tone.js', 'VexFlow', 'ONNX Runtime', 'Web Audio API'],
                image: 'https://picsum.photos/id/48/800/450',
                highlights: [
                    'Web Audio API 低延遲鋼琴合成，延遲 < 20ms',
                    'ONNX Edge Inference 在瀏覽器端即時生成伴奏',
                    'VexFlow SVG 動態渲染，支援滾動跟隨播放位置',
                ],
                demoUrl: 'https://accompartner.dev/',
                githubUrl: '',
            },
        ],
    },
});

const filters = [
    { key: 'all', label: 'All' },
    { key: 'frontend', label: 'Frontend' },
    { key: 'backend', label: 'Backend' },
    { key: 'fullstack', label: 'Full Stack' },
];

const activeFilter = ref('all');
const selectedProject = ref(null);

const filteredProjects = computed(() =>
    activeFilter.value === 'all'
        ? props.projects
        : props.projects.filter((p) => p.type === activeFilter.value)
);

const typeLabel = (type) => {
    const map = { frontend: 'Frontend', backend: 'Backend', fullstack: 'Full Stack' };
    return map[type] ?? type;
};

const openDetail = (project) => { selectedProject.value = project; };
const closeDetail = () => { selectedProject.value = null; };
</script>

<style scoped>
.showcase-section {
    padding: 80px 4vw;
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ================= Section Header ================= */
.section-header {
    text-align: center;
    margin-bottom: 48px;
}

.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    color: #3b82f6;
    text-transform: uppercase;
}

.mode-dark .section-label {
    color: #4ecdc4;
}

.section-title {
    font-size: 36px;
    font-weight: 800;
    color: #0f1724;
    margin: 8px 0 12px;
    line-height: 1.2;
}

.mode-dark .section-title {
    color: #e6eef8;
}

.section-sub {
    font-size: 15px;
    color: #475569;
    margin: 0;
}

.mode-dark .section-sub {
    color: #94a3b8;
}

/* ================= Filter Bar ================= */
.filter-bar {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 40px;
    flex-wrap: wrap;
}

.filter-btn {
    padding: 8px 20px;
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.2);
    background: transparent;
    color: #475569;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease;
    font-family: inherit;
}

.filter-btn:hover {
    border-color: #3b82f6;
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.05);
}

.filter-btn.active {
    background: #3b82f6;
    border-color: #3b82f6;
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
}

.mode-dark .filter-btn {
    border-color: rgba(78, 205, 196, 0.2);
    color: #94a3b8;
}

.mode-dark .filter-btn:hover {
    border-color: #4ecdc4;
    color: #4ecdc4;
    background: rgba(78, 205, 196, 0.05);
}

.mode-dark .filter-btn.active {
    background: #4ecdc4;
    border-color: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 4px 14px rgba(78, 205, 196, 0.35);
}

/* ================= Project Grid ================= */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}

/* ================= Glass Base ================= */
.glass {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(16px);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.8);
}

.mode-dark .glass {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

/* ================= Project Card ================= */
.project-card {
    display: flex;
    flex-direction: column;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    overflow: hidden;
}

.project-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 48px rgba(59, 130, 246, 0.15);
}

.mode-dark .project-card:hover {
    box-shadow: 0 16px 48px rgba(78, 205, 196, 0.15);
}

/* 縮圖區 */
.card-thumbnail {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    overflow: hidden;
    border-radius: 24px 24px 0 0;
}

.card-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.project-card:hover .card-thumbnail img {
    transform: scale(1.05);
}

.placeholder-img {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #e2e8f0, #f1f5f9);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
}

.mode-dark .placeholder-img {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    color: #475569;
}

.placeholder-img.large {
    aspect-ratio: 16/9;
    border-radius: 16px 16px 0 0;
}

/* 類型標籤 */
.type-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    backdrop-filter: blur(8px);
}

.type-badge.frontend {
    background: rgba(59, 130, 246, 0.9);
    color: #ffffff;
}

.type-badge.backend {
    background: rgba(139, 92, 246, 0.9);
    color: #ffffff;
}

.type-badge.fullstack {
    background: rgba(16, 185, 129, 0.9);
    color: #ffffff;
}

/* 卡片內容 */
.card-content {
    padding: 20px 24px 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex: 1;
}

.card-title {
    font-size: 17px;
    font-weight: 700;
    color: #0f1724;
    margin: 0;
    line-height: 1.3;
}

.mode-dark .card-title {
    color: #e6eef8;
}

.card-desc {
    font-size: 14px;
    line-height: 1.7;
    color: #475569;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.mode-dark .card-desc {
    color: #94a3b8;
}

/* 技術標籤 */
.tech-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.tech-tags span {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.mode-dark .tech-tags span {
    background: rgba(78, 205, 196, 0.15);
    color: #4ecdc4;
}

/* 動作按鈕 */
.card-actions {
    display: flex;
    gap: 8px;
    margin-top: auto;
}

.action-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.25s ease;
    font-family: inherit;
    cursor: pointer;
}

.action-btn.primary {
    background: #3b82f6;
    color: #ffffff;
    box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3);
}

.action-btn.primary:hover {
    background: #2563eb;
    box-shadow: 0 6px 18px rgba(59, 130, 246, 0.4);
    transform: translateY(-1px);
}

.action-btn.ghost {
    background: transparent;
    color: #475569;
    border: 1px solid rgba(71, 85, 105, 0.2);
}

.action-btn.ghost:hover {
    color: #0f1724;
    border-color: #0f1724;
    background: rgba(0, 0, 0, 0.03);
}

.mode-dark .action-btn.primary {
    background: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 3px 10px rgba(78, 205, 196, 0.3);
}

.mode-dark .action-btn.primary:hover {
    background: #2dd4bf;
    box-shadow: 0 6px 18px rgba(78, 205, 196, 0.4);
}

.mode-dark .action-btn.ghost {
    color: #94a3b8;
    border-color: rgba(148, 163, 184, 0.2);
}

.mode-dark .action-btn.ghost:hover {
    color: #e6eef8;
    border-color: rgba(230, 238, 248, 0.3);
    background: rgba(255, 255, 255, 0.04);
}

.action-btn.large {
    padding: 10px 24px;
    font-size: 14px;
}

/* ================= Modal ================= */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(6px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}

.modal-card {
    position: relative;
    max-width: 680px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    border-radius: 24px;
    padding: 0;
}

.modal-card::-webkit-scrollbar {
    width: 4px;
}
.modal-card::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

.modal-close {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 10;
    width: 36px;
    height: 36px;
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

.modal-close:hover {
    background: #ffffff;
    color: #0f1724;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mode-dark .modal-close {
    background: rgba(15, 23, 42, 0.9);
    border-color: rgba(255, 255, 255, 0.08);
    color: #94a3b8;
}

.mode-dark .modal-close:hover {
    color: #e6eef8;
}

.modal-thumbnail {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    overflow: hidden;
    border-radius: 24px 24px 0 0;
}

.modal-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.modal-body {
    padding: 28px 32px 32px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.modal-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f1724;
    margin: 0;
}

.mode-dark .modal-title {
    color: #e6eef8;
}

.modal-desc {
    font-size: 15px;
    line-height: 1.8;
    color: #475569;
    margin: 0;
    text-align: justify;
}

.mode-dark .modal-desc {
    color: #cbd5e1;
}

.modal-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.modal-section-title {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #94a3b8;
    text-transform: uppercase;
    margin: 0;
}

.highlight-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.highlight-list li {
    font-size: 14px;
    line-height: 1.6;
    color: #475569;
    padding-left: 20px;
    position: relative;
}

.highlight-list li::before {
    content: '▸';
    position: absolute;
    left: 0;
    color: #3b82f6;
    font-size: 12px;
    top: 2px;
}

.mode-dark .highlight-list li {
    color: #cbd5e1;
}

.mode-dark .highlight-list li::before {
    color: #4ecdc4;
}

.modal-actions {
    display: flex;
    gap: 10px;
    padding-top: 4px;
}

/* ================= Transition ================= */
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.25s ease;
}

.modal-fade-enter-active .modal-card,
.modal-fade-leave-active .modal-card {
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.modal-fade-enter-from .modal-card {
    transform: scale(0.92) translateY(20px);
}

.modal-fade-leave-to .modal-card {
    transform: scale(0.96) translateY(10px);
}

/* ================= Responsive ================= */
@media (max-width: 1023px) {
    .projects-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 767px) {
    .showcase-section {
        padding: 60px 5vw;
    }

    .section-title {
        font-size: 28px;
    }

    .projects-grid {
        grid-template-columns: 1fr;
    }

    .modal-body {
        padding: 20px 20px 24px;
    }
}
</style>
