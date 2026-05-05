<template>
  <div class="nnv" :class="{ dark: isDark }">

    <!-- ── 架構設定列 ────────────────────────────── -->
    <div class="nnv-config">
      <div class="nnv-cfg-group">
        <span class="nnv-cfg-label">輸入節點</span>
        <div class="nnv-stepper">
          <button @click="changeInputs(-1)" :disabled="cfg.inputs <= 1 || isAnimating">−</button>
          <span>{{ cfg.inputs }}</span>
          <button @click="changeInputs(1)" :disabled="cfg.inputs >= 4 || isAnimating">+</button>
        </div>
      </div>

      <div class="nnv-cfg-group nnv-cfg-layers">
        <span class="nnv-cfg-label">隱藏層</span>
        <div class="nnv-layer-list">
          <div v-for="(n, i) in cfg.hidden" :key="i" class="nnv-layer-row">
            <span class="nnv-layer-badge">L{{ i + 1 }}</span>
            <div class="nnv-stepper nnv-stepper--sm">
              <button @click="changeHidden(i, -1)" :disabled="n <= 1 || isAnimating">−</button>
              <span>{{ n }}</span>
              <button @click="changeHidden(i, 1)" :disabled="n >= 5 || isAnimating">+</button>
            </div>
            <button class="nnv-rm-layer" @click="removeLayer(i)"
              :disabled="cfg.hidden.length <= 1 || isAnimating">×</button>
          </div>
          <button class="nnv-add-layer" @click="addLayer" :disabled="cfg.hidden.length >= 4 || isAnimating">+
            新增層</button>
        </div>
      </div>

      <div class="nnv-cfg-group">
        <span class="nnv-cfg-label">激活函數</span>
        <select v-model="cfg.hiddenActivation" :disabled="isAnimating" class="nnv-select">
          <option value="sigmoid">Sigmoid</option>
          <option value="relu">ReLU</option>
          <option value="linear">Linear</option>
        </select>
      </div>
    </div>

    <!-- ── 主體：SVG + OOP 面板 ────────────────── -->
    <div class="nnv-body">

      <!-- SVG 網路圖 -->
      <div class="nnv-canvas-wrap">
        <svg :viewBox="`0 0 ${SVG_W} ${SVG_H}`" class="nnv-svg" preserveAspectRatio="xMidYMid meet">

          <!-- 邊（先畫，讓節點在上層） -->
          <g v-for="e in svgEdges" :key="e.id" class="nnv-edge-g">
            <line :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" :stroke="e.color" :stroke-width="e.width"
              :opacity="e.opacity" stroke-linecap="round" class="nnv-edge" />
            <!-- 權重標籤 -->
            <text :x="e.mx" :y="e.my - 5" text-anchor="middle" dominant-baseline="auto" font-size="8"
              font-family="monospace" font-weight="700" :fill="e.color" :fill-opacity="Math.max(0.45, e.opacity)"
              stroke="#fffef5" stroke-width="2" paint-order="stroke" class="nnv-edge-lbl">{{ e.weightLabel }}</text>
            <!-- 梯度標籤（反向傳播後） -->
            <text v-if="e.backActive && e.gradLabel != null" :x="e.mx" :y="e.my + 12" text-anchor="middle"
              dominant-baseline="auto" font-size="8" font-family="monospace" font-weight="700" fill="#c084fc"
              fill-opacity="0.95" stroke="#fffef5" stroke-width="2" paint-order="stroke" class="nnv-edge-lbl">∇{{
                e.gradLabel }}</text>
          </g>

          <!-- 節點 -->
          <g v-for="n in svgNodes" :key="n.id" @click="selectNode(n.id)"
            :class="['nnv-node-g', { 'is-bias': n.isBias, 'is-selected': n.id === selectedId }]">
            <circle :cx="n.x" :cy="n.y" :r="n.isBias ? NODE_R * 0.52 : NODE_R" :fill="n.fill"
              :stroke="n.id === selectedId ? '#2a7a5a' : (n.backActive && !n.isBias ? '#9333ea' : '#a08870')"
              :stroke-width="n.id === selectedId ? 3 : (n.backActive && !n.isBias ? 2.5 : 2)" />
            <text :x="n.x" :y="n.y" text-anchor="middle" dominant-baseline="middle" :font-size="n.isBias ? 8 : 10"
              :fill="n.isBias ? '#7a6a5a' : '#1a0f08'" font-weight="600" font-family="monospace">{{ n.label }}</text>
          </g>

          <!-- 層標題 -->
          <text v-for="ll in layerLabels" :key="ll.text" :x="ll.x" :y="14" text-anchor="middle" font-size="10"
            fill="#a08870" font-weight="700" letter-spacing="0.3">
            {{ ll.text }}
          </text>
        </svg>
      </div>

    </div>

    <!-- ── 輸入控制列 ───────────────────────────── -->
    <div class="nnv-controls">
      <div class="nnv-inputs-row">
        <div v-for="(_, i) in Array(cfg.inputs)" :key="i" class="nnv-input-cell">
          <label class="nnv-input-label">I{{ i + 1 }}</label>
          <input type="number" v-model.number="inputValues[i]" step="0.1" min="-3" max="3" class="nnv-input-num"
            :disabled="isAnimating" />
        </div>
      </div>
      <div class="nnv-btn-row">
        <button class="nnv-btn-run" @click="runForward" :disabled="isAnimating">
          <span v-if="isAnimating" class="nnv-spinner" />
          <span v-else>▶ 前向傳播</span>
        </button>
        <button class="nnv-btn-reset" @click="doReset" :disabled="isAnimating">↺ 重置</button>
      </div>
    </div>

    <!-- ── 反向傳播控制列 ─────────────────────────── -->
    <Transition name="nnv-slide">
      <div v-if="phase !== 'idle'" class="nnv-backward">
        <div class="nnv-bw-header">
          <span class="nnv-bw-title">反向傳播</span>
          <span v-if="lossValue != null" class="nnv-loss-badge">
            損失 = {{ fmt(lossValue) }}
          </span>
        </div>
        <div class="nnv-bw-row">
          <div v-for="(_, i) in Array(cfg.outputs)" :key="i" class="nnv-input-cell">
            <label class="nnv-input-label">期望 O{{ i + 1 }}</label>
            <input type="number" v-model.number="expectedValues[i]" step="0.1" min="-3" max="3" class="nnv-input-num"
              :disabled="isAnimating" />
          </div>
          <div class="nnv-cfg-group">
            <span class="nnv-cfg-label">損失函數</span>
            <select v-model="lossType" class="nnv-select" :disabled="isAnimating">
              <option value="mse">MSE</option>
              <option value="bce">BCE</option>
            </select>
          </div>
          <div class="nnv-input-cell">
            <label class="nnv-input-label">LR</label>
            <input type="number" v-model.number="learningRate" step="0.01" min="0.001" max="1" class="nnv-input-num"
              style="width:64px" :disabled="isAnimating" />
          </div>
          <div class="nnv-bw-actions">
            <button class="nnv-btn-bw" @click="runBackward" :disabled="isAnimating || phase === 'backwarded'">
              <span v-if="isAnimating && phase === 'backward'" class="nnv-spinner" />
              <span v-else>◀ 反向傳播</span>
            </button>
            <button v-if="phase === 'backwarded'" class="nnv-btn-update" @click="applyUpdate" :disabled="isAnimating">
              ↓ 更新權重
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── 節點詳細資訊卡 ─────────────────────────── -->
    <Transition name="nnv-slide">
      <div v-if="selectedInfo" class="nnv-detail">
        <div class="nnv-detail-head">
          <span class="nnv-detail-id">{{ selectedInfo.id }}</span>
          <button class="nnv-detail-close" @click="selectedId = null">×</button>
        </div>
        <div v-if="selectedInfo.rawOutput != null" class="nnv-detail-row">
          <span>加權和（raw）</span>
          <code>{{ fmt(selectedInfo.rawOutput) }}</code>
        </div>
        <div v-if="selectedInfo.output != null && !selectedInfo.isBias" class="nnv-detail-row">
          <span>激活後輸出</span>
          <code>{{ fmt(selectedInfo.output) }}</code>
        </div>
        <div v-if="selectedInfo.dTLdRaw != null" class="nnv-detail-row">
          <span>梯度 dL/dRaw</span>
          <code :class="selectedInfo.dTLdRaw >= 0 ? 'pos' : 'neg'">{{ fmt(selectedInfo.dTLdRaw) }}</code>
        </div>
        <template v-if="selectedInfo.weights.length">
          <div class="nnv-detail-sub">傳入連結權重</div>
          <div v-for="w in selectedInfo.weights" :key="w.from" class="nnv-detail-row">
            <span>{{ w.from }}</span>
            <code :class="w.val > 0 ? 'pos' : 'neg'">{{ fmt(w.val) }}</code>
          </div>
        </template>
        <template v-if="selectedInfo.gradients && selectedInfo.gradients.some(g => g.val !== 0)">
          <div class="nnv-detail-sub">權重梯度 ∇w</div>
          <div v-for="g in selectedInfo.gradients" :key="g.from" class="nnv-detail-row">
            <span>∇{{ g.from }}</span>
            <code :class="g.val >= 0 ? 'pos' : 'neg'">{{ fmt(g.val) }}</code>
          </div>
        </template>
      </div>
    </Transition>

    <!-- ── Python 原始碼展示 ─────────────────────────── -->
    <div class="nnv-code">
      <div class="nnv-code-header">
        <span class="nnv-code-title">Python 原始實作 · <code>class Network</code></span>
        <span class="nnv-code-badge">純 Python 標準函式庫 · 無框架依賴</span>
      </div>
      <div class="nnv-code-tabs">
        <button v-for="(sec, i) in codeSections" :key="i"
          :class="['nnv-code-tab', { active: activeSection === i }]"
          @click="activeSection = i">{{ sec.label }}</button>
      </div>
      <div class="nnv-code-panel">
        <div class="nnv-code-meta">
          <span class="nnv-code-file">Assignment.py</span>
          <span class="nnv-code-lines">lines {{ codeSections[activeSection].lineStart }}–{{ codeSections[activeSection].lineEnd }}</span>
          <span class="nnv-code-tag">{{ codeSections[activeSection].tag }}</span>
        </div>
        <div class="nnv-code-scroll">
          <table class="nnv-code-table" cellspacing="0">
            <tbody>
              <tr v-for="(row, ri) in codeRows" :key="ri">
                <td class="nnv-ln">{{ codeSections[activeSection].lineStart + ri }}</td>
                <td class="nnv-lc" v-html="row.html"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'

defineProps({ isDark: Boolean })

// ══════════════════════════════════════════════════════════
//  Neural Network Classes  ──  完整移植自 Python OOP 設計
// ══════════════════════════════════════════════════════════

class NNNode {
  constructor(id, preLayer = null, weights = [], isBias = false) {
    this.id = id
    this.preLayer = preLayer
    this.isBias = isBias
    this.rawOutput = null
    this.output = isBias ? 1 : null
    /** @type {Map<NNNode, number>} */
    this.weightMap = new Map()
    /** @type {Map<NNNode, number>} */
    this.gradientMap = new Map()
    if (preLayer && weights.length) {
      preLayer.nodes.forEach((n, i) => {
        this.weightMap.set(n, weights[i])
        this.gradientMap.set(n, 0)
      })
    }
  }
}

class NNLayer {
  constructor(nodes, type, activation) {
    this.nodes = nodes
    this.type = type
    this.activation = activation
  }
  [Symbol.iterator]() { return this.nodes[Symbol.iterator]() }
}

class NetworkMap {
  constructor() {
    this.inputs = null
    /** @type {NNLayer[]} */
    this.hidden = []
    this.outputs = null
  }
  get layers() {
    return [this.inputs, ...this.hidden, this.outputs].filter(Boolean)
  }
}

class Network {
  static Activation = {
    linear: (x) => [...x],
    relu: (x) => x.map(v => Math.max(0, v)),
    sigmoid: (x) => x.map(v => 1 / (1 + Math.exp(-v))),
    softmax: (x) => {
      const m = Math.max(...x)
      const e = x.map(v => Math.exp(v - m))
      const s = e.reduce((a, b) => a + b, 0)
      return e.map(v => v / s)
    },
    linearDerivative: () => 1,
    reluDerivative: (x) => x > 0 ? 1 : 0,
    sigmoidDerivative: (o) => o * (1 - o),
  }

  static Loss = {
    mse: (exp, out) => exp.reduce((s, e, i) => s + (e - out[i]) ** 2, 0) / exp.length,
    mseDerivative: (e, o) => 2 * (o - e),
    binaryCrossEntropy: (exp, out) =>
      -exp.reduce((s, e, i) =>
        s + e * Math.log(out[i] + 1e-15) + (1 - e) * Math.log(1 - out[i] + 1e-15), 0),
    binaryCrossEntropyDerivative: (e, o) =>
      ((1 - e) / (1 - o + 1e-15)) - (e / (o + 1e-15)),
  }

  constructor(inputCount, hiddenCounts, outputCount, hiddenAct = 'sigmoid', outputAct = 'linear') {
    this.map = new NetworkMap()
    const r = () => (Math.random() - 0.5) * 0.8

    const inNodes = Array.from({ length: inputCount }, (_, i) => new NNNode(`I${i + 1}`))
    inNodes.push(new NNNode('B0', null, [], true))
    this.map.inputs = new NNLayer(inNodes, 'I', 'linear')

    let prev = this.map.inputs
    hiddenCounts.forEach((count, li) => {
      const nodes = Array.from({ length: count }, (_, ni) =>
        new NNNode(`H${li + 1}_${ni + 1}`, prev, prev.nodes.map(() => r()))
      )
      nodes.push(new NNNode(`B${li + 1}`, null, [], true))
      const layer = new NNLayer(nodes, 'H', hiddenAct)
      this.map.hidden.push(layer)
      prev = layer
    })

    const outNodes = Array.from({ length: outputCount }, (_, oi) =>
      new NNNode(`O${oi + 1}`, prev, prev.nodes.map(() => r()))
    )
    this.map.outputs = new NNLayer(outNodes, 'O', outputAct)
  }

  setOutputGradients(expects, loss = 'mse') {
    const outNodes = this.map.outputs.nodes.filter(n => !n.isBias)
    const lossDerivFn = loss === 'mse' ? Network.Loss.mseDerivative : Network.Loss.binaryCrossEntropyDerivative
    const dAct = Network.Activation[this.map.outputs.activation + 'Derivative'] ?? (() => 1)
    outNodes.forEach((node, i) => {
      const actInput = this.map.outputs.activation === 'sigmoid' ? node.output : node.rawOutput
      node.dTLdRaw = lossDerivFn(expects[i] ?? 0, node.output ?? 0) * dAct(actInput)
      node.weightMap.forEach((_, pre) => {
        node.gradientMap.set(pre, node.dTLdRaw * (pre.output ?? 0))
      })
    })
  }

  computeLoss(expects, loss = 'mse') {
    const outNodes = this.map.outputs.nodes.filter(n => !n.isBias)
    const outVals = outNodes.map(n => n.output ?? 0)
    const fn = loss === 'mse' ? Network.Loss.mse : Network.Loss.binaryCrossEntropy
    return fn(expects, outVals)
  }

  forward(inputValues) {
    const pureInputs = this.map.inputs.nodes.filter(n => !n.isBias)
    pureInputs.forEach((n, i) => { n.output = inputValues[i] ?? 0; n.rawOutput = n.output })

    this.map.layers.slice(1).forEach(layer => {
      const raws = []
      layer.nodes.forEach(node => {
        if (node.isBias) { node.rawOutput = 1; node.output = 1; return }
        let raw = 0
        node.weightMap.forEach((w, pre) => { raw += (pre.output ?? 0) * w })
        node.rawOutput = raw
        raws.push(raw)
      })
      const act = Network.Activation[layer.activation] ?? Network.Activation.linear
      const activated = act(raws)
      let ai = 0
      layer.nodes.forEach(node => { if (!node.isBias) node.output = activated[ai++] })
    })

    return this.map.outputs.nodes.map(n => n.output)
  }

  backward() {
    const rev = this.map.layers.slice().reverse()
    for (let i = 1; i < rev.length - 1; i++) {
      const nextLayer = rev[i - 1]
      const layer = rev[i]
      const dAct = Network.Activation[layer.activation + 'Derivative'] ?? (() => 1)
      layer.nodes.forEach(node => {
        if (node.isBias) return
        const actInput = layer.activation === 'sigmoid' ? node.output : node.rawOutput
        const dActVal = dAct(actInput)
        let dTL = 0
        nextLayer.nodes.forEach(nNode => {
          if (nNode.isBias) return
          dTL += (nNode.dTLdRaw ?? 0) * (nNode.weightMap.get(node) ?? 0)
        })
        node.dTLdRaw = dActVal * dTL
        node.weightMap.forEach((_, pre) => {
          node.gradientMap.set(pre, node.dTLdRaw * (pre.output ?? 0))
        })
      })
    }
  }

  zeroGrad(lr) {
    this.map.layers.slice(1).forEach(layer => {
      layer.nodes.forEach(node => {
        node.weightMap.forEach((w, pre) => {
          node.weightMap.set(pre, w - (node.gradientMap.get(pre) ?? 0) * lr)
          node.gradientMap.set(pre, 0)
        })
      })
    })
  }
}

// ══════════════════════════════════════════════════════════
//  SVG constants
// ══════════════════════════════════════════════════════════

const SVG_W = 680
const SVG_H = 310
const NODE_R = 20

// ══════════════════════════════════════════════════════════
//  Reactive state
// ══════════════════════════════════════════════════════════

const cfg = reactive({ inputs: 2, hidden: [2, 2], hiddenActivation: 'sigmoid', outputs: 1 })
const inputValues = ref([0.5, -0.3])
const isAnimating = ref(false)
const animStep = ref(-1)
const selectedId = ref(null)
const networkVer = ref(0)

const phase = ref('idle')          // 'idle' | 'forwarded' | 'backward' | 'backwarded'
const backAnimStep = ref(-1)       // layers.length-1 → 1, counting down
const expectedValues = ref([0])
const lossType = ref('mse')
const learningRate = ref(0.1)
const lossValue = ref(null)

let network = null

function rebuildNetwork() {
  network = new Network(cfg.inputs, [...cfg.hidden], cfg.outputs, cfg.hiddenActivation)
  animStep.value = -1
  backAnimStep.value = -1
  selectedId.value = null
  networkVer.value++
  phase.value = 'idle'
  lossValue.value = null
  while (inputValues.value.length < cfg.inputs) inputValues.value.push(0)
  if (inputValues.value.length > cfg.inputs) inputValues.value.splice(cfg.inputs)
  while (expectedValues.value.length < cfg.outputs) expectedValues.value.push(0)
  if (expectedValues.value.length > cfg.outputs) expectedValues.value.splice(cfg.outputs)
}
rebuildNetwork()

watch(cfg, () => rebuildNetwork(), { deep: true })

// ── config handlers ──────────────────────────────────────
function changeInputs(d) { cfg.inputs = Math.max(1, Math.min(4, cfg.inputs + d)) }
function changeHidden(i, d) { cfg.hidden[i] = Math.max(1, Math.min(5, cfg.hidden[i] + d)) }
function addLayer() { if (cfg.hidden.length < 4) cfg.hidden.push(2) }
function removeLayer(i) { if (cfg.hidden.length > 1) cfg.hidden.splice(i, 1) }

// ══════════════════════════════════════════════════════════
//  SVG layout helpers
// ══════════════════════════════════════════════════════════

function buildLayout() {
  if (!network) return []
  const layers = network.map.layers
  const PX = 62, PY = 32
  const W = SVG_W - PX * 2
  const H = SVG_H - PY * 2 - 28   // 28 px reserved for bias at bottom

  return layers.map((layer, li) => {
    const x = layers.length === 1 ? SVG_W / 2 : PX + (li / (layers.length - 1)) * W
    const nonBias = layer.nodes.filter(n => !n.isBias)
    const bias = layer.nodes.find(n => n.isBias)
    const items = nonBias.map((node, ni) => ({
      node,
      x,
      y: PY + ((ni + 0.5) / nonBias.length) * H,
    }))
    if (bias) items.push({ node: bias, x, y: SVG_H - 18 })
    return { layer, li, x, items }
  })
}

// ══════════════════════════════════════════════════════════
//  Computed SVG data
// ══════════════════════════════════════════════════════════

const svgNodes = computed(() => {
  void networkVer.value
  void animStep.value
  if (!network) return []

  const result = []
  buildLayout().forEach(({ li, items }) => {
    items.forEach(({ node, x, y }) => {
      const active = animStep.value >= li
      const val = node.output
      const backActive = backAnimStep.value >= 0 && li >= backAnimStep.value

      let fill = '#e5e0da'
      if (backActive && !node.isBias && node.dTLdRaw != null) {
        const t = Math.max(0, Math.min(1, Math.abs(node.dTLdRaw) * 2))
        fill = lerpColor('#f0ede8', '#9333ea', t)
      } else if (active && val != null && !node.isBias) {
        const t = Math.max(-1, Math.min(1, val))
        fill = t >= 0
          ? lerpColor('#f0ede8', '#d9622e', t)
          : lerpColor('#f0ede8', '#4d8fbf', -t)
      }

      result.push({
        id: node.id,
        x, y, li,
        isBias: node.isBias,
        fill: node.isBias ? '#d0cbc4' : fill,
        active,
        backActive,
        rawOutput: node.rawOutput,
        output: node.output,
        dTLdRaw: node.dTLdRaw ?? null,
        label: node.isBias ? '1'
          : (backActive && node.dTLdRaw != null
            ? fmtShort(node.dTLdRaw)
            : (active && val != null ? fmtShort(val) : node.id)),
        weights: [...(node.weightMap?.entries() ?? [])].map(([n, w]) => ({ from: n.id, val: w })),
        gradients: [...(node.gradientMap?.entries() ?? [])].map(([n, g]) => ({ from: n.id, val: g })),
      })
    })
  })
  return result
})

const svgEdges = computed(() => {
  void networkVer.value
  void animStep.value
  if (!network) return []

  const posMap = {}
  buildLayout().forEach(({ items }) =>
    items.forEach(({ node, x, y }) => { posMap[node.id] = { x, y } })
  )

  const result = []
  network.map.layers.forEach((layer, li) => {
    if (li === 0) return
    layer.nodes.forEach(node => {
      if (node.isBias) return
      node.weightMap.forEach((w, pre) => {
        const p1 = posMap[pre.id], p2 = posMap[node.id]
        if (!p1 || !p2) return
        const active = animStep.value >= li
        const backActive = backAnimStep.value >= 0 && li >= backAnimStep.value
        const grad = node.gradientMap?.get(pre) ?? null
        result.push({
          id: `${pre.id}→${node.id}`,
          x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
          mx: (p1.x + p2.x) / 2,
          my: (p1.y + p2.y) / 2,
          color: w > 0 ? '#d9622e' : '#4d8fbf',
          width: Math.max(0.5, Math.min(4.5, Math.abs(w) * 5.5)),
          opacity: active ? 0.72 : 0.16,
          weightLabel: fmtShort(w),
          backActive,
          gradLabel: backActive && grad !== null ? fmtShort(grad) : null,
        })
      })
    })
  })
  return result
})

const layerLabels = computed(() => {
  void networkVer.value
  if (!network) return []
  const layers = network.map.layers
  const PX = 62
  const W = SVG_W - PX * 2
  return layers.map((_, li) => ({
    x: layers.length === 1 ? SVG_W / 2 : PX + (li / (layers.length - 1)) * W,
    text: li === 0 ? '輸入層' : li === layers.length - 1 ? '輸出層' : `隱藏層 ${li}`,
  }))
})

const selectedInfo = computed(() =>
  selectedId.value ? svgNodes.value.find(n => n.id === selectedId.value) ?? null : null
)

function selectNode(id) {
  selectedId.value = selectedId.value === id ? null : id
}

// ══════════════════════════════════════════════════════════
//  Animation
// ══════════════════════════════════════════════════════════

const sleep = ms => new Promise(r => setTimeout(r, ms))

async function runForward() {
  if (!network || isAnimating.value) return
  isAnimating.value = true
  phase.value = 'idle'
  backAnimStep.value = -1
  lossValue.value = null
  animStep.value = -1
  await sleep(60)

  network.forward(inputValues.value.slice(0, cfg.inputs))
  networkVer.value++

  const count = network.map.layers.length
  for (let li = 0; li < count; li++) {
    animStep.value = li
    await sleep(520)
  }
  phase.value = 'forwarded'
  isAnimating.value = false
}

async function runBackward() {
  if (!network || isAnimating.value || phase.value !== 'forwarded') return
  isAnimating.value = true
  phase.value = 'backward'
  backAnimStep.value = -1

  const expects = expectedValues.value.slice(0, cfg.outputs)
  lossValue.value = network.computeLoss(expects, lossType.value)
  network.setOutputGradients(expects, lossType.value)
  network.backward()

  const layerCount = network.map.layers.length
  for (let li = layerCount - 1; li >= 1; li--) {
    backAnimStep.value = li
    networkVer.value++
    await sleep(520)
  }
  networkVer.value++
  isAnimating.value = false
  phase.value = 'backwarded'
}

function applyUpdate() {
  if (!network) return
  network.zeroGrad(learningRate.value)
  animStep.value = -1
  backAnimStep.value = -1
  phase.value = 'idle'
  lossValue.value = null
  networkVer.value++
}

function doReset() { rebuildNetwork() }

// ══════════════════════════════════════════════════════════
//  Helpers
// ══════════════════════════════════════════════════════════

function lerpColor(h1, h2, t) {
  const p = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]
  const [r1, g1, b1] = p(h1), [r2, g2, b2] = p(h2)
  return `rgb(${Math.round(r1 + (r2 - r1) * t)},${Math.round(g1 + (g2 - g1) * t)},${Math.round(b1 + (b2 - b1) * t)})`
}

const fmt = v => v != null ? Number(v).toFixed(4) : '—'
const fmtShort = v => {
  if (v == null) return ''
  const a = Math.abs(v)
  return a < 10 ? v.toFixed(2) : v.toFixed(1)
}

// ══════════════════════════════════════════════════════════
//  Python Code Viewer
// ══════════════════════════════════════════════════════════

const activeSection = ref(0)

const codeSections = [
  {
    label: 'Activation', tag: '激活函數', lineStart: 17, lineEnd: 49,
    code: `    class Activation:
        """定義常見激勵函數"""

        @staticmethod
        def linear(x: Sequence[float]) -> List[float]:
            return list(x)

        @staticmethod
        def linear_derivative(x: float) -> float:
            return 1

        @staticmethod
        def relu(x: Sequence[float]) -> List[float]:
            return [max(0, v) for v in x]

        @staticmethod
        def relu_derivative(x: float) -> float:
            return 1 if x > 0 else 0

        @staticmethod
        def sigmoid(x: Sequence[float]) -> List[float]:
            return [1 / (1 + math.exp(-v)) for v in x]

        @staticmethod
        def sigmoid_derivative(node_output: float) -> float:
            return node_output * (1 - node_output)

        @staticmethod
        def softmax(x: Sequence[float]) -> List[float]:
            max_x = max(x)
            exp_x = [math.exp(v - max_x) for v in x]
            total = sum(exp_x)
            return [v / total for v in exp_x]`,
  },
  {
    label: 'Loss', tag: '損失函數', lineStart: 54, lineEnd: 86,
    code: `    class Loss:
        """定義常見損失函數"""

        @staticmethod
        def mse(expects, outputs):
            """Mean Squared Error"""
            expects = Network._to_list(expects)
            outputs = Network._to_list(outputs)
            n = len(expects)
            return sum((e - o) ** 2 for e, o in zip(expects, outputs)) / n

        @staticmethod
        def mse_derivative(expect: float, output: float) -> float:
            return 2 * (output - expect)

        @staticmethod
        def binary_cross_entropy(expects, outputs):
            expects = Network._to_list(expects)
            outputs = Network._to_list(outputs)
            return -sum(
                (e * math.log(o)) + ((1 - e) * math.log(1 - o))
                for e, o in zip(expects, outputs)
            )

        @staticmethod
        def binary_cross_entropy_derivative(expect: float, output: float) -> float:
            return ((1 - expect) / (1 - output)) - (expect / output)

        @staticmethod
        def categorical_cross_entropy(expects, outputs):
            expects = Network._to_list(expects)
            outputs = Network._to_list(outputs)
            return -sum(e * math.log(o) for e, o in zip(expects, outputs))`,
  },
  {
    label: '_Node', tag: '節點', lineStart: 91, lineEnd: 130,
    code: `    class _Node:
        """神經網路中的單一節點"""

        def __init__(
            self,
            pre_layer: "Network._Layer" = None,
            weights: Sequence[float] = None,
            node_type: str = "I",
            layer_idx: int = None,
            node_idx: int = None,
        ):
            self.id = self._generate_id(node_type, layer_idx, node_idx)
            self.pre_layer = pre_layer
            self.raw_output = None
            self.output = 1 if node_type == "B" else None  # 設定 bias output
            self.weight_mapping = {}
            self.d_TL_d_raw = None
            self.d_activation_output = 0
            self.gradient_mapping = {}

            # 若有前一層與權重，建立對應表
            weights = list(weights or [])
            if self.pre_layer and weights:
                if len(self.pre_layer.nodes) != len(weights):
                    raise ValueError(f"{self.id}: 前一層節點數與權重數量不一致")
                self.weight_mapping = dict(zip(self.pre_layer.nodes, weights))

        @staticmethod
        def _generate_id(node_type, layer_idx, node_idx):
            """自動生成節點 ID"""
            if node_type == "I":
                return f"I{node_idx + 1}"
            if node_type == "H":
                return f"H{(layer_idx or 0) + 1}_{node_idx + 1}"
            if node_type == "B":
                return f"B{(0 if layer_idx == None else layer_idx + 1)}"
            if node_type == "O":
                return f"O{node_idx + 1}"
            return f"N{node_idx}"`,
  },
  {
    label: '_Layer', tag: '層', lineStart: 135, lineEnd: 151,
    code: `    class _Layer:
        """神經網路中的一層（input, hidden, output）"""

        def __init__(
            self, nodes: List["Network._Node"], layer_type: str, activation: str
        ):
            self.nodes = nodes
            self.type = layer_type
            self.activation = activation.lower()

        def __getitem__(self, idx):
            """支援索引與切片"""
            return self.nodes[idx]

        def __iter__(self):
            """支援迭代"""
            return iter(self.nodes)`,
  },
  {
    label: 'NetworkMap', tag: '網路圖', lineStart: 156, lineEnd: 200,
    code: `    class NetworkMap:
        """儲存整體網路架構與顯示"""

        def __init__(self):
            self.inputs: Network._Layer = None
            self.hidden: List[Network._Layer] = []
            self.outputs: Network._Layer = None

        def show(self):
            """以文字方式顯示網路結構、連線與 activation"""
            print("\\n=== Network Structure ===")

            # 輸入層
            print("\\n[Input Layer] (activation: {})".format(self.inputs.activation))
            for n in self.inputs:
                print(f"  {n.id}")

            # 隱藏層
            for idx, layer in enumerate(self.hidden, start=1):
                print(f"\\n[Hidden Layer {idx}] (activation: {layer.activation})")
                for node in layer.nodes:
                    if node.id.startswith("B"):
                        continue
                    for pre_node, w in node.weight_mapping.items():
                        print(f"  {pre_node.id:<6} --{w:>6.2f}--> {node.id}")

            # 輸出層
            print(f"\\n[Output Layer] (activation: {self.outputs.activation})")
            for node in self.outputs.nodes:
                for pre_node, w in node.weight_mapping.items():
                    print(f"  {pre_node.id:<6} --{w:>6.2f}--> {node.id}")

            print("\\n===========================\\n")

        @property
        def layers(self):
            return [self.inputs] + self.hidden + [self.outputs]

        def __getitem__(self, idx):
            return self.layers[idx]

        def __iter__(self):
            return iter(self.layers)`,
  },
  {
    label: '__init__', tag: '初始化', lineStart: 205, lineEnd: 228,
    code: `    def __init__(self, network_setting_json: str):
        config: dict = json.loads(network_setting_json)
        self.map = Network.NetworkMap()

        # 建立 input nodes
        input_setting = config.get("input", {})
        self.map.inputs = self._build_layer(
            input_setting, pre_layer=None, layer_type="I"
        )

        pre_layer = self.map.inputs

        # 建立 hidden layers
        for layer_idx, layer_cfg in enumerate(config.get("layer", [])):
            layer = self._build_layer(
                layer_cfg, pre_layer, layer_type="H", layer_idx=layer_idx
            )
            self.map.hidden.append(layer)
            pre_layer = layer

        # 建立 output nodes
        output_cfg = config.get("output", {})
        self.map.outputs = self._build_layer(output_cfg, pre_layer, layer_type="O")`,
  },
  {
    label: '_build_layer', tag: '建構層', lineStart: 230, lineEnd: 271,
    code: `    def _build_layer(
        self,
        cfg: dict,
        pre_layer: "Network._Layer",
        layer_type: str,
        layer_idx: int = None,
    ) -> "Network._Layer":
        """建立一層（input / hidden / output）"""

        activation = cfg.get("activation", "linear").lower()
        node_count = cfg.get("nodes", 0)

        # input layer
        if layer_type == "I":
            nodes = [
                Network._Node(node_type="I", node_idx=i) for i in range(node_count)
            ]
            nodes.append(Network._Node(node_type="B"))  # bias node
            return Network._Layer(nodes, layer_type="I", activation=activation)

        # hidden/output layer
        weights_matrix = cfg.get("weights", [])
        bias_weights = cfg.get("bias_weights", [])
        nodes = []

        for node_idx in range(node_count):
            weights = list(weights_matrix[node_idx]) + [bias_weights[node_idx]]
            node = Network._Node(
                pre_layer=pre_layer,
                weights=weights,
                node_type=layer_type,
                layer_idx=layer_idx,
                node_idx=node_idx,
            )
            nodes.append(node)

        # Hidden 層需要 bias node
        if layer_type != "O":
            nodes.append(
                Network._Node(pre_layer=pre_layer, node_type="B", layer_idx=layer_idx)
            )
        return Network._Layer(nodes, layer_type=layer_type, activation=activation)`,
  },
  {
    label: 'forward', tag: '前向傳播', lineStart: 274, lineEnd: 310,
    code: `    def forward(self, input_values: Sequence[float]) -> List[float]:
        """執行前向傳遞（Forward propagation）"""

        input_values = Network._to_list(input_values)
        if len(input_values) != len(self.map.inputs.nodes) - 1:  # 忽略 bias
            raise ValueError("輸入數量與 input node 數量不一致")

        for val, node in zip(input_values, self.map.inputs[:-1]):
            node.output = val

        for layer, pre_layer in zip(self.map[1:], self.map[:-1]):
            # raw_output 計算
            nodes_raw_output_list = []
            for node in layer:
                if node.id.startswith("B"):
                    node.raw_output = 1
                    continue
                raw_output = sum(
                    pre_node.output * node.weight_mapping[pre_node]
                    for pre_node in pre_layer
                )
                node.raw_output = raw_output
                nodes_raw_output_list.append(raw_output)

            # activated_output 計算
            activation_func = getattr(
                Network.Activation,
                layer.activation,
                Network.Activation.linear,
            )
            activated_outputs = activation_func(nodes_raw_output_list)
            if len(layer.nodes) != len(activated_outputs):
                activated_outputs.append(1.0)  # bias output
            for node, output in zip(layer.nodes, activated_outputs):
                node.output = output

        return [node.output for node in self.map.outputs]`,
  },
  {
    label: 'set_output_gradients', tag: '輸出梯度', lineStart: 313, lineEnd: 347,
    code: `    def set_output_gradients(
        self,
        output_values: Sequence[float],
        expect_values: Sequence[float],
        loss_func: str,
    ):
        """手動設定 outputs d_TL_d_raw"""
        output_values = Network._to_list(output_values)
        expect_values = Network._to_list(expect_values)
        if len(output_values) != len(expect_values):
            raise ValueError("outputs 數量與 expects 數量不一致")
        loss_func = loss_func.strip().lower()
        d_loss_func = getattr(Network.Loss, loss_func + "_derivative", None)
        output_layer_activation = self.map.outputs.activation
        d_output_layer_activation_func = getattr(
            Network.Activation,
            output_layer_activation + "_derivative",
            None,
        )
        for o, e, output_node in zip(output_values, expect_values, self.map.outputs):
            act_input = (
                output_node.output
                if output_layer_activation == "sigmoid"
                else output_node.raw_output
            )
            d_TL_d_raw = (
                d_loss_func(e, o) / (len(output_values) if loss_func == "mse" else 1)
            ) * d_output_layer_activation_func(act_input)
            output_node.d_TL_d_raw = d_TL_d_raw
            output_node.gradient_mapping = {
                pre_node: d_TL_d_raw * pre_node.output
                for pre_node in self.map.layers[-2]
            }`,
  },
  {
    label: 'backward', tag: '反向傳播', lineStart: 350, lineEnd: 380,
    code: `    def backward(self):
        """計算梯度"""

        rev_list = self.map.layers[::-1]
        for next_layer, layer, pre_layer in zip(rev_list, rev_list[1:], rev_list[2:]):

            d_activation = getattr(
                Network.Activation,
                layer.activation + "_derivative",
                Network.Activation.linear_derivative,
            )
            node_d_act_input_type = (
                "output" if layer.activation == "sigmoid" else "raw_output"
            )
            for node in layer:
                if node.id.startswith("B"):
                    continue
                d_activation_output = d_activation(
                    getattr(node, node_d_act_input_type)
                )
                node.d_activation_output = d_activation_output
                d_TL_d_raw = d_activation_output * (
                    sum(
                        next_layer_node.d_TL_d_raw
                        * next_layer_node.weight_mapping[node]
                        for next_layer_node in next_layer
                        if not next_layer_node.id.startswith("B")
                    )
                )
                node.d_TL_d_raw = d_TL_d_raw
                node.gradient_mapping = {
                    pre_node: d_TL_d_raw * pre_node.output
                    for pre_node in pre_layer
                }`,
  },
  {
    label: 'zero_grad', tag: '更新權重', lineStart: 408, lineEnd: 416,
    code: `    def zero_grad(self, learning_rate: float):
        """更新權重並歸零梯度"""
        for layer in self.map[1:]:
            for node in layer:
                for pre_node in node.weight_mapping:
                    node.weight_mapping[pre_node] -= (
                        node.gradient_mapping[pre_node] * learning_rate
                    )
                    node.gradient_mapping[pre_node] = 0`,
  },
  {
    label: 'build_model_json', tag: '建立設定', lineStart: 456, lineEnd: 503,
    code: `    @staticmethod
    def build_model_json(
        input_nodes,
        hidden_nodes_list,
        output_nodes,
        hidden_activation="sigmoid",
        output_activation="linear",
        input_activation="linear",
    ):
        def rand():
            return random.uniform(-0.1, 0.1)

        def weight_matrix(rows, cols):
            return [[rand() for _ in range(cols)] for _ in range(rows)]

        def bias_vector(size):
            return [rand() for _ in range(size)]

        model = {}

        # input
        model["input"] = {"nodes": input_nodes, "activation": input_activation}

        # hidden layers
        layers = []
        prev_nodes = input_nodes
        for h_nodes in hidden_nodes_list:
            layer = {
                "nodes": h_nodes,
                "activation": hidden_activation,
                "weights": weight_matrix(h_nodes, prev_nodes),
                "bias_weights": bias_vector(h_nodes),
            }
            layers.append(layer)
            prev_nodes = h_nodes

        model["layer"] = layers

        # output layer
        model["output"] = {
            "nodes": output_nodes,
            "activation": output_activation,
            "weights": weight_matrix(output_nodes, prev_nodes),
            "bias_weights": bias_vector(output_nodes),
        }

        return model`,
  },
]

function highlightPy(src) {
  const KW = new Set(['class','def','return','if','elif','else','for','while','in','not','and','or','is','None','True','False','from','import','raise','try','except','with','as','continue','break','pass','lambda','yield','global','nonlocal','assert','del'])
  const BI = new Set(['int','float','str','list','dict','tuple','set','bool','len','sum','max','min','zip','range','enumerate','print','getattr','hasattr','isinstance','type','super','any','all','List','Dict','Tuple','Sequence','Any','Optional'])
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  const w = (cls, s) => `<span class="${cls}">${s}</span>`

  function tokenize(line) {
    const toks = []; let i = 0
    while (i < line.length) {
      if (line[i] === '#') { toks.push({t:'cmt',v:line.slice(i)}); break }
      // Triple-quoted strings
      if ((line[i] === '"' || line[i] === "'") && line[i+1] === line[i] && line[i+2] === line[i]) {
        const q = line[i].repeat(3), s = i; i += 3
        const e = line.indexOf(q, i); const end = e >= 0 ? e+3 : line.length
        toks.push({t:'str',v:line.slice(s,end)}); i = end; continue
      }
      // f-strings
      if (line[i] === 'f' && (line[i+1] === '"' || line[i+1] === "'")) {
        const q = line[i+1], s = i; i += 2
        while (i < line.length && line[i] !== q) { if (line[i] === '\\') i++; i++ }
        toks.push({t:'str',v:line.slice(s,++i)}); continue
      }
      // Regular strings
      if (line[i] === '"' || line[i] === "'") {
        const q = line[i], s = i++
        while (i < line.length && line[i] !== q) { if (line[i] === '\\') i++; i++ }
        toks.push({t:'str',v:line.slice(s,++i)}); continue
      }
      // Decorators
      if (line[i] === '@') {
        let j = i+1; while (j < line.length && /\w/.test(line[j])) j++
        toks.push({t:'dec',v:line.slice(i,j)}); i = j; continue
      }
      // Identifiers
      if (/[a-zA-Z_]/.test(line[i])) {
        let j = i; while (j < line.length && /\w/.test(line[j])) j++
        const word = line.slice(i,j)
        const t = KW.has(word) ? 'kw' : BI.has(word) ? 'bi' : word === 'self' ? 'slf' : 'id'
        toks.push({t,v:word}); i = j; continue
      }
      // Numbers
      if (/\d/.test(line[i])) {
        let j = i; while (j < line.length && /[\d.eE]/.test(line[j])) j++
        toks.push({t:'num',v:line.slice(i,j)}); i = j; continue
      }
      toks.push({t:'o',v:line[i++]})
    }
    return toks
  }

  return src.split('\n').map(line => {
    return tokenize(line).map(({t,v}) => {
      const e = esc(v)
      if (t === 'kw')  return w('py-kw',  e)
      if (t === 'bi')  return w('py-bi',  e)
      if (t === 'slf') return w('py-self', e)
      if (t === 'cmt') return w('py-cmt', e)
      if (t === 'str') return w('py-str', e)
      if (t === 'dec') return w('py-dec', e)
      if (t === 'num') return w('py-num', e)
      return e
    }).join('')
  })
}

const codeRows = computed(() =>
  highlightPy(codeSections[activeSection.value].code).map(html => ({ html }))
)
</script>

<style scoped>
/* ── 根容器 ──────────────────────────────────────── */
.nnv {
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-family: 'Noto Sans TC', system-ui, sans-serif;
  color: #1a0f08;
}

/* ── 架構設定列 ──────────────────────────────────── */
.nnv-config {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  align-items: flex-start;
  background: rgba(255, 254, 245, 0.7);
  border: 1px solid rgba(160, 130, 100, 0.25);
  border-radius: 12px;
  padding: 12px 16px;
}

.dark .nnv-config {
  background: rgba(40, 25, 15, 0.7);
  border-color: rgba(160, 130, 100, 0.2);
}

.nnv-cfg-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: #8b6e50;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 6px;
}

.dark .nnv-cfg-label {
  color: #b09070;
}

.nnv-cfg-group {
  display: flex;
  flex-direction: column;
}

.nnv-cfg-layers {
  flex: 1;
  min-width: 180px;
}

/* ── Stepper ─────────────────────────────────────── */
.nnv-stepper {
  display: inline-flex;
  align-items: center;
  gap: 0;
  border: 1px solid rgba(139, 110, 80, 0.35);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.dark .nnv-stepper {
  background: #2a1a0e;
  border-color: rgba(160, 130, 100, 0.3);
}

.nnv-stepper button {
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  color: #8b6e50;
  transition: background 0.15s;
}

.nnv-stepper button:hover:not(:disabled) {
  background: rgba(139, 110, 80, 0.12);
}

.nnv-stepper button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.nnv-stepper span {
  min-width: 28px;
  text-align: center;
  font-weight: 700;
  font-size: 14px;
  color: #3a2010;
}

.dark .nnv-stepper span {
  color: #f0e8e0;
}

.nnv-stepper--sm button {
  width: 24px;
  height: 24px;
  font-size: 14px;
}

.nnv-stepper--sm span {
  min-width: 20px;
  font-size: 13px;
}

/* ── 隱藏層列表 ──────────────────────────────────── */
.nnv-layer-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.nnv-layer-row {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(139, 110, 80, 0.08);
  border-radius: 8px;
  padding: 3px 6px;
}

.dark .nnv-layer-row {
  background: rgba(139, 110, 80, 0.15);
}

.nnv-layer-badge {
  font-size: 11px;
  font-weight: 700;
  color: #8b6e50;
  min-width: 18px;
}

.nnv-rm-layer {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #c0705a;
  font-size: 14px;
  line-height: 1;
  padding: 0 2px;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.nnv-rm-layer:hover:not(:disabled) {
  opacity: 1;
}

.nnv-rm-layer:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

.nnv-add-layer {
  border: 1px dashed rgba(139, 110, 80, 0.4);
  background: transparent;
  cursor: pointer;
  color: #8b6e50;
  font-size: 12px;
  border-radius: 7px;
  padding: 4px 10px;
  transition: all 0.15s;
}

.nnv-add-layer:hover:not(:disabled) {
  background: rgba(139, 110, 80, 0.1);
  border-style: solid;
}

.nnv-add-layer:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ── Select ─────────────────────────────────────── */
.nnv-select {
  padding: 6px 10px;
  border: 1px solid rgba(139, 110, 80, 0.35);
  border-radius: 8px;
  background: #fff;
  font-size: 13px;
  color: #3a2010;
  cursor: pointer;
}

.dark .nnv-select {
  background: #2a1a0e;
  color: #f0e8e0;
  border-color: rgba(160, 130, 100, 0.3);
}

/* ── 主體：SVG + OOP ─────────────────────────────── */
.nnv-body {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

/* ── SVG 容器 ────────────────────────────────────── */
.nnv-canvas-wrap {
  flex: 1;
  min-width: 0;
  background: rgba(255, 254, 245, 0.55);
  border: 1px solid rgba(160, 130, 100, 0.22);
  border-radius: 12px;
  overflow: hidden;
}

.dark .nnv-canvas-wrap {
  background: rgba(30, 18, 10, 0.7);
  border-color: rgba(160, 130, 100, 0.2);
}

.nnv-svg {
  width: 100%;
  display: block;
}

.nnv-edge {
  transition: opacity 0.4s ease, stroke-width 0.4s ease;
}

.nnv-edge-lbl {
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.dark .nnv-edge-lbl {
  stroke: #1e1208 !important;
}

.nnv-node-g {
  cursor: pointer;
}

.nnv-node-g circle {
  transition: fill 0.45s ease, stroke 0.3s ease;
}


/* ── 輸入控制列 ──────────────────────────────────── */
.nnv-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  background: rgba(255, 254, 245, 0.7);
  border: 1px solid rgba(160, 130, 100, 0.22);
  border-radius: 12px;
  padding: 10px 14px;
}

.dark .nnv-controls {
  background: rgba(40, 25, 15, 0.7);
  border-color: rgba(160, 130, 100, 0.2);
}

.nnv-inputs-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.nnv-input-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nnv-input-label {
  font-size: 12px;
  font-weight: 700;
  color: #8b6e50;
  min-width: 18px;
}

.nnv-input-num {
  width: 72px;
  padding: 5px 8px;
  border: 1px solid rgba(139, 110, 80, 0.35);
  border-radius: 7px;
  background: #fff;
  font-size: 13px;
  color: #3a2010;
  font-family: monospace;
  text-align: right;
}

.dark .nnv-input-num {
  background: #2a1a0e;
  color: #f0e8e0;
  border-color: rgba(160, 130, 100, 0.3);
}

.nnv-input-num:disabled {
  opacity: 0.5;
}

.nnv-btn-row {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.nnv-btn-run {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: #8b5e3c;
  color: #fff;
  border: none;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
}

.nnv-btn-run:hover:not(:disabled) {
  background: #a06840;
}

.nnv-btn-run:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nnv-btn-reset {
  padding: 8px 14px;
  border: 1px solid rgba(139, 110, 80, 0.4);
  background: transparent;
  color: #8b6e50;
  border-radius: 9px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.nnv-btn-reset:hover:not(:disabled) {
  background: rgba(139, 110, 80, 0.1);
}

.nnv-btn-reset:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 執行中 spinner */
.nnv-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: nnv-spin 0.7s linear infinite;
}

@keyframes nnv-spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── 節點詳細資訊卡 ──────────────────────────────── */
.nnv-detail {
  background: rgba(255, 254, 245, 0.9);
  border: 1px solid rgba(139, 110, 80, 0.3);
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 13px;
  backdrop-filter: blur(4px);
}

.dark .nnv-detail {
  background: rgba(35, 22, 12, 0.92);
  border-color: rgba(160, 130, 100, 0.25);
}

.nnv-detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.nnv-detail-id {
  font-weight: 700;
  font-size: 14px;
  font-family: monospace;
  color: #8b5e3c;
}

.nnv-detail-close {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #a08070;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.nnv-detail-close:hover {
  color: #c05040;
}

.nnv-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid rgba(139, 110, 80, 0.12);
  gap: 12px;
}

.nnv-detail-row span {
  color: #6a5040;
  font-size: 12px;
}

.dark .nnv-detail-row span {
  color: #a09080;
}

.nnv-detail-row code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #3a2010;
  background: rgba(139, 110, 80, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
}

.dark .nnv-detail-row code {
  color: #f0e8e0;
  background: rgba(139, 110, 80, 0.2);
}

.nnv-detail-row code.pos {
  color: #b04020;
}

.nnv-detail-row code.neg {
  color: #2060a0;
}

.dark .nnv-detail-row code.pos {
  color: #f08060;
}

.dark .nnv-detail-row code.neg {
  color: #70b0e0;
}

.nnv-detail-sub {
  font-size: 11px;
  font-weight: 700;
  color: #a08070;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 10px 0 4px;
}

/* ── Transition ─────────────────────────────────── */
.nnv-slide-enter-active {
  transition: all 0.25s ease;
}

.nnv-slide-leave-active {
  transition: all 0.2s ease;
}

.nnv-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.nnv-slide-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

/* ── 反向傳播控制列 ──────────────────────────────── */
.nnv-backward {
  background: rgba(147, 51, 234, 0.06);
  border: 1px solid rgba(147, 51, 234, 0.22);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dark .nnv-backward {
  background: rgba(147, 51, 234, 0.1);
  border-color: rgba(192, 132, 252, 0.25);
}

.nnv-bw-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.nnv-bw-title {
  font-size: 12px;
  font-weight: 700;
  color: #7e22ce;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.dark .nnv-bw-title {
  color: #c084fc;
}

.nnv-loss-badge {
  font-size: 12px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: #7e22ce;
  background: rgba(147, 51, 234, 0.12);
  border: 1px solid rgba(147, 51, 234, 0.25);
  border-radius: 20px;
  padding: 2px 12px;
}

.dark .nnv-loss-badge {
  color: #c084fc;
  background: rgba(192, 132, 252, 0.15);
  border-color: rgba(192, 132, 252, 0.3);
}

.nnv-bw-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.nnv-bw-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.nnv-btn-bw {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: #7e22ce;
  color: #fff;
  border: none;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
}

.nnv-btn-bw:hover:not(:disabled) {
  background: #9333ea;
}

.nnv-btn-bw:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.nnv-btn-update {
  padding: 8px 14px;
  border: 1px solid rgba(147, 51, 234, 0.45);
  background: transparent;
  color: #7e22ce;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.dark .nnv-btn-update {
  color: #c084fc;
  border-color: rgba(192, 132, 252, 0.4);
}

.nnv-btn-update:hover:not(:disabled) {
  background: rgba(147, 51, 234, 0.12);
}

.nnv-btn-update:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ── Python 原始碼展示 ────────────────────────────── */
.nnv-code {
  border-top: 1px solid rgba(139, 110, 80, 0.2);
  padding-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nnv-code-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.nnv-code-title {
  font-size: 13px;
  font-weight: 700;
  color: #5a3e28;
}

.dark .nnv-code-title { color: #c8a880; }

.nnv-code-title code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #86efac;
  background: rgba(20, 10, 4, 0.7);
  padding: 1px 6px;
  border-radius: 4px;
}

.nnv-code-badge {
  font-size: 11px;
  color: #8b6e50;
  background: rgba(139, 110, 80, 0.1);
  border: 1px solid rgba(139, 110, 80, 0.2);
  border-radius: 20px;
  padding: 2px 10px;
}

.dark .nnv-code-badge {
  background: rgba(139, 110, 80, 0.18);
  border-color: rgba(139, 110, 80, 0.3);
  color: #b09070;
}

/* ── Tabs ────────────────────────────────────────── */
.nnv-code-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.nnv-code-tab {
  padding: 4px 12px;
  border: 1px solid rgba(139, 110, 80, 0.28);
  border-radius: 6px;
  background: transparent;
  font-size: 11.5px;
  font-family: 'JetBrains Mono', monospace;
  color: #7a5a3a;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.dark .nnv-code-tab { color: #b09070; border-color: rgba(160, 130, 100, 0.25); }

.nnv-code-tab:hover:not(.active) {
  background: rgba(139, 110, 80, 0.1);
}

.nnv-code-tab.active {
  background: #1e1410;
  color: #86efac;
  border-color: rgba(134, 239, 172, 0.35);
}

.dark .nnv-code-tab.active {
  background: #130d08;
  border-color: rgba(134, 239, 172, 0.4);
}

/* ── Code Panel ──────────────────────────────────── */
.nnv-code-panel {
  background: #141008;
  border: 1px solid rgba(255, 200, 140, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.dark .nnv-code-panel {
  background: #0e0a05;
  border-color: rgba(255, 200, 140, 0.12);
}

.nnv-code-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px;
  background: rgba(255, 200, 140, 0.05);
  border-bottom: 1px solid rgba(255, 200, 140, 0.08);
  flex-wrap: wrap;
}

.nnv-code-file {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #a08060;
  font-weight: 600;
}

.nnv-code-lines {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #6a5040;
}

.nnv-code-tag {
  font-size: 10px;
  font-weight: 600;
  color: #7dd3fc;
  background: rgba(125, 211, 252, 0.1);
  border: 1px solid rgba(125, 211, 252, 0.2);
  border-radius: 10px;
  padding: 1px 8px;
}

.nnv-code-scroll {
  overflow-x: auto;
  max-height: 520px;
  overflow-y: auto;
}

.nnv-code-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12.5px;
  line-height: 1.7;
}

.nnv-ln {
  width: 40px;
  min-width: 40px;
  text-align: right;
  padding: 0 10px 0 14px;
  color: #4a3828;
  user-select: none;
  vertical-align: top;
  font-size: 11px;
  padding-top: 1px;
  border-right: 1px solid rgba(255, 200, 140, 0.06);
}

.nnv-lc {
  padding: 0 16px;
  color: #c8b8a0;
  white-space: pre;
  vertical-align: top;
}

/* Python syntax colours */
.py-kw   { color: #c084fc; }
.py-bi   { color: #7dd3fc; }
.py-self { color: #fbbf24; }
.py-cmt  { color: #5a6a4a; font-style: italic; }
.py-str  { color: #86efac; }
.py-dec  { color: #fb923c; }
.py-num  { color: #f9a8d4; }

/* ── RWD ─────────────────────────────────────────── */
@media (max-width: 640px) {
  .nnv-code-scroll { max-height: 360px; }
  .nnv-code-table  { font-size: 11px; }
}
</style>
