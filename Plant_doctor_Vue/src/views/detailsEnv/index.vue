<template>
  <div class="env-monitor-container">
    <!-- 左侧面板 - 环境数据 -->
    <div class="left-panel">
      <!-- 温室选择 -->
      <el-card shadow="hover" class="select-card">
        <el-select
            v-model="selectedGreenhouse"
            placeholder="请选择温室"
            size="large"
            @change="loadGreenhouseData"
            class="greenhouse-select"
        >
          <el-option
              v-for="gh in greenhouseList"
              :key="gh.id"
              :label="gh.greenhouseName"
              :value="gh.id"
          >
            <span style="float: left">{{ gh.greenhouseName }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">{{ gh.cropType }}</span>
          </el-option>
        </el-select>
      </el-card>

      <!-- 作物信息卡片 -->
      <el-card shadow="hover" class="crop-info-card" v-if="currentGreenhouse">
        <div class="crop-header">
          <div class="crop-icon-wrapper">
            <el-icon class="crop-icon"><Sunny /></el-icon>
          </div>
          <div class="crop-details">
            <h3>{{ currentGreenhouse.cropType }}</h3>
            <p>种植数量：{{ currentGreenhouse.quantity }}株</p>
            <el-tag :type="getStatusType(currentGreenhouse.growthStatus)" effect="dark">
              {{ currentGreenhouse.growthStatus }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 环境监测数据 -->
      <el-row :gutter="20" class="env-data-grid">
        <!-- 第一行 - 温度、湿度、土壤 -->
        <el-col :span="8" v-for="(item, index) in envMetrics.slice(0, 3)" :key="index">
          <el-card shadow="hover" class="metric-card" :class="{ 'warning': item.warning }">
            <div class="metric-content">
              <div class="metric-icon" :style="{ background: item.color }">
                <el-icon><component :is="getIconComponent(item.icon)" /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-label">{{ item.label }}</div>
                <div class="metric-value">{{ item.value }}</div>
                <div class="metric-unit">{{ item.unit }}</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 第二行 - CO2、PH、光照 -->
        <el-col :span="8" v-for="(item, index) in envMetrics.slice(3, 6)" :key="index + 3">
          <el-card shadow="hover" class="metric-card" :class="{ 'warning': item.warning }">
            <div class="metric-content">
              <div class="metric-icon" :style="{ background: item.color }">
                <el-icon><component :is="getIconComponent(item.icon)" /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-label">{{ item.label }}</div>
                <div class="metric-value">{{ item.value }}</div>
                <div class="metric-unit">{{ item.unit }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 设备控制 -->
      <el-card shadow="hover" class="control-card">
        <div class="control-header">
          <el-icon><Switch /></el-icon>
          <h3>设备控制</h3>
        </div>
        <el-row :gutter="20" class="control-grid">
          <el-col :span="8" v-for="(device, index) in devices" :key="index">
            <div class="device-item">
              <div class="device-icon" :class="{ active: device.status }">
                <el-icon><component :is="getDeviceIcon(device.icon)" /></el-icon>
              </div>
              <div class="device-name">{{ device.name }}</div>
              <el-switch
                  v-model="device.status"
                  @change="handleDeviceChange(device)"
                  active-color="#409EFF"
                  inactive-color="#DCDFE6"
              />
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 右侧面板 - 智能建议 -->
    <div class="right-panel">
      <el-card shadow="hover" class="suggestion-card">
        <div class="suggestion-header">
          <el-icon class="header-icon"><ChatDotRound /></el-icon>
          <h3>🌱 植物医生-老张的智能建议</h3>
        </div>

        <el-button
            type="primary"
            @click="getSuggestions"
            :loading="loading"
            size="large"
            class="get-suggestion-btn"
        >
          <el-icon><MagicStick /></el-icon>
          获取智能建议
        </el-button>

        <div v-if="suggestions.length > 0" class="suggestions-content">
          <el-divider content-position="left">
            <el-icon><Document /></el-icon>
            <span>诊断报告</span>
          </el-divider>

          <div class="suggestion-list">
            <div
                v-for="(suggestion, index) in suggestions"
                :key="index"
                class="suggestion-item"
            >
              <div class="item-number">{{ index + 1 }}</div>
              <div class="item-content">{{ suggestion }}</div>
            </div>
          </div>
        </div>

        <el-empty
            v-else-if="!loading"
            description="点击按钮获取环境优化建议"
            :image-size="120"
        >
          <template #description>
            <p>老张会根据当前环境数据<br/>为您提供专业的种植建议</p>
          </template>
        </el-empty>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Sunny,
  Switch,
  ChatDotRound,
  MagicStick,
  Document,
  VideoPlay,
  Lightning,
  WindPower
} from '@element-plus/icons-vue';
import axios from 'axios';
import request from '/@/utils/request';

interface Greenhouse {
  id: number;
  greenhouseName: string;
  cropType: string;
  quantity: number;
  growthStatus: string;
  temperature: number;
  airHumidity: number;
  soilHumidity: number;
  co2Concentration: number;
  soilPh: number;
  lightIntensity: number;
  manager: string;
  recordTime: string;
}

const selectedGreenhouse = ref<number>(0);
const greenhouseList = ref<Greenhouse[]>([]);
const loading = ref(false);
const suggestions = ref<string[]>([]);

const currentGreenhouse = computed(() => {
  return greenhouseList.value.find(gh => gh.id === selectedGreenhouse.value) || null;
});

// 图标映射函数
const getIconComponent = (iconName: string) => {
  const iconMap: Record<string, any> = {
    'Odometer': Lightning,
    'Drop': Sunny,
    'Watermelon': Sunny,
    'CoffeeCup': Sunny,
    'ScaleToOriginal': Sunny,
    'Sunny': Sunny
  };
  return iconMap[iconName] || Sunny;
};

const getDeviceIcon = (iconName: string) => {
  const iconMap: Record<string, any> = {
    'VideoPlay': VideoPlay,
    'Light': Lightning,
    'Fan': WindPower
  };
  return iconMap[iconName] || VideoPlay;
};

// 环境指标数据
const envMetrics = reactive([
  {
    label: '室内温度',
    value: 0,
    unit: '°C',
    icon: 'Odometer',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    warning: false
  },
  {
    label: '空气湿度',
    value: 0,
    unit: '%',
    icon: 'Drop',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    warning: false
  },
  {
    label: '土壤湿度',
    value: 0,
    unit: '%',
    icon: 'Watermelon',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    warning: false
  },
  {
    label: '二氧化碳',
    value: 0,
    unit: 'ppm',
    icon: 'CoffeeCup',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    warning: false
  },
  {
    label: '土壤PH值',
    value: 0,
    unit: '',
    icon: 'ScaleToOriginal',
    color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    warning: false
  },
  {
    label: '光照强度',
    value: 0,
    unit: 'lux',
    icon: 'Sunny',
    color: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    warning: false
  }
]);

// 设备控制
const devices = reactive([
  { name: '水泵', status: false, icon: 'VideoPlay' },
  { name: '补光灯', status: false, icon: 'Light' },
  { name: '风扇', status: false, icon: 'Fan' }
]);

// 加载温室列表
const loadGreenhouseList = async () => {
  try {
    const res = await request.get('/api/greenhouse', {
      params: { pageNum: 1, pageSize: 100 }
    });

    if (res.code === 0 && res.data.records) {
      // 获取最新的温室数据（每个温室取最新的一条）
      const latestData = new Map();
      res.data.records.forEach((gh: Greenhouse) => {
        if (!latestData.has(gh.greenhouseName) ||
            new Date(gh.recordTime) > new Date(latestData.get(gh.greenhouseName).recordTime)) {
          latestData.set(gh.greenhouseName, gh);
        }
      });

      greenhouseList.value = Array.from(latestData.values());

      if (greenhouseList.value.length > 0) {
        selectedGreenhouse.value = greenhouseList.value[0].id;
        loadGreenhouseData();
      }
    }
  } catch (error) {
    console.error('加载温室列表失败:', error);
    ElMessage.error('加载温室数据失败');
  }
};

// 加载选定温室的数据
const loadGreenhouseData = () => {
  const gh = currentGreenhouse.value;
  if (!gh) return;

  // 更新环境指标
  envMetrics[0].value = gh.temperature;
  envMetrics[1].value = gh.airHumidity;
  envMetrics[2].value = gh.soilHumidity;
  envMetrics[3].value = gh.co2Concentration;
  envMetrics[4].value = gh.soilPh;
  envMetrics[5].value = gh.lightIntensity;

  // 检查是否需要警告
  checkWarnings(gh);

  // 清空之前的建议
  suggestions.value = [];
};

// 检查环境参数是否需要警告
const checkWarnings = (gh: Greenhouse) => {
  // 温度警告（根据作物类型可以调整）
  envMetrics[0].warning = gh.temperature > 35 || gh.temperature < 10;

  // 湿度警告
  envMetrics[1].warning = gh.airHumidity > 90 || gh.airHumidity < 30;

  // 土壤湿度警告
  envMetrics[2].warning = gh.soilHumidity > 80 || gh.soilHumidity < 20;
};

// 获取状态标签类型
const getStatusType = (status: string): 'success' | 'warning' | 'info' | 'danger' => {
  if (status.includes('生长')) return 'success';
  if (status.includes('成熟')) return 'warning';
  if (status.includes('收获')) return 'info';
  return 'success';
};

// 设备控制变化
const handleDeviceChange = (device: any) => {
  ElMessage.success(`${device.name}已${device.status ? '开启' : '关闭'}`);
  // TODO: 这里可以调用后端接口控制实际设备
};

// 获取智能建议（使用环境数据）
const getSuggestions = async () => {
  const gh = currentGreenhouse.value;
  if (!gh) {
    ElMessage.warning('请先选择温室');
    return;
  }

  loading.value = true;
  suggestions.value = [];

  try {
    console.log('=== 开始请求环境建议 ===');
    console.log('温室数据:', {
      greenhouse_name: gh.greenhouseName,
      crop_type: gh.cropType,
      growth_status: gh.growthStatus,
      temperature: gh.temperature,
      air_humidity: gh.airHumidity,
      soil_humidity: gh.soilHumidity,
      co2_concentration: gh.co2Concentration,
      soil_ph: gh.soilPh,
      light_intensity: gh.lightIntensity
    });

    // 调用后端 Spring Boot 代理接口
    const response = await request.post('/flask/env_advice', {
      greenhouse_name: gh.greenhouseName,
      crop_type: gh.cropType,
      growth_status: gh.growthStatus,
      temperature: gh.temperature,
      air_humidity: gh.airHumidity,
      soil_humidity: gh.soilHumidity,
      co2_concentration: gh.co2Concentration,
      soil_ph: gh.soilPh,
      light_intensity: gh.lightIntensity
    });

    console.log('=== 收到响应 ===');
    console.log('完整响应对象:', response);
    console.log('response 的类型:', typeof response);
    console.log('response 的键:', Object.keys(response));

    // Flask 直接返回的数据结构：{ success, advice, source }
    // 没有 Spring Boot 的包装层
    const flaskResponse = response;

    console.log('flaskResponse.success:', flaskResponse.success);
    console.log('flaskResponse.advice:', flaskResponse.advice ? '有值' : '无值');
    console.log('flaskResponse.source:', flaskResponse.source);

    // 检查 Flask 返回
    if (flaskResponse && flaskResponse.success === true && flaskResponse.advice) {
      const replyText = flaskResponse.advice;
      console.log('=== 原始建议文本 ===');
      console.log('文本长度:', replyText.length);
      console.log('文本前200字符:', replyText.substring(0, 200));

      // 清理 Markdown 格式符号
      let cleanedText = replyText
          // 移除加粗标记 **
          .replace(/\*\*/g, '')
          // 移除斜体标记 *
          .replace(/\*(?!\*)/g, '')
          // 移除标题标记 #
          .replace(/^#+\s*/gm, '')
          // 移除列表标记 - 、* 、+
          .replace(/^\s*[-*+]\s+/gm, '')
          // 移除数字列表标记 1. 2. 等
          .replace(/^\s*\d+\.\s+/gm, '');

      // 将回复内容按行分割并清理
      suggestions.value = cleanedText
          .split('\n')
          .map((line: string) => line.trim())
          .filter((line: string) => line.length > 0)
          // 合并连续的短行为一条建议
          .reduce((acc: string[], line: string) => {
            // 如果当前行很短（少于20字符）且不是最后一行，可能与下一行相关
            if (line.length < 20 && acc.length > 0 && !line.includes('：') && !line.includes(':')) {
              acc[acc.length - 1] += ' ' + line;
            } else {
              acc.push(line);
            }
            return acc;
          }, []);

      console.log('=== 处理后的建议列表 ===');
      console.log('建议数组:', suggestions.value);
      console.log('建议条数:', suggestions.value.length);

      if (suggestions.value.length > 0) {
        console.log('第一条建议:', suggestions.value[0]);
        console.log('第二条建议:', suggestions.value[1]);
        console.log('第三条建议:', suggestions.value[2]);
      }

      if (suggestions.value.length === 0) {
        // 如果分割后为空，直接使用原文本
        suggestions.value = [replyText.replace(/\*\*/g, '')];
        console.log('使用原始文本作为单条建议');
      }

      ElMessage.success(`获取智能建议成功（共${suggestions.value.length}条）`);
    } else {
      console.error('❌ Flask 返回数据不完整或不满足条件');
      console.error('flaskResponse:', flaskResponse);
      console.error('flaskResponse.success:', flaskResponse?.success);
      console.error('flaskResponse.advice:', flaskResponse?.advice);
      ElMessage.warning(flaskResponse?.error || 'AI服务未返回有效建议');
    }
  } catch (error: any) {
    console.error('=== 请求异常 ===');
    console.error('错误对象:', error);
    console.error('错误消息:', error.message);
    console.error('错误代码:', error.code);

    if (error.code === 'ECONNREFUSED' || error.message === 'Network Error') {
      ElMessage.error('无法连接到AI服务，请确保Flask服务已启动（端口5000）');
    } else if (error.response) {
      const errorMsg = error.response.data?.msg || error.response.data?.error || error.response.statusText;
      ElMessage.error(`请求失败：${errorMsg}`);
    } else {
      ElMessage.error('获取建议失败，请稍后重试');
    }
  } finally {
    loading.value = false;
    console.log('=== 请求结束 ===');
  }
};

onMounted(() => {
  loadGreenhouseList();
});
</script>

<style scoped lang="scss">
.env-monitor-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 60px);
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
}

// 左侧面板
.left-panel {
  flex: 1.5;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.select-card {
  .greenhouse-select {
    width: 100%;
  }
}

.crop-info-card {
  .crop-header {
    display: flex;
    align-items: center;
    gap: 16px;

    .crop-icon-wrapper {
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;

      .crop-icon {
        font-size: 32px;
        color: white;
      }
    }

    .crop-details {
      flex: 1;

      h3 {
        margin: 0 0 8px 0;
        font-size: 20px;
        color: #303133;
      }

      p {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #909399;
      }
    }
  }
}

.env-data-grid {
  .metric-card {
    transition: all 0.3s ease;
    border: 2px solid transparent;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    &.warning {
      border-color: #f56c6c;
      animation: pulse 2s infinite;
    }

    .metric-content {
      display: flex;
      align-items: center;
      gap: 12px;

      .metric-icon {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        flex-shrink: 0;
      }

      .metric-info {
        flex: 1;

        .metric-label {
          font-size: 13px;
          color: #909399;
          margin-bottom: 4px;
        }

        .metric-value {
          font-size: 24px;
          font-weight: 700;
          color: #303133;
          line-height: 1;
        }

        .metric-unit {
          font-size: 12px;
          color: #c0c4cc;
          margin-top: 2px;
        }
      }
    }
  }
}

.control-card {
  .control-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;

    .el-icon {
      font-size: 20px;
      color: #409EFF;
    }

    h3 {
      margin: 0;
      font-size: 16px;
      color: #303133;
    }
  }

  .control-grid {
    .device-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;
      transition: all 0.3s ease;

      &:hover {
        background: #e4e8eb;
      }

      .device-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: #909399;
        background: #dcdfe6;
        transition: all 0.3s ease;

        &.active {
          color: white;
          background: #409EFF;
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
        }
      }

      .device-name {
        font-size: 13px;
        color: #606266;
      }
    }
  }
}

// 右侧面板
.right-panel {
  flex: 1;
  display: flex;
}

.suggestion-card {
  width: 100%;
  display: flex;
  flex-direction: column;

  .suggestion-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 2px solid #f0f0f0;

    .header-icon {
      font-size: 28px;
      color: #667eea;
    }

    h3 {
      margin: 0;
      font-size: 18px;
      color: #303133;
      font-weight: 600;
    }
  }

  .get-suggestion-btn {
    width: 100%;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
  }

  .suggestions-content {
    flex: 1;
    overflow-y: auto;

    .suggestion-list {
      .suggestion-item {
        display: flex;
        gap: 12px;
        margin-bottom: 12px;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;
        transition: all 0.3s ease;

        &:hover {
          background: #e9ecef;
          transform: translateX(4px);
        }

        .item-number {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 600;
          flex-shrink: 0;
        }

        .item-content {
          flex: 1;
          font-size: 14px;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }
}

// 动画
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
}

// 滚动条样式
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;

  &:hover {
    background: #a8a8a8;
  }
}
</style>