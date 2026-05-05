<template>
  <div class="cns">

    <!-- ── Scene ──────────────────────────────── -->
    <div class="cns-scene">

      <!-- 底層：背景 -->
      <img class="cns-bg" :src="bgImg" alt="" draggable="false" />

      <!-- 夫子層 -->
      <div class="cns-layer">
        <!-- 等待回應：跳動點點 -->
        <Transition name="cns-fade">
          <div v-if="isLoading" class="cns-thinking">
            <span /><span /><span />
          </div>
        </Transition>

        <!-- 夫子對話框（逐字顯示） -->
        <Transition name="cns-pop-r">
          <div v-if="displayedTeacherText" class="cns-bubble cns-bubble--teacher">
            <p>{{ displayedTeacherText }}</p>
          </div>
        </Transition>

        <img class="cns-teacher" :src="teacherImg" alt="夫子" draggable="false" />
      </div>

      <!-- 學生層 -->
      <div class="cns-layer">
        <!-- 學生對話框（送出後立即完整顯示） -->
        <Transition name="cns-pop-c">
          <div v-if="studentText" class="cns-bubble cns-bubble--student">
            <p>{{ studentText }}</p>
          </div>
        </Transition>

        <!-- 靜止學生群 -->
        <img class="cns-students-right" :src="studentsRightImg" alt="學生" draggable="false" />
        <!-- 發問時隱藏左側學生，改由 student-talk 取代 -->
        <Transition name="cns-fade">
          <img v-if="!isTalking" class="cns-students-left" :src="studentsLeftImg" alt="學生" draggable="false" />
        </Transition>

        <!-- 發問中學生（覆蓋中間那位） -->
        <Transition name="cns-fade">
          <img v-if="isTalking" class="cns-student-talk" :src="studentTalkImg" alt="" draggable="false" />
        </Transition>
      </div>

    </div>

    <!-- ── 輸入欄 ───────────────────────────────── -->
    <div class="cns-bar">
      <div class="cns-field">
        <input ref="inputRef" v-model="inputText" :disabled="isLoading" maxlength="20" class="cns-input"
          placeholder="向夫子提問…（最多 20 字）" @keyup.enter="ask" />
        <span class="cns-count" :class="{ 'cns-count--warn': inputText.length >= 18 }">
          {{ inputText.length }}/20
        </span>
      </div>
      <button class="cns-btn" :disabled="!inputText.trim() || isLoading" @click="ask">
        <span v-if="isLoading" class="cns-spinner" />
        <template v-else>問</template>
      </button>
    </div>

    <Transition name="cns-fade">
      <p v-if="errorMsg" class="cns-err">{{ errorMsg }}</p>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import bgImg from '../assets/classical/classroom-bg.jpg'
import teacherImg from '../assets/classical/teacher.png'
import studentsRightImg from '../assets/classical/students_right.png'
import studentsLeftImg from '../assets/classical/students_left.png'
import studentTalkImg from '../assets/classical/student-talk.png'

defineProps({ isDark: Boolean })

const inputText = ref('')
const submittedQ = ref('')  // 已送出的問題
const displayedTeacherText = ref('') // 逐字建立的夫子泡泡文字
const isLoading = ref(false)
const errorMsg = ref('')
const inputRef = ref(null)

// 用來取消過期的 typewriter / 計時器
let currentGen = 0

// 送出後才顯示發問學生
const isTalking = computed(() => !!submittedQ.value)

// 學生泡泡：送出後立即完整顯示
const studentText = computed(() => submittedQ.value ? `${submittedQ.value}` : '')

// ── 工具函式 ──────────────────────────────────────

const delay = (ms) => new Promise(r => setTimeout(r, ms))

// 逐字打印，genId 不符時中止（代表有新的問答開始）
async function typewrite(text, targetRef, speedMs, genId) {
  targetRef.value = ''
  for (const char of [...text]) {
    if (currentGen !== genId) return
    targetRef.value += char
    await delay(speedMs)
  }
}

function calcMaxLen(n) {
  return Math.min(60, Math.max(20, Math.round(n * 2 + 15)))
}

// ── 主流程 ────────────────────────────────────────

async function ask() {
  const q = inputText.value.trim()
  if (!q || isLoading.value) return

  // 每次問答取得新的 genId，舊的 typewriter / setTimeout 自動作廢
  const genId = ++currentGen

  submittedQ.value = q
  inputText.value = ''
  displayedTeacherText.value = ''
  errorMsg.value = ''
  isLoading.value = true

  try {
    // 使用 Promise.all 讓 fetch 與 800ms 延遲同時進行
    const [res] = await Promise.all([
      fetch('/api/nlp/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: `曰：「${q}？」曰：「`,
          style: 'classical',
          max_length: calcMaxLen(q.length),
          temperature: 0.85,
        }),
      }),
      delay(800) // 強制等待至少 0.8 秒 (800毫秒)
    ])

    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const { output } = await res.json()

    const marker = '曰：「'
    const idx = output.lastIndexOf(marker)
    let ans = idx !== -1 ? output.slice(idx + marker.length) : output
    ans = ans.replace(/」[\s\S]*$/, '').replace(/\n[\s\S]*$/, '').trim()

    if (ans && !ans.endsWith('。') && !ans.endsWith('？')) {
      // 定義全形標點符號的正則表達式
      const punctuationRegex = /[\u3000-\u303F\uFF00-\uFFEF]$/

      if (punctuationRegex.test(ans)) {
        // 如果末尾是其他標點（如：，；！），將其替換為「。」
        ans = ans.slice(0, -1) + '。'
      } else {
        // 如果末尾是普通文字，則直接補上「。」
        ans += '。'
      }
    }

    // API 回應完成且至少經過 0.8 秒 → 關閉 loading，開始夫子逐字回答
    isLoading.value = false
    await typewrite(ans || '…', displayedTeacherText, 100, genId)

    inputRef.value?.focus()

    // 打完後等 10 秒，若無新問答則重置場景
    await delay(10000)
    if (currentGen !== genId) return
    submittedQ.value = ''
    displayedTeacherText.value = ''
  } catch (e) {
    isLoading.value = false
    if (currentGen === genId) {
      const msg = e?.message || ''
      errorMsg.value = msg.includes('500')
        ? '夫子正在準備中，請稍後片刻再試'
        : '無法連線，請確認網路後再試'
    }
  } finally {
    inputRef.value?.focus()
  }
}
</script>

<style scoped>
/* ── 根容器 ─────────────────────────────────── */
.cns {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
  font-family: 'Noto Serif TC', 'Noto Serif SC', 'Source Han Serif TC', serif;
}

/* ── 場景容器（維持 16:9） ────────────────────── */
.cns-scene {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: 12px;
  background: #1a0f08;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

/* 每一層都貼滿場景容器 */
.cns-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* ── 背景圖 ─────────────────────────────────── */
.cns-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  user-select: none;
}

/* ── 夫子 Sprite ────────────────────────────── */
/* teacher.png 540×720 (比例 0.75)
   顯示寬度 13% → 顯示高 = 13% × (720/540) × (16/9) = 30.8% scene 高
   對應背景中椅子位置：top 27% 讓夫子坐進椅子 */
.cns-teacher {
  position: absolute;
  width: 20%;
  top: 25%;
  left: 50%;
  transform: translateX(-50%);
  user-select: none;
}

/* ── 學生群 Sprite ───────────────────────────── */
/* students.png 1280×640 (比例 2:1)
   顯示寬度 60% → 顯示高 = 60% × (640/1280) × (16/9) = 53.3% scene 高
   底部貼齊，頭部在 scene top ≈ 47% */
.cns-students-right {
  position: absolute;
  width: 45%;
  bottom: 0;
  left: 62%;
  transform: translateX(-50%);
  user-select: none;
}

.cns-students-left {
  position: absolute;
  width: 25.5%;
  bottom: 0;
  left: 26.5%;
  transform: translateX(-50%);
  user-select: none;
}

/* ── 發問學生 Sprite ─────────────────────────── */
/* student-talk.png 480×720 (比例 0.667)
   顯示寬度 20% → 高同為 53.3%，精準覆蓋中間那位學生 */
.cns-student-talk {
  position: absolute;
  width: 23%;
  bottom: -8px;
  left: 29%;
  transform: translateX(-50%);
  user-select: none;
}

/* ── 對話框基底樣式 ──────────────────────────── */
.cns-bubble {
  position: absolute;
  background: #fffef5;
  border: 2.5px solid #2c1810;
  border-radius: 14px;
  padding: 8px 13px;
  max-width: clamp(110px, 20vw, 230px);
  font-size: clamp(10px, 1.3vw, 15px);
  line-height: 1.75;
  color: #1a0f08;
  word-break: break-all;
  z-index: 20;
  filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.35));
  pointer-events: none;
}

.cns-bubble p {
  margin: 0;
  white-space: pre-wrap;
}

/* 對話框尾巴（通用：指向下方） */
.cns-bubble::before,
.cns-bubble::after {
  content: '';
  position: absolute;
  border-style: solid;
  border-color: transparent;
}

/* ── 夫子對話框：右上角，尾巴指向左下（夫子頭頂） ── */
.cns-bubble--teacher {
  /* 1. 移除原本的 top: 5% */
  bottom: 78%;
  /* 將底部固定在夫子頭部上方約 22% 處 */
  right: 18%;

  /* 2. 將高度設定為自動 */
  width: clamp(160px, 20vw, 320px);
  height: auto;
  max-height: 72%;
  min-height: 72px;
  /* 設定最小高度，確保沒文字時也不會縮太小 */
  max-width: none;

  /* 3. 確保動畫中心點在尾巴（左下角） */
  transform-origin: bottom left;
}

.cns-bubble--teacher p {
  margin: 0;
  white-space: pre-wrap;
  display: -webkit-box;
  line-clamp: 5;
  -webkit-line-clamp: 5;
  /* 可選：若想限制最大行數，避免對話框長到螢幕外 */
  -webkit-box-orient: vertical;
}

/* 尾巴在左側底部，指向左下 */
.cns-bubble--teacher::before {
  bottom: -15px;
  left: 18px;
  border-width: 14px 11px 0 11px;
  border-top-color: #2c1810;
}

.cns-bubble--teacher::after {
  bottom: -11px;
  left: 20px;
  border-width: 11px 9px 0 9px;
  border-top-color: #fffef5;
}

/* ── RWD：小螢幕夫子對話框） ── */
@media (max-width: 1100px) {
  .cns-bubble--teacher {
    right: 30%;
  }
}
@media (max-width: 725px) {
  .cns-bubble--teacher {
    right: 25%;
  }
}

@media (max-width: 599px) {
  .cns-bubble--teacher {
    bottom: auto;
    top: 2%;
    right: 8%;
    width: clamp(140px, 55%, 260px);
    max-height: 38%;
    overflow: hidden;
  }

  .cns-bubble--teacher p {
    -webkit-line-clamp: 4;
    line-clamp: 4;
  }
}

/* ── 學生對話框：左側偏上，尾巴指向右下（學生頭頂） ── */
/* 學生頭在 scene ≈ left 50%, top 47%
   對話框放在 top 33% 留出 14% 給尾巴與空間 */
.cns-bubble--student {
  bottom: 60%;
  right: 76%;
  transform-origin: bottom right;
  text-align: left;
}

/* 尾巴在底部右側，clip-path 直角三角形指向右下（↘） */
.cns-bubble--student::before {
  border: none;
  width: 18px;
  height: 18px;
  background: #2c1810;
  bottom: -16px;
  right: 11px;
  left: auto;
  clip-path: polygon(0 0, 100% 0, 100% 100%);
}

.cns-bubble--student::after {
  border: none;
  width: 14px;
  height: 14px;
  background: #fffef5;
  bottom: -11px;
  right: 14px;
  left: auto;
  clip-path: polygon(0 0, 100% 0, 100% 100%);
}

/* ── 等待跳動點點（與夫子對話框同位置） ──────── */
.cns-thinking {
  position: absolute;
  top: 15%;
  right: 40%;
  background: #fffef5;
  border: 2.5px solid #2c1810;
  border-radius: 14px;
  padding: 9px 14px;
  display: flex;
  gap: 5px;
  align-items: center;
  z-index: 20;
  filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.35));
}

@media (max-width: 1100px) {
.cns-thinking {
  right: 45%;
}
}
.cns-thinking span {
  width: clamp(5px, 0.7vw, 9px);
  height: clamp(5px, 0.7vw, 9px);
  background: #2c1810;
  border-radius: 50%;
  animation: cns-bounce 1.2s ease-in-out infinite;
}

.cns-thinking span:nth-child(2) {
  animation-delay: 0.2s;
}

.cns-thinking span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes cns-bounce {

  0%,
  80%,
  100% {
    transform: scale(0.55);
    opacity: 0.45;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* ── 輸入欄 ─────────────────────────────────── */
.cns-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cns-field {
  flex: 1;
  position: relative;
}

.cns-input {
  width: 100%;
  padding: 10px 52px 10px 16px;
  border: 1.5px solid rgba(44, 24, 16, 0.25);
  border-radius: 12px;
  background: rgba(255, 254, 245, 0.92);
  font-family: inherit;
  font-size: clamp(13px, 1.2vw, 16px);
  color: #1a0f08;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.cns-input:focus {
  outline: none;
  border-color: #8b5e3c;
  box-shadow: 0 0 0 3px rgba(139, 94, 60, 0.15);
}

.cns-input::placeholder {
  color: #a07050;
}

.cns-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cns-count {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: #a07050;
  font-family: 'Noto Sans TC', sans-serif;
  pointer-events: none;
  transition: color 0.2s;
}

.cns-count--warn {
  color: #c0392b;
  font-weight: 700;
}

.cns-btn {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  border-radius: 12px;
  border: none;
  background: #2c1810;
  color: #fffef5;
  font-family: inherit;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
}

.cns-btn:hover:not(:disabled) {
  background: #4a2c1c;
  transform: translateY(-2px);
}

.cns-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.cns-spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 254, 245, 0.3);
  border-top-color: #fffef5;
  border-radius: 50%;
  animation: cns-spin 0.7s linear infinite;
}

@keyframes cns-spin {
  to {
    transform: rotate(360deg);
  }
}

.cns-err {
  margin: 0;
  font-size: 12px;
  color: #c0392b;
  font-family: 'Noto Sans TC', sans-serif;
  text-align: center;
}

/* ── Transitions ────────────────────────────── */

/* 淡入淡出（學生切換、等待點點、錯誤訊息） */
.cns-fade-enter-active,
.cns-fade-leave-active {
  transition: opacity 0.3s ease;
}

.cns-fade-enter-from,
.cns-fade-leave-to {
  opacity: 0;
}

/* 夫子對話框：右側彈出（transform 無 translate，直接 scale） */
.cns-pop-r-enter-active {
  transition: all 0.38s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.cns-pop-r-enter-from {
  opacity: 0;
  transform: scale(0.55);
}

.cns-pop-r-leave-active {
  transition: opacity 0.2s;
}

.cns-pop-r-leave-to {
  opacity: 0;
}

/* 學生對話框：中央彈出（需保留 translateX(-50%)） */
.cns-pop-c-enter-active {
  transition: all 0.38s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.cns-pop-c-enter-from {
  opacity: 0;
  transform: translateX(-50%) scale(0.55);
}

.cns-pop-c-leave-active {
  transition: opacity 0.2s;
}

.cns-pop-c-leave-to {
  opacity: 0;
  transform: translateX(-50%);
}
</style>
