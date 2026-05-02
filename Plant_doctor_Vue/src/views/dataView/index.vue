<template>
  <div class="data-dashboard">
    <!-- ===== Top Header ===== -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="header-decoration"></div>
        <span class="header-title">智能农作物病害监测系统</span>
        <div class="header-decoration"></div>
      </div>
      <div class="header-right">
        <div class="header-stat-item">
          <span class="stat-dot online"></span>
          <span>系统运行中</span>
        </div>
        <div class="header-stat-item">
          <span class="stat-dot"></span>
          <span>在线设备: <b>36</b></span>
        </div>
        <div class="header-time">{{ currentTime }}</div>
      </div>
    </header>

    <!-- ===== Main Content ===== -->
    <div class="dashboard-body">
      <!-- ===== Left Column ===== -->
      <div class="col-left">
        <!-- Card 1: Disease Alert -->
        <div class="data-card card-disease">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">病虫害预警</span>
            <el-tag size="small" type="danger" effect="dark">实时监测</el-tag>
          </div>
          <div class="card-body">
            <div class="disease-sample">
              <div class="sample-img">
                <img src="/data/img/demo_pic.png" alt="样本图片" />
              </div>
              <div class="sample-info">
                <span class="sample-label">样本图片</span>
                <span class="sample-sub">作物病害大数据库</span>
              </div>
            </div>
            <div class="disease-wave" ref="waveRef">
              <canvas ref="waveCanvas"></canvas>
            </div>
            <div class="disease-progress">
              <div class="progress-label">
                <span>坏叶病</span>
                <span class="progress-similar">相似度: 98%</span>
              </div>
              <el-progress :percentage="98" :stroke-width="6" color="#0efcff" :show-text="false" />
            </div>
            <div class="disease-detail">
              <div class="detail-item symptom">
                <div class="detail-title">病症症状</div>
                <div class="detail-text">叶片黄化或枯黄<br/>水渍状斑块、整株萎蔫<br/>边缘枯死、叶脉变黑</div>
              </div>
              <div class="detail-item prevent">
                <div class="detail-title">防治方法</div>
                <div class="detail-text">抗性品种选择<br/>合理灌溉、轮作<br/>生物防治、化学防治</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Card 2: Soil Environment -->
        <div class="data-card card-soil">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">土壤环境监测</span>
            <el-tag size="small" type="success" effect="dark">正常</el-tag>
          </div>
          <div class="card-body">
            <div class="soil-bars">
              <div v-for="(item, idx) in soilData" :key="idx" class="soil-item">
                <span class="soil-depth">{{ item.depth }}</span>
                <div class="soil-bar-track">
                  <div class="soil-bar-fill temp-bar" :style="{ width: item.temp + '%' }"></div>
                </div>
                <span class="soil-value">{{ item.temp }}°C</span>
                <div class="soil-bar-track">
                  <div class="soil-bar-fill humi-bar" :style="{ width: item.humi + '%' }"></div>
                </div>
                <span class="soil-value">{{ item.humi }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Card 3: Disease Statistics Pie -->
        <div class="data-card card-chart">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">病害分布统计</span>
          </div>
          <div class="card-body chart-body">
            <div ref="pieChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- ===== Center Column ===== -->
      <div class="col-center">
        <!-- Card 1: Farm Map -->
        <div class="data-card card-map">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">智能农田可视化</span>
          </div>
          <div class="card-body map-body">
            <div class="farm-map" ref="mapRef">
              <img src="/data/img/dp.png" alt="农田地图" class="map-bg" />
              <!-- Interactive hotspots -->
              <div
                v-for="(hotspot, idx) in hotspots"
                :key="idx"
                class="map-hotspot"
                :style="{ left: hotspot.x + '%', top: hotspot.y + '%' }"
                @mouseenter="activeHotspot = idx"
                @mouseleave="activeHotspot = null"
              >
                <div class="hotspot-pulse"></div>
                <div class="hotspot-dot" :class="{ active: activeHotspot === idx }"></div>
                <transition name="fade">
                  <div v-if="activeHotspot === idx" class="hotspot-tooltip">
                    <div class="tooltip-title">{{ hotspot.title }}</div>
                    <div v-for="(v, k) in hotspot.data" :key="k" class="tooltip-row">
                      <span class="tooltip-key">{{ k }}：</span>
                      <span class="tooltip-val">{{ v }}</span>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
          </div>
        </div>

        <!-- Card 2: Growth + Weather -->
        <div class="card-row-2">
          <div class="data-card card-growth">
            <div class="card-header">
              <span class="card-title-icon"></span>
              <span class="card-title">生长监测</span>
            </div>
            <div class="card-body growth-body">
              <div class="growth-left">
                <img src="/data/img/tree_pic.png" alt="生长周期" class="growth-tree" />
              </div>
              <div class="growth-right">
                <div class="growth-item"><span>生长周期</span><b>8 周</b></div>
                <div class="growth-item"><span>土壤类型</span><b>黏土</b></div>
                <div class="growth-item"><span>10cm 含水量</span><b>22.88%</b></div>
                <div class="growth-item"><span>未来 5 天降水</span><b>0 mm</b></div>
                <div class="growth-suggest">
                  <div class="suggest-title">专家建议</div>
                  <div class="suggest-text">加入有机物料（如堆肥）和砂质物质来改善土壤结构</div>
                </div>
              </div>
            </div>
          </div>
          <div class="data-card card-weather">
            <div class="card-header">
              <span class="card-title-icon"></span>
              <span class="card-title">气象数据</span>
            </div>
            <div class="card-body weather-body">
              <div class="weather-grid">
                <div class="weather-cell">
                  <span class="weather-icon">🌡️</span>
                  <span class="weather-label">温度</span>
                  <span class="weather-value">19°C</span>
                </div>
                <div class="weather-cell">
                  <span class="weather-icon">💧</span>
                  <span class="weather-label">湿度</span>
                  <span class="weather-value">52%</span>
                </div>
                <div class="weather-cell">
                  <span class="weather-icon">🌬️</span>
                  <span class="weather-label">风速</span>
                  <span class="weather-value">2m/s</span>
                </div>
                <div class="weather-cell">
                  <span class="weather-icon">🧭</span>
                  <span class="weather-label">风向</span>
                  <span class="weather-value">东南风</span>
                </div>
                <div class="weather-cell">
                  <span class="weather-icon">🌧️</span>
                  <span class="weather-label">降雨量</span>
                  <span class="weather-value">0mm</span>
                </div>
                <div class="weather-cell">
                  <span class="weather-icon">🔽</span>
                  <span class="weather-label">气压</span>
                  <span class="weather-value">0.326MPa</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Card 3: Charts Row (Line + Radar) -->
        <div class="card-row-3">
          <div class="data-card card-line-chart">
            <div class="card-header">
              <span class="card-title-icon"></span>
              <span class="card-title">检测趋势</span>
            </div>
            <div class="card-body chart-body">
              <div ref="lineChartRef" class="chart-container"></div>
            </div>
          </div>
          <div class="data-card card-radar-chart">
            <div class="card-header">
              <span class="card-title-icon"></span>
              <span class="card-title">环境指标</span>
            </div>
            <div class="card-body chart-body">
              <div ref="radarChartRef" class="chart-container"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== Right Column ===== -->
      <div class="col-right">
        <!-- Card 1: Hardware Devices -->
        <div class="data-card card-devices">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">硬件设备</span>
          </div>
          <div class="card-body">
            <div class="device-tabs">
              <button
                v-for="(dev, idx) in devices"
                :key="idx"
                class="device-tab"
                :class="{ active: activeDevice === idx }"
                @click="activeDevice = idx"
              >{{ dev.name }}</button>
            </div>
            <div class="device-display">
              <img :src="devices[activeDevice].img" :alt="devices[activeDevice].name" class="device-img" />
            </div>
            <div class="device-status">
              <span>{{ devices[activeDevice].desc }}</span>
            </div>
          </div>
        </div>

        <!-- Card 2: Irrigation Data -->
        <div class="data-card card-irrigation">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">灌溉数据</span>
          </div>
          <div class="card-body irrigation-body">
            <div class="irrigation-top">
              <div class="irri-item">
                <span class="irri-label">累计灌溉水量 (m³)</span>
                <span class="irri-num" ref="waterNumRef">23,678</span>
              </div>
              <div class="irri-item">
                <span class="irri-label">灌溉压力 (MPa)</span>
                <span class="irri-num">0.29</span>
              </div>
            </div>
            <div class="water-gauge" ref="gaugeChartRef"></div>
            <div class="irrigation-bottom">
              <div class="irri-row">
                <span>当前灌溉流量</span><i>0.78 m³/h</i>
              </div>
              <div class="irri-row">
                <span>阀门开启数</span><i>49.2</i>
              </div>
              <div class="irri-row">
                <span>茶园水池液位</span><i>2.30 m</i>
              </div>
            </div>
          </div>
        </div>

        <!-- Card 3: Data Log -->
        <div class="data-card card-log">
          <div class="card-header">
            <span class="card-title-icon"></span>
            <span class="card-title">数据日志</span>
          </div>
          <div class="card-body log-body" ref="logScrollRef">
            <table>
              <thead>
                <tr><th>设备</th><th>类型</th><th>数值</th><th>时间</th></tr>
              </thead>
              <tbody>
                <tr v-for="(log, idx) in logData" :key="idx">
                  <td>{{ log.id }}</td>
                  <td>{{ log.type }}</td>
                  <td>{{ log.value }}</td>
                  <td>{{ log.time }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'

// ===== Time =====
const currentTime = ref('')
let timeTimer: ReturnType<typeof setInterval>
const updateTime = () => {
  const now = new Date()
  const pad = (n: number) => n.toString().padStart(2, '0')
  currentTime.value = `${now.getFullYear()}/${pad(now.getMonth() + 1)}/${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

// ===== Wave Canvas =====
const waveRef = ref<HTMLDivElement>()
const waveCanvas = ref<HTMLCanvasElement>()
let waveAnimId = 0
function initWave() {
  const canvas = waveCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  canvas.width = (waveRef.value?.clientWidth || 300) * 0.95
  canvas.height = 60
  const w = canvas.width, h = canvas.height
  let offset = 0
  const draw = () => {
    ctx.clearRect(0, 0, w, h)
    ctx.strokeStyle = '#0efcff'
    ctx.lineWidth = 2
    ctx.beginPath()
    for (let x = 0; x < w; x += 1) {
      const y = h / 2 + Math.sin((x + offset) * 0.04) * 15 + Math.sin((x + offset) * 0.08) * 6
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.stroke()
    // Second wave
    ctx.strokeStyle = 'rgba(14, 252, 255, 0.4)'
    ctx.lineWidth = 1
    ctx.beginPath()
    for (let x = 0; x < w; x += 1) {
      const y = h / 2 + Math.sin((x + offset + 30) * 0.05) * 12 + Math.sin((x + offset + 30) * 0.1) * 4
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.stroke()
    offset += 2
    waveAnimId = requestAnimationFrame(draw)
  }
  draw()
}

// ===== Hotspot Data =====
interface Hotspot {
  x: number; y: number; title: string; data: Record<string, string>
}
const activeHotspot = ref<number | null>(null)
const hotspots: Hotspot[] = [
  { x: 18, y: 45, title: '土壤数据', data: { '湿度': '63%', '酸碱度': 'pH 6.8', '肥沃度': '56%' } },
  { x: 55, y: 20, title: '气象信息', data: { '温度': '19°C', '湿度': '52%', '风速': '2m/s' } },
  { x: 40, y: 65, title: '植被信息', data: { '品种': '华北小麦', '数量': '76,000株', '长势': '良好' } },
  { x: 75, y: 55, title: '设备信息', data: { '设备': '无人机', '持续工作': '3h', '状态': '正常' } },
]

// ===== Soil Data =====
const soilData = [
  { depth: '10cm', temp: 25, humi: 54 },
  { depth: '20cm', temp: 29, humi: 59 },
  { depth: '30cm', temp: 32, humi: 67 },
]

// ===== Devices =====
const activeDevice = ref(0)
const devices = [
  { name: '农业无人机', img: '/data/img/uva.png', desc: '型号 DJI-M30 · 续航 45min' },
  { name: '大堋控制器', img: '/data/img/control.png', desc: '可控范围 500m² · 防水 IP67' },
  { name: '监控摄像头', img: '/data/img/camera.png', desc: '4K 高清 · 红外夜视 · 360° 旋转' },
  { name: '土壤检测仪', img: '/data/img/detector.png', desc: '多参数传感 · 精度 ±0.1' },
]

// ===== Data Log =====
const logTypes = ['传感器数据', '无人机数据', '控制器数据', '监视器数据', '土壤仪数据', '灌溉阀数据']
const logData = ref(Array.from({ length: 15 }, (_, i) => ({
  id: ['u78', '006', 's07', '872', 'd59', '299', '256', '026', '037', 'a12', 'b34', 'c56', 'f78', 'g90', 'h11'][i],
  type: logTypes[i % logTypes.length],
  value: (130 + Math.random() * 40).toFixed(2),
  time: new Date().toLocaleTimeString(),
})))
let logTimer: ReturnType<typeof setInterval>

// ===== ECharts =====
const pieChartRef = ref<HTMLDivElement>()
const lineChartRef = ref<HTMLDivElement>()
const radarChartRef = ref<HTMLDivElement>()
const gaugeChartRef = ref<HTMLDivElement>()
let pieChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null
let gaugeChart: echarts.ECharts | null = null

function initPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#0f1f3f', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{d}%', color: '#a0c4ff', fontSize: 11 },
      labelLine: { lineStyle: { color: '#2a4a7f' } },
      data: [
        { value: 35, name: '坏叶病', itemStyle: { color: '#ff6b6b' } },
        { value: 25, name: '白粉病', itemStyle: { color: '#ffa94d' } },
        { value: 20, name: '锈病', itemStyle: { color: '#ffd43b' } },
        { value: 12, name: '枯萎病', itemStyle: { color: '#69db7c' } },
        { value: 8, name: '其他', itemStyle: { color: '#748ffc' } },
      ],
    }],
  })
}

function initLineChart() {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['检测量', '病害率'], textStyle: { color: '#a0c4ff', fontSize: 11 }, bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '22%', top: '5%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'],
      axisLine: { lineStyle: { color: '#2a4a7f' } },
      axisLabel: { color: '#7a9ecf' },
    },
    yAxis: [
      { type: 'value', name: '检测数', splitLine: { lineStyle: { color: '#1a2a4f' } }, axisLabel: { color: '#7a9ecf' } },
      { type: 'value', name: '病害率 %', splitLine: { show: false }, axisLabel: { color: '#7a9ecf' } },
    ],
    series: [
      {
        name: '检测量', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#0efcff', width: 2 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(14,252,255,0.3)' }, { offset: 1, color: 'rgba(14,252,255,0.02)' }]) },
        data: [820, 932, 901, 1290, 1330, 1420, 1510],
      },
      {
        name: '病害率', type: 'line', smooth: true, symbol: 'diamond', symbolSize: 6,
        yAxisIndex: 1, lineStyle: { color: '#ff6b6b', width: 2 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(255,107,107,0.3)' }, { offset: 1, color: 'rgba(255,107,107,0.02)' }]) },
        data: [12, 15, 11, 9, 7, 5, 4],
      },
    ],
  })
}

function initRadarChart() {
  if (!radarChartRef.value) return
  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    radar: {
      indicator: [
        { name: '光照', max: 100 },
        { name: '温度', max: 50 },
        { name: '湿度', max: 100 },
        { name: '土壤肥力', max: 100 },
        { name: '空气质量', max: 100 },
      ],
      radius: '65%',
      axisName: { color: '#a0c4ff', fontSize: 10 },
      splitArea: { areaStyle: { color: ['rgba(14,252,255,0.02)', 'rgba(14,252,255,0.05)'] } },
      axisLine: { lineStyle: { color: '#2a4a7f' } },
      splitLine: { lineStyle: { color: '#2a4a7f' } },
    },
    series: [{
      type: 'radar',
      symbol: 'none',
      lineStyle: { color: '#0efcff', width: 2 },
      areaStyle: { color: 'rgba(14,252,255,0.15)' },
      data: [{ value: [85, 28, 62, 70, 90] }],
    }],
  })
}

function initGaugeChart() {
  if (!gaugeChartRef.value) return
  gaugeChart = echarts.init(gaugeChartRef.value)
  gaugeChart.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '55%'],
      radius: '85%',
      startAngle: 220, endAngle: -40,
      min: 0, max: 100,
      splitNumber: 5,
      progress: { show: true, width: 8, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#0efcff' }, { offset: 1, color: '#4dabf7' }] } } },
      axisLine: { lineStyle: { width: 8, color: [[1, '#1a2a4f']] } },
      axisTick: { show: false },
      splitLine: { length: 8, lineStyle: { color: '#2a4a7f' } },
      axisLabel: { distance: 18, color: '#7a9ecf', fontSize: 9 },
      detail: { formatter: '{value}%', color: '#0efcff', fontSize: 14, offsetCenter: [0, '40%'] },
      data: [{ value: 63 }],
    }],
  })
}

// ===== Log Scroll =====
const logScrollRef = ref<HTMLDivElement>()
let logScrollTimer: ReturnType<typeof setInterval>
function startLogScroll() {
  logScrollTimer = setInterval(() => {
    const el = logScrollRef.value
    if (!el) return
    if (el.scrollTop >= el.scrollHeight - el.clientHeight - 50) {
      el.scrollTop = 0
    } else {
      el.scrollTop += 1
    }
  }, 80)
}

// ===== Resize Handler =====
function handleResize() {
  [pieChart, lineChart, radarChart, gaugeChart].forEach(c => c?.resize())
}

// ===== Lifecycle =====
onMounted(() => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  nextTick(() => {
    initWave()
    initPieChart()
    initLineChart()
    initRadarChart()
    initGaugeChart()
    startLogScroll()
  })
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer)
  clearInterval(logTimer)
  clearInterval(logScrollTimer)
  cancelAnimationFrame(waveAnimId)
  window.removeEventListener('resize', handleResize)
  ;[pieChart, lineChart, radarChart, gaugeChart].forEach(c => c?.dispose())
})
</script>

<style scoped>
/* ===== Global ===== */
.data-dashboard {
  width: 100%;
  min-height: 100vh;
  background: radial-gradient(ellipse at 20% 20%, #0a1628, #050d1a 70%);
  color: #c8d6e5;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  padding: 8px 12px;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* ===== Header ===== */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, rgba(14,252,255,0.06), rgba(77,171,247,0.04));
  border: 1px solid rgba(14,252,255,0.12);
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}
.dashboard-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #0efcff, #4dabf7, transparent);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-decoration {
  width: 30px; height: 2px;
  background: linear-gradient(90deg, transparent, #0efcff);
}
.header-title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, #0efcff, #4dabf7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 3px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 13px;
}
.header-stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.stat-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #4a6a8a;
  display: inline-block;
}
.stat-dot.online {
  background: #0efcff;
  box-shadow: 0 0 6px #0efcff;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.header-time {
  color: #0efcff;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  letter-spacing: 1px;
}

/* ===== Body Grid ===== */
.dashboard-body {
  display: grid;
  grid-template-columns: 22% 1fr 22%;
  gap: 10px;
  height: calc(100vh - 82px);
}

/* ===== Cards Base ===== */
.data-card {
  background: linear-gradient(160deg, rgba(15,31,63,0.7), rgba(5,13,26,0.85));
  border: 1px solid rgba(42,74,127,0.4);
  border-radius: 10px;
  overflow: hidden;
  backdrop-filter: blur(6px);
  transition: border-color 0.3s;
}
.data-card:hover {
  border-color: rgba(14,252,255,0.3);
}
.card-header {
  display: flex;
  align-items: center;
  padding: 10px 14px 6px;
  gap: 8px;
  border-bottom: 1px solid rgba(42,74,127,0.3);
}
.card-title-icon {
  width: 3px; height: 16px;
  background: linear-gradient(180deg, #0efcff, #4dabf7);
  border-radius: 2px;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #e0f0ff;
  flex: 1;
}
.card-body {
  padding: 10px 14px 14px;
}
.chart-body {
  padding: 6px 6px 10px;
}
.chart-container {
  width: 100%;
  height: 140px;
}

/* ===== Left Column ===== */
.col-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.card-disease { flex: 0 0 auto; }
.card-soil { flex: 0 0 auto; }
.card-chart { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.card-chart .card-body { flex: 1; display: flex; }

/* Disease Alert */
.disease-sample {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}
.sample-img {
  width: 70px; height: 50px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid rgba(14,252,255,0.2);
}
.sample-img img { width: 100%; height: 100%; object-fit: cover; }
.sample-info { display: flex; flex-direction: column; }
.sample-label { font-size: 13px; color: #e0f0ff; }
.sample-sub { font-size: 11px; color: #5a8abf; }

.disease-wave { margin-bottom: 6px; }
.disease-wave canvas { display: block; width: 100%; }

.disease-progress { margin-bottom: 8px; }
.progress-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 3px; }
.progress-similar { color: #0efcff; }

.disease-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.detail-item {
  background: rgba(14,252,255,0.05);
  border: 1px solid rgba(14,252,255,0.1);
  border-radius: 6px;
  padding: 8px;
}
.detail-title {
  font-size: 12px;
  font-weight: 600;
  color: #0efcff;
  margin-bottom: 4px;
}
.detail-text {
  font-size: 11px;
  line-height: 1.6;
  color: #8ab4e0;
}

/* Soil */
.soil-bars { display: flex; flex-direction: column; gap: 8px; }
.soil-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.soil-depth { width: 40px; color: #5a8abf; }
.soil-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(42,74,127,0.3);
  border-radius: 4px;
  overflow: hidden;
}
.soil-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease;
}
.temp-bar { background: linear-gradient(90deg, #ff6b6b, #ffa94d); }
.humi-bar { background: linear-gradient(90deg, #4dabf7, #0efcff); }
.soil-value { width: 40px; text-align: right; color: #e0f0ff; font-size: 11px; }

/* ===== Center Column ===== */
.col-center {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.card-map { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.card-map .card-body { flex: 1; padding: 4px; }
.card-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; flex: 0 0 auto; }
.card-row-3 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; flex: 1; min-height: 0; }
.card-row-3 .data-card { display: flex; flex-direction: column; }
.card-row-3 .card-body { flex: 1; }

/* Farm Map */
.map-body { position: relative; overflow: hidden; }
.farm-map {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 6px;
  overflow: hidden;
}
.map-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.85;
}
.map-hotspot { position: absolute; cursor: pointer; z-index: 10; }
.hotspot-pulse {
  width: 20px; height: 20px;
  border-radius: 50%;
  border: 2px solid #0efcff;
  position: absolute;
  top: -4px; left: -4px;
  animation: hotspot-pulse 2s infinite;
  opacity: 0.5;
}
@keyframes hotspot-pulse {
  0% { transform: scale(0.8); opacity: 0.8; }
  100% { transform: scale(2); opacity: 0; }
}
.hotspot-dot {
  width: 12px; height: 12px;
  border-radius: 50%;
  background: #0efcff;
  box-shadow: 0 0 10px #0efcff;
  transition: transform 0.2s;
}
.hotspot-dot.active { transform: scale(1.4); }
.hotspot-tooltip {
  position: absolute;
  left: 20px; top: -10px;
  background: rgba(5,13,26,0.92);
  border: 1px solid rgba(14,252,255,0.3);
  border-radius: 8px;
  padding: 8px 12px;
  min-width: 120px;
  z-index: 20;
  backdrop-filter: blur(8px);
}
.tooltip-title { font-size: 13px; font-weight: 600; color: #0efcff; margin-bottom: 4px; }
.tooltip-row { font-size: 11px; line-height: 1.8; }
.tooltip-key { color: #5a8abf; }
.tooltip-val { color: #e0f0ff; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Growth */
.growth-body { display: flex; gap: 10px; }
.growth-left { flex-shrink: 0; }
.growth-tree { width: 60px; height: auto; }
.growth-right { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.growth-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 2px 0;
  border-bottom: 1px solid rgba(42,74,127,0.2);
}
.growth-item span { color: #5a8abf; }
.growth-item b { color: #e0f0ff; }
.growth-suggest {
  margin-top: 4px;
  background: rgba(14,252,255,0.06);
  border-radius: 6px;
  padding: 6px 8px;
}
.suggest-title { font-size: 11px; font-weight: 600; color: #0efcff; margin-bottom: 2px; }
.suggest-text { font-size: 10px; color: #8ab4e0; line-height: 1.5; }

/* Weather */
.weather-body { padding: 8px 12px 12px; }
.weather-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.weather-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 4px;
  background: rgba(14,252,255,0.04);
  border-radius: 6px;
  border: 1px solid rgba(42,74,127,0.2);
}
.weather-icon { font-size: 18px; }
.weather-label { font-size: 11px; color: #5a8abf; }
.weather-value { font-size: 13px; font-weight: 600; color: #e0f0ff; }

/* ===== Right Column ===== */
.col-right {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.card-devices { flex: 0 0 auto; }
.card-irrigation { flex: 0 0 auto; }
.card-log { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.card-log .card-body { flex: 1; overflow: hidden; padding: 6px 10px 10px; }

/* Devices */
.device-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}
.device-tab {
  flex: 1;
  padding: 5px 4px;
  font-size: 11px;
  background: rgba(42,74,127,0.2);
  border: 1px solid transparent;
  border-radius: 4px;
  color: #7a9ecf;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}
.device-tab:hover { background: rgba(14,252,255,0.08); }
.device-tab.active {
  color: #0efcff;
  border-color: rgba(14,252,255,0.3);
  background: rgba(14,252,255,0.1);
}
.device-display {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(3,14,38,0.5);
  border-radius: 6px;
  margin-bottom: 6px;
}
.device-img {
  max-height: 80px;
  max-width: 80%;
  object-fit: contain;
  filter: drop-shadow(0 0 8px rgba(14,252,255,0.2));
}
.device-status { font-size: 11px; color: #5a8abf; text-align: center; }

/* Irrigation */
.irrigation-body { padding: 8px 12px 12px; }
.irrigation-top {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 6px;
}
.irri-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(14,252,255,0.04);
  border-radius: 6px;
  padding: 6px;
}
.irri-label { font-size: 11px; color: #5a8abf; }
.irri-num { font-size: 18px; font-weight: 700; color: #0efcff; font-family: 'Courier New', monospace; }

.water-gauge { height: 80px; margin-bottom: 4px; }

.irrigation-bottom { display: flex; flex-direction: column; gap: 4px; }
.irri-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 8px;
  background: rgba(14,252,255,0.04);
  border-radius: 4px;
  font-size: 12px;
}
.irri-row span { color: #5a8abf; }
.irri-row i { color: #e0f0ff; font-style: normal; font-weight: 600; }

/* Data Log */
.log-body { overflow-y: auto; padding: 4px 0; }
.log-body::-webkit-scrollbar { width: 3px; }
.log-body::-webkit-scrollbar-thumb { background: #2a4a7f; border-radius: 2px; }
.log-body table { width: 100%; border-collapse: collapse; font-size: 11px; }
.log-body th {
  position: sticky;
  top: 0;
  background: #0a1628;
  color: #5a8abf;
  font-weight: 500;
  padding: 4px 6px;
  text-align: left;
  border-bottom: 1px solid rgba(42,74,127,0.3);
}
.log-body td {
  padding: 4px 6px;
  border-bottom: 1px solid rgba(42,74,127,0.08);
  color: #a0c4ff;
}
.log-body tr:hover td { background: rgba(14,252,255,0.03); }

/* ===== Responsive ===== */
@media (max-width: 1200px) {
  .dashboard-body { grid-template-columns: 1fr; }
  .card-row-2, .card-row-3 { grid-template-columns: 1fr; }
}
</style>
