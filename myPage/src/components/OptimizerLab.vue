<template>
    <div class="opt-lab" :class="{ 'is-dark': isDark }">
        <div class="lab-layout">

            <!-- ═══ Left: Canvas + Controls ═══ -->
            <div class="lab-left">

                <!-- Canvas -->
                <div class="canvas-wrap">
                    <canvas ref="canvasRef" :width="CW" :height="CH"></canvas>

                    <div class="click-guide"><span>🖱️</span> 點擊設定起點</div>

                    <div v-if="statusText" class="status-badge" :class="statusClass">
                        {{ statusText }}
                    </div>

                    <div class="terrain-legend">
                        <div class="legend-title">Height Map (Loss)</div>
                        <div class="legend-gradient"></div>
                        <div class="legend-labels">
                            <span>Low (Minima)</span>
                            <span>High (Peak)</span>
                        </div>
                    </div>

                    <div class="terrain-info" v-html="terrainFormulaHtml"></div>
                </div>

                <!-- Controls -->
                <div class="controls-card">

                    <!-- Terrain + Max Steps -->
                    <div class="ctrl-row">
                        <div class="ctrl-col">
                            <span class="ctrl-label">選擇地形 (Terrain)</span>
                            <select v-model="currentTerrainKey" @change="onTerrainChange">
                                <option value="valley">Ravine (峽谷)</option>
                                <option value="bowl">Bowl (碗狀)</option>
                                <option value="saddle">Saddle (鞍點)</option>
                                <option value="multi">Multi-Peak (多峰)</option>
                            </select>
                        </div>
                        <div class="ctrl-col ctrl-narrow">
                            <span class="ctrl-label">MAX STEPS</span>
                            <input type="number" v-model.number="maxIter" min="100" max="5000" />
                        </div>
                    </div>

                    <!-- Buttons -->
                    <div>
                        <span class="ctrl-label">操作控制</span>
                        <div class="btn-group">
                            <button class="btn-run" :class="{ paused: isRunning }" @click="togglePlay">
                                {{ isRunning ? '⏸ Pause' : '▶ Run' }}
                            </button>
                            <button class="btn-step" @click="doStep">⏯ Step</button>
                            <button class="btn-reset" @click="doReset">↺ Reset</button>
                        </div>
                    </div>

                    <!-- LR Slider -->
                    <div>
                        <div class="ctrl-lr-header">
                            <span class="ctrl-label">Learning Rate (η)</span>
                            <span class="lr-display">{{ baseLr.toFixed(3) }}</span>
                        </div>
                        <input type="range" v-model.number="baseLr" min="0.001" max="0.1" step="0.001"
                            class="lr-slider" />
                    </div>

                    <!-- Monitor Table -->
                    <div>
                        <span class="ctrl-label">即時監控 (Real-time Monitor)</span>
                        <table class="monitor-table">
                            <thead>
                                <tr>
                                    <th>Algo</th>
                                    <th>Scale</th>
                                    <th>Steps</th>
                                    <th>Speed (px)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="row in displayRows" :key="row.name">
                                    <td>
                                        <span class="opt-dot" :style="{ background: row.color }"></span>
                                        {{ row.name }}
                                    </td>
                                    <td class="mono">x{{ row.visualScale }}</td>
                                    <td>
                                        <span v-if="row.finished" class="s-done">{{ row.finishIter }}</span>
                                        <span v-else-if="!row.active" class="s-fail">Failed</span>
                                        <span v-else-if="iterDisplay >= maxIter" class="s-timeout">{{ iterDisplay
                                            }}+</span>
                                        <span v-else class="s-run">{{ iterDisplay }}</span>
                                    </td>
                                    <td>
                                        <div class="mono small">{{ row.stepSize.toFixed(1) }}</div>
                                        <div class="vel-track">
                                            <div class="vel-fill" :style="{
                                                width: Math.min(100, (row.stepSize / 25) * 100) + '%',
                                                background: row.color,
                                                boxShadow: `0 0 4px ${row.color}`
                                            }">
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Info box -->
                    <div class="info-box">
                        <span class="info-title">ℹ️ 關於 Scale（視覺補償）</span>
                        Adam/RMSprop 內部有除法歸一化，導致步長遠小於 SGD。為在同一畫面比較，各算法套用不同倍率：
                        <br>• <strong>SGD / Momentum / Nesterov / Adagrad</strong>：×100
                        <br>• <strong>RMSprop / Adam</strong>：×180
                    </div>

                </div>
            </div>

            <!-- ═══ Right: Math Formulas ═══ -->
            <div class="lab-right">
                <div v-for="card in algoCards" :key="card.name" class="algo-card"
                    :style="{ borderLeftColor: isDark ? card.color : card.uiColor }">
                    <div class="card-name" :style="{ color: isDark ? card.color : card.uiColor }">{{ card.name }}</div>
                    <div class="card-desc">{{ card.desc }}</div>
                    <div class="math-box" v-html="card.mathHtml"></div>
                </div>
            </div>

        </div>
    </div>
</template>

<script setup>
import { ref, shallowRef, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({ isDark: { type: Boolean, default: false } });
const isDark = computed(() => props.isDark);

// Canvas internal resolution
const CW = 520, CH = 400;

// ── Reactive UI state ──
const canvasRef = ref(null);
const isRunning = ref(false);
const iterDisplay = ref(0);     // shown in table; updated every few frames
const maxIter = ref(500);
const baseLr = ref(0.02);
const currentTerrainKey = ref('valley');
const statusText = ref('');
const statusClass = ref('');
const terrainFormulaHtml = ref('');
const displayRows = shallowRef([]);

// ── Terrain definitions ──
const TERRAINS = {
    valley: {
        formulaText: '0.1x² + 2y²',
        formulaLatex: '0.1x^2 + 2y^2',
        scale: 28,
        start: { x: 60, y: 360 },
        loss: (x, y) => 0.1 * x * x + 2 * y * y,
        grad: (x, y) => ({ dx: 0.2 * x, dy: 4 * y }),
    },
    bowl: {
        formulaText: 'x² + y²',
        formulaLatex: 'x^2 + y^2',
        scale: 35,
        start: { x: 50, y: 50 },
        loss: (x, y) => x * x + y * y,
        grad: (x, y) => ({ dx: 2 * x, dy: 2 * y }),
    },
    saddle: {
        formulaText: 'x² − y²',
        formulaLatex: 'x^2 - y^2',
        scale: 30,
        start: { x: 450, y: 200 },
        loss: (x, y) => x * x - y * y,
        grad: (x, y) => ({ dx: 2 * x, dy: -2 * y }),
    },
    multi: {
        formulaText: '0.5(x²+y²) − 20cos(x) − 20cos(y)',
        formulaLatex: '0.5(x^2+y^2) - 20\\cos x - 20\\cos y',
        scale: 25,
        start: { x: 50, y: 350 },
        loss: (x, y) => 0.5 * (x * x + y * y) - 20 * Math.cos(x / 2) - 20 * Math.cos(y / 2),
        grad: (x, y) => ({ dx: x + 10 * Math.sin(x / 2), dy: y + 10 * Math.sin(y / 2) }),
    },
};

// ── Algo cards (formulas rendered after KaTeX loads) ──
const algoCards = ref([
    {
        name: 'SGD', color: '#ff2a6d', uiColor: '#e11d48', desc: '基礎梯度下降。',
        latex: ['\\theta_{t+1} = \\theta_t - \\eta \\cdot \\nabla J(\\theta_t)'], mathHtml: ''
    },
    {
        name: 'Momentum', color: '#05d5fa', uiColor: '#0284c7', desc: '引入速度變數 v，具有慣性。',
        latex: ['v_t = \\gamma v_{t-1} + \\eta \\nabla J(\\theta_t)',
            '\\theta_{t+1} = \\theta_t - v_t'], mathHtml: ''
    },
    {
        name: 'Nesterov (NAG)', color: '#ff9f1c', uiColor: '#d97706', desc: '預先計算下一步的梯度 (Look-ahead)。',
        latex: ['v_t = \\gamma v_{t-1} + \\eta \\nabla J(\\theta_t - \\gamma v_{t-1})',
            '\\theta_{t+1} = \\theta_t - v_t'], mathHtml: ''
    },
    {
        name: 'Adagrad', color: '#f7ea48', uiColor: '#b45309', desc: '累積歷史梯度平方 G_t。',
        latex: ['G_t = G_{t-1} + (\\nabla J)^2',
            '\\theta_{t+1} = \\theta_t - \\dfrac{\\eta}{\\sqrt{G_t+\\epsilon}} \\nabla J'], mathHtml: ''
    },
    {
        name: 'RMSprop', color: '#e056fd', uiColor: '#9333ea', desc: '使用指數加權平均限制歷史影響。',
        latex: ['E[g^2]_t = \\beta E[g^2]_{t-1} + (1-\\beta)(\\nabla J)^2',
            '\\theta_{t+1} = \\theta_t - \\dfrac{\\eta}{\\sqrt{E[g^2]_t+\\epsilon}} \\nabla J'], mathHtml: ''
    },
    {
        name: 'Adam', color: '#e2e8f0', uiColor: '#334155', desc: '結合一階矩 m̂ 與二階矩 v̂。',
        latex: ['m_t = \\beta_1 m_{t-1} + (1-\\beta_1)\\nabla J',
            'v_t = \\beta_2 v_{t-1} + (1-\\beta_2)(\\nabla J)^2',
            '\\theta_{t+1} = \\theta_t - \\dfrac{\\eta}{\\sqrt{\\hat{v}_t}+\\epsilon}\\hat{m}_t'], mathHtml: ''
    },
]);

// ── Plain-JS animation state (non-reactive) ──
// Canvas (always dark bg) vs UI (depends on theme)
const OPT_COLORS = {
    SGD: '#ff2a6d', Momentum: '#05d5fa', Nesterov: '#ff9f1c',
    Adagrad: '#f7ea48', RMSprop: '#e056fd', Adam: '#e2e8f0'
};
const OPT_UI_COLORS = {
    SGD: '#e11d48', Momentum: '#0284c7', Nesterov: '#d97706',
    Adagrad: '#b45309', RMSprop: '#9333ea', Adam: '#334155'
};
const OPT_SCALES = [100, 100, 100, 100, 180, 180];
const OPT_NAMES = ['SGD', 'Momentum', 'Nesterov', 'Adagrad', 'RMSprop', 'Adam'];
const TARGET_TH = 5;

let ctx = null;
let animId = null;
let terrain = TERRAINS['valley'];
let instances = [];
let bgCache = null;
let _iter = 0;   // plain fast counter
let _frameCount = 0;

// ── Helpers ──
function toMath(cx, cy) {
    return { x: (cx - CW / 2) / terrain.scale, y: (cy - CH / 2) / terrain.scale };
}

function getGrad(cx, cy) {
    const m = toMath(cx, cy);
    return terrain.grad(m.x, m.y);
}

function buildBg() {
    const imgData = ctx.createImageData(CW, CH);
    const d = imgData.data;
    const key = currentTerrainKey.value;
    for (let py = 0; py < CH; py++) {
        for (let px = 0; px < CW; px++) {
            const m = toMath(px, py);
            const val = terrain.loss(m.x, m.y);
            let norm = key === 'valley' ? val / 200
                : key === 'bowl' ? val / 150
                    : key === 'saddle' ? (val + 100) / 200
                        : (val + 40) / 140;
            norm = Math.max(0, Math.min(1, norm));
            let r, g, b;
            if (norm < 0.5) {
                const t = norm * 2;
                r = 2 + t * (34 - 2); g = 6 + t * (197 - 6); b = 23 + t * (94 - 23);
            } else {
                const t = (norm - 0.5) * 2;
                r = 34 + t * (255 - 34); g = 197 + t * (255 - 197); b = 94 + t * (255 - 94);
            }
            const intv = key === 'multi' ? 10 : 5;
            const dv = Math.abs(val) % intv;
            if (dv < 0.5 || intv - dv < 0.5) { r += 30; g += 30; b += 30; }
            const i = (py * CW + px) * 4;
            d[i] = Math.min(255, r); d[i + 1] = Math.min(255, g); d[i + 2] = Math.min(255, b); d[i + 3] = 255;
        }
    }
    bgCache = imgData;
}

function drawScene() {
    if (!bgCache) buildBg();
    ctx.putImageData(bgCache, 0, 0);
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.beginPath();
    ctx.moveTo(0, CH / 2); ctx.lineTo(CW, CH / 2);
    ctx.moveTo(CW / 2, 0); ctx.lineTo(CW / 2, CH);
    ctx.stroke();
    const s = instances.length ? { x: instances[0].startX, y: instances[0].startY } : terrain.start;
    ctx.strokeStyle = '#fff'; ctx.setLineDash([4, 4]);
    ctx.strokeRect(s.x - 8, s.y - 8, 16, 16); ctx.setLineDash([]);
    ctx.fillStyle = '#fff'; ctx.font = '11px Inter,sans-serif'; ctx.fillText('Start', s.x - 13, s.y + 22);
}

// ── Optimizer class ──
class Opt {
    constructor(name, color, x, y, vscale) {
        this.name = name; this.color = color;
        this.x = x; this.y = y; this.startX = x; this.startY = y;
        this.visualScale = vscale;
        this.path = [{ x, y }]; this.finished = false; this.active = true;
        this.stepSize = 0; this.finishIter = 0;
        this.vx = 0; this.vy = 0; this.cX = 0; this.cY = 0;
        this.mX = 0; this.mY = 0; this.vX = 0; this.vY = 0; this.t = 0;
    }
    move(dx, dy) {
        if (this.finished || !this.active) { this.stepSize = 0; return; }
        const ox = this.x, oy = this.y;
        this.x -= dx; this.y -= dy;
        if (this.x < -100 || this.x > CW + 100 || this.y < -100 || this.y > CH + 100) { this.active = false; return; }
        const dist = Math.hypot(this.x - CW / 2, this.y - CH / 2);
        const key = currentTerrainKey.value;
        if (dist < TARGET_TH && (key === 'valley' || key === 'bowl')) { this.finished = true; this.finishIter = _iter; }
        this.stepSize = Math.hypot(this.x - ox, this.y - oy);
        if (this.stepSize < 0.005 && _iter > 5) { this.finished = true; this.finishIter = _iter; }
        this.path.push({ x: this.x, y: this.y });
    }
    draw() {
        if (!this.active && this.path.length < 2) return;
        ctx.shadowBlur = 6; ctx.shadowColor = this.color;
        ctx.beginPath(); ctx.strokeStyle = this.color; ctx.lineWidth = 2;
        ctx.lineJoin = 'round'; ctx.lineCap = 'round';
        ctx.moveTo(this.path[0].x, this.path[0].y);
        for (let i = 1; i < this.path.length; i++) ctx.lineTo(this.path[i].x, this.path[i].y);
        ctx.stroke();
        ctx.fillStyle = this.color;
        ctx.beginPath(); ctx.arc(this.x, this.y, 4, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
    }
}

// ── Algorithm step functions ──
const Algos = {
    SGD: (o, lr) => {
        const g = getGrad(o.x, o.y); o.move(lr * g.dx * o.visualScale, lr * g.dy * o.visualScale);
    },
    Momentum: (o, lr) => {
        const g = getGrad(o.x, o.y);
        o.vx = 0.9 * o.vx + lr * g.dx * o.visualScale; o.vy = 0.9 * o.vy + lr * g.dy * o.visualScale;
        o.move(o.vx, o.vy);
    },
    Nesterov: (o, lr) => {
        const m = toMath(o.x - 0.9 * o.vx, o.y - 0.9 * o.vy);
        const g = terrain.grad(m.x, m.y);
        o.vx = 0.9 * o.vx + lr * g.dx * o.visualScale; o.vy = 0.9 * o.vy + lr * g.dy * o.visualScale;
        o.move(o.vx, o.vy);
    },
    Adagrad: (o, lr) => {
        const g = getGrad(o.x, o.y); o.cX += g.dx ** 2; o.cY += g.dy ** 2;
        o.move((lr / (Math.sqrt(o.cX) + 1e-8)) * g.dx * o.visualScale, (lr / (Math.sqrt(o.cY) + 1e-8)) * g.dy * o.visualScale);
    },
    RMSprop: (o, lr) => {
        const g = getGrad(o.x, o.y);
        o.cX = 0.99 * o.cX + 0.01 * g.dx ** 2; o.cY = 0.99 * o.cY + 0.01 * g.dy ** 2;
        o.move((lr / (Math.sqrt(o.cX) + 1e-8)) * g.dx * o.visualScale, (lr / (Math.sqrt(o.cY) + 1e-8)) * g.dy * o.visualScale);
    },
    Adam: (o, lr) => {
        o.t++; const g = getGrad(o.x, o.y);
        o.mX = 0.9 * o.mX + 0.1 * g.dx; o.mY = 0.9 * o.mY + 0.1 * g.dy;
        o.vX = 0.999 * o.vX + 0.001 * g.dx ** 2; o.vY = 0.999 * o.vY + 0.001 * g.dy ** 2;
        const mhX = o.mX / (1 - 0.9 ** o.t), mhY = o.mY / (1 - 0.9 ** o.t);
        const vhX = o.vX / (1 - 0.999 ** o.t), vhY = o.vY / (1 - 0.999 ** o.t);
        o.move((lr * mhX / (Math.sqrt(vhX) + 1e-8)) * o.visualScale, (lr * mhY / (Math.sqrt(vhY) + 1e-8)) * o.visualScale);
    },
};
const algoFns = OPT_NAMES.map(n => Algos[n]);

// ── Init / Reset ──
function init() {
    terrain = TERRAINS[currentTerrainKey.value];
    const s = terrain.start;
    instances = OPT_NAMES.map((name, i) =>
        new Opt(name, OPT_COLORS[name], s.x, s.y, OPT_SCALES[i])
    );
    _iter = 0; _frameCount = 0;
    iterDisplay.value = 0;
    statusText.value = '';
    bgCache = null;
    drawScene();
    pushDisplay();
    refreshTerrainFormula();
}

function pushDisplay() {
    const dark = props.isDark;
    displayRows.value = instances.map(o => ({
        name: o.name,
        color: dark ? o.color : OPT_UI_COLORS[o.name],
        visualScale: o.visualScale,
        finished: o.finished, finishIter: o.finishIter,
        active: o.active, stepSize: o.stepSize,
    }));
}

function refreshTerrainFormula() {
    const t = TERRAINS[currentTerrainKey.value];
    if (window.katex) {
        try {
            terrainFormulaHtml.value = 'Loss: ' +
                window.katex.renderToString(t.formulaLatex, { throwOnError: false, displayMode: false });
            return;
        } catch (_) { }
    }
    terrainFormulaHtml.value = `Loss: ${t.formulaText}`;
}

// ── Animation ──
function runStep() {
    _iter++; _frameCount++;
    let anyActive = false;
    const lr = baseLr.value;
    instances.forEach((o, i) => { algoFns[i](o, lr); if (!o.finished && o.active) anyActive = true; });
    drawScene();
    instances.forEach(o => o.draw());
    if (_frameCount % 4 === 0) {
        iterDisplay.value = _iter;
        pushDisplay();
    }
    return anyActive;
}

function loop() {
    if (!isRunning.value) return;
    const anyActive = runStep();
    if (_iter >= maxIter.value) { stop(); setStatus('TIMEOUT', 'timeout'); return; }
    if (!anyActive) { stop(); setStatus('FINISHED', 'finished'); return; }
    animId = requestAnimationFrame(loop);
}

function stop() {
    isRunning.value = false;
    cancelAnimationFrame(animId);
    iterDisplay.value = _iter;
    pushDisplay();
}

function setStatus(text, cls) { statusText.value = text; statusClass.value = 'badge-' + cls; }

function togglePlay() {
    if (!instances.length) init();
    if (_iter >= maxIter.value && !isRunning.value) maxIter.value += 500;
    if (isRunning.value) { stop(); }
    else { statusText.value = ''; isRunning.value = true; loop(); }
}

function doStep() {
    if (!instances.length) init();
    stop();
    const anyActive = runStep();
    iterDisplay.value = _iter;
    pushDisplay();
    if (!anyActive) setStatus('FINISHED', 'finished');
    else if (_iter >= maxIter.value) setStatus('TIMEOUT', 'timeout');
}

function doReset() { stop(); init(); }
function onTerrainChange() { stop(); init(); }

// ── Canvas click: set start point ──
function onCanvasClick(e) {
    if (_iter > 0) return;
    const r = canvasRef.value.getBoundingClientRect();
    const sx = CW / r.width, sy = CH / r.height;
    const nx = (e.clientX - r.left) * sx, ny = (e.clientY - r.top) * sy;
    instances.forEach(o => { o.x = nx; o.y = ny; o.startX = nx; o.startY = ny; o.path = [{ x: nx, y: ny }]; });
    terrain.start = { x: nx, y: ny };
    drawScene();
}

// ── KaTeX loading ──
async function loadKatex() {
    if (window.katex) return;
    if (!document.querySelector('link[href*="katex"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
        document.head.appendChild(link);
    }
    await new Promise((res, rej) => {
        const s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
        s.onload = res; s.onerror = rej;
        document.head.appendChild(s);
    });
}

function renderFormulas() {
    if (!window.katex) return;
    algoCards.value.forEach(card => {
        card.mathHtml = card.latex
            .map(f => window.katex.renderToString(f, { displayMode: true, throwOnError: false }))
            .join('');
    });
    refreshTerrainFormula();
}

// ── Lifecycle ──
onMounted(async () => {
    ctx = canvasRef.value.getContext('2d');
    canvasRef.value.addEventListener('mousedown', onCanvasClick);
    init();
    try { await loadKatex(); renderFormulas(); }
    catch (e) { console.warn('KaTeX not loaded:', e); }
});

onUnmounted(() => {
    cancelAnimationFrame(animId);
    canvasRef.value?.removeEventListener('mousedown', onCanvasClick);
});
</script>

<style scoped>
.opt-lab {
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', sans-serif;
    -webkit-font-smoothing: antialiased;
}

.lab-layout {
    display: grid;
    grid-template-columns: minmax(280px, 460px) 1fr;
    gap: 16px;
    align-items: start;
}

/* ── Left column ── */
.lab-left {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* ── Canvas ── */
.canvas-wrap {
    position: relative;
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5);
}

canvas {
    display: block;
    width: 100%;
    height: auto;
    cursor: crosshair;
}

.click-guide {
    position: absolute;
    top: 12px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 11px;
    backdrop-filter: blur(4px);
    pointer-events: none;
    display: flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.status-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(4px);
}

.badge-finished {
    color: #4ade80;
    border: 1px solid #4ade80;
}

.badge-timeout {
    color: #facc15;
    border: 1px solid #facc15;
}

.terrain-legend {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    padding: 7px 10px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    pointer-events: none;
}

.legend-title {
    font-size: 10px;
    color: #ddd;
    margin-bottom: 4px;
    font-weight: 600;
}

.legend-gradient {
    width: 110px;
    height: 8px;
    border-radius: 2px;
    margin-bottom: 2px;
    background: linear-gradient(to right, #020617 0%, #22c55e 50%, #ffffff 100%);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.legend-labels {
    display: flex;
    justify-content: space-between;
    width: 110px;
    font-size: 9px;
    color: #aaa;
}

.terrain-info {
    position: absolute;
    bottom: 10px;
    right: 10px;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.9);
    background: rgba(0, 0, 0, 0.55);
    padding: 3px 8px;
    border-radius: 4px;
    pointer-events: none;
    max-width: 55%;
}

/* ── Controls card ── */
.controls-card {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.ctrl-label {
    display: block;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 700;
    color: #475569;
    margin-bottom: 5px;
}

.ctrl-row {
    display: flex;
    gap: 10px;
}

.ctrl-col {
    flex: 1;
}

.ctrl-narrow {
    flex: 0 0 88px;
}

select,
input[type="number"] {
    width: 100%;
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 7px 8px;
    border-radius: 6px;
    font-size: 12px;
    outline: none;
    font-family: inherit;
    transition: border-color 0.15s;
}

select:focus,
input[type="number"]:focus {
    border-color: #3b82f6;
}

.btn-group {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 7px;
}

.btn-group button {
    border: none;
    padding: 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    font-family: inherit;
    color: #fff;
}

.btn-run {
    background: linear-gradient(135deg, #10b981, #059669);
}

.btn-run:hover {
    filter: brightness(1.12);
}

.btn-run.paused {
    background: linear-gradient(135deg, #f59e0b, #d97706);
}

.btn-step {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-step:hover {
    background: #334155;
}

.btn-reset {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #f87171;
}

.btn-reset:hover {
    background: #334155;
}

.ctrl-lr-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
}

.lr-display {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    color: #3b82f6;
    font-weight: 700;
}

.lr-slider {
    width: 100%;
    cursor: pointer;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    border-radius: 999px;
    outline: none;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
}

.lr-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #3b82f6;
    border: 2px solid #0f172a;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.35);
    cursor: pointer;
}

.lr-slider::-moz-range-thumb {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #3b82f6;
    border: 2px solid #0f172a;
    cursor: pointer;
}

/* Monitor table */
.monitor-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 3px;
    font-size: 12px;
}

.monitor-table th {
    text-align: left;
    color: #475569;
    padding: 0 6px;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.monitor-table td {
    background: rgba(255, 255, 255, 0.03);
    padding: 5px 6px;
}

.monitor-table tr td:first-child {
    border-radius: 4px 0 0 4px;
}

.monitor-table tr td:last-child {
    border-radius: 0 4px 4px 0;
}

.opt-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}

.mono {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 11px;
    opacity: 0.8;
}

.small {
    font-size: 10px;
}

.s-done {
    color: #4ade80;
    font-weight: 700;
}

.s-fail {
    color: #f87171;
}

.s-timeout {
    color: #facc15;
}

.s-run {
    color: #64748b;
}

.vel-track {
    width: 100%;
    height: 3px;
    background: rgba(255, 255, 255, 0.07);
    margin-top: 3px;
    border-radius: 2px;
}

.vel-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.08s linear;
}

/* Info box */
.info-box {
    background: rgba(59, 130, 246, 0.07);
    border: 1px solid rgba(59, 130, 246, 0.18);
    border-radius: 8px;
    padding: 10px;
    font-size: 11px;
    color: #93c5fd;
    line-height: 1.55;
}

.info-title {
    display: block;
    font-weight: 700;
    margin-bottom: 4px;
    color: #bfdbfe;
}

/* ── Right column: Formulas ── */
.lab-right {
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow-y: auto;
    padding-right: 2px;
}

.lab-right::-webkit-scrollbar {
    width: 4px;
}

.lab-right::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 2px;
}

.lab-right::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
}

.algo-card {
    background: rgba(30, 41, 59, 0.92);
    border-radius: 8px;
    padding: 12px 14px;
    border-left: 3px solid transparent;
}

.card-name {
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 4px;
}

.card-desc {
    font-size: 11px;
    color: #94a3b8;
    margin-bottom: 8px;
    line-height: 1.4;
}

.math-box {
    background: rgba(0, 0, 0, 0.35);
    padding: 8px 10px;
    border-radius: 6px;
    overflow-x: auto;
    color: #e2e8f0;
}

.math-box :deep(.katex-display) {
    margin: 4px 0;
}

.math-box :deep(.katex) {
    font-size: 0.95em;
}

/* ── RWD ── */
@media (max-width: 1325px) {
    .lab-layout {
        grid-template-columns: 1fr;
    }

    .lab-right {
        max-height: none;
    }
}

@media (max-width: 1100px) {
    .lab-layout {
        grid-template-columns: minmax(280px, 460px) 1fr;
    }

    .lab-right {
        max-height: none;
    }
}

@media (max-width: 850px) {
    .lab-layout {
        grid-template-columns: 1fr;
    }

    .lab-right {
        max-height: none;
    }
}

/* ═══════════════════════════════════
   Light mode overrides (.opt-lab 無 .is-dark)
   Canvas 永遠深色，只改控制面板與公式區
   ═══════════════════════════════════ */

.opt-lab:not(.is-dark) .controls-card {
    background: rgba(248, 250, 252, 0.97);
    border-color: rgba(0, 0, 0, 0.08);
}

.opt-lab:not(.is-dark) .ctrl-label {
    color: #94a3b8;
}

.opt-lab:not(.is-dark) select,
.opt-lab:not(.is-dark) input[type="number"] {
    background: #ffffff;
    color: #1e293b;
    border-color: rgba(0, 0, 0, 0.12);
}

.opt-lab:not(.is-dark) select:focus,
.opt-lab:not(.is-dark) input[type="number"]:focus {
    border-color: #3b82f6;
}

.opt-lab:not(.is-dark) .btn-step {
    background: #f1f5f9;
    border-color: rgba(0, 0, 0, 0.1);
    color: #374151;
}

.opt-lab:not(.is-dark) .btn-step:hover {
    background: #e2e8f0;
}

.opt-lab:not(.is-dark) .btn-reset {
    background: #f1f5f9;
    border-color: rgba(0, 0, 0, 0.1);
    color: #dc2626;
}

.opt-lab:not(.is-dark) .btn-reset:hover {
    background: #fee2e2;
}

.opt-lab:not(.is-dark) .lr-display {
    color: #2563eb;
}

.opt-lab:not(.is-dark) .lr-slider::-webkit-slider-thumb {
    border-color: #ffffff;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3);
}

.opt-lab:not(.is-dark) .lr-slider::-moz-range-thumb {
    border-color: #ffffff;
}

/* Monitor table */
.opt-lab:not(.is-dark) .monitor-table th {
    color: #94a3b8;
}

.opt-lab:not(.is-dark) .monitor-table td {
    background: rgba(0, 0, 0, 0.03);
    color: #374151;
}

.opt-lab:not(.is-dark) .mono {
    color: #374151;
}

.opt-lab:not(.is-dark) .s-done {
    color: #16a34a;
}

.opt-lab:not(.is-dark) .s-fail {
    color: #dc2626;
}

.opt-lab:not(.is-dark) .s-timeout {
    color: #d97706;
}

.opt-lab:not(.is-dark) .s-run {
    color: #9ca3af;
}

.opt-lab:not(.is-dark) .vel-track {
    background: rgba(0, 0, 0, 0.08);
}

/* Info box */
.opt-lab:not(.is-dark) .info-box {
    background: rgba(59, 130, 246, 0.06);
    border-color: rgba(59, 130, 246, 0.2);
    color: #2563eb;
}

.opt-lab:not(.is-dark) .info-title {
    color: #1d4ed8;
}

.opt-lab:not(.is-dark) .info-box strong {
    color: #1e40af;
}

/* Formula panel scrollbar */
.opt-lab:not(.is-dark) .lab-right::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.04);
}

.opt-lab:not(.is-dark) .lab-right::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.15);
}

/* Algo cards */
.opt-lab:not(.is-dark) .algo-card {
    background: rgba(248, 250, 252, 0.97);
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-left-width: 3px;
}

.opt-lab:not(.is-dark) .card-desc {
    color: #64748b;
}

.opt-lab:not(.is-dark) .math-box {
    background: rgba(241, 245, 249, 0.9);
    color: #1e293b;
}

.opt-lab:not(.is-dark) .math-box :deep(.katex) {
    color: #1e293b;
}
</style>
