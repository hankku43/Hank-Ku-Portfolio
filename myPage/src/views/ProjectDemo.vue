<template>
    <n-config-provider :theme="isDark ? darkTheme : null">
        <div class="demo-page" :class="{ 'mode-dark': isDark }">

            <!-- ===== 頂部導覽列 ===== -->
            <header class="demo-header glass">
                <button class="back-btn" @click="goBack">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16">
                        <line x1="19" y1="12" x2="5" y2="12" />
                        <polyline points="12 19 5 12 12 5" />
                    </svg>
                    返回作品集
                </button>
                <span class="header-title">{{ project?.name ?? 'Demo' }}</span>
                <button class="theme-toggle" @click="toggleDark">
                    {{ isDark ? '☀️' : '🌙' }}
                </button>
            </header>

            <!-- ===== 主要內容 ===== -->
            <main class="demo-content">

                <!-- 404 狀態 -->
                <div v-if="!project" class="not-found">
                    <div class="not-found-card glass">
                        <p class="not-found-emoji">🔍</p>
                        <h2>找不到此專案</h2>
                        <p>ID「{{ $route.params.id }}」不存在於專案列表中。</p>
                        <button class="back-btn-lg" @click="goBack">← 返回作品集</button>
                    </div>
                </div>

                <template v-else>

                    <!-- Hero -->
                    <section class="hero-section">
                        <div class="hero-inner glass">
                            <div class="hero-top">
                                <span class="hero-badge" :class="project.type">{{ typeLabel(project.type) }}</span>
                                <h1 class="hero-title">{{ project.name }}</h1>
                            </div>
                            <p class="hero-desc">{{ project.shortDesc }}</p>
                            <div class="tech-tags">
                                <span v-for="tag in project.tags" :key="tag">{{ tag }}</span>
                            </div>
                        </div>
                    </section>

                    <!-- Demo + About 雙欄 -->
                    <section class="content-section">
                        <div class="content-grid" :class="{ embedded: project.demoMode === 'embedded-html' }">

                            <!-- ===== Demo 互動面板 ===== -->
                            <div class="demo-panel glass">
                                <h2 class="panel-title">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                        width="18" height="18">
                                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                                    </svg>
                                    互動示範
                                </h2>

                                <!-- ===== text-input 模式 ===== -->
                                <template v-if="project.demoMode === 'text-input'">
                                    <label class="input-label">{{ project.demoConfig.inputLabel }}</label>

                                    <div class="sample-chips">
                                        <button v-for="q in project.demoConfig.sampleQueries" :key="q"
                                            class="chip" @click="inputText = q">
                                            {{ q }}
                                        </button>
                                    </div>

                                    <textarea
                                        v-model="inputText"
                                        :placeholder="project.demoConfig.inputPlaceholder"
                                        class="demo-textarea"
                                        rows="4"
                                    ></textarea>

                                    <button class="run-btn" :class="{ loading: isLoading }"
                                        :disabled="!inputText.trim() || isLoading" @click="handleSubmit">
                                        <template v-if="isLoading">
                                            <span class="spinner-sm"></span> 處理中...
                                        </template>
                                        <template v-else>
                                            執行
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                                stroke-width="2.5" width="14" height="14">
                                                <line x1="5" y1="12" x2="19" y2="12" />
                                                <polyline points="12 5 19 12 12 19" />
                                            </svg>
                                        </template>
                                    </button>
                                </template>

                                <!-- ===== image-select 模式 ===== -->
                                <template v-else-if="project.demoMode === 'image-select'">
                                    <label class="input-label">{{ project.demoConfig.selectLabel }}</label>

                                    <div class="image-grid">
                                        <div v-for="s in project.demoConfig.samples" :key="s.id"
                                            class="image-thumb"
                                            :class="{ selected: selectedSample?.id === s.id }"
                                            @click="selectedSample = s; showResult = false">
                                            <img :src="s.url" :alt="s.label" />
                                            <span class="thumb-label">{{ s.label }}</span>
                                            <div v-if="selectedSample?.id === s.id" class="check-mark">✓</div>
                                        </div>
                                    </div>

                                    <button class="run-btn" :class="{ loading: isLoading }"
                                        :disabled="!selectedSample || isLoading" @click="handleRun">
                                        <template v-if="isLoading">
                                            <span class="spinner-sm"></span> 辨識中...
                                        </template>
                                        <template v-else>
                                            執行辨識
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                                stroke-width="2.5" width="14" height="14">
                                                <line x1="5" y1="12" x2="19" y2="12" />
                                                <polyline points="12 5 19 12 12 19" />
                                            </svg>
                                        </template>
                                    </button>
                                </template>

                                <!-- ===== interactive 模式 ===== -->
                                <template v-else-if="project.demoMode === 'interactive'">
                                    <p class="interactive-instruction">{{ project.demoConfig.instruction }}</p>
                                    <!-- TODO: 在此加入專案的互動介面 -->
                                    <div class="interactive-placeholder">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
                                            width="48" height="48">
                                            <rect x="3" y="3" width="18" height="18" rx="3" />
                                            <path d="M9 12h6M12 9v6" />
                                        </svg>
                                        <p>互動區域</p>
                                        <span>請在此實作專案的互動介面</span>
                                    </div>
                                    <button class="run-btn" :disabled="isLoading" @click="handleInteractive">
                                        <template v-if="isLoading">
                                            <span class="spinner-sm"></span> 處理中...
                                        </template>
                                        <template v-else>執行</template>
                                    </button>
                                </template>

                                <!-- ===== tfjs-optimize 模式 ===== -->
                                <template v-else-if="project.demoMode === 'tfjs-optimize'">
                                    <Suspense>
                                        <CloudDemoPanel :is-dark="isDark" />
                                        <template #fallback>
                                            <div class="interactive-placeholder">
                                                <span class="spinner-sm" style="width:28px;height:28px;border-width:3px;"></span>
                                                <p style="margin:8px 0 0;">載入元件中...</p>
                                            </div>
                                        </template>
                                    </Suspense>
                                </template>

                                <!-- ===== embedded-html 模式 ===== -->
                                <template v-else-if="project.demoMode === 'embedded-html'">
                                    <iframe
                                        :src="project.demoConfig.src"
                                        class="embedded-demo-iframe"
                                        :style="{
                                            height: project.demoConfig.iframeHeight || '720px',
                                            maxWidth: project.demoConfig.iframeMaxWidth || '100%',
                                        }"
                                        frameborder="0"
                                        scrolling="no"
                                        allow="accelerometer"
                                        title="互動示範"
                                    ></iframe>
                                </template>

                                <!-- ===== digit-canvas 模式 ===== -->
                                <template v-else-if="project.demoMode === 'digit-canvas'">
                                    <Suspense>
                                        <DigitCanvas :is-dark="isDark" />
                                        <template #fallback>
                                            <div class="interactive-placeholder">
                                                <span class="spinner-sm" style="width:28px;height:28px;border-width:3px;"></span>
                                                <p style="margin:8px 0 0;">載入元件中...</p>
                                            </div>
                                        </template>
                                    </Suspense>
                                </template>

                                <!-- ===== optimizer-lab 模式 ===== -->
                                <template v-else-if="project.demoMode === 'optimizer-lab'">
                                    <Suspense>
                                        <OptimizerLab :is-dark="isDark" />
                                        <template #fallback>
                                            <div class="interactive-placeholder">
                                                <span class="spinner-sm" style="width:28px;height:28px;border-width:3px;"></span>
                                                <p style="margin:8px 0 0;">載入元件中...</p>
                                            </div>
                                        </template>
                                    </Suspense>
                                </template>

                                <!-- ===== ptt-classify 模式 ===== -->
                                <template v-else-if="project.demoMode === 'ptt-classify'">
                                    <Suspense>
                                        <PttClassifier :is-dark="isDark" @status-change="onSubStatus" />
                                        <template #fallback>
                                            <div class="interactive-placeholder">
                                                <span class="spinner-sm" style="width:28px;height:28px;border-width:3px;"></span>
                                                <p style="margin:8px 0 0;">載入元件中...</p>
                                            </div>
                                        </template>
                                    </Suspense>
                                </template>

                                <!-- ===== nn-viz 模式 ===== -->
                                <template v-else-if="project.demoMode === 'nn-viz'">
                                    <Suspense>
                                        <NeuralNetworkViz :is-dark="isDark" />
                                        <template #fallback>
                                            <div class="interactive-placeholder">
                                                <span class="spinner-sm" style="width:28px;height:28px;border-width:3px;"></span>
                                                <p style="margin:8px 0 0;">載入元件中...</p>
                                            </div>
                                        </template>
                                    </Suspense>
                                </template>

                                <!-- ===== classical-scene 模式 ===== -->
                                <template v-else-if="project.demoMode === 'classical-scene'">
                                    <Suspense>
                                        <ClassicalNlpScene :is-dark="isDark" />
                                        <template #fallback>
                                            <div class="interactive-placeholder">
                                                <span class="spinner-sm" style="width:28px;height:28px;border-width:3px;"></span>
                                                <p style="margin:8px 0 0;">載入元件中...</p>
                                            </div>
                                        </template>
                                    </Suspense>
                                </template>

                                <!-- ===== 狀態顯示器 ===== -->
                                <Transition name="status-fade">
                                    <div v-if="statusMsg" class="status-bar" :class="{ 'status-done': statusDone }">
                                        <div v-if="!statusDone" class="status-spinner"></div>
                                        <span v-else class="status-check-icon">✓</span>
                                        <span class="status-text">{{ statusDone ? '完成' : statusMsg }}</span>
                                        <div class="status-progress"></div>
                                    </div>
                                </Transition>

                                <!-- ===== 結果區域 (text / image / interactive only) ===== -->
                                <Transition name="result-fade">
                                    <div v-if="showResult && !['tfjs-optimize','embedded-html','digit-canvas','classical-scene','nn-viz'].includes(project.demoMode)" class="result-area">
                                        <h4 class="result-title">
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                                stroke-width="2" width="15" height="15">
                                                <polyline points="20 6 9 17 4 12" />
                                            </svg>
                                            輸出結果
                                        </h4>

                                        <!-- RAG 結果（交通法規專案） -->
                                        <div v-if="project.demoMode === 'text-input' && project.id === 'rag-traffic'" class="text-result">
                                            <div v-if="apiError" class="api-error">{{ apiError }}</div>
                                            <template v-else-if="ragResult">
                                                <div class="rag-answer-block">
                                                    <span class="rag-section-label">▸ Gemma3 4B 回答</span>
                                                    <p class="rag-answer-text">{{ ragResult.answer }}</p>
                                                </div>
                                                <div v-if="ragResult.retrieved?.length" class="rag-retrieved-block">
                                                    <span class="rag-section-label">召回條文（{{ ragResult.retrieved.length }} 筆）</span>
                                                    <details v-for="(doc, i) in ragResult.retrieved" :key="i" class="rag-article">
                                                        <summary class="rag-summary">
                                                            <span class="rag-triangle">▶</span>
                                                            <span class="rag-meta">條文 {{ doc.article }}</span>
                                                            <span class="rag-score">相似度 {{ doc.similarity }}</span>
                                                            <span class="rag-preview">{{ doc.content.slice(0, 50) }}…</span>
                                                        </summary>
                                                        <p class="rag-full-text">{{ doc.content }}</p>
                                                    </details>
                                                </div>
                                            </template>
                                            <template v-else>
                                                <pre class="result-text">{{ mockTextResult }}</pre>
                                                <span class="result-note">⚡ 靜態示範輸出 · 請連接後端 Ollama 取得真實結果</span>
                                            </template>
                                        </div>

                                        <!-- 一般文字結果 -->
                                        <div v-else-if="project.demoMode === 'text-input'" class="text-result">
                                            <div v-if="apiError" class="api-error">{{ apiError }}</div>
                                            <template v-else-if="textResult">
                                                <pre class="result-text">{{ textResult }}</pre>
                                            </template>
                                            <template v-else>
                                                <pre class="result-text">{{ mockTextResult }}</pre>
                                                <span class="result-note">⚡ 靜態示範輸出 · 請連接後端 API 獲取真實結果</span>
                                            </template>
                                        </div>

                                        <!-- 圖片辨識結果 -->
                                        <div v-else-if="project.demoMode === 'image-select'" class="image-result">
                                            <div v-if="apiError" class="api-error">{{ apiError }}</div>
                                            <template v-else>
                                                <div class="result-image-wrap">
                                                    <img :src="selectedSample.url" alt="辨識結果" />
                                                    <!-- 真實 API 偵測框 -->
                                                    <template v-if="vehicleResult?.detections?.length">
                                                        <div v-for="(det, i) in vehicleResult.detections" :key="i"
                                                            class="det-box" :style="getBoxStyle(det)">
                                                            <span class="det-label" :style="{ background: det.color }">
                                                                {{ det.label }} {{ (det.score * 100).toFixed(0) }}%
                                                            </span>
                                                        </div>
                                                    </template>
                                                    <!-- 靜態示範框（API 尚未連接時） -->
                                                    <template v-else-if="!vehicleResult">
                                                        <div class="det-box"
                                                            style="top:18%;left:12%;width:38%;height:48%;border-color:#ef4444">
                                                            <span class="det-label" style="background:#ef4444">Car 94%</span>
                                                        </div>
                                                        <div class="det-box"
                                                            style="top:28%;left:58%;width:26%;height:36%;border-color:#3b82f6">
                                                            <span class="det-label" style="background:#3b82f6">Truck 87%</span>
                                                        </div>
                                                    </template>
                                                </div>
                                                <span v-if="!vehicleResult" class="result-note">⚡ 靜態示範輸出 · 請連接後端 API 獲取真實結果</span>
                                                <div v-else-if="vehicleResult.detections.length === 0" class="result-note">
                                                    未偵測到車輛（信心度 > 50%）
                                                </div>
                                                <div v-else class="det-summary">
                                                    <span class="det-summary-label">偵測結果：</span>
                                                    <span v-for="(det, i) in vehicleResult.detections" :key="i"
                                                        class="det-chip"
                                                        :style="{ background: det.color + '22', color: det.color, borderColor: det.color + '66' }">
                                                        {{ det.label }} {{ (det.score * 100).toFixed(0) }}%
                                                    </span>
                                                </div>
                                            </template>
                                        </div>

                                        <!-- 互動結果 -->
                                        <div v-else class="text-result">
                                            <pre class="result-text">{{ mockTextResult }}</pre>
                                            <span class="result-note">⚡ 靜態示範輸出 · 請連接後端 API 獲取真實結果</span>
                                        </div>

                                    </div>
                                </Transition>

                            </div>

                            <!-- ===== 關於此專案面板 ===== -->
                            <div class="about-panel glass">
                                <h2 class="panel-title">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                        width="18" height="18">
                                        <circle cx="12" cy="12" r="10" />
                                        <line x1="12" y1="8" x2="12" y2="12" />
                                        <line x1="12" y1="16" x2="12.01" y2="16" />
                                    </svg>
                                    關於此專案
                                </h2>

                                <p class="about-desc">{{ project.fullDesc }}</p>

                                <div v-if="project.highlights?.length" class="about-highlights">
                                    <h4 class="highlights-label">技術亮點</h4>
                                    <ul>
                                        <li v-for="h in project.highlights" :key="h">{{ h }}</li>
                                    </ul>
                                </div>

                                <div class="about-tags">
                                    <h4 class="highlights-label">技術棧</h4>
                                    <div class="tech-tags">
                                        <span v-for="tag in project.tags" :key="tag">{{ tag }}</span>
                                    </div>
                                </div>

                                <div v-if="project.githubUrl" class="about-links">
                                    <a :href="project.githubUrl" target="_blank" rel="noopener noreferrer"
                                        class="github-link">
                                        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                                            <path
                                                d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
                                        </svg>
                                        查看原始碼
                                    </a>
                                </div>
                            </div>

                        </div>
                    </section>

                </template>

            </main>

        </div>
    </n-config-provider>
</template>

<script setup>
import { ref, computed, watch, onMounted, defineAsyncComponent } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NConfigProvider, darkTheme } from 'naive-ui';
import { projects } from '../data/projects.js';
import { image } from '@tensorflow/tfjs';

const CloudDemoPanel = defineAsyncComponent(() =>
    import('../components/CloudDemoPanel.vue')
);
const DigitCanvas = defineAsyncComponent(() =>
    import('../components/DigitCanvas.vue')
);
const OptimizerLab = defineAsyncComponent(() =>
    import('../components/OptimizerLab.vue')
);
const PttClassifier = defineAsyncComponent(() =>
    import('../components/PttClassifier.vue')
);
const ClassicalNlpScene = defineAsyncComponent(() =>
    import('../components/ClassicalNlpScene.vue')
);
const NeuralNetworkViz = defineAsyncComponent(() =>
    import('../components/NeuralNetworkViz.vue')
);

const route = useRoute();
const router = useRouter();

const project = computed(() => projects.find(p => p.id === route.params.id) ?? null);

// ---- 主題 (與 PortfolioHome 同步 localStorage) ----
const isDark = ref(false);
onMounted(() => {
    isDark.value = localStorage.getItem('mypage-theme-dark') === 'true';
});
const toggleDark = () => {
    isDark.value = !isDark.value;
    localStorage.setItem('mypage-theme-dark', isDark.value);
};

const goBack = () => router.push('/');

// ---- 類型標籤 ----
const typeMap = { image: '影像處理', nlp: '自然語言處理', other: '其他展示' };
const typeLabel = (t) => typeMap[t] ?? t;

// ---- Demo 互動狀態 ----
const inputText = ref('');
const selectedSample = ref(null);
const isLoading = ref(false);
const showResult = ref(false);
const textResult = ref('');
const apiError = ref('');

// 切換專案時重置
watch(() => route.params.id, () => {
    inputText.value = '';
    selectedSample.value = null;
    isLoading.value = false;
    showResult.value = false;
    textResult.value = '';
    apiError.value = '';
    ragResult.value = null;
    statusMsg.value = '';
    vehicleResult.value = null;
});

// text-input 的示範回應 — 優先使用 demoConfig.mockResult，否則顯示通用佔位
const mockTextResult = computed(() => {
    const custom = project.value?.demoConfig?.mockResult;
    if (custom) return custom;
    const name = project.value?.name ?? '';
    return `【靜態示範輸出】\n\n此為「${name}」的模擬回應結果。\n\n` +
        `請在 .env 設定 VITE_API_BASE_URL 並連接後端 API。\n\n` +
        `// TODO: Replace with real API call`;
});

const handleSubmit = async () => {
    if (!inputText.value.trim()) return;
    isLoading.value = true;
    showResult.value = false;
    textResult.value = '';
    apiError.value = '';
    ragResult.value = null;
    statusMsg.value = '';

    const endpoint = project.value?.demoConfig?.apiEndpoint;
    const pid = project.value?.id;

    if (endpoint && pid === 'rag-traffic') {
        // SSE 串流模式（交通法規 RAG）
        try {
            const base = import.meta.env.VITE_API_BASE_URL || '';
            const res = await fetch(`${base}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: inputText.value.trim(), top_k: 3 }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() ?? '';
                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    let event;
                    try {
                        event = JSON.parse(line.slice(6));
                    } catch (_) { continue; }
                    if (event.type === 'status') {
                        statusMsg.value = event.message;
                    } else if (event.type === 'result') {
                        ragResult.value = event;
                        _doneStatus();
                    } else if (event.type === 'error') {
                        throw new Error(event.message);
                    }
                }
            }
        } catch (e) {
            apiError.value = `錯誤: ${e.message}`;
            statusMsg.value = '';
        }
    } else if (endpoint && pid !== 'custom-nn') {
        // 一般 JSON 模式（有狀態顯示）
        try {
            statusMsg.value = _processingMsg(pid);
            const base = import.meta.env.VITE_API_BASE_URL || '';
            const res = await fetch(`${base}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: inputText.value.trim(),
                    max_length: 100,
                    temperature: 0.85,
                }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const data = await res.json();
            textResult.value = data.output ?? JSON.stringify(data, null, 2);
            _doneStatus();
        } catch (e) {
            apiError.value = `錯誤: ${e.message}`;
            statusMsg.value = '';
        }
    } else if (endpoint) {
        // 未開通專案（無狀態顯示）
        try {
            const base = import.meta.env.VITE_API_BASE_URL || '';
            const res = await fetch(`${base}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: inputText.value.trim(), max_length: 100, temperature: 0.85 }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const data = await res.json();
            textResult.value = data.output ?? JSON.stringify(data, null, 2);
        } catch (e) {
            apiError.value = `錯誤: ${e.message}`;
        }
    } else {
        await new Promise(r => setTimeout(r, 1200));
    }

    isLoading.value = false;
    showResult.value = true;
};

const ragResult = ref(null);
const statusMsg = ref('');
const statusDone = computed(() => statusMsg.value.startsWith('✓'));
const vehicleResult = ref(null);

const _processingMsg = (id) => ({
    'rag-traffic':        null,
    'ptt-classifier':     'Doc2Vec 嵌入 → MLP 分類中...',
    'vehicle-detection':  'Faster R-CNN 車輛偵測中...',
    'cv-digits':          'CNN 辨識字符中...',
    'classical-nlp':      'Transformer 生成回答中...',
})[id] ?? '模型推論中...';

const _doneStatus = () => {
    statusMsg.value = '✓';
    setTimeout(() => { statusMsg.value = ''; }, 1600);
};

const onSubStatus = (msg) => {
    statusMsg.value = msg;
    if (msg === '✓') setTimeout(() => { statusMsg.value = ''; }, 1600);
};

const getBoxStyle = (det) => {
    if (!vehicleResult.value) return {};
    const { image_width, image_height } = vehicleResult.value;
    const [x1, y1, x2, y2] = det.box;
    return {
        left:        `${(x1 / image_width)  * 100}%`,
        top:         `${(y1 / image_height) * 100}%`,
        width:       `${((x2 - x1) / image_width)  * 100}%`,
        height:      `${((y2 - y1) / image_height) * 100}%`,
        borderColor: det.color,
    };
};

const handleRun = async () => {
    if (!selectedSample.value) return;
    isLoading.value = true;
    showResult.value = false;
    vehicleResult.value = null;
    apiError.value = '';
    statusMsg.value = '';

    const endpoint = project.value?.demoConfig?.apiEndpoint;
    if (endpoint) {
        try {
            statusMsg.value = '載入影像中...';
            const imgRes = await fetch(selectedSample.value.url);
            const blob = await imgRes.blob();
            const formData = new FormData();
            formData.append('file', blob, 'image.jpg');

            statusMsg.value = 'Faster R-CNN 車輛偵測中...';
            const base = import.meta.env.VITE_API_BASE_URL || '';
            const res = await fetch(`${base}${endpoint}`, {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            vehicleResult.value = await res.json();
            _doneStatus();
        } catch (e) {
            apiError.value = `錯誤: ${e.message}`;
            statusMsg.value = '';
        }
    } else {
        await new Promise(r => setTimeout(r, 1400));
    }

    isLoading.value = false;
    showResult.value = true;
};

// TODO: 替換為真實互動邏輯
const handleInteractive = async () => {
    isLoading.value = true;
    showResult.value = false;
    await new Promise(r => setTimeout(r, 1000));
    isLoading.value = false;
    showResult.value = true;
};
</script>

<style scoped>
.glass {
    min-width: 0;
}
/* ================= 頁面基底 ================= */
.demo-page {
    min-height: 100vh;
    background: linear-gradient(180deg, #f3f6fb, #ffffff);
    transition: background 0.5s, color 0.5s;
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    position: relative;
}

.demo-page::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(circle at 20% 30%, rgba(120, 161, 255, 0.35), transparent 65%),
        radial-gradient(circle at 80% 70%, rgba(200, 160, 255, 0.3), transparent 80%);
    z-index: 0;
    pointer-events: none;
    animation: subtleGlow-light 8s ease-in-out infinite alternate;
}

.demo-page.mode-dark {
    background: linear-gradient(180deg, #020617 0%, #0a1128 35%, #0f172a 65%, #1e1b4b 100%);
    color: #e6eef8;
}

.demo-page.mode-dark::before {
    background:
        radial-gradient(circle at 30% 20%, rgba(56, 189, 248, 0.4), transparent 70%),
        radial-gradient(circle at 70% 80%, rgba(168, 85, 247, 0.2), transparent 75%);
    mix-blend-mode: screen;
    animation: subtleGlow 12s ease-in-out infinite alternate;
}

@keyframes subtleGlow-light { 0% { opacity: 0.4; } 100% { opacity: 0.9; } }
@keyframes subtleGlow { 0% { opacity: 0.5; } 100% { opacity: 0.95; } }

/* ================= 頂部導覽 ================= */
.demo-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    background: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(16px) !important;
    border-radius: 0 !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04) !important;
}

.mode-dark .demo-header {
    background: rgba(15, 23, 42, 0.8) !important;
    border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

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

.back-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 16px;
    border-radius: 20px;
    border: 1px solid rgba(71, 85, 105, 0.2);
    background: transparent;
    color: #475569;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
}
.back-btn:hover { color: #0f1724; border-color: rgba(15, 23, 42, 0.3); background: rgba(0,0,0,0.03); }
.mode-dark .back-btn { color: #94a3b8; border-color: rgba(148, 163, 184, 0.15); }
.mode-dark .back-btn:hover { color: #e6eef8; border-color: rgba(230, 238, 248, 0.3); }

.header-title {
    font-size: 14px;
    font-weight: 700;
    color: #0f1724;
    max-width: 40%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.mode-dark .header-title { color: #e6eef8; }

.theme-toggle {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: transparent;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}
.theme-toggle:hover { background: rgba(0,0,0,0.05); }
.mode-dark .theme-toggle { border-color: rgba(255,255,255,0.1); }
.mode-dark .theme-toggle:hover { background: rgba(255,255,255,0.08); }

/* ================= 主要內容 ================= */
.demo-content {
    position: relative;
    z-index: 1;
    padding-top: 60px;
}

/* ===== Hero ===== */
.hero-section { padding: 20px 4vw 12px; }
.hero-inner {
    max-width: 1360px;
    margin: 0 auto;
    padding: 16px 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.hero-top { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }

.hero-badge {
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    flex-shrink: 0;
}
.hero-badge.image  { background: rgba(59, 130, 246, 0.12); color: #3b82f6; }
.hero-badge.nlp   { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
.hero-badge.other { background: rgba(16, 185, 129, 0.12); color: #10b981; }
.mode-dark .hero-badge.image  { background: rgba(59, 130, 246, 0.2); }
.mode-dark .hero-badge.nlp   { background: rgba(139, 92, 246, 0.2); }
.mode-dark .hero-badge.other { background: rgba(16, 185, 129, 0.2); }

.hero-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f1724;
    margin: 0;
    line-height: 1.2;
}
.mode-dark .hero-title { color: #e6eef8; }

.hero-desc { font-size: 15px; line-height: 1.7; color: #475569; margin: 0; text-align: justify;}
.mode-dark .hero-desc { color: #cbd5e1; }

.tech-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tech-tags span {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.mode-dark .tech-tags span { background: rgba(78, 205, 196, 0.15); color: #4ecdc4; }

/* ===== 雙欄佈局 ===== */
.content-section { padding: 0 4vw 60px; }
.content-grid {
    max-width: 1360px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 400px;
    gap: 24px;
    align-items: start;
}

/* ===== 共用面板樣式 ===== */
.demo-panel,
.about-panel {
    padding: 28px 28px 32px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.about-panel {
    position: sticky;
    top: 76px;
    overflow-y: auto;
}

.panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 0 0 4px;
}
.mode-dark .panel-title { color: #94a3b8; }

/* ===== text-input 模式 ===== */
.input-label {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
}
.mode-dark .input-label { color: #cbd5e1; }

.sample-chips {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}
.chip {
    padding: 5px 12px;
    border-radius: 12px;
    border: 1px solid rgba(59, 130, 246, 0.2);
    background: rgba(59, 130, 246, 0.06);
    color: #3b82f6;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
    text-align: left;
}
.chip:hover { background: rgba(59, 130, 246, 0.12); border-color: #3b82f6; }
.mode-dark .chip {
    background: rgba(78, 205, 196, 0.08);
    border-color: rgba(78, 205, 196, 0.2);
    color: #4ecdc4;
}
.mode-dark .chip:hover { background: rgba(78, 205, 196, 0.15); }

.demo-textarea {
    width: 100%;
    padding: 12px 16px;
    border-radius: 14px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    line-height: 1.7;
    color: #0f1724;
    resize: vertical;
    min-height: 100px;
    font-family: inherit;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-sizing: border-box;
}
.demo-textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.mode-dark .demo-textarea {
    background: rgba(15, 23, 42, 0.5);
    border-color: rgba(255, 255, 255, 0.08);
    color: #e6eef8;
}
.mode-dark .demo-textarea::placeholder { color: #475569; }
.mode-dark .demo-textarea:focus { border-color: #4ecdc4; box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1); }

/* ===== image-select 模式 ===== */
.image-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}
.image-thumb {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s ease;
    aspect-ratio: 4/3;
}
.image-thumb img { width: 100%; height: 100%; object-fit: cover; }
.image-thumb:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(59, 130, 246, 0.2); }
.image-thumb.selected { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); }
.mode-dark .image-thumb.selected { border-color: #4ecdc4; box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.15); }

.thumb-label {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.6), transparent);
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 8px 8px 6px;
    text-align: center;
}
.check-mark {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #3b82f6;
    color: white;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}
.mode-dark .check-mark { background: #4ecdc4; color: #0f172a; }

/* ===== interactive 模式 ===== */
.interactive-instruction {
    font-size: 14px;
    color: #475569;
    line-height: 1.7;
    margin: 0;
    padding: 12px 16px;
    background: rgba(59, 130, 246, 0.05);
    border-radius: 12px;
    border-left: 3px solid #3b82f6;
}
.mode-dark .interactive-instruction {
    color: #cbd5e1;
    background: rgba(78, 205, 196, 0.05);
    border-left-color: #4ecdc4;
}

.interactive-placeholder {
    border: 2px dashed rgba(100, 116, 139, 0.25);
    border-radius: 16px;
    min-height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #94a3b8;
}
.interactive-placeholder p { font-size: 15px; font-weight: 600; margin: 0; color: #64748b; }
.interactive-placeholder span { font-size: 12px; }
.mode-dark .interactive-placeholder { border-color: rgba(148, 163, 184, 0.1); }

/* ===== Run 按鈕 ===== */
.run-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 11px 24px;
    border-radius: 20px;
    background: #3b82f6;
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    transition: all 0.25s ease;
    font-family: inherit;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
    align-self: flex-start;
}
.run-btn:hover:not(:disabled) {
    background: #2563eb;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
    transform: translateY(-1px);
}
.run-btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; box-shadow: none; }
.mode-dark .run-btn { background: #4ecdc4; color: #0f172a; box-shadow: 0 4px 14px rgba(78, 205, 196, 0.35); }
.mode-dark .run-btn:hover:not(:disabled) { background: #2dd4bf; }

.spinner-sm {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
}
.mode-dark .spinner-sm { border-color: rgba(15, 23, 42, 0.3); border-top-color: #0f172a; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== 結果區域 ===== */
.result-area {
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.15);
    background: rgba(59, 130, 246, 0.04);
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.mode-dark .result-area {
    border-color: rgba(78, 205, 196, 0.15);
    background: rgba(78, 205, 196, 0.04);
}

.result-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #3b82f6;
    margin: 0;
}
.mode-dark .result-title { color: #4ecdc4; }

.result-text {
    font-size: 13px;
    line-height: 1.8;
    color: #374151;
    margin: 0;
    white-space: pre-wrap;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    background: rgba(0, 0, 0, 0.03);
    border-radius: 8px;
    padding: 12px 14px;
}
.mode-dark .result-text { color: #cbd5e1; background: rgba(255, 255, 255, 0.04); }

.result-note {
    font-size: 11px;
    color: #94a3b8;
    font-style: italic;
}

.api-error {
    font-size: 13px;
    color: #ef4444;
    background: rgba(239, 68, 68, 0.06);
    border-radius: 8px;
    padding: 10px 14px;
    line-height: 1.6;
}
.mode-dark .api-error { background: rgba(239, 68, 68, 0.1); }

/* image result */
.result-image-wrap {
    position: relative;
    width: 100%;
    border-radius: 10px;
    overflow: hidden;
}
.result-image-wrap img { width: 100%; display: block; }

.det-box {
    position: absolute;
    border: 2px solid;
    border-radius: 4px;
}
.det-label {
    position: absolute;
    top: -20px;
    left: -1px;
    color: white;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px 4px 0 0;
    white-space: nowrap;
}

/* detection summary chips */
.det-summary {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
}
.det-summary-label {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.mode-dark .det-summary-label { color: #94a3b8; }
.det-chip {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 10px;
    border: 1px solid;
    white-space: nowrap;
}

/* Result Transition */
.result-fade-enter-active { transition: all 0.35s ease; }
.result-fade-enter-from { opacity: 0; transform: translateY(10px); }

/* ===== About 面板 ===== */
.about-desc { font-size: 14px; line-height: 1.8; color: #475569; margin: 0; text-align: justify;}
.mode-dark .about-desc { color: #cbd5e1; }

.highlights-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #94a3b8;
    text-transform: uppercase;
    margin: 0 0 8px;
}
.about-highlights ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.about-highlights li {
    font-size: 13px;
    line-height: 1.6;
    color: #475569;
    padding-left: 16px;
    position: relative;
    text-align: justify;
}
.about-highlights li::before {
    content: '▸';
    position: absolute;
    left: 0;
    color: #3b82f6;
    font-size: 11px;
    top: 2px;
}
.mode-dark .about-highlights li { color: #cbd5e1; }
.mode-dark .about-highlights li::before { color: #4ecdc4; }

.about-tags { display: flex; flex-direction: column; gap: 8px; }

.github-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 18px;
    border-radius: 20px;
    border: 1px solid rgba(71, 85, 105, 0.2);
    color: #475569;
    text-decoration: none;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.2s;
}
.github-link:hover { color: #0f1724; border-color: rgba(15, 23, 42, 0.3); background: rgba(0,0,0,0.03); }
.mode-dark .github-link { color: #94a3b8; border-color: rgba(148, 163, 184, 0.15); }
.mode-dark .github-link:hover { color: #e6eef8; }

/* ===== 404 ===== */
.not-found {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 60px);
    padding: 24px;
}
.not-found-card {
    max-width: 400px;
    width: 100%;
    padding: 48px 32px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}
.not-found-emoji { font-size: 48px; margin: 0; }
.not-found-card h2 { font-size: 20px; font-weight: 800; color: #0f1724; margin: 0; }
.mode-dark .not-found-card h2 { color: #e6eef8; }
.not-found-card p { font-size: 14px; color: #475569; margin: 0; }
.mode-dark .not-found-card p { color: #cbd5e1; }
.back-btn-lg {
    margin-top: 8px;
    padding: 10px 24px;
    border-radius: 20px;
    border: none;
    background: #3b82f6;
    color: white;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
}
.back-btn-lg:hover { background: #2563eb; }
.mode-dark .back-btn-lg { background: #4ecdc4; color: #0f172a; }

/* ===== 狀態顯示器 ===== */
.status-bar {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 16px 14px;
    margin-top: 10px;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.18);
    border-radius: 12px;
    overflow: hidden;
    transition: background 0.3s ease, border-color 0.3s ease;
}
.mode-dark .status-bar {
    background: rgba(78, 205, 196, 0.05);
    border-color: rgba(78, 205, 196, 0.18);
}
.status-bar.status-done {
    background: rgba(34, 197, 94, 0.05);
    border-color: rgba(34, 197, 94, 0.22);
}
.status-spinner {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
    border: 2px solid rgba(59, 130, 246, 0.2);
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: status-spin 0.7s linear infinite;
}
.mode-dark .status-spinner {
    border-color: rgba(78, 205, 196, 0.2);
    border-top-color: #4ecdc4;
}
.status-check-icon {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #22c55e;
}
.status-text {
    flex: 1;
    font-size: 12px;
    color: #475569;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1;
}
.mode-dark .status-text { color: #94a3b8; }
.status-done .status-text { color: #15803d; }
.mode-dark .status-done .status-text { color: #4ade80; }
.status-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #3b82f6 30%, #818cf8 70%, transparent 100%);
    background-size: 200% 100%;
    animation: status-shimmer 1.6s linear infinite;
}
.mode-dark .status-progress {
    background: linear-gradient(90deg, transparent 0%, #4ecdc4 30%, #818cf8 70%, transparent 100%);
    background-size: 200% 100%;
}
.status-done .status-progress {
    background: #22c55e;
    opacity: 0.5;
    animation: none;
}
@keyframes status-spin { to { transform: rotate(360deg); } }
@keyframes status-shimmer {
    0%   { background-position: 100% 0; }
    100% { background-position: -100% 0; }
}
.status-fade-enter-active,
.status-fade-leave-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.status-fade-enter-from,
.status-fade-leave-to { opacity: 0; transform: translateY(-5px); }

/* ===== RAG 結果 ===== */
.rag-answer-block {
    background: rgba(59, 130, 246, 0.06);
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.mode-dark .rag-answer-block {
    background: rgba(78, 205, 196, 0.08);
    border-left-color: #4ecdc4;
}
.rag-section-label {
    display: block;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: #3b82f6;
    margin-bottom: 6px;
}
.mode-dark .rag-section-label { color: #4ecdc4; }
.rag-answer-text {
    margin: 0;
    font-size: 13px;
    line-height: 1.75;
    color: #1e293b;
    white-space: pre-wrap;
}
.mode-dark .rag-answer-text { color: #e2e8f0; }

.rag-retrieved-block {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.rag-article {
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-radius: 8px;
    overflow: hidden;
}
.mode-dark .rag-article { border-color: rgba(255, 255, 255, 0.07); }
.rag-article[open] .rag-triangle { transform: rotate(90deg); }
.rag-summary {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 12px;
    background: rgba(0, 0, 0, 0.02);
    list-style: none;
    user-select: none;
}
.rag-summary::-webkit-details-marker { display: none; }
.mode-dark .rag-summary { background: rgba(255, 255, 255, 0.03); }
.rag-triangle {
    font-size: 9px;
    color: #94a3b8;
    transition: transform 0.18s ease;
    flex-shrink: 0;
}
.rag-meta {
    font-weight: 700;
    color: #475569;
    white-space: nowrap;
    flex-shrink: 0;
}
.mode-dark .rag-meta { color: #94a3b8; }
.rag-score {
    font-size: 11px;
    color: #64748b;
    white-space: nowrap;
    padding: 1px 6px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    flex-shrink: 0;
}
.mode-dark .rag-score { background: rgba(255, 255, 255, 0.07); color: #94a3b8; }
.rag-preview {
    color: #64748b;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    min-width: 0;
}
.mode-dark .rag-preview { color: #94a3b8; }
.rag-full-text {
    margin: 0;
    padding: 10px 12px;
    font-size: 12px;
    line-height: 1.75;
    color: #334155;
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    white-space: pre-wrap;
}
.mode-dark .rag-full-text { color: #cbd5e1; border-top-color: rgba(255, 255, 255, 0.05); }

/* ===== embedded-html 模式 ===== */
.embedded-demo-iframe {
    width: 100%;
    height: 720px;
    border: none;
    border-radius: 12px;
    display: block;
    margin: 0 auto;
    overflow: hidden;
    background: #0f172a;
}

/* 當 demo 是 embedded-html 時，讓 demo-panel 佔滿整行 */
.content-grid.embedded {
    grid-template-columns: 1fr;
}
.content-grid.embedded .demo-panel {
    max-width: 100%;
}

/* ================= RWD ================= */
@media (max-width: 1100px) {
    .content-grid { grid-template-columns: 1fr; }
    .about-panel { position: static; max-height: none; overflow-y: visible; }
    .hero-title { font-size: 20px; }
    .demo-panel, .about-panel { padding: 20px 20px 24px; }
    .header-title { display: none; }
    .embedded-demo-iframe { height: 480px; }
}
@media (max-width: 400px) {
.sample-chips {
    display: block;
}}
</style>
