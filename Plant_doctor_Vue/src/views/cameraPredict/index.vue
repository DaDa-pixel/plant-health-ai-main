<template>
  <div class="camera-predict-container">
    <div class="camera-wrapper">
      <!-- 左侧：摄像头区域 -->
      <div class="camera-section">
        <el-card shadow="hover" class="camera-card">
          <div class="camera-header">
            <div class="header-left">
              <el-icon class="camera-icon"><Camera /></el-icon>
              <span class="camera-title">实时视频检测</span>
            </div>
            <div class="camera-controls">
              <el-button
                  :type="isCameraActive ? 'danger' : 'primary'"
                  @click="toggleCamera"
                  :loading="cameraLoading"
                  class="control-btn"
              >
                <el-icon><VideoCamera v-if="!isCameraActive" /><VideoPause v-else /></el-icon>
                {{ isCameraActive ? '停止检测' : '开启摄像头' }}
              </el-button>
              <el-button
                  type="success"
                  @click="captureAndPredict"
                  :disabled="!isCameraActive || state.predictLoading"
                  :loading="state.predictLoading"
                  class="control-btn"
              >
                <el-icon><Camera /></el-icon>
                拍照检测
              </el-button>
            </div>
          </div>

          <div class="video-container" ref="videoContainerRef">
            <video
                ref="videoRef"
                autoplay
                playsinline
                class="video-stream"
                :class="{ 'video-active': isCameraActive }"
            ></video>
            <canvas ref="canvasRef" style="display: none;"></canvas>
            <div v-if="!isCameraActive && !cameraLoading" class="camera-placeholder">
              <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
              <p>点击"开启摄像头"开始实时检测</p>
              <p class="placeholder-tip">确保摄像头权限已开启</p>
            </div>
            <div v-if="cameraLoading" class="camera-loading">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <p>正在启动摄像头...</p>
            </div>
            <!-- 实时检测框 -->
            <div v-if="isCameraActive && currentFrameResult" class="detection-overlay">
              <div class="detection-tag">
                <span class="disease-name">{{ currentFrameResult.disease_name }}</span>
                <span class="confidence">{{ (currentFrameResult.confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- 置信度阈值滑块 -->
          <div class="threshold-section">
            <div class="threshold-label">
              <el-icon><Setting /></el-icon>
              <span>最小置信度阈值</span>
            </div>
            <el-slider
                v-model="conf"
                :format-tooltip="formatTooltip"
                :disabled="state.predictLoading"
                style="flex: 1; margin: 0 20px;"
            />
            <span class="threshold-value">{{ (conf / 100).toFixed(2) }}</span>
          </div>
        </el-card>
      </div>

      <!-- 右侧：检测结果区域 -->
      <div class="result-section">
        <!-- 预测进度面板 -->
        <transition name="fade-slide">
          <div v-if="state.predictLoading" class="progress-panel">
            <div class="progress-panel-inner">
              <div class="progress-header">
                <div class="icon-wrapper">
                  <el-icon class="pulse-icon"><Loading /></el-icon>
                </div>
                <span class="progress-title">{{ progressTitle }}</span>
                <span class="progress-time">{{ elapsedTime }}s</span>
              </div>
              <div class="progress-bar-wrapper">
                <el-progress
                    :percentage="progressPercent"
                    :stroke-width="6"
                    :color="progressColor"
                    :show-text="false"
                />
              </div>
              <div class="progress-steps">
                <div
                    v-for="(step, index) in progressSteps"
                    :key="index"
                    :class="['step-item', step.status]"
                >
                  <el-icon v-if="step.status === 'completed'" class="step-icon"><CircleCheckFilled /></el-icon>
                  <el-icon v-else-if="step.status === 'active'" class="step-icon rotating"><Loading /></el-icon>
                  <div v-else class="step-icon pending-dot"></div>
                  <span class="step-label">{{ step.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <!-- 热力图结果 -->
        <el-card shadow="hover" class="result-card heatmap-card">
          <div class="result-header">
            <el-icon><Picture /></el-icon>
            <span>热力图分析</span>
          </div>
          <div class="heatmap-container">
            <img
                v-if="predictedImageUrl"
                :src="predictedImageUrl"
                class="heatmap-image"
                alt="病害热力图"
            />
            <div v-else class="heatmap-placeholder">
              <el-icon><Picture /></el-icon>
              <span>拍照后将显示病害热力图</span>
            </div>
          </div>
        </el-card>

        <!-- 识别结果 -->
        <el-card shadow="hover" class="result-card" v-if="state.predictionResult.label">
          <div class="result-header">
            <el-icon><Search /></el-icon>
            <span>识别结果</span>
          </div>
          <div class="detection-result">
            <div class="result-item">
              <span class="result-label">病害名称</span>
              <span class="result-value disease-name">{{ state.predictionResult.label }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">置信度</span>
              <span class="result-value confidence-value" :style="{ color: getConfidenceColor(state.predictionResult.confidenceValue) }">
                {{ state.predictionResult.confidence }}
              </span>
            </div>
            <div class="result-item">
              <span class="result-label">可靠性</span>
              <el-tag :type="isReliable ? 'success' : 'warning'" size="default">
                {{ isReliable ? '可靠' : '较低' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 防治建议 -->
        <el-card shadow="hover" class="result-card advice-card" v-if="state.knowledgeAdvice">
          <div class="result-header">
            <el-icon><Document /></el-icon>
            <span>防治建议</span>
          </div>
          <div class="advice-content" v-html="formatAdvice(state.knowledgeAdvice)"></div>
        </el-card>

        <!-- 智能医生对话 -->
        <el-card shadow="hover" class="result-card doctor-card">
          <div class="result-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>🩺 智能医生</span>
          </div>
          <div class="chat-container">
            <div class="chat-messages" ref="chatMessagesRef">
              <div v-for="(msg, index) in state.chatMessages" :key="index" :class="['message', msg.role]">
                <div class="message-content">{{ msg.content }}</div>
              </div>
              <div v-if="state.doctorTyping" class="message doctor">
                <div class="message-content typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
            <div class="chat-input">
              <el-input
                  v-model="state.userQuestion"
                  placeholder="向医生提问..."
                  @keyup.enter="sendToDoctor"
                  :disabled="!state.predictionResult.label"
              >
                <template #append>
                  <el-button @click="sendToDoctor" :disabled="!state.userQuestion || !state.predictionResult.label">
                    <el-icon><Promotion /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, nextTick, computed, onUnmounted, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import {
  Camera, VideoCamera, VideoPause, Loading, Setting, Picture,
  Search, Document, ChatDotRound, Promotion, CircleCheckFilled
} from '@element-plus/icons-vue';

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

// 摄像头相关
const videoRef = ref(null);
const canvasRef = ref(null);
const videoContainerRef = ref(null);
const isCameraActive = ref(false);
const cameraLoading = ref(false);
const conf = ref(50);
const predictedImageUrl = ref('');
const isReliable = ref(false);
const chatMessagesRef = ref(null);
const currentFrameResult = ref(null);

// 进度动画相关
const startTime = ref(0);
const elapsedTime = ref('0.0');
let timerInterval = null;
let stepTimers = [];

const progressSteps = ref([
  { label: '图像预处理', desc: '图像尺寸调整、归一化处理', status: 'pending' },
  { label: '模型推理', desc: 'AI神经网络分析病害特征', status: 'pending' },
  { label: '生成热力图', desc: 'Grad-CAM 可视化关注区域', status: 'pending' },
  { label: '检索知识库', desc: '匹配防治建议与专家知识', status: 'pending' },
]);

const state = reactive({
  predictLoading: false,
  predictionResult: {
    label: '',
    confidence: '',
    confidenceValue: 0,
  },
  knowledgeAdvice: '',
  chatMessages: [],
  userQuestion: '',
  doctorTyping: false,
});

const progressPercent = computed(() => {
  const completedCount = progressSteps.value.filter(s => s.status === 'completed').length;
  const activeExists = progressSteps.value.some(s => s.status === 'active') ? 0.5 : 0;
  return Math.min(((completedCount + activeExists) / progressSteps.value.length) * 100, 100);
});

const progressColor = computed(() => {
  if (progressPercent.value >= 80) return '#67C23A';
  if (progressPercent.value >= 40) return '#E6A23C';
  return '#409EFF';
});

const progressTitle = computed(() => {
  const activeStep = progressSteps.value.find(s => s.status === 'active');
  if (activeStep) return activeStep.label;
  return '准备就绪';
});

const formatTooltip = (val) => {
  return (val / 100).toFixed(2);
};

const startProgressAnimation = () => {
  progressSteps.value.forEach(step => step.status = 'pending');
  startTime.value = Date.now();
  elapsedTime.value = '0.0';

  if (progressSteps.value.length > 0) {
    progressSteps.value[0].status = 'active';
  }

  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    if (state.predictLoading) {
      const elapsed = (Date.now() - startTime.value) / 1000;
      elapsedTime.value = elapsed.toFixed(1);
    }
  }, 100);

  const stepDelays = [1200, 2400, 3600, 4800];
  stepDelays.forEach((delay, index) => {
    const timer = setTimeout(() => {
      if (state.predictLoading) {
        if (index >= 0 && progressSteps.value[index]) {
          progressSteps.value[index].status = 'completed';
        }
        if (index + 1 < progressSteps.value.length) {
          progressSteps.value[index + 1].status = 'active';
        }
      }
    }, delay);
    stepTimers.push(timer);
  });
};

const stopProgressAnimation = () => {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  stepTimers.forEach(timer => clearTimeout(timer));
  stepTimers = [];
  progressSteps.value.forEach(step => step.status = 'completed');
};

// 开启/关闭摄像头
const toggleCamera = async () => {
  if (isCameraActive.value) {
    stopCamera();
  } else {
    await startCamera();
  }
};

const startCamera = async () => {
  cameraLoading.value = true;
  try {
    const constraints = {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
      }
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      isCameraActive.value = true;
      ElMessage.success('摄像头已开启');
    }
  } catch (error) {
    console.error('摄像头开启失败:', error);
    if (error.name === 'NotAllowedError') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问');
    } else if (error.name === 'NotFoundError') {
      ElMessage.error('未检测到摄像头设备');
    } else if (error.name === 'NotReadableError') {
      ElMessage.error('摄像头被其他应用占用');
    } else {
      ElMessage.error('摄像头启动失败：' + error.message);
    }
  } finally {
    cameraLoading.value = false;
  }
};

const stopCamera = () => {
  if (videoRef.value && videoRef.value.srcObject) {
    const tracks = videoRef.value.srcObject.getTracks();
    tracks.forEach(track => track.stop());
    videoRef.value.srcObject = null;
    isCameraActive.value = false;
    currentFrameResult.value = null;
    ElMessage.info('摄像头已关闭');
  }
};

// 拍照并预测
const captureAndPredict = async () => {
  if (!videoRef.value || !isCameraActive.value) {
    ElMessage.warning('请先开启摄像头');
    return;
  }

  const canvas = canvasRef.value;
  const video = videoRef.value;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(async (blob) => {
    await predictImage(blob);
  }, 'image/jpeg', 0.8);
};

// 预测图片
const predictImage = async (imageBlob) => {
  if (!imageBlob) {
    ElMessage.error('图片捕获失败');
    return;
  }

  state.predictLoading = true;
  startProgressAnimation();

  const formData = new FormData();
  formData.append('image', imageBlob, 'camera_capture.jpg');
  formData.append('conf', (conf.value / 100).toFixed(2));
  formData.append('generate_heatmap', 'true');

  try {
    // 直接调用Flask服务（因为需要上传文件）
    const response = await fetch('/flask/predict', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    console.log('Flask响应数据:', data);

    if (response.ok && data.success) {
      state.predictionResult.label = data.disease_name || '未知病害';
      const confidencePercent = (data.confidence * 100).toFixed(2);
      state.predictionResult.confidence = confidencePercent + '%';
      state.predictionResult.confidenceValue = data.confidence;
      isReliable.value = data.is_reliable || false;
      currentFrameResult.value = data;

      if (data.heatmap_base64) {
        console.log('热力图数据长度:', data.heatmap_base64.length);
        predictedImageUrl.value = data.heatmap_base64;

        // 确保图片加载完成后打印尺寸
        setTimeout(() => {
          const imgElement = document.querySelector('.heatmap-image');
          if (imgElement) {
            console.log('热力图实际显示尺寸:', {
              width: imgElement.clientWidth,
              height: imgElement.clientHeight,
              naturalWidth: imgElement.naturalWidth,
              naturalHeight: imgElement.naturalHeight
            });
          }
        }, 100);
      } else {
        console.warn('未收到热力图数据');
      }

      if (data.advice) {
        state.knowledgeAdvice = data.advice;
        const initialMessage = `您好！我是智能植物医生 🩺\n\n**诊断结果：**${data.disease_name}\n**置信度：**${confidencePercent}%\n\n请问您想了解什么？`;
        state.chatMessages = [{ role: 'doctor', content: initialMessage }];
      }

      ElMessage.success('检测完成！');

      // 保存摄像检测记录到数据库（异步执行，不影响主流程）
      saveCameraRecord(data).catch(err => {
        console.error('保存摄像记录失败:', err);
      });
    } else {
      ElMessage.error(data.error || '检测失败');
    }
  } catch (error) {
    console.error('预测失败:', error);
    ElMessage.error(`检测失败：${error.message || '网络请求失败'}`);
  } finally {
    stopProgressAnimation();
    setTimeout(() => {
      state.predictLoading = false;
    }, 500);
  }
};

// 发送对话消息
const sendToDoctor = async () => {
  if (!state.userQuestion.trim() || !state.predictionResult.label) return;

  const question = state.userQuestion.trim();
  state.userQuestion = '';
  state.chatMessages.push({ role: 'user', content: question });
  state.doctorTyping = true;
  scrollToBottom();

  try {
    // 通过Spring Boot代理调用（JSON格式可以正常代理）
    const response = await request.post('/api/flask/chat', {
      message: question,
      disease_context: state.predictionResult.label
    });

    if (response.code === 0) {
      const data = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;

      if (data.success && data.response) {
        state.chatMessages.push({ role: 'doctor', content: data.response });
      } else {
        throw new Error(data.error || '对话失败');
      }
    } else {
      throw new Error(response.msg || '对话失败');
    }
  } catch (error) {
    console.error('询问医生出错:', error);

    // 降级方案：直接调用Flask
    try {
      const fallbackResponse = await fetch('/flask/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: question,
          disease_context: state.predictionResult.label
        })
      });

      const result = await fallbackResponse.json();
      if (result.success && result.response) {
        state.chatMessages.push({ role: 'doctor', content: result.response });
      } else {
        throw new Error(result.error || '对话失败');
      }
    } catch (fallbackError) {
      state.chatMessages.push({
        role: 'doctor',
        content: '抱歉，医生暂时无法回答，请确保以下服务已启动：\n1. Flask服务: python flask_api.py\n2. Ollama服务: ollama serve'
      });
    }
  } finally {
    state.doctorTyping = false;
    scrollToBottom();
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight;
    }
  });
};

const formatAdvice = (advice) => {
  if (!advice) return '';
  return advice.replace(/\n/g, '<br/>');
};

const getConfidenceColor = (value) => {
  if (value >= 0.8) return '#67C23A';
  if (value >= 0.5) return '#E6A23C';
  return '#F56C6C';
};

// 保存摄像检测记录
const saveCameraRecord = async (predictionData) => {
  try {
    if (!predictionData || !predictionData.disease_name) {
      console.warn('预测数据不完整，跳过保存记录');
      return;
    }

    const now = new Date();
    const timeStr = now.getFullYear() + '-' +
                   String(now.getMonth() + 1).padStart(2, '0') + '-' +
                   String(now.getDate()).padStart(2, '0') + ' ' +
                   String(now.getHours()).padStart(2, '0') + ':' +
                   String(now.getMinutes()).padStart(2, '0') + ':' +
                   String(now.getSeconds()).padStart(2, '0');

    const recordData = {
      weight: 'default',
      conf: conf.value ? (conf.value / 100).toFixed(2) : '0.5',
      username: userInfos.value.userNickname || userInfos.value.userName || 'unknown',
      startTime: timeStr,
      outVideo: '',
      kind: extractCropType(predictionData.disease_name)
    };

    const res = await request.post('/api/cameraRecords', recordData);
    if (res.code === 0) {
      console.log('摄像检测记录保存成功');
    } else {
      console.error('保存摄像记录失败:', res.msg);
    }
  } catch (error) {
    console.error('保存摄像记录异常:', error);
  }
};

// 从病害名称中提取作物类型
const extractCropType = (diseaseName) => {
  const cropMap = {
    '大豆': '大豆',
    '番茄': '番茄',
    '玉米': '玉米',
    '水稻': '水稻',
    '小麦': '小麦',
    '马铃薯': '马铃薯',
    '棉花': '棉花',
    '苹果': '苹果',
    '葡萄': '葡萄',
    '草莓': '草莓',
    '花生': '花生',
    '柑橘': '柑橘',
    'Orange': '柑橘',
    'Wheat': '小麦',
    'Corn': '玉米',
    'Rice': '水稻',
    'Tomato': '番茄',
    'Potato': '马铃薯',
    'Cotton': '棉花',
    'Apple': '苹果',
    'Grape': '葡萄',
    'Strawberry': '草莓',
    'Soybean': '大豆',
    'Peanut': '花生'
  };

  for (const [key, value] of Object.entries(cropMap)) {
    if (diseaseName.includes(key)) {
      return value;
    }
  }

  return '未知作物';
};

onUnmounted(() => {
  stopCamera();
  if (timerInterval) clearInterval(timerInterval);
  stepTimers.forEach(timer => clearTimeout(timer));
});
</script>

<style scoped lang="scss">
.camera-predict-container {
  width: 100%;
  height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  padding: 20px;
  overflow: hidden;

  .camera-wrapper {
    display: flex;
    gap: 20px;
    height: 100%;
  }
}

// 左侧摄像头区域
.camera-section {
  flex: 1.3;
  min-width: 0;
  height: 100%;

  .camera-card {
    height: 100%;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 20px;
      overflow: hidden;
    }

    .camera-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-shrink: 0;
      flex-wrap: wrap;
      gap: 12px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 10px;

        .camera-icon {
          font-size: 24px;
          color: #409EFF;
        }

        .camera-title {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }
      }

      .camera-controls {
        display: flex;
        gap: 12px;

        .control-btn {
          padding: 10px 20px;
        }
      }
    }

    .video-container {
      flex: 1;
      background: #1a1a2e;
      border-radius: 16px;
      overflow: hidden;
      position: relative;
      min-height: 0;

      .video-stream {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: none;

        &.video-active {
          display: block;
        }
      }

      .camera-placeholder {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: #fff;

        .placeholder-icon {
          font-size: 64px;
          margin-bottom: 16px;
        }

        p {
          margin: 8px 0;
          font-size: 14px;
        }

        .placeholder-tip {
          font-size: 12px;
          opacity: 0.7;
        }
      }

      .camera-loading {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: #fff;

        .loading-icon {
          font-size: 48px;
          animation: rotate 1s linear infinite;
          margin-bottom: 16px;
        }
      }

      .detection-overlay {
        position: absolute;
        bottom: 20px;
        left: 20px;
        right: 20px;
        pointer-events: none;

        .detection-tag {
          display: inline-block;
          background: rgba(64, 158, 255, 0.9);
          backdrop-filter: blur(10px);
          padding: 8px 16px;
          border-radius: 40px;
          color: white;
          font-size: 14px;
          font-weight: 600;

          .disease-name {
            margin-right: 12px;
          }

          .confidence {
            background: rgba(255, 255, 255, 0.2);
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 12px;
          }
        }
      }
    }

    .threshold-section {
      display: flex;
      align-items: center;
      margin-top: 16px;
      padding: 12px 0;
      border-top: 1px solid #ebeef5;
      flex-shrink: 0;

      .threshold-label {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #606266;
        font-size: 14px;
      }

      .threshold-value {
        font-weight: 600;
        color: #409EFF;
        min-width: 45px;
      }
    }
  }
}

// 右侧结果区域
.result-section {
  flex: 0.9;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 400px;
  max-width: 600px;
  padding-right: 8px;

  // 自定义滚动条样式
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
  }

  .progress-panel {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 16px;
    padding: 20px;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

    .progress-panel-inner {
      .progress-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;

        .icon-wrapper {
          width: 40px;
          height: 40px;
          background: rgba(64, 158, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;

          .pulse-icon {
            font-size: 24px;
            color: #409EFF;
            animation: pulse 1.5s ease-in-out infinite;
          }
        }

        .progress-title {
          flex: 1;
          font-size: 16px;
          font-weight: 600;
          color: white;
        }

        .progress-time {
          font-size: 20px;
          font-weight: 700;
          color: #409EFF;
          font-family: 'Courier New', monospace;
        }
      }

      .progress-bar-wrapper {
        margin-bottom: 16px;
      }

      .progress-steps {
        display: flex;
        justify-content: space-between;
        gap: 8px;

        .step-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          flex: 1;

          .step-icon {
            font-size: 18px;
          }

          .step-label {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
            text-align: center;
            line-height: 1.2;
          }

          &.active {
            .step-icon {
              color: #409EFF;
            }
            .step-label {
              color: #409EFF;
            }
          }

          &.completed {
            .step-icon {
              color: #67C23A;
            }
            .step-label {
              color: #67C23A;
            }
          }
        }
      }
    }
  }

  .result-card {
    border-radius: 16px;
    overflow: visible;
    flex-shrink: 0;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    :deep(.el-card__body) {
      padding: 16px 20px;
    }

    .result-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding-bottom: 12px;
      margin-bottom: 12px;
      border-bottom: 2px solid #f0f0f0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;

      .el-icon {
        font-size: 18px;
        color: #409EFF;
      }
    }

    // 热力图卡片
    &.heatmap-card {
      :deep(.el-card__body) {
        padding: 16px;
        display: flex;
        flex-direction: column;
      }

      .result-header {
        margin-bottom: 12px;
        flex-shrink: 0;
      }

      .heatmap-container {
        width: 100%;
        flex: 1;
        min-height: 240px;
        max-height: 320px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        padding: 0;

        .heatmap-image {
          width: 100%;
          height: 100%;
          max-width: 100%;
          max-height: 100%;
          object-fit: contain;
          display: block;
          transition: transform 0.3s ease;
          background: white;

          &:hover {
            transform: scale(1.02);
          }
        }

        .heatmap-placeholder {
          text-align: center;
          color: #909399;
          padding: 40px 20px;
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 240px;

          .el-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.4;
          }

          span {
            display: block;
            font-size: 14px;
            line-height: 1.6;
          }
        }
      }
    }

    // 识别结果卡片
    &.detection-card {
      .detection-result {
        .result-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px dashed #f0f0f0;

          &:last-child {
            border-bottom: none;
          }

          .result-label {
            color: #909399;
            font-size: 14px;
            font-weight: 500;
          }

          .result-value {
            font-weight: 600;

            &.disease-name {
              font-size: 16px;
              color: #303133;
            }

            &.confidence-value {
              font-size: 20px;
              font-family: 'Courier New', monospace;
            }
          }
        }
      }
    }

    // 防治建议卡片
    &.advice-card {
      .advice-content {
        max-height: 180px;
        overflow-y: auto;
        font-size: 13px;
        line-height: 1.8;
        color: #606266;
        padding: 8px;
        background: #fafafa;
        border-radius: 8px;

        // 内部滚动条样式
        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 3px;

          &:hover {
            background: #a1a1a1;
          }
        }
      }
    }

    // 智能医生卡片
    &.doctor-card {
      flex: 1;
      min-height: 350px;
      max-height: 450px;
      display: flex;
      flex-direction: column;

      :deep(.el-card__body) {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 16px;
        overflow: hidden;
      }

      .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        flex: 1;

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
          background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
          border-radius: 12px;
          margin-bottom: 12px;

          // 聊天区域滚动条样式
          &::-webkit-scrollbar {
            width: 6px;
          }

          &::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
          }

          &::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;

            &:hover {
              background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }
          }

          .message {
            margin-bottom: 12px;
            animation: messageSlideIn 0.3s ease;

            &.user {
              text-align: right;

              .message-content {
                background: linear-gradient(135deg, #409EFF 0%, #36a2f1 100%);
                color: white;
                border-radius: 16px 16px 4px 16px;
                display: inline-block;
                max-width: 85%;
                padding: 10px 14px;
                font-size: 13px;
                line-height: 1.6;
                box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
              }
            }

            &.doctor {
              .message-content {
                background: white;
                border-radius: 16px 16px 16px 4px;
                display: inline-block;
                max-width: 85%;
                padding: 10px 14px;
                font-size: 13px;
                line-height: 1.6;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                white-space: pre-wrap;
                color: #303133;

                &.typing {
                  padding: 12px 16px;

                  span {
                    display: inline-block;
                    width: 7px;
                    height: 7px;
                    border-radius: 50%;
                    background: #909399;
                    margin: 0 2px;
                    animation: typing 1.4s infinite;

                    &:nth-child(2) {
                      animation-delay: 0.2s;
                    }

                    &:nth-child(3) {
                      animation-delay: 0.4s;
                    }
                  }
                }
              }
            }
          }
        }

        .chat-input {
          flex-shrink: 0;

          :deep(.el-input-group__append) {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;

            .el-button {
              color: white;

              &:hover {
                opacity: 0.9;
              }
            }
          }

          :deep(.el-input__wrapper) {
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          }
        }
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.1); }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.rotating {
  animation: rotate 1s linear infinite;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ===== 手机端适配（≤768px） ===== */
@media screen and (max-width: 768px) {
  .camera-predict-container {
    height: auto;
    padding: 12px;
    overflow: visible;
  }

  .camera-predict-container .camera-wrapper {
    flex-direction: column;
    height: auto;
    gap: 12px;
  }

  .camera-section {
    flex: none;
    width: 100%;
    height: auto;
  }

  .camera-section .camera-card {
    border-radius: 14px;
  }

  .camera-section .camera-card :deep(.el-card__body) {
    padding: 12px;
  }

  .camera-section .camera-card .camera-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .camera-section .camera-card .camera-header .camera-controls {
    width: 100%;
    flex-direction: column;
    gap: 8px;
  }

  .camera-section .camera-card .camera-header .camera-controls .control-btn {
    width: 100%;
    justify-content: center;
  }

  .camera-section .camera-card .video-container {
    min-height: 240px;
    max-height: 50vh;
  }

  .camera-section .camera-card .threshold-section {
    flex-wrap: wrap;
    gap: 8px;
  }

  .camera-section .camera-card .threshold-section .el-slider {
    margin: 0 !important;
    min-width: 100%;
    order: 3;
  }

  .result-section {
    flex: none;
    width: 100%;
    min-width: unset;
    max-width: unset;
    overflow-y: visible;
    padding-right: 0;
  }

  .result-section .result-card {
    margin-bottom: 0;
  }

  .result-section .progress-panel {
    padding: 14px;
  }

  .result-section .progress-panel .progress-panel-inner .progress-header .progress-title {
    font-size: 14px;
  }

  .result-section .progress-panel .progress-panel-inner .progress-steps {
    flex-wrap: wrap;
  }

  .result-section .progress-panel .progress-panel-inner .progress-steps .step-item {
    min-width: 45%;
    flex: none;
  }

  .result-section .doctor-card {
    min-height: 300px;
    max-height: 400px;
  }

  .result-section .progress-panel .progress-panel-inner .progress-steps .step-item .step-label {
    font-size: 10px;
  }
}
</style>