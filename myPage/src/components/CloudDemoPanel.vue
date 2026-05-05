<template>
    <div class="cloud-demo" :class="{ 'cd-dark': isDark }">

        <!-- ── Main Tab Toggle ── -->
        <div class="main-tabs">
            <button :class="['main-tab', { active: mainTab === 'quiz' }]" @click="mainTab = 'quiz'"
                :disabled="isRunning">
                🎮 猜猜我是誰
            </button>
            <button :class="['main-tab', { active: mainTab === 'generate' }]" @click="mainTab = 'generate'"
                :disabled="isRunning">
                ⚡ 即時雲朵化
            </button>
        </div>

        <!-- ═══════════════ QUIZ TAB ═══════════════ -->
        <template v-if="mainTab === 'quiz'">

            <!-- Idle -->
            <div v-if="quizPhase === 'idle'" class="quiz-idle">
                <p class="quiz-idle-desc">
                    用 PyTorch 精調模型生成的 151 隻第一世代寶可夢雲朵圖像，<br />
                    看著輪廓，猜猜牠是哪隻？
                </p>
                <div class="quiz-teaser-grid">
                    <div v-for="p in teaserPokemon" :key="p[0]" class="quiz-teaser-cell">
                        <img :src="`/images/pokemon/claudify/${p[0]}_${p[1]}.png`" class="quiz-teaser-img" alt="???" />
                        <span class="quiz-teaser-q">?</span>
                    </div>
                </div>
                <button class="quiz-start-btn" @click="startQuiz">開始挑戰 →</button>
            </div>

            <!-- Active (question / revealed) -->
            <div v-else-if="quizPhase === 'question' || quizPhase === 'revealed'" class="quiz-active">

                <!-- Progress dots + score -->
                <div class="quiz-header">
                    <div class="quiz-dots">
                        <span v-for="i in QUIZ_TOTAL" :key="i" :class="['qdot', roundDotClass(i)]" />
                    </div>
                    <span class="quiz-score-badge">{{ quizScore }}/{{ quizAnswers.length }}</span>
                </div>

                <!-- Question: single large cloud image -->
                <div v-if="quizPhase === 'question'" class="quiz-img-stage">
                    <img :src="quizQuestion.cloudUrl" class="quiz-cloud-img" alt="猜猜是誰" />
                    <p class="quiz-prompt">☁️ 這是哪隻寶可夢？</p>
                </div>

                <!-- Revealed: side by side -->
                <div v-else class="quiz-reveal-stage">
                    <div class="qr-col">
                        <img :src="quizQuestion.cloudUrl" class="qr-img" alt="cloud" />
                        <span class="qr-lbl">AI 精調雲朵</span>
                    </div>
                    <div class="qr-sep">≈</div>
                    <div class="qr-col">
                        <img :src="quizQuestion.origUrl" class="qr-img" alt="original" />
                        <span class="qr-lbl">{{ quizQuestion.name }}</span>
                    </div>
                </div>

                <!-- Result banner -->
                <Transition name="quiz-pop">
                    <div v-if="quizPhase === 'revealed'"
                        :class="['quiz-result-banner', quizPicked === quizQuestion.name ? 'correct' : 'wrong']">
                        {{ quizPicked === quizQuestion.name
                            ? '✓ 答對了！'
                            : `✗ 答錯了，是 ${quizQuestion.name}！` }}
                    </div>
                </Transition>

                <!-- 2×2 choice grid -->
                <div class="quiz-choices">
                    <button v-for="choice in quizQuestion.choices" :key="choice"
                        :class="['quiz-choice', choiceClass(choice)]" :disabled="quizPhase === 'revealed'"
                        @click="pickAnswer(choice)">
                        {{ choice }}
                    </button>
                </div>

                <!-- Next button -->
                <Transition name="quiz-pop">
                    <div v-if="quizPhase === 'revealed'" class="quiz-next-wrap">
                        <button class="quiz-next-btn" @click="advanceQuiz">
                            {{ quizRound >= QUIZ_TOTAL ? '查看成績 →' : '下一題 →' }}
                        </button>
                    </div>
                </Transition>
            </div>

            <!-- Done -->
            <div v-else-if="quizPhase === 'done'" class="quiz-done">
                <div class="quiz-done-score">
                    <span class="qds-num">{{ quizScore }}</span>
                    <span class="qds-sep">/</span>
                    <span class="qds-total">{{ QUIZ_TOTAL }}</span>
                </div>
                <p class="quiz-done-msg">{{ doneMessage }}</p>
                <div class="quiz-done-dots">
                    <span v-for="(correct, i) in quizAnswers" :key="i"
                        :class="['qdot', correct ? 'correct' : 'wrong']" />
                </div>
                <button class="quiz-start-btn" @click="startQuiz">再來一次</button>
            </div>

            <!-- Bridge to generate tab -->
            <div class="tab-bridge">
                <span class="bridge-text">想試試線上版本？</span>
                <button class="bridge-btn" @click="mainTab = 'generate'">即時雲朵化 ⚡</button>
            </div>

        </template>

        <!-- ═══════════════ GENERATE TAB ═══════════════ -->
        <template v-else>

            <!-- Bridge back to quiz -->
            <div class="tab-bridge-top">
                <button class="bridge-link" @click="mainTab = 'quiz'">← 猜猜我是誰</button>
            </div>

            <!-- Model Loading -->
            <div v-if="modelStatus === 'loading'" class="model-loading">
                <div class="prog-track">
                    <div class="prog-fill" :style="{ width: loadProgress + '%' }"></div>
                </div>
                <p class="loading-text">載入 AI 模型中... {{ loadProgress }}%</p>
            </div>

            <div v-else-if="modelStatus === 'error'" class="model-error">
                ⚠️ 模型載入失敗，請確認 /tfjs_model_dir 路徑正確並重新整理頁面。
            </div>

            <template v-else>

                <!-- Image source toggle -->
                <div class="src-toggle-row">
                    <p class="input-label">選擇要轉換的圖片</p>
                    <div class="src-toggle">
                        <button :class="['src-tab', { active: imgSource === 'preset' }]" @click="setImgSource('preset')"
                            :disabled="isRunning">預設圖片</button>
                        <button :class="['src-tab', { active: imgSource === 'upload' }]" @click="setImgSource('upload')"
                            :disabled="isRunning">上傳 PNG</button>
                    </div>
                </div>

                <!-- Preset image grid -->
                <div v-if="imgSource === 'preset'" class="img-grid">
                    <div v-for="s in samples" :key="s.id" class="img-thumb"
                        :class="{ selected: selectedSample?.id === s.id, locked: isRunning }"
                        @click="!isRunning && selectImage(s)">
                        <img :src="s.url" :alt="s.label" />
                        <span class="thumb-label">{{ s.label }}</span>
                        <div v-if="selectedSample?.id === s.id" class="checkmark">✓</div>
                    </div>
                </div>

                <!-- Upload zone -->
                <div v-else class="upload-zone" :class="{ 'uz-has-file': !!uploadedDataUrl, 'uz-locked': isRunning }"
                    @click="!isRunning && fileInputRef?.click()" @dragover.prevent @drop.prevent="handleDrop">
                    <input ref="fileInputRef" type="file" accept="image/png" style="display:none"
                        @change="handleFileChange" />
                    <template v-if="!uploadedDataUrl">
                        <div class="uz-icon">📁</div>
                        <p class="uz-title">點擊或拖曳上傳 PNG</p>
                        <p class="uz-note">⚠️ 請上傳已去背的 PNG<br />（線上版本不支援自動去背）</p>
                    </template>
                    <template v-else>
                        <img :src="uploadedDataUrl" class="uz-preview" alt="preview" />
                        <div class="uz-file-info">
                            <p class="uz-name">{{ uploadedName }}</p>
                            <p class="uz-change">點擊更換圖片</p>
                        </div>
                    </template>
                </div>

                <!-- Hyperparameter panel -->
                <div class="hp-section">
                    <button class="hp-toggle" :disabled="isRunning" @click="showHyperParams = !showHyperParams">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13"
                            height="13">
                            <circle cx="12" cy="12" r="3" />
                            <path
                                d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                        </svg>
                        超參數設定
                        <span class="hp-arrow" :class="{ open: showHyperParams }">▾</span>
                    </button>
                    <Transition name="hp-expand">
                        <div v-if="showHyperParams" class="hp-panel">
                            <div class="hp-mode-row">
                                <button :class="['hp-tab', { active: hpMode === 'auto' }]" @click="hpMode = 'auto'"
                                    :disabled="isRunning">僅調整 Epoch</button>
                                <button :class="['hp-tab', { active: hpMode === 'manual' }]" @click="hpMode = 'manual'"
                                    :disabled="isRunning">全手動</button>
                            </div>
                            <div class="epoch-row">
                                <span class="hp-label-sm">Epoch</span>
                                <div class="epoch-slider-wrap">
                                    <span class="epoch-limit">101</span>
                                    <input type="range" v-model.number="epochs" min="101" max="1001" step="100"
                                        class="epoch-slider" :disabled="isRunning" />
                                    <span class="epoch-limit">1001</span>
                                </div>
                                <span class="epoch-cur">{{ epochs }}</span>
                            </div>
                            <template v-if="hpMode === 'auto'">
                                <p class="hp-auto-hint">其他超參數依 Epoch 線性插值自動計算</p>
                                <div class="hp-auto-grid">
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">CLOUD_GEN_WEIGHT</span>
                                        <span class="hp-auto-val">{{ autoParams.cloudGenWeight.toFixed(1) }}</span>
                                    </div>
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">SHAPE_LOSS_WEIGHT</span>
                                        <span class="hp-auto-val">{{ autoParams.shapeLossWeight }}</span>
                                    </div>
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">COLOR_KEEP_WEIGHT</span>
                                        <span class="hp-auto-val">{{ autoParams.colorKeepWeight.toFixed(1) }}</span>
                                    </div>
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">TV_LOSS_WEIGHT</span>
                                        <span class="hp-auto-val">{{ autoParams.tvLossWeight.toFixed(2) }}</span>
                                    </div>
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">LR</span>
                                        <span class="hp-auto-val">{{ autoParams.lr.toFixed(4) }}</span>
                                    </div>
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">模糊間隔</span>
                                        <span class="hp-auto-val">{{ autoParams.blurInterval }}</span>
                                    </div>
                                    <div class="hp-auto-item">
                                        <span class="hp-auto-key">模糊 sigma</span>
                                        <span class="hp-auto-val">{{ autoParams.blurSigma.toFixed(2) }}</span>
                                    </div>
                                </div>
                            </template>
                            <template v-else>
                                <p class="hp-auto-hint">請手動調整超參數</p>
                                <div class="hp-grid">
                                    <div class="hp-item">
                                        <label class="hp-label">CLOUD_GEN_WEIGHT</label>
                                        <input type="number" v-model.number="cloudGenWeight" min="0.5" max="100"
                                            step="0.5" class="hp-input" />
                                    </div>
                                    <div class="hp-item">
                                        <label class="hp-label">SHAPE_LOSS_WEIGHT</label>
                                        <input type="number" v-model.number="shapeLossWeight" min="100" max="50000"
                                            step="100" class="hp-input" />
                                    </div>
                                    <div class="hp-item">
                                        <label class="hp-label">COLOR_KEEP_WEIGHT</label>
                                        <input type="number" v-model.number="colorKeepWeight" min="0" max="500" step="1"
                                            class="hp-input" />
                                    </div>
                                    <div class="hp-item">
                                        <label class="hp-label">TV_LOSS_WEIGHT</label>
                                        <input type="number" v-model.number="tvLossWeight" min="0" max="20" step="0.1"
                                            class="hp-input" />
                                    </div>
                                    <div class="hp-item">
                                        <label class="hp-label">LR</label>
                                        <input type="number" v-model.number="lr" min="0.001" max="0.5" step="0.001"
                                            class="hp-input" />
                                    </div>
                                    <div class="hp-item">
                                        <label class="hp-label">模糊間隔 (epoch)</label>
                                        <input type="number" v-model.number="blurInterval" min="1" max="500" step="1"
                                            class="hp-input" />
                                    </div>
                                    <div class="hp-item">
                                        <label class="hp-label">模糊 sigma</label>
                                        <input type="number" v-model.number="blurSigma" min="0.1" max="2.0" step="0.05"
                                            class="hp-input" />
                                    </div>
                                    <button class="hp-reset" @click="resetHyperParams">重置預設值</button>
                                </div>
                            </template>
                        </div>
                    </Transition>
                </div>

                <!-- Run Button -->
                <button class="cd-run-btn" :disabled="!selectedSample || isRunning" @click="startOpt">
                    <span v-if="isRunning" class="btn-inner">
                        <span class="spin-sm"></span>
                        優化中... ({{ currentIter }}/{{ epochs }})
                    </span>
                    <span v-else class="btn-inner">
                        轉換成雲朵 ☁️
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14"
                            height="14">
                            <line x1="5" y1="12" x2="19" y2="12" />
                            <polyline points="12 5 19 12 12 19" />
                        </svg>
                    </span>
                </button>

                <!-- Progress -->
                <Transition name="cd-fade">
                    <div v-if="isRunning || isDone" class="opt-info">
                        <div class="prog-track">
                            <div class="prog-fill" :style="{ width: (currentIter / epochs * 100) + '%' }"></div>
                        </div>
                        <div class="opt-meta">
                            <span>第 {{ currentIter }} / {{ epochs }} 輪</span>
                            <span v-if="currentLoss !== null" class="loss-val">Loss: {{ currentLoss }}</span>
                        </div>
                    </div>
                </Transition>

                <!-- Canvas Comparison -->
                <Transition name="cd-fade">
                    <div v-if="showCanvases" class="canvas-compare">
                        <div class="canvas-box">
                            <p class="canvas-label">輸入基底</p>
                            <canvas ref="beforeCanvas" width="224" height="224" class="res-canvas"></canvas>
                        </div>
                        <div class="arrow-sep">→</div>
                        <div class="canvas-box">
                            <p class="canvas-label">雲朵化結果 ☁️</p>
                            <canvas ref="afterCanvas" width="224" height="224" class="res-canvas"></canvas>
                        </div>
                    </div>
                </Transition>

                <!-- Done Note -->
                <Transition name="cd-fade">
                    <p v-if="isDone" class="done-note">
                        ✓ {{ epochs }} 輪梯度優化完成！所有運算均在您的瀏覽器 GPU 上執行，未傳送任何資料至伺服器。
                    </p>
                </Transition>

                <!-- Tech Note -->
                <div class="tech-note">
                    <span>🔬</span>
                    <span>MobileNetV2 雲朵分類器 (TF.js) · Adam 梯度下降直接優化像素值 · 純前端 WebGL 推論</span>
                </div>

            </template>
        </template>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({ isDark: { type: Boolean, default: false } });

// ── Pokémon data (Gen 1, 151) ──
const POKEMON = [
    ['0001', '妙蛙種子'], ['0002', '妙蛙草'], ['0003', '妙蛙花'], ['0004', '小火龍'], ['0005', '火恐龍'], ['0006', '噴火龍'],
    ['0007', '傑尼龜'], ['0008', '卡咪龜'], ['0009', '水箭龜'], ['0010', '綠毛蟲'], ['0011', '鐵甲蛹'], ['0012', '巴大蝶'],
    ['0013', '獨角蟲'], ['0014', '鐵殼蛹'], ['0015', '大針蜂'], ['0016', '波波'], ['0017', '比比鳥'], ['0018', '大比鳥'],
    ['0019', '小拉達'], ['0020', '拉達'], ['0021', '烈雀'], ['0022', '大嘴雀'], ['0023', '阿柏蛇'], ['0024', '阿柏怪'],
    ['0025', '皮卡丘'], ['0026', '雷丘'], ['0027', '穿山鼠'], ['0028', '穿山王'], ['0029', '尼多蘭'], ['0030', '尼多娜'],
    ['0031', '尼多后'], ['0032', '尼多朗'], ['0033', '尼多力諾'], ['0034', '尼多王'], ['0035', '皮皮'], ['0036', '皮可西'],
    ['0037', '六尾'], ['0038', '九尾'], ['0039', '胖丁'], ['0040', '胖可丁'], ['0041', '超音蝠'], ['0042', '大嘴蝠'],
    ['0043', '走路草'], ['0044', '臭臭花'], ['0045', '霸王花'], ['0046', '派拉斯'], ['0047', '派拉斯特'], ['0048', '毛球'],
    ['0049', '摩魯蛾'], ['0050', '地鼠'], ['0051', '三地鼠'], ['0052', '喵喵'], ['0053', '貓老大'], ['0054', '可達鴨'],
    ['0055', '哥達鴨'], ['0056', '猴怪'], ['0057', '火爆猴'], ['0058', '卡蒂狗'], ['0059', '風速狗'], ['0060', '蚊香蝌蚪'],
    ['0061', '蚊香君'], ['0062', '蚊香泳士'], ['0063', '凱西'], ['0064', '勇基拉'], ['0065', '胡地'], ['0066', '腕力'],
    ['0067', '豪力'], ['0068', '怪力'], ['0069', '喇叭芽'], ['0070', '口呆花'], ['0071', '大食花'], ['0072', '瑪瑙水母'],
    ['0073', '毒刺水母'], ['0074', '小拳石'], ['0075', '隆隆石'], ['0076', '隆隆岩'], ['0077', '小火馬'], ['0078', '烈焰馬'],
    ['0079', '呆呆獸'], ['0080', '呆殼獸'], ['0081', '小磁怪'], ['0082', '三合一磁怪'], ['0083', '大蔥鴨'], ['0084', '嘟嘟'],
    ['0085', '嘟嘟利'], ['0086', '小海獅'], ['0087', '白海獅'], ['0088', '臭泥'], ['0089', '臭臭泥'], ['0090', '大舌貝'],
    ['0091', '刺甲貝'], ['0092', '鬼斯'], ['0093', '鬼斯通'], ['0094', '耿鬼'], ['0095', '大岩蛇'], ['0096', '催眠貘'],
    ['0097', '引夢貘人'], ['0098', '大鉗蟹'], ['0099', '巨鉗蟹'], ['0100', '霹靂電球'], ['0101', '頑皮雷彈'], ['0102', '蛋蛋'],
    ['0103', '椰蛋樹'], ['0104', '卡拉卡拉'], ['0105', '嘎啦嘎啦'], ['0106', '飛腿郎'], ['0107', '快拳郎'], ['0108', '大舌頭'],
    ['0109', '瓦斯彈'], ['0110', '雙彈瓦斯'], ['0111', '獨角犀牛'], ['0112', '鑽角犀獸'], ['0113', '吉利蛋'], ['0114', '蔓藤怪'],
    ['0115', '袋獸'], ['0116', '墨海馬'], ['0117', '海刺龍'], ['0118', '角金魚'], ['0119', '金魚王'], ['0120', '海星星'],
    ['0121', '寶石海星'], ['0122', '魔牆人偶'], ['0123', '飛天螳螂'], ['0124', '迷唇姐'], ['0125', '電擊獸'], ['0126', '鴨嘴火獸'],
    ['0127', '凱羅斯'], ['0128', '肯泰羅'], ['0129', '鯉魚王'], ['0130', '暴鯉龍'], ['0131', '拉普拉斯'], ['0132', '百變怪'],
    ['0133', '伊布'], ['0134', '水伊布'], ['0135', '雷伊布'], ['0136', '火伊布'], ['0137', '多邊獸'], ['0138', '菊石獸'],
    ['0139', '多刺菊石獸'], ['0140', '化石盔'], ['0141', '鐮刀盔'], ['0142', '化石翼龍'], ['0143', '卡比獸'], ['0144', '急凍鳥'],
    ['0145', '閃電鳥'], ['0146', '火焰鳥'], ['0147', '迷你龍'], ['0148', '哈克龍'], ['0149', '快龍'], ['0150', '超夢'],
    ['0151', '夢幻'],
];

const QUIZ_TOTAL = 8;
const teaserPokemon = [['0006', '噴火龍'], ['0025', '皮卡丘'], ['0131', '拉普拉斯'], ['0143', '卡比獸']];

// ── Main tab ──
const mainTab = ref('quiz');

// ── Quiz state ──
const quizPhase = ref('idle');
const quizQuestion = ref(null);
const quizPicked = ref(null);
const quizScore = ref(0);
const quizRound = ref(0);
const quizAnswers = ref([]);

// ── Image source ──
const imgSource = ref('preset');
const fileInputRef = ref(null);
const uploadedDataUrl = ref(null);
const uploadedName = ref('');

// ── Hyperparameters ──
const HP_DEFAULTS = {
    cloudGenWeight: 20.0, shapeLossWeight: 11000.0, colorKeepWeight: 100.0,
    tvLossWeight: 3.8, lr: 0.04, epochs: 101, blurInterval: 50, blurSigma: 0.4,
};
const cloudGenWeight = ref(HP_DEFAULTS.cloudGenWeight);
const shapeLossWeight = ref(HP_DEFAULTS.shapeLossWeight);
const colorKeepWeight = ref(HP_DEFAULTS.colorKeepWeight);
const tvLossWeight = ref(HP_DEFAULTS.tvLossWeight);
const lr = ref(HP_DEFAULTS.lr);
const epochs = ref(HP_DEFAULTS.epochs);
const blurInterval = ref(HP_DEFAULTS.blurInterval);
const blurSigma = ref(HP_DEFAULTS.blurSigma);
const showHyperParams = ref(false);
const hpMode = ref('auto');

const autoParams = computed(() => {
    const t = Math.max(0, Math.min(1, (epochs.value - 101) / 900));
    return {
        cloudGenWeight: 20.0,
        shapeLossWeight: Math.round(11000 - 1000 * t),
        colorKeepWeight: 100.0,
        tvLossWeight: +(3.8 - 1.8 * t).toFixed(3),
        lr: +(0.04 - 0.035 * t).toFixed(5),
        blurInterval: Math.round(50 + 200 * t),
        blurSigma: +(0.4 - 0.1 * t).toFixed(3),
    };
});

function resetHyperParams() {
    cloudGenWeight.value = HP_DEFAULTS.cloudGenWeight;
    shapeLossWeight.value = HP_DEFAULTS.shapeLossWeight;
    colorKeepWeight.value = HP_DEFAULTS.colorKeepWeight;
    tvLossWeight.value = HP_DEFAULTS.tvLossWeight;
    lr.value = HP_DEFAULTS.lr;
    epochs.value = HP_DEFAULTS.epochs;
    blurInterval.value = HP_DEFAULTS.blurInterval;
    blurSigma.value = HP_DEFAULTS.blurSigma;
}

const samples = [
    { id: '0025', label: '皮卡丘', url: '/images/pokemon/original/0025_皮卡丘.png' },
    { id: '0004', label: '小火龍', url: '/images/pokemon/original/0004_小火龍.png' },
    { id: '0001', label: '妙蛙種子', url: '/images/pokemon/original/0001_妙蛙種子.png' },
    { id: '0007', label: '傑尼龜', url: '/images/pokemon/original/0007_傑尼龜.png' },
];

const modelStatus = ref('loading');
const loadProgress = ref(0);
const selectedSample = ref(null);
const isRunning = ref(false);
const isDone = ref(false);
const currentIter = ref(0);
const currentLoss = ref(null);
const showCanvases = ref(false);
const beforeCanvas = ref(null);
const afterCanvas = ref(null);

let tf = null;
let model = null;
let blurFilter05 = null;
let stopFlag = false;

onMounted(async () => {
    try {
        tf = await import('@tensorflow/tfjs');
        await tf.ready();
        model = await tf.loadGraphModel('/tfjs_model_dir/model.json', {
            onProgress: (p) => { loadProgress.value = Math.round(p * 100); },
        });
        tf.tidy(() => { model.execute(tf.zeros([1, 224, 224, 3])); });
        blurFilter05 = buildGaussianFilter(0.5);
        modelStatus.value = 'ready';
    } catch (e) {
        console.error('TF.js model load error:', e);
        modelStatus.value = 'error';
    }
});

onUnmounted(() => {
    stopFlag = true;
    blurFilter05?.dispose();
    model?.dispose();
});

// ── Quiz functions ──

function getRandomChoices(correctName) {
    const others = POKEMON.filter(p => p[1] !== correctName);
    const shuffled = [...others].sort(() => Math.random() - 0.5);
    return [...shuffled.slice(0, 3).map(p => p[1]), correctName].sort(() => Math.random() - 0.5);
}

function startQuiz() {
    quizScore.value = 0;
    quizRound.value = 0;
    quizAnswers.value = [];
    nextQuestion();
}

function nextQuestion() {
    const idx = Math.floor(Math.random() * POKEMON.length);
    const [id, name] = POKEMON[idx];
    quizQuestion.value = {
        id, name,
        cloudUrl: `/images/pokemon/claudify/${id}_${name}.png`,
        origUrl: `/images/pokemon/original/${id}_${name}.png`,
        choices: getRandomChoices(name),
    };
    quizPicked.value = null;
    quizRound.value++;
    quizPhase.value = 'question';
}

function pickAnswer(choice) {
    if (quizPhase.value !== 'question') return;
    quizPicked.value = choice;
    const correct = choice === quizQuestion.value.name;
    if (correct) quizScore.value++;
    quizAnswers.value.push(correct);
    quizPhase.value = 'revealed';
}

function advanceQuiz() {
    if (quizRound.value >= QUIZ_TOTAL) {
        quizPhase.value = 'done';
    } else {
        nextQuestion();
    }
}

function roundDotClass(i) {
    if (i <= quizAnswers.value.length) return quizAnswers.value[i - 1] ? 'correct' : 'wrong';
    if (i === quizRound.value) return 'current';
    return 'empty';
}

function choiceClass(choice) {
    if (quizPhase.value !== 'revealed') return '';
    if (choice === quizQuestion.value.name) return 'ans-correct';
    if (choice === quizPicked.value) return 'ans-wrong';
    return 'ans-other';
}

const doneMessage = computed(() => {
    const s = quizScore.value;
    if (s >= 7) return '🏆 驚人！你是真正的寶可夢大師！';
    if (s >= 5) return '🌟 很厲害！對雲朵形狀很有感覺！';
    if (s >= 3) return '🌤️ 不錯！下次繼續加油！';
    return '☁️ 雲朵可不好認，再試一次吧！';
});

// ── Image source functions ──

function setImgSource(src) {
    if (src === imgSource.value) return;
    imgSource.value = src;
    selectedSample.value = null;
    uploadedDataUrl.value = null;
    uploadedName.value = '';
    isDone.value = false;
    currentIter.value = 0;
    currentLoss.value = null;
    showCanvases.value = false;
}

function processFile(file) {
    const reader = new FileReader();
    reader.onload = (ev) => {
        uploadedDataUrl.value = ev.target.result;
        uploadedName.value = file.name.replace(/\.png$/i, '');
        selectImage({ id: 'upload', label: uploadedName.value, url: ev.target.result });
    };
    reader.readAsDataURL(file);
}

function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) processFile(file);
}

function handleDrop(e) {
    const file = e.dataTransfer?.files?.[0];
    if (file && file.type === 'image/png') processFile(file);
}

// ── TF.js helpers ──

function buildGaussianFilter(sigma) {
    const raw = [];
    let sum = 0;
    for (let h = 0; h < 3; h++) {
        for (let w = 0; w < 3; w++) {
            const v = Math.exp(-((h - 1) ** 2 + (w - 1) ** 2) / (2 * sigma * sigma));
            raw.push(v); sum += v;
        }
    }
    const data = [];
    for (let h = 0; h < 3; h++)
        for (let w = 0; w < 3; w++)
            for (let c = 0; c < 3; c++)
                data.push(raw[h * 3 + w] / sum);
    return tf.tensor4d(data, [3, 3, 3, 1]);
}

function applyBlur(img4d, filter) {
    return tf.depthwiseConv2d(img4d, filter, [1, 1], 'same');
}

async function renderToCanvas(tensor4d, canvasEl) {
    const squeezed = tf.tidy(() => tensor4d.squeeze().clipByValue(0, 1));
    await tf.browser.toPixels(squeezed, canvasEl);
    squeezed.dispose();
}

async function buildBasis(src) {
    const imgEl = await new Promise((res, rej) => {
        const img = new Image();
        if (!src.startsWith('data:')) img.crossOrigin = 'anonymous';
        img.onload = () => res(img);
        img.onerror = rej;
        img.src = src;
    });

    const cvWhite = document.createElement('canvas');
    cvWhite.width = cvWhite.height = 224;
    const ctxW = cvWhite.getContext('2d');
    ctxW.fillStyle = '#ffffff';
    ctxW.fillRect(0, 0, 224, 224);
    ctxW.drawImage(imgEl, 0, 0, 224, 224);
    const pixW = ctxW.getImageData(0, 0, 224, 224).data;

    const cvAlpha = document.createElement('canvas');
    cvAlpha.width = cvAlpha.height = 224;
    const ctxA = cvAlpha.getContext('2d');
    ctxA.clearRect(0, 0, 224, 224);
    ctxA.drawImage(imgEl, 0, 0, 224, 224);
    const pixA = ctxA.getImageData(0, 0, 224, 224).data;

    let alphaMin = 255;
    for (let i = 3; i < pixA.length; i += 4)
        if (pixA[i] < alphaMin) alphaMin = pixA[i];
    const hasTransparency = alphaMin < 250;

    return tf.tidy(() => {
        const rgbF = new Float32Array(224 * 224 * 3);
        for (let i = 0; i < 224 * 224; i++) {
            rgbF[i * 3] = pixW[i * 4] / 255;
            rgbF[i * 3 + 1] = pixW[i * 4 + 1] / 255;
            rgbF[i * 3 + 2] = pixW[i * 4 + 2] / 255;
        }
        const origT = tf.tensor4d(rgbF, [1, 224, 224, 3]);

        let mask;
        if (hasTransparency) {
            const aF = new Float32Array(224 * 224);
            for (let i = 0; i < 224 * 224; i++)
                aF[i] = pixA[i * 4 + 3] / 255 > 0.1 ? 1.0 : 0.0;
            mask = tf.tensor4d(aF, [1, 224, 224, 1]);
        } else {
            mask = tf.ones([1, 224, 224, 1]);
        }

        const r = origT.slice([0, 0, 0, 0], [1, 224, 224, 1]);
        const g = origT.slice([0, 0, 0, 1], [1, 224, 224, 1]);
        const b = origT.slice([0, 0, 0, 2], [1, 224, 224, 1]);
        const grayRaw = r.mul(0.299).add(g.mul(0.587)).add(b.mul(0.114));
        const gMin = grayRaw.min();
        const gMax = grayRaw.max();
        const grayNorm = grayRaw.sub(gMin).div(gMax.sub(gMin).add(1e-5)).mul(0.6).add(0.3);
        const grayLifted = grayNorm
            .add(tf.scalar(1).sub(grayNorm).square().mul(0.5))
            .clipByValue(0, 1);

        const gray3 = tf.concat([grayLifted, grayLifted, grayLifted], 3);
        const bg = tf.tensor4d([0.4, 0.65, 0.9], [1, 1, 1, 3]);
        const mask3 = tf.concat([mask, mask, mask], 3);
        const invMask = tf.scalar(1).sub(mask3);

        return gray3.mul(mask3).add(bg.mul(invMask));
    });
}

// ── UI actions ──

function selectImage(s) {
    selectedSample.value = s;
    isDone.value = false;
    currentIter.value = 0;
    currentLoss.value = null;
    showCanvases.value = false;
}

async function startOpt() {
    if (!selectedSample.value || isRunning.value) return;

    stopFlag = false;
    isRunning.value = true;
    isDone.value = false;
    currentIter.value = 0;
    currentLoss.value = null;
    showCanvases.value = false;

    const N = epochs.value;

    let _cgw, _slw, _ckw, _tvw, _lr, _blurInterval, _blurSigma;
    if (hpMode.value === 'auto') {
        const p = autoParams.value;
        _cgw = p.cloudGenWeight;
        _slw = p.shapeLossWeight;
        _ckw = p.colorKeepWeight;
        _tvw = p.tvLossWeight;
        _lr = p.lr;
        _blurInterval = p.blurInterval;
        _blurSigma = p.blurSigma;
    } else {
        _cgw = cloudGenWeight.value;
        _slw = shapeLossWeight.value;
        _ckw = colorKeepWeight.value;
        _tvw = tvLossWeight.value;
        _lr = lr.value;
        _blurInterval = Math.max(1, Math.round(blurInterval.value));
        _blurSigma = blurSigma.value;
    }

    let processedBasis = null;
    let genImg = null;
    let periodicFilter = null;
    const optimizer = tf.train.adam(_lr);

    try {
        periodicFilter = buildGaussianFilter(_blurSigma);
        processedBasis = await buildBasis(selectedSample.value.url);
        genImg = tf.variable(processedBasis.clone());

        showCanvases.value = true;
        await tf.nextFrame();
        await renderToCanvas(processedBasis, beforeCanvas.value);

        for (let i = 0; i <= N; i++) {
            if (stopFlag) break;

            const cost = optimizer.minimize(() => {
                return tf.tidy(() => {
                    const blurred = applyBlur(genImg, blurFilter05);
                    const imgPrep = blurred.mul(2).sub(1);
                    const pred = model.execute(imgPrep);

                    const cloudScore = pred.slice([0, 0], [1, 1]).squeeze();
                    const lossCloud = cloudScore.mul(-_cgw);

                    const diff = genImg.sub(processedBasis);
                    const lossStruct = diff.square().mean().mul(_slw);

                    const rCh = genImg.slice([0, 0, 0, 0], [1, 224, 224, 1]);
                    const gCh = genImg.slice([0, 0, 0, 1], [1, 224, 224, 1]);
                    const bCh = genImg.slice([0, 0, 0, 2], [1, 224, 224, 1]);
                    const lossColor = rCh.sub(gCh).square().mean()
                        .add(gCh.sub(bCh).square().mean())
                        .mul(_ckw);

                    const h1 = genImg.slice([0, 0, 0, 0], [1, 224, 223, 3]);
                    const h2 = genImg.slice([0, 0, 1, 0], [1, 224, 223, 3]);
                    const v1 = genImg.slice([0, 0, 0, 0], [1, 223, 224, 3]);
                    const v2 = genImg.slice([0, 1, 0, 0], [1, 223, 224, 3]);
                    const lossTV = h1.sub(h2).abs().sum()
                        .add(v1.sub(v2).abs().sum())
                        .mul(_tvw);

                    return lossCloud.add(lossStruct).add(lossColor).add(lossTV);
                });
            }, true, [genImg]);

            const lossVal = cost?.dataSync()[0];
            cost?.dispose();

            tf.tidy(() => { genImg.assign(tf.clipByValue(genImg, 0, 1)); });

            if (i > 0 && i % _blurInterval === 0) {
                tf.tidy(() => { genImg.assign(applyBlur(genImg, periodicFilter)); });
            }

            currentIter.value = i;
            if (lossVal != null) currentLoss.value = lossVal.toFixed(2);

            if (i % 5 === 0) {
                await renderToCanvas(genImg, afterCanvas.value);
                await tf.nextFrame();
            }
        }

        await renderToCanvas(genImg, afterCanvas.value);
        isDone.value = true;

    } catch (e) {
        console.error('Optimization error:', e);
    } finally {
        genImg?.dispose();
        processedBasis?.dispose();
        periodicFilter?.dispose();
        try { optimizer.dispose(); } catch (_) { }
        isRunning.value = false;
    }
}
</script>

<style scoped>
.cloud-demo {
    display: flex;
    flex-direction: column;
    gap: 14px;
    font-family: 'Inter', 'PingFang TC', 'Noto Sans TC', sans-serif;
}

/* ── Main tabs ── */
.main-tabs {
    display: flex;
    gap: 0;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(100, 116, 139, 0.15);
    background: rgba(100, 116, 139, 0.05);
    padding: 4px;
    gap: 4px;
}

.main-tab {
    flex: 1;
    padding: 8px 12px;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
}

.main-tab.active {
    background: #fff;
    color: #1e293b;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.main-tab:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.cd-dark .main-tabs {
    border-color: rgba(148, 163, 184, 0.12);
    background: rgba(15, 23, 42, 0.3);
}

.cd-dark .main-tab {
    color: #94a3b8;
}

.cd-dark .main-tab.active {
    background: rgba(30, 41, 59, 0.9);
    color: #e2e8f0;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

/* ── Tab bridges ── */
.tab-bridge {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 10px 0 2px;
    border-top: 1px solid rgba(100, 116, 139, 0.1);
    margin-top: 4px;
}

.bridge-text {
    font-size: 12px;
    color: #94a3b8;
}

.bridge-btn {
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    background: rgba(59, 130, 246, 0.06);
    color: #3b82f6;
    font-size: 12px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
}

.bridge-btn:hover {
    background: rgba(59, 130, 246, 0.12);
}

.cd-dark .bridge-btn {
    border-color: rgba(78, 205, 196, 0.3);
    background: rgba(78, 205, 196, 0.06);
    color: #4ecdc4;
}

.cd-dark .bridge-btn:hover {
    background: rgba(78, 205, 196, 0.12);
}

.tab-bridge-top {
    display: flex;
    align-items: center;
    padding: 0 0 2px;
}

.bridge-link {
    padding: 4px 0;
    border: none;
    background: transparent;
    color: #94a3b8;
    font-size: 12px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: color 0.2s;
}

.bridge-link:hover {
    color: #3b82f6;
}

.cd-dark .bridge-link:hover {
    color: #4ecdc4;
}

/* ── Quiz: idle ── */
.quiz-idle {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 4px 0;
}

.quiz-idle-desc {
    font-size: 13px;
    color: #475569;
    text-align: center;
    line-height: 1.6;
    margin: 0;
}

.cd-dark .quiz-idle-desc {
    color: #94a3b8;
}

.quiz-teaser-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    width: 100%;
}

.quiz-teaser-cell {
    position: relative;
    aspect-ratio: 1 / 1;
    border-radius: 12px;
    overflow: hidden;
    background: #f1f5f9;
}

.cd-dark .quiz-teaser-cell {
    background: rgba(15, 23, 42, 0.4);
}

.quiz-teaser-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 4px;
    box-sizing: border-box;
    filter: blur(0px);
}

.quiz-teaser-q {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 900;
    color: rgba(255, 255, 255, 0.85);
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    background: rgba(0, 0, 0, 0.18);
    pointer-events: none;
}

.quiz-start-btn {
    padding: 10px 28px;
    border-radius: 20px;
    border: none;
    background: #3b82f6;
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
}

.quiz-start-btn:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
}

.cd-dark .quiz-start-btn {
    background: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 4px 14px rgba(78, 205, 196, 0.35);
}

.cd-dark .quiz-start-btn:hover {
    background: #2dd4bf;
}

/* ── Quiz: active ── */
.quiz-active {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.quiz-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.quiz-dots {
    display: flex;
    gap: 5px;
    align-items: center;
}

.qdot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(148, 163, 184, 0.25);
    border: 1.5px solid rgba(148, 163, 184, 0.3);
    transition: all 0.2s;
}

.qdot.correct {
    background: #10b981;
    border-color: #10b981;
}

.qdot.wrong {
    background: #ef4444;
    border-color: #ef4444;
}

.qdot.current {
    background: #3b82f6;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.cd-dark .qdot.current {
    background: #4ecdc4;
    border-color: #4ecdc4;
    box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
}

.quiz-score-badge {
    font-size: 12px;
    font-weight: 700;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #64748b;
    background: rgba(100, 116, 139, 0.08);
    padding: 3px 8px;
    border-radius: 8px;
}

.cd-dark .quiz-score-badge {
    color: #94a3b8;
}

/* Question image stage */
.quiz-img-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.quiz-cloud-img {
    width: 100%;
    max-width: 300px;
    height: auto;
    border-radius: 14px;
    background: #f1f5f9;
    border: 1px solid rgba(0, 0, 0, 0.06);
    object-fit: contain;
}

.cd-dark .quiz-cloud-img {
    background: rgba(15, 23, 42, 0.4);
    border-color: rgba(255, 255, 255, 0.06);
}

.quiz-prompt {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    margin: 0;
    text-align: center;
}

.cd-dark .quiz-prompt {
    color: #94a3b8;
}

/* Reveal stage */
.quiz-reveal-stage {
    display: flex;
    align-items: center;
    gap: 8px;
}

.qr-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    min-width: 0;
}

.qr-img {
    width: 100%;
    max-width: 300px;
    height: auto;
    border-radius: 10px;
    background: #f1f5f9;
    border: 1px solid rgba(0, 0, 0, 0.06);
    object-fit: contain;
}

.cd-dark .qr-img {
    background: rgba(15, 23, 42, 0.4);
    border-color: rgba(255, 255, 255, 0.06);
}

.qr-lbl {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    text-align: center;
}

.qr-sep {
    font-size: 20px;
    color: #94a3b8;
    flex-shrink: 0;
    user-select: none;
}

/* Result banner */
.quiz-result-banner {
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
}

.quiz-result-banner.correct {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #059669;
}

.quiz-result-banner.wrong {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #dc2626;
}

.cd-dark .quiz-result-banner.correct {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
}

.cd-dark .quiz-result-banner.wrong {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
}

/* Choice grid */
.quiz-choices {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.quiz-choice {
    padding: 9px 10px;
    border-radius: 10px;
    border: 1.5px solid rgba(100, 116, 139, 0.2);
    background: rgba(100, 116, 139, 0.05);
    color: #374151;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.18s;
    text-align: center;
    line-height: 1.3;
}

.quiz-choice:hover:not(:disabled) {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.08);
    color: #1d4ed8;
    transform: translateY(-1px);
}

.quiz-choice:disabled {
    cursor: default;
}

.quiz-choice.ans-correct {
    background: rgba(16, 185, 129, 0.12);
    border-color: #10b981;
    color: #059669;
}

.quiz-choice.ans-wrong {
    background: rgba(239, 68, 68, 0.1);
    border-color: #ef4444;
    color: #dc2626;
}

.quiz-choice.ans-other {
    opacity: 0.4;
}

.cd-dark .quiz-choice {
    color: #cbd5e1;
    border-color: rgba(148, 163, 184, 0.15);
}

.cd-dark .quiz-choice:hover:not(:disabled) {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.08);
    color: #4ecdc4;
}

.cd-dark .quiz-choice.ans-correct {
    background: rgba(16, 185, 129, 0.15);
    border-color: #10b981;
    color: #34d399;
}

.cd-dark .quiz-choice.ans-wrong {
    background: rgba(239, 68, 68, 0.12);
    border-color: #ef4444;
    color: #f87171;
}

/* Next button */
.quiz-next-wrap {
    display: flex;
    justify-content: flex-end;
}

.quiz-next-btn {
    padding: 8px 20px;
    border-radius: 16px;
    border: none;
    background: #3b82f6;
    color: #fff;
    font-size: 13px;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3);
}

.quiz-next-btn:hover {
    background: #2563eb;
    transform: translateY(-1px);
}

.cd-dark .quiz-next-btn {
    background: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 3px 10px rgba(78, 205, 196, 0.3);
}

.cd-dark .quiz-next-btn:hover {
    background: #2dd4bf;
}

/* ── Quiz: done ── */
.quiz-done {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 8px 0 4px;
}

.quiz-done-score {
    display: flex;
    align-items: baseline;
    gap: 4px;
}

.qds-num {
    font-size: 52px;
    font-weight: 900;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #3b82f6;
    line-height: 1;
}

.qds-sep {
    font-size: 28px;
    font-weight: 700;
    color: #94a3b8;
}

.qds-total {
    font-size: 28px;
    font-weight: 700;
    color: #94a3b8;
}

.cd-dark .qds-num {
    color: #4ecdc4;
}

.quiz-done-msg {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin: 0;
    text-align: center;
}

.cd-dark .quiz-done-msg {
    color: #cbd5e1;
}

.quiz-done-dots {
    display: flex;
    gap: 6px;
}

/* ── Quiz transitions ── */
.quiz-pop-enter-active {
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.quiz-pop-leave-active {
    transition: all 0.15s ease;
}

.quiz-pop-enter-from {
    opacity: 0;
    transform: scale(0.85) translateY(4px);
}

.quiz-pop-leave-to {
    opacity: 0;
}

/* ── Image source toggle ── */
.src-toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.src-toggle {
    display: flex;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(100, 116, 139, 0.18);
    background: rgba(100, 116, 139, 0.05);
    flex-shrink: 0;
}

.src-tab {
    padding: 4px 10px;
    border: none;
    background: transparent;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.18s;
}

.src-tab.active {
    background: #3b82f6;
    color: #fff;
}

.src-tab:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.cd-dark .src-tab.active {
    background: #4ecdc4;
    color: #0f172a;
}

/* ── Upload zone ── */
.upload-zone {
    min-height: 100px;
    border-radius: 14px;
    border: 2px dashed rgba(100, 116, 139, 0.25);
    background: rgba(100, 116, 139, 0.04);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 16px 12px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}

.upload-zone:hover:not(.uz-locked) {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.04);
}

.upload-zone.uz-has-file {
    border-style: solid;
    border-color: rgba(59, 130, 246, 0.4);
    background: rgba(59, 130, 246, 0.04);
    flex-direction: row;
    justify-content: flex-start;
    gap: 12px;
    padding: 10px 14px;
}

.upload-zone.uz-locked {
    cursor: default;
    opacity: 0.7;
}

.cd-dark .upload-zone {
    border-color: rgba(148, 163, 184, 0.2);
    background: rgba(15, 23, 42, 0.2);
}

.cd-dark .upload-zone:hover:not(.uz-locked) {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.04);
}

.cd-dark .upload-zone.uz-has-file {
    border-color: rgba(78, 205, 196, 0.35);
    background: rgba(78, 205, 196, 0.04);
}

.uz-icon {
    font-size: 24px;
    line-height: 1;
}

.uz-title {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    margin: 0;
}

.cd-dark .uz-title {
    color: #94a3b8;
}

.uz-note {
    font-size: 11px;
    color: #94a3b8;
    margin: 0;
    line-height: 1.5;
}

.uz-preview {
    width: 64px;
    height: 64px;
    object-fit: contain;
    border-radius: 8px;
    flex-shrink: 0;
    background: rgba(148, 163, 184, 0.1);
}

.uz-file-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    text-align: left;
    min-width: 0;
}

.uz-name {
    font-size: 12px;
    font-weight: 600;
    color: #374151;
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.cd-dark .uz-name {
    color: #cbd5e1;
}

.uz-change {
    font-size: 11px;
    color: #94a3b8;
    margin: 0;
}

/* ── Loading / Error ── */
.model-loading,
.model-error {
    padding: 20px 0 8px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.loading-text,
.model-error {
    font-size: 13px;
    color: #64748b;
    margin: 0;
}

.cd-dark .loading-text,
.cd-dark .model-error {
    color: #94a3b8;
}

/* ── Progress track ── */
.prog-track {
    height: 6px;
    border-radius: 999px;
    background: rgba(59, 130, 246, 0.12);
    overflow: hidden;
}

.prog-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    transition: width 0.3s ease;
}

.cd-dark .prog-track {
    background: rgba(78, 205, 196, 0.12);
}

.cd-dark .prog-fill {
    background: linear-gradient(90deg, #4ecdc4, #8b5cf6);
}

/* ── Image grid ── */
.input-label {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin: 0;
}

.cd-dark .input-label {
    color: #cbd5e1;
}

.img-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.img-thumb {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s ease;
    aspect-ratio: 1 / 1;
    background: #f1f5f9;
}

.img-thumb img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 4px;
    box-sizing: border-box;
}

.img-thumb:hover:not(.locked) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.2);
}

.img-thumb.selected {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.img-thumb.locked {
    cursor: default;
    opacity: 0.7;
}

.cd-dark .img-thumb {
    background: rgba(15, 23, 42, 0.4);
}

.cd-dark .img-thumb.selected {
    border-color: #4ecdc4;
    box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.15);
}

.thumb-label {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.55), transparent);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 10px 6px 5px;
    text-align: center;
}

.checkmark {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #3b82f6;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cd-dark .checkmark {
    background: #4ecdc4;
    color: #0f172a;
}

/* ── Run button ── */
.cd-run-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 11px 22px;
    border-radius: 20px;
    background: #3b82f6;
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    transition: all 0.25s;
    font-family: inherit;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
    align-self: flex-start;
}

.cd-run-btn:hover:not(:disabled) {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
}

.cd-run-btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.cd-dark .cd-run-btn {
    background: #4ecdc4;
    color: #0f172a;
    box-shadow: 0 4px 14px rgba(78, 205, 196, 0.35);
}

.cd-dark .cd-run-btn:hover:not(:disabled) {
    background: #2dd4bf;
}

.btn-inner {
    display: flex;
    align-items: center;
    gap: 8px;
}

.spin-sm {
    width: 13px;
    height: 13px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: cdSpin 0.7s linear infinite;
    flex-shrink: 0;
}

.cd-dark .spin-sm {
    border-color: rgba(15, 23, 42, 0.3);
    border-top-color: #0f172a;
}

@keyframes cdSpin {
    to {
        transform: rotate(360deg);
    }
}

/* ── Opt progress ── */
.opt-info {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.opt-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #64748b;
}

.cd-dark .opt-meta {
    color: #94a3b8;
}

.loss-val {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ── Canvas comparison ── */
.canvas-compare {
    display: flex;
    align-items: center;
    gap: 10px;
}

.canvas-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}

.canvas-label {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.5px;
    margin: 0;
    text-align: center;
}

.res-canvas {
    width: 100%;
    max-width: 300px;
    height: auto;
    border-radius: 10px;
    display: block;
    border: 1px solid rgba(0, 0, 0, 0.06);
    background: #f1f5f9;
    image-rendering: pixelated;
}

.cd-dark .res-canvas {
    border-color: rgba(255, 255, 255, 0.06);
    background: rgba(15, 23, 42, 0.4);
}

.arrow-sep {
    font-size: 18px;
    color: #94a3b8;
    flex-shrink: 0;
    user-select: none;
}

/* ── Done note ── */
.done-note {
    font-size: 12px;
    color: #10b981;
    margin: 0;
    padding: 8px 12px;
    border-radius: 10px;
    background: rgba(16, 185, 129, 0.07);
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.cd-dark .done-note {
    background: rgba(16, 185, 129, 0.08);
    border-color: rgba(16, 185, 129, 0.15);
}

/* ── Tech note ── */
.tech-note {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    font-size: 11px;
    color: #94a3b8;
    line-height: 1.5;
    padding: 8px 10px;
    background: rgba(148, 163, 184, 0.06);
    border-radius: 8px;
}

/* ── Hyperparameter panel ── */
.hp-section {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.hp-toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 12px;
    border: 1px solid rgba(100, 116, 139, 0.18);
    background: rgba(100, 116, 139, 0.06);
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    align-self: flex-start;
}

.hp-toggle:hover:not(:disabled) {
    background: rgba(100, 116, 139, 0.12);
    color: #475569;
}

.hp-toggle:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.cd-dark .hp-toggle {
    color: #94a3b8;
    border-color: rgba(148, 163, 184, 0.15);
}

.cd-dark .hp-toggle:hover:not(:disabled) {
    color: #cbd5e1;
}

.hp-arrow {
    display: inline-block;
    transition: transform 0.2s;
    font-size: 11px;
    margin-left: 2px;
}

.hp-arrow.open {
    transform: rotate(180deg);
}

.hp-panel {
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px;
    border-radius: 14px;
    background: rgba(59, 130, 246, 0.04);
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.cd-dark .hp-panel {
    background: rgba(78, 205, 196, 0.04);
    border-color: rgba(78, 205, 196, 0.1);
}

.hp-mode-row {
    display: flex;
    gap: 6px;
}

.hp-tab {
    flex: 1;
    padding: 5px 0;
    border-radius: 8px;
    border: 1px solid rgba(100, 116, 139, 0.2);
    background: transparent;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.18s;
}

.hp-tab.active {
    background: #3b82f6;
    border-color: #3b82f6;
    color: #fff;
}

.hp-tab:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.cd-dark .hp-tab.active {
    background: #4ecdc4;
    border-color: #4ecdc4;
    color: #0f172a;
}

.epoch-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.hp-label-sm {
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    white-space: nowrap;
    min-width: 36px;
}

.epoch-slider-wrap {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 6px;
}

.epoch-limit {
    font-size: 10px;
    color: #94a3b8;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    white-space: nowrap;
}

.epoch-slider {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    border-radius: 999px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    outline: none;
    cursor: pointer;
}

.epoch-slider:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.epoch-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #3b82f6;
    border: 2px solid #fff;
    box-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
    cursor: pointer;
}

.epoch-slider::-moz-range-thumb {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #3b82f6;
    border: 2px solid #fff;
    box-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
    cursor: pointer;
}

.cd-dark .epoch-slider {
    background: linear-gradient(90deg, #4ecdc4, #8b5cf6);
}

.cd-dark .epoch-slider::-webkit-slider-thumb {
    background: #4ecdc4;
    border-color: #0f172a;
}

.cd-dark .epoch-slider::-moz-range-thumb {
    background: #4ecdc4;
    border-color: #0f172a;
}

.epoch-cur {
    font-size: 12px;
    font-weight: 700;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #3b82f6;
    min-width: 32px;
    text-align: right;
}

.cd-dark .epoch-cur {
    color: #4ecdc4;
}

.hp-auto-hint {
    font-size: 10px;
    color: #94a3b8;
    margin: 0;
    font-style: italic;
}

.hp-auto-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 5px 10px;
}

.hp-auto-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 3px 6px;
    border-radius: 6px;
    background: rgba(148, 163, 184, 0.06);
}

.hp-auto-key {
    font-size: 9px;
    font-weight: 700;
    color: #94a3b8;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    letter-spacing: 0.3px;
}

.hp-auto-val {
    font-size: 11px;
    font-weight: 700;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #3b82f6;
}

.cd-dark .hp-auto-val {
    color: #4ecdc4;
}

.hp-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}

.hp-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.hp-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #94a3b8;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.hp-input {
    width: 100%;
    padding: 5px 8px;
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.8);
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #0f1724;
    box-sizing: border-box;
    transition: border-color 0.15s, box-shadow 0.15s;
}

.hp-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.cd-dark .hp-input {
    background: rgba(15, 23, 42, 0.5);
    border-color: rgba(255, 255, 255, 0.08);
    color: #e6eef8;
}

.cd-dark .hp-input:focus {
    border-color: #4ecdc4;
    box-shadow: 0 0 0 2px rgba(78, 205, 196, 0.15);
}

.hp-reset {
    grid-column: 1 / -1;
    padding: 5px 0;
    border-radius: 8px;
    border: 1px dashed rgba(100, 116, 139, 0.25);
    background: transparent;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
}

.hp-reset:hover {
    background: rgba(100, 116, 139, 0.07);
    color: #64748b;
}

.cd-dark .hp-reset:hover {
    color: #cbd5e1;
}

/* ── Transitions ── */
.hp-expand-enter-active {
    transition: all 0.25s ease;
}

.hp-expand-leave-active {
    transition: all 0.18s ease;
}

.hp-expand-enter-from,
.hp-expand-leave-to {
    opacity: 0;
    transform: translateY(-6px);
}

.cd-fade-enter-active {
    transition: all 0.35s ease;
}

.cd-fade-enter-from {
    opacity: 0;
    transform: translateY(8px);
}

/* ── RWD ── */
@media (max-width: 767px) {

    /* 圖片選擇格：4欄 → 2欄 */
    .img-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    /* 測驗題預覽格：4欄 → 2欄 */
    .quiz-teaser-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    /* 超參格：3欄 → 2欄 */
    .hp-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 400px) {
    .epoch-row {
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;

        /* 如果你想放在參數區左邊或右邊 */
        width: auto;
        min-width: 48px;
    }

    .epoch-slider-wrap {
        flex-direction: column-reverse;
        gap: 8px;
    }

    .epoch-slider {
        writing-mode: bt-lr;
        /* 垂直 */
        -webkit-appearance: slider-vertical;
        appearance: slider-vertical;

        width: 6px;
        height: 140px;
    }

    .epoch-cur {
        font-size: 11px;
    }

    .hp-auto-grid {
        display: flex;
        flex-direction: column;
        justify-content: space-between
    }

    .hp-grid {
        display: block;
    }

    .hp-panel {
        display: grid;
        /* 2 columns */
        grid-template-columns: 1fr 1fr;
        /* 3 rows */
        grid-template-rows: auto auto auto auto;
    }

    .hp-mode-row {
        grid-column: 1 / 3;
        grid-row: 1;
    }

    .hp-auto-hint {
        /* 橫跨兩欄 */
        grid-column: 1 / 3;
        grid-row: 2;
    }

    .epoch-row {
        grid-column: 1;
        grid-row: 3;
    }

    .hp-auto-grid {
        /* 橫跨兩欄 */
        grid-column: 2;
        grid-row: 3;
    }

    .epoch-cur {
        text-align: center
    }

    .hp-auto-hint {
        text-align: center
    }

    .cd-run-btn {
        margin: auto;
    }

    .canvas-compare {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }

    .canvas-box{
        flex-direction: column-reverse;
    }

    .arrow-sep {
        transform: rotate(90deg);
    }
}
</style>
