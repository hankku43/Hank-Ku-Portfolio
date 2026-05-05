<script setup>
import { ref } from 'vue';

defineProps({
    isDark: { type: Boolean, default: false },
});

const emit = defineEmits(['status-change']);

const BOARDS = [
    'Baseball', 'Boy-Girl', 'C_Chat', 'HatePolitics',
    'Lifeismoney', 'Military', 'PC_Shopping', 'Stock', 'Tech_Job',
];

const BOARD_META = {
    Baseball: { zh: '棒球板', emoji: '⚾' },
    'Boy-Girl': { zh: '男女板', emoji: '💑' },
    C_Chat: { zh: 'C洽板', emoji: '💬' },
    HatePolitics: { zh: '政黑板', emoji: '🗳️' },
    Lifeismoney: { zh: '省錢板', emoji: '💰' },
    Military: { zh: '軍事板', emoji: '🎖️' },
    PC_Shopping: { zh: '電腦購物板', emoji: '🖥️' },
    Stock: { zh: '股票板', emoji: '📈' },
    Tech_Job: { zh: '科技工作板', emoji: '👨‍💻' },
};

const SAMPLES = [
    '[問卦] 今天台積電漲停，是不是要起飛了？',
    '[心得] M4 MacBook Pro 入手一個月的感想',
    '[討論] 現在買車比較划算還是租車？',
    '[閒聊] 為什麼台灣年輕人越來越不想生小孩',
];

const title = ref('');
const isLoading = ref(false);
const result = ref(null);
const errorMsg = ref('');
const feedbackLabel = ref('');
const feedbackMsg = ref('');
const feedbackLoading = ref(false);

function useSample(s) {
    title.value = s;
    result.value = null;
    errorMsg.value = '';
    feedbackMsg.value = '';
}

async function predict() {
    if (!title.value.trim() || isLoading.value) return;
    isLoading.value = true;
    result.value = null;
    errorMsg.value = '';
    feedbackMsg.value = '';
    emit('status-change', 'Doc2Vec 嵌入 → MLP 分類中...');
    try {
        const res = await fetch('/api/ptt/classify-board', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title.value.trim() }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        result.value = data;
        feedbackLabel.value = data.board;
        emit('status-change', '✓');
    } catch {
        errorMsg.value = '無法連線至後端，請確認 API 服務已啟動。';
        emit('status-change', '');
    } finally {
        isLoading.value = false;
    }
}

async function submitFeedback() {
    if (!feedbackLabel.value || !title.value || feedbackLoading.value) return;
    feedbackLoading.value = true;
    try {
        await fetch('/api/ptt/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ label: feedbackLabel.value, article_title: title.value }),
        });
        feedbackMsg.value = '✓ 感謝您的回饋，已記錄';
        setTimeout(() => { feedbackMsg.value = ''; }, 3000);
    } catch {
        feedbackMsg.value = '回饋送出失敗，請稍後再試';
    } finally {
        feedbackLoading.value = false;
    }
}
</script>

<template>
    <div class="ptt-wrap">

        <!-- 樣本快速填入 -->
        <div class="sample-chips">
            <button v-for="s in SAMPLES" :key="s" class="chip" @click="useSample(s)">{{ s }}</button>
        </div>

        <!-- 輸入列 -->
        <div class="input-row">
            <input v-model="title" placeholder="輸入 PTT 標題..." class="title-input" @keyup.enter="predict" />
            <button class="predict-btn" :disabled="!title.trim() || isLoading" @click="predict">
                <span v-if="isLoading" class="spinner-sm"></span>
                <template v-else>分析</template>
            </button>
        </div>

        <!-- 錯誤訊息 -->
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <!-- 結果 -->
        <Transition name="result-pop">
            <div v-if="result" class="result-card">

                <!-- 主要預測 -->
                <div class="main-pred">
                    <span class="pred-emoji">{{ BOARD_META[result.board]?.emoji }}</span>
                    <div class="pred-names">
                        <span class="pred-board">{{ result.board }}</span>
                        <span class="pred-zh">{{ BOARD_META[result.board]?.zh }}</span>
                    </div>
                    <span class="pred-conf">{{ (result.confidence * 100).toFixed(1) }}%</span>
                </div>

                <!-- Top-3 機率條 -->
                <div class="top3-list">
                    <div v-for="item in result.top3" :key="item.board" class="top3-item">
                        <span class="top3-label">{{ item.board }}</span>
                        <div class="top3-bar-wrap">
                            <div class="top3-bar" :style="{ width: (item.prob * 100).toFixed(1) + '%' }"></div>
                        </div>
                        <span class="top3-pct">{{ (item.prob * 100).toFixed(1) }}%</span>
                    </div>
                </div>

                <!-- 回饋 -->
                <div class="feedback-section">
                    <p class="fb-label">預測有誤？請選擇正確版面：</p>
                    <div class="feedback-row">
                        <select v-model="feedbackLabel" class="fb-select">
                            <option v-for="b in BOARDS" :key="b" :value="b">{{ b }}</option>
                        </select>
                        <button class="fb-btn" :disabled="feedbackLoading" @click="submitFeedback">
                            {{ feedbackLoading ? '送出中...' : '送出回饋' }}
                        </button>
                    </div>
                    <p v-if="feedbackMsg" class="feedback-msg">{{ feedbackMsg }}</p>
                </div>

            </div>
        </Transition>

    </div>
</template>

<style scoped>
.ptt-wrap {
    display: flex;
    flex-direction: column;
    gap: 14px;
    width: 100%;
}

/* ── 樣本 chips ── */
.sample-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.chip {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: transparent;
    color: inherit;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 240px;
}

.chip:hover {
    background: rgba(99, 102, 241, 0.15);
    border-color: rgba(99, 102, 241, 0.5);
    color: #818cf8;
}

/* ── 輸入列 ── */
.input-row {
    display: flex;
    gap: 8px;
}

.title-input {
    flex: 1;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(255, 255, 255, 0.07);
    color: inherit;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}

.title-input:focus {
    border-color: rgba(99, 102, 241, 0.6);
}

.predict-btn {
    padding: 10px 20px;
    border-radius: 10px;
    border: none;
    background: #6366f1;
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, opacity 0.15s;
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
}

.predict-btn:hover:not(:disabled) {
    background: #4f46e5;
}

.predict-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* ── spinner ── */
.spinner-sm {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* ── 錯誤 ── */
.error-msg {
    font-size: 12px;
    color: #f87171;
    margin: 0;
}

/* ── 結果卡片 ── */
.result-card {
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 14px;
    padding: 18px 20px;
    background: rgba(99, 102, 241, 0.05);
    display: flex;
    flex-direction: column;
    gap: 16px;
}

/* 主要預測 */
.main-pred {
    display: flex;
    align-items: center;
    gap: 14px;
}

.pred-emoji {
    font-size: 32px;
    line-height: 1;
}

.pred-names {
    display: flex;
    flex-direction: column;
    flex: 1;
}

.pred-board {
    font-size: 20px;
    font-weight: 700;
    color: #818cf8;
    line-height: 1.2;
}

.pred-zh {
    font-size: 12px;
    opacity: 0.6;
}

.pred-conf {
    font-size: 22px;
    font-weight: 800;
    color: #34d399;
}

/* Top-3 條 */
.top3-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.top3-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.top3-label {
    font-size: 11px;
    width: 90px;
    flex-shrink: 0;
    opacity: 0.75;
}

.top3-bar-wrap {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: rgba(148, 163, 184, 0.15);
    overflow: hidden;
}

.top3-bar {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #6366f1, #818cf8);
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.top3-pct {
    font-size: 11px;
    width: 44px;
    text-align: right;
    opacity: 0.75;
}

/* 回饋 */
.feedback-section {
    border-top: 1px solid rgba(148, 163, 184, 0.15);
    padding-top: 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.fb-label {
    font-size: 11px;
    opacity: 0.55;
    margin: 0;
    font-weight: 500;
    letter-spacing: 0.03em;
}

.feedback-row {
    display: flex;
    gap: 8px;
}

.fb-select {
    flex: 1;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    background: rgba(255, 255, 255, 0.06);
    color: inherit;
    font-size: 12px;
    outline: none;
}

.fb-btn {
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
    background: rgba(52, 211, 153, 0.2);
    color: #34d399;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
    white-space: nowrap;
}

.fb-btn:hover:not(:disabled) {
    background: rgba(52, 211, 153, 0.35);
}

.fb-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.feedback-msg {
    font-size: 11px;
    color: #34d399;
    margin: 0;
    font-weight: 600;
}

/* ── Transition ── */
.result-pop-enter-active {
    transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.result-pop-enter-from {
    opacity: 0;
    transform: translateY(12px) scale(0.97);
}

@media (max-width: 500px) {
    .input-row {
        flex-direction: column;
    }
    .predict-btn{
        width: 100%;
        margin: auto;
        display: block;
        text-align: center;
        letter-spacing: 0.3em;
    }
}

@media (max-width: 400px) {
    .pred-emoji {
        font-size: 24px;
    }

    .pred-board {
        font-size: 16px;
        font-weight: 500
    }

    .pred-zh {
        font-size: 10px;
    }

    .pred-conf {
        font-size: 18px;
    }

    .feedback-row{
        flex-direction: column;
    }

    .fb-btn{
        letter-spacing: 0.3em;
    }

    .top3-label{
        max-width: 90px;
        width: 40%;
        min-width: 40px;
    }

    .top3-bar-wrap{
        width: 30%;
    }
}
</style>
