<template>
  <div class="home-page">
    <!-- 顶部欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="welcome-text">
          <h1>🌾 欢迎回来，智慧农业云平台</h1>
          <p>实时监测 | 智能诊断 | 科学管理 | 增产增收</p>
        </div>
        <div class="banner-stats">
          <div class="banner-stat">
            <span class="stat-number">{{ statistics.users }}</span>
            <span class="stat-label">注册用户</span>
          </div>
          <div class="banner-stat">
            <span class="stat-number">{{ statistics.greenhouse }}</span>
            <span class="stat-label">智能温室</span>
          </div>
          <div class="banner-stat">
            <span class="stat-number">{{ statistics.diseases }}</span>
            <span class="stat-label">病害库</span>
          </div>
          <div class="banner-stat">
            <span class="stat-number">{{ statistics.yield }}</span>
            <span class="stat-label">今日产量(kg)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- 左侧主区域 -->
      <div class="main-content">
        <!-- 快捷入口 -->
        <el-card shadow="hover" class="quick-entry-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Grid /></el-icon>
                <span>快捷入口</span>
              </div>
              <el-button type="primary" link>更多</el-button>
            </div>
          </template>
          <div class="entry-grid">
            <div class="entry-item" @click="navigateTo('/imgPredict')">
              <div class="entry-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><Picture /></el-icon>
              </div>
              <span>图片检测</span>
            </div>
            <div class="entry-item" @click="navigateTo('/cameraPredict')">
              <div class="entry-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon><Camera /></el-icon>
              </div>
              <span>摄像检测</span>
            </div>
            <div class="entry-item" @click="navigateTo('/infoDisease')">
              <div class="entry-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <span>病虫害库</span>
            </div>
            <div class="entry-item" @click="navigateTo('/smartChat')">
              <div class="entry-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <span>智能助手</span>
            </div>
            <div class="entry-item" @click="navigateTo('/detectionRecords')">
              <div class="entry-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <el-icon><Document /></el-icon>
              </div>
              <span>检测记录</span>
            </div>
            <div class="entry-item" @click="navigateTo('/greenhouse/index')">
              <div class="entry-icon" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <span>温室管理</span>
            </div>
          </div>
        </el-card>

        <!-- 系统公告 -->
        <el-card shadow="hover" class="notice-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Bell /></el-icon>
                <span>系统公告</span>
              </div>
              <el-tag size="small" type="danger">最新</el-tag>
            </div>
          </template>
          <div class="notice-content">
            <el-icon class="quote-icon"><ChatLineRound /></el-icon>
            <p>尊敬的各位系统用户：您好！欢迎使用本智慧农业云平台系统。为确保您能够顺畅、高效地运用本系统，充分发挥其功能优势，现将首页关键使用事项公告如下，请您仔细阅读并予以配合。本智慧农业云平台集成了多项先进技术，通过首页，您可一键快速实时查看环境监测、病害生长数据分析、园林作物病虫害监控。促进病虫害及时发现及防治，助力农业智能化。</p>
          </div>
        </el-card>

        <!-- 温室作物信息 -->
        <el-card shadow="hover" class="crop-info-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Grid /></el-icon>
                <span>温室作物信息</span>
              </div>
              <el-button type="primary" link @click="navigateTo('/greenhouse/index')">查看全部</el-button>
            </div>
          </template>
          <div class="crop-grid">
            <div v-for="(item, index) in cropTypes.slice(0, 6)" :key="index" class="crop-item">
              <div class="crop-header">
                <span class="crop-name">{{ item.name }}</span>
                <el-tag :type="item.status === '生长良好' ? 'success' : 'warning'" size="small" effect="light">
                  {{ item.status }}
                </el-tag>
              </div>
              <div class="crop-detail">
                <div class="crop-type">
                  <el-icon><Grape /></el-icon>
                  {{ item.crop }}
                </div>
                <div class="crop-numbers">
                  <span class="plant-count">🌱 {{ item.plantCount }}株</span>
                  <span class="disease-count">⚠️ {{ item.diseaseCount }}例</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧边栏 -->
      <div class="sidebar">
        <!-- 天气卡片 - 已移除空气质量 -->
        <el-card shadow="hover" class="weather-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Sunny /></el-icon>
                <span>天气预报</span>
              </div>
              <el-button type="primary" link>详情</el-button>
            </div>
          </template>
          <div class="weather-content">
            <div class="weather-location">
              <el-icon><Location /></el-icon>
              <span>{{ weatherInfo.city }}</span>
            </div>
            <div class="weather-main">
              <div class="weather-temp">{{ weatherInfo.temperature }}</div>
              <div class="weather-condition">{{ weatherInfo.weather }}</div>
            </div>
            <div class="weather-date">{{ weatherInfo.date }} {{ weatherInfo.weekday }}</div>
            <div class="weather-detail">
              <div class="detail-item">
                <el-icon><WindPower /></el-icon>
                <span>{{ weatherInfo.wind }}</span>
              </div>
            </div>
            <div class="weather-notice">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ weatherInfo.notice }}</span>
            </div>
          </div>
        </el-card>

        <!-- 实用链接 -->
        <el-card shadow="hover" class="links-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><Link /></el-icon>
                <span>实用链接</span>
              </div>
            </div>
          </template>
          <div class="links-list">
            <a v-for="(link, index) in agricultureLinks.slice(0, 8)"
               :key="index"
               :href="link.url"
               target="_blank"
               class="link-item">
              <el-icon><Link /></el-icon>
              <span>{{ link.name }}</span>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </a>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Grid, Picture, Camera, DataAnalysis, ChatDotRound, Document,
  OfficeBuilding, Bell, ChatLineRound, Sunny, Location, WindPower,
  InfoFilled, Link, ArrowRight, Grape
} from '@element-plus/icons-vue'
import { ElCard, ElTag, ElButton, ElMessage } from 'element-plus'

const router = useRouter()

// 统计数据
const statistics = ref({
  users: 42,
  greenhouse: 9,
  diseases: 141,
  yield: 1232
})

// 天气信息 - 移除空气质量
const weatherInfo = ref({
  date: '',
  weekday: '',
  city: '',
  temperature: '',
  weather: '',
  wind: '',
  notice: ''
})

// 种植作物数据
const cropTypes = ref([
  { name: '1号温室', crop: '玉米', status: '生长良好', plantCount: 350, diseaseCount: 20 },
  { name: '2号温室', crop: '水稻', status: '生长良好', plantCount: 400, diseaseCount: 15 },
  { name: '3号温室', crop: '小麦', status: '需要关注', plantCount: 350, diseaseCount: 18 },
  { name: '4号温室', crop: '马铃薯', status: '生长良好', plantCount: 250, diseaseCount: 12 },
  { name: '5号温室', crop: '棉花', status: '生长良好', plantCount: 300, diseaseCount: 16 },
  { name: '6号温室', crop: '苹果', status: '需要关注', plantCount: 80, diseaseCount: 14 },
  { name: '7号温室', crop: '葡萄', status: '生长良好', plantCount: 120, diseaseCount: 17 },
  { name: '8号温室', crop: '番茄', status: '生长良好', plantCount: 150, diseaseCount: 14 },
  { name: '9号温室', crop: '草莓', status: '生长良好', plantCount: 200, diseaseCount: 15 }
])

// 农业链接
const agricultureLinks = ref([
  { name: '中国农村网', url: 'https://www.crnews.net/', icon: 'icon-nongye' },
  { name: '中国农业网', url: 'https://www.zgny.com/', icon: 'icon-keji' },
  { name: '农业气象网', url: 'http://www.nmc.cn/publish/agro/soil-moisture-monitoring-10cm.html', icon: 'icon-zhihui' },
  { name: '农业病虫害服务站', url: 'https://farm.sino-eco.com/website/bingchonghai/', icon: 'icon-qixiang' },
  { name: '国家农业数据中心', url: 'https://www.agridata.cn/', icon: 'icon-qixiang' },
  { name: '农业病虫害研究图库', url: 'http://www.icgroupcas.cn/website_bchtk/zhenduan.aspx', icon: 'icon-qixiang' },
  { name: '中国害虫防治网', url: 'http://zghcfzw.com/', icon: 'icon-qixiang' },
  { name: '中国农业科学院', url: 'https://www.caas.cn/', icon: 'icon-qixiang' },
  { name: '中国农业农村信息网', url: 'https://www.agri.cn/', icon: 'icon-qixiang' },
  { name: '农业中国_中国网', url: 'http://agri.china.com.cn/', icon: 'icon-bingchonghai' }
])

// 路由跳转函数
const navigateTo = (path: string) => {
  router.push(path)
}

// 获取天气数据 - 定位到贵阳（已移除空气质量）
const fetchWeatherData = async () => {
  try {
    const city = '贵阳'

    const response = await fetch(`https://wttr.in/${encodeURIComponent(city)}?format=j1&lang=zh`)

    if (response.ok) {
      const data = await response.json()
      const current = data.current_condition[0]

      weatherInfo.value = {
        date: new Date().toLocaleDateString('zh-CN'),
        weekday: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'][new Date().getDay()],
        city: city,
        temperature: current.temp_C + '°C',
        weather: current.weatherDesc[0].value,
        wind: `${current.windspeedKmph} km/h ${current.winddir16Point}`,
        notice: current.lang_zh && current.lang_zh[0] ? current.lang_zh[0].value : '注意天气变化'
      }
    } else {
      throw new Error('获取天气失败')
    }
  } catch (err) {
    console.error('获取天气数据失败:', err)
    const now = new Date()
    weatherInfo.value = {
      date: now.toLocaleDateString('zh-CN'),
      weekday: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'][now.getDay()],
      city: '贵阳',
      temperature: '--°C',
      weather: '数据加载中',
      wind: '--',
      notice: '天气服务暂时不可用，请稍后重试'
    }
  }
}

onMounted(() => {
  fetchWeatherData()
})
</script>

<style scoped lang="scss">
.home-page {
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  padding: 20px;
}

// 欢迎横幅
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3);

  .banner-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;

    .welcome-text {
      h1 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: white;
      }

      p {
        margin: 0;
        font-size: 14px;
        color: rgba(255, 255, 255, 0.85);
      }
    }

    .banner-stats {
      display: flex;
      gap: 32px;

      .banner-stat {
        text-align: center;

        .stat-number {
          display: block;
          font-size: 28px;
          font-weight: 700;
          color: white;
          line-height: 1.2;
        }

        .stat-label {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.75);
        }
      }
    }
  }
}

// 内容区域
.content-area {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 20px;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

// 主内容区
.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 通用卡片样式
.el-card {
  border-radius: 16px;
  overflow: hidden;
  border: none;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  :deep(.el-card__header) {
    padding: 16px 20px;
    background: white;
    border-bottom: 1px solid #f0f0f0;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #303133;

        .el-icon {
          font-size: 18px;
          color: #409eff;
        }
      }
    }
  }

  :deep(.el-card__body) {
    padding: 20px;
  }
}

// 快捷入口
.quick-entry-card {
  .entry-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;

    .entry-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      padding: 16px;
      background: #f8f9fc;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-4px);
        background: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      .entry-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        .el-icon {
          font-size: 24px;
          color: white;
        }
      }

      span {
        font-size: 13px;
        color: #606266;
        font-weight: 500;
      }
    }
  }
}

// 系统公告
.notice-card {
  .notice-content {
    position: relative;
    padding: 8px 0;

    .quote-icon {
      position: absolute;
      top: 0;
      left: 0;
      font-size: 32px;
      color: rgba(64, 158, 255, 0.1);
    }

    p {
      margin: 0;
      padding-left: 28px;
      font-size: 14px;
      line-height: 1.8;
      color: #606266;
      text-indent: 2em;
    }
  }
}

// 温室作物信息
.crop-info-card {
  .crop-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .crop-item {
      background: #f8f9fc;
      border-radius: 12px;
      padding: 14px;
      transition: all 0.3s ease;

      &:hover {
        background: #ecf5ff;
        transform: translateX(4px);
      }

      .crop-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        .crop-name {
          font-size: 15px;
          font-weight: 600;
          color: #303133;
        }
      }

      .crop-detail {
        .crop-type {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: #409eff;
          margin-bottom: 8px;
        }

        .crop-numbers {
          display: flex;
          justify-content: space-between;
          font-size: 12px;

          .plant-count {
            color: #67c23a;
          }

          .disease-count {
            color: #f56c6c;
          }
        }
      }
    }
  }
}

// 侧边栏
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 天气卡片（已移除空气质量）
.weather-card {
  .weather-content {
    .weather-location {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #606266;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #f0f0f0;
    }

    .weather-main {
      text-align: center;
      margin-bottom: 16px;

      .weather-temp {
        font-size: 48px;
        font-weight: 700;
        color: #409eff;
        line-height: 1;
      }

      .weather-condition {
        font-size: 16px;
        color: #606266;
        margin-top: 8px;
      }
    }

    .weather-date {
      text-align: center;
      font-size: 13px;
      color: #909399;
      margin-bottom: 16px;
    }

    .weather-detail {
      display: flex;
      justify-content: center;
      padding: 12px 0;
      background: #f8f9fc;
      border-radius: 12px;
      margin-bottom: 16px;

      .detail-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #606266;
      }
    }

    .weather-notice {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      padding: 12px;
      background: #fff7e6;
      border-radius: 12px;
      font-size: 12px;
      color: #e6a23c;
      line-height: 1.5;

      .el-icon {
        flex-shrink: 0;
        margin-top: 2px;
      }
    }
  }
}

// 实用链接
.links-card {
  .links-list {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .link-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      background: #f8f9fc;
      border-radius: 10px;
      text-decoration: none;
      transition: all 0.3s ease;

      &:hover {
        background: #ecf5ff;
        transform: translateX(4px);

        .arrow-icon {
          opacity: 1;
          transform: translateX(0);
        }
      }

      .el-icon:first-child {
        font-size: 16px;
        color: #409eff;
      }

      span {
        flex: 1;
        font-size: 13px;
        color: #606266;
      }

      .arrow-icon {
        font-size: 12px;
        color: #909399;
        opacity: 0;
        transform: translateX(-4px);
        transition: all 0.3s ease;
      }
    }
  }
}
</style>