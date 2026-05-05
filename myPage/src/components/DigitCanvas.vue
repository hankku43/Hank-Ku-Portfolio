<template>
    <div class="dc-wrap" :class="{ 'dc-dark': isDark }">
        <div class="dc-main">

            <!-- ── 左側：畫布區 ── -->
            <div class="dc-left">
                <div class="dc-canvas-frame">
                    <canvas
                        ref="canvasRef"
                        width="280"
                        height="280"
                        class="dc-canvas"
                        @mousedown="startDraw"
                        @mousemove="draw"
                        @mouseup="stopDraw"
                        @mouseleave="stopDraw"
                        @touchstart.prevent="startDrawTouch"
                        @touchmove.prevent="drawTouch"
                        @touchend="stopDraw"
                    ></canvas>
                    <div v-if="isEmpty" class="dc-hint">在此手繪字符</div>
                </div>

                <div class="dc-btns">
                    <button class="dc-btn-clear" @click="clearCanvas">清除</button>
                    <button
                        class="dc-btn-run"
                        :disabled="isEmpty || isLoading"
                        @click="runPredict"
                    >
                        <span v-if="isLoading" class="dc-spin"></span>
                        {{ isLoading ? '辨識中...' : '辨識' }}
                    </button>
                </div>

                <p class="dc-caption">數字 0–9、大寫 A–Z、小寫 a–z，共 62 類</p>
            </div>

            <!-- ── 右側：結果區 ── -->
            <Transition name="dc-slide">
                <div v-if="showResult" class="dc-right">

                    <template v-if="result">
                        <div class="dc-big-char">{{ result.prediction }}</div>
                        <div class="dc-big-conf">{{ fmtPct(result.confidence) }}</div>

                        <div class="dc-section-label">Top-5 預測</div>
                        <div class="dc-top5">
                            <div
                                v-for="(item, i) in result.top5"
                                :key="item.label"
                                class="dc-bar-row"
                                :class="{ 'dc-bar-top': i === 0 }"
                            >
                                <span class="dc-bar-char">{{ item.label }}</span>
                                <div class="dc-bar-track">
                                    <div
                                        class="dc-bar-fill"
                                        :style="{ width: (item.prob * 100) + '%' }"
                                    ></div>
                                </div>
                                <span class="dc-bar-pct">{{ fmtPct(item.prob) }}</span>
                            </div>
                        </div>

                        <div v-if="isMock" class="dc-mock-note">
                            ⚡ 示範輸出 · 連接後端 API 取得真實結果
                        </div>
                    </template>

                    <div v-else-if="loadError" class="dc-error">{{ loadError }}</div>

                </div>
            </Transition>

        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
    isDark: { type: Boolean, default: false },
});

const canvasRef = ref(null);
let ctx = null;
let drawing = false;

const isEmpty   = ref(true);
const isLoading = ref(false);
const result    = ref(null);
const loadError = ref(null);
const isMock    = ref(false);

const showResult = computed(() => !!(result.value || loadError.value));
const fmtPct = (v) => (v * 100).toFixed(1) + '%';

// ─── Canvas init ───────────────────────────────────────────────────────────
onMounted(() => {
    ctx = canvasRef.value.getContext('2d');
    resetCanvas();
});

function resetCanvas() {
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 280, 280);
    ctx.strokeStyle = '#ffffff';
    ctx.fillStyle   = '#ffffff';
    ctx.lineWidth   = 10;
    ctx.lineCap     = 'round';
    ctx.lineJoin    = 'round';
}

// ─── Coordinate helper ─────────────────────────────────────────────────────
function getPos(clientX, clientY) {
    const r = canvasRef.value.getBoundingClientRect();
    return {
        x: (clientX - r.left) * (280 / r.width),
        y: (clientY - r.top)  * (280 / r.height),
    };
}

// ─── Mouse ─────────────────────────────────────────────────────────────────
function startDraw(e) {
    drawing = true;
    isEmpty.value   = false;
    result.value    = null;
    loadError.value = null;
    isMock.value    = false;

    const { x, y } = getPos(e.clientX, e.clientY);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(x, y, ctx.lineWidth / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function draw(e) {
    if (!drawing) return;
    const { x, y } = getPos(e.clientX, e.clientY);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function stopDraw() { drawing = false; }

// ─── Touch ─────────────────────────────────────────────────────────────────
function startDrawTouch(e) {
    const t = e.touches[0];
    startDraw({ clientX: t.clientX, clientY: t.clientY });
}

function drawTouch(e) {
    const t = e.touches[0];
    draw({ clientX: t.clientX, clientY: t.clientY });
}

// ─── Actions ───────────────────────────────────────────────────────────────
function clearCanvas() {
    resetCanvas();
    isEmpty.value   = true;
    result.value    = null;
    loadError.value = null;
    isMock.value    = false;
}

async function runPredict() {
    if (isEmpty.value || isLoading.value) return;
    isLoading.value = true;
    result.value    = null;
    loadError.value = null;
    isMock.value    = false;

    const imageData = canvasRef.value.toDataURL('image/png');

    try {
        const res = await fetch('/api/digit/predict', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ image: imageData }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        result.value = await res.json();
    } catch (err) {
        loadError.value = `連線失敗：${err.message}`;
        result.value    = mockResult();
        isMock.value    = true;
    } finally {
        isLoading.value = false;
    }
}

function mockResult() {
    return {
        prediction: '5',
        confidence: 0.9312,
        top5: [
            { label: '5', prob: 0.9312 },
            { label: 'S', prob: 0.0421 },
            { label: 's', prob: 0.0183 },
            { label: '6', prob: 0.0061 },
            { label: '3', prob: 0.0023 },
        ],
    };
}
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.dc-wrap { width: 100%; }

.dc-main {
    display: flex;
    gap: 20px;
    align-items: flex-start;
}

.dc-left {
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex-shrink: 0;
    margin: auto;
}

.dc-right { flex: 1; min-width: 0; }

/* ── Canvas frame ────────────────────────────────────────────────────────── */
.dc-canvas-frame {
    position: relative;
    width: 230px;
    height: 230px;
    border-radius: 14px;
    overflow: hidden;
    border: 1.5px solid rgba(99, 102, 241, 0.3);
    box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.08), inset 0 0 20px rgba(0, 0, 0, 0.25);
}

.dc-canvas {
    width: 100%;
    height: 100%;
    display: block;
    cursor: crosshair;
    touch-action: none;
    user-select: none;
}

.dc-hint {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.16);
    font-size: 13px;
    font-weight: 600;
    pointer-events: none;
    letter-spacing: 0.5px;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.dc-btns { display: flex; gap: 8px; }

.dc-btn-clear,
.dc-btn-run {
    flex: 1;
    padding: 9px 0;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}

.dc-btn-clear {
    background: rgba(100, 116, 139, 0.1);
    color: #64748b;
    border: 1px solid rgba(100, 116, 139, 0.18);
}
.dc-btn-clear:hover { background: rgba(100, 116, 139, 0.18); color: #475569; }

.dc-btn-run {
    background: #3b82f6;
    color: #fff;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.dc-btn-run:hover:not(:disabled) {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}
.dc-btn-run:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }

/* dark overrides */
.dc-dark .dc-btn-clear { color: #94a3b8; border-color: rgba(148, 163, 184, 0.15); }
.dc-dark .dc-btn-clear:hover { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; }
.dc-dark .dc-btn-run { background: #4ecdc4; color: #0f172a; box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3); }
.dc-dark .dc-btn-run:hover:not(:disabled) { background: #2dd4bf; }

/* ── Caption ─────────────────────────────────────────────────────────────── */
.dc-caption { font-size: 11px; color: #94a3b8; margin: 0; text-align: center; }

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.dc-spin {
    width: 12px;
    height: 12px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: dc-spin 0.7s linear infinite;
    flex-shrink: 0;
}
.dc-dark .dc-spin { border-color: rgba(15, 23, 42, 0.3); border-top-color: #0f172a; }
@keyframes dc-spin { to { transform: rotate(360deg); } }

/* ── Result panel ────────────────────────────────────────────────────────── */
.dc-right {
    background: rgba(59, 130, 246, 0.04);
    border: 1px solid rgba(59, 130, 246, 0.12);
    border-radius: 16px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 230px;
    justify-content: center;
}
.dc-dark .dc-right {
    background: rgba(78, 205, 196, 0.04);
    border-color: rgba(78, 205, 196, 0.12);
}

.dc-big-char {
    font-size: 80px;
    font-weight: 800;
    line-height: 1;
    text-align: center;
    color: #3b82f6;
    letter-spacing: -2px;
}
.dc-dark .dc-big-char { color: #4ecdc4; }

.dc-big-conf {
    font-size: 20px;
    font-weight: 700;
    text-align: center;
    color: #0f1724;
    margin-top: -6px;
}
.dc-dark .dc-big-conf { color: #e6eef8; }

.dc-section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-top: 4px;
}

/* ── Top-5 bars ──────────────────────────────────────────────────────────── */
.dc-top5 { display: flex; flex-direction: column; gap: 5px; }

.dc-bar-row {
    display: grid;
    grid-template-columns: 22px 1fr 44px;
    align-items: center;
    gap: 8px;
}

.dc-bar-char {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    text-align: center;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.dc-bar-row.dc-bar-top .dc-bar-char { color: #3b82f6; }
.dc-dark .dc-bar-char { color: #94a3b8; }
.dc-dark .dc-bar-row.dc-bar-top .dc-bar-char { color: #4ecdc4; }

.dc-bar-track {
    height: 6px;
    background: rgba(0, 0, 0, 0.06);
    border-radius: 3px;
    overflow: hidden;
}
.dc-dark .dc-bar-track { background: rgba(255, 255, 255, 0.06); }

.dc-bar-fill {
    height: 100%;
    background: rgba(59, 130, 246, 0.45);
    border-radius: 3px;
    transition: width 0.5s cubic-bezier(.4,0,.2,1);
}
.dc-bar-row.dc-bar-top .dc-bar-fill { background: #3b82f6; }
.dc-dark .dc-bar-fill { background: rgba(78, 205, 196, 0.4); }
.dc-dark .dc-bar-row.dc-bar-top .dc-bar-fill { background: #4ecdc4; }

.dc-bar-pct {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-align: right;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.dc-dark .dc-bar-pct { color: #94a3b8; }

/* ── Error & mock note ───────────────────────────────────────────────────── */
.dc-error {
    font-size: 12px;
    color: #ef4444;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 10px;
    padding: 10px 14px;
}

.dc-mock-note {
    font-size: 11px;
    color: #94a3b8;
    font-style: italic;
    text-align: center;
}

/* ── Slide-in transition ─────────────────────────────────────────────────── */
.dc-slide-enter-active { transition: all 0.32s ease; }
.dc-slide-enter-from   { opacity: 0; transform: translateX(14px); }

/* ── Mobile ──────────────────────────────────────────────────────────────── */
@media (max-width: 560px) {
    .dc-main            { flex-direction: column; }
    .dc-canvas-frame    { width: 100%; height: 220px; }
    .dc-right           { width: 100%; min-height: unset; }
    .dc-slide-enter-from { transform: translateY(10px); }
    .dc-big-char        { font-size: 60px; }
}
</style>
