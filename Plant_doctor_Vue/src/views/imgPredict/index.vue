<template>
  <div class="system-predict-container layout-padding">
    <div class="system-predict-padding layout-padding-auto layout-padding-view">
      <div class="header">
        <div class="conf" style="display: flex; flex-direction: row; align-items: center;">
          <div style="font-size: 14px;margin-right: 20px;color: #909399;">
            设置最小置信度阈值
          </div>
          <el-slider v-model="conf" :format-tooltip="formatTooltip" style="width: 300px;" />
        </div>
        <div class="button-section" style="margin-left: auto">
          <el-button
              type="primary"
              @click="upData"
              class="predict-button"
              :loading="state.predictLoading"
              :disabled="state.predictLoading"
              size="large"
          >
            <el-icon v-if="!state.predictLoading"><Promotion /></el-icon>
            <el-icon v-else><Loading /></el-icon>
            {{ state.predictLoading ? '诊断中...' : '开始检测' }}
          </el-button>
        </div>
      </div>

      <!-- 预测进度面板 -->
      <transition name="fade-slide">
        <div v-if="state.predictLoading || showProgressPanel" class="progress-panel">
          <div class="progress-panel-inner">
            <div class="progress-header">
              <div class="header-left">
                <div class="icon-wrapper">
                  <el-icon class="pulse-icon"><Loading /></el-icon>
                </div>
                <div class="header-info">
                  <span class="progress-title">{{ progressTitle }}</span>
                  <span class="progress-subtitle">AI 智能诊断中</span>
                </div>
              </div>
              <div class="progress-time-wrapper">
                <span class="progress-time-label">耗时</span>
                <span class="progress-time-value">{{ elapsedTime }}<span class="time-unit">s</span></span>
              </div>
            </div>

            <div class="steps-container">
              <div
                  v-for="(step, index) in progressSteps"
                  :key="index"
                  :class="['step-item', step.status]"
              >
                <div class="step-indicator">
                  <div class="step-dot">
                    <el-icon v-if="step.status === 'completed'" class="check-icon"><CircleCheckFilled /></el-icon>
                    <el-icon v-else-if="step.status === 'active'" class="loading-icon rotating"><Loading /></el-icon>
                    <div v-else class="pending-dot"></div>
                  </div>
                  <div v-if="index < progressSteps.length - 1" class="step-line" :class="{ active: step.status === 'completed' || progressSteps[index + 1]?.status !== 'pending' }"></div>
                </div>
                <div class="step-content">
                  <div class="step-label">{{ step.label }}</div>
                  <div class="step-desc">{{ step.desc }}</div>
                </div>
              </div>
            </div>

            <div class="progress-footer">
              <div class="progress-bar-wrapper">
                <el-progress
                    :percentage="progressPercent"
                    :stroke-width="6"
                    :color="progressColor"
                    :show-text="false"
                />
              </div>
              <div class="progress-percent">{{ Math.floor(progressPercent) }}%</div>
            </div>
          </div>
        </div>
      </transition>

      <!-- 图片显示区域 -->
      <el-row :gutter="20" class="image-display">
        <el-col :span="8">
          <el-card shadow="hover" class="card">
            <div class="image-title">📷 原图片</div>
            <el-upload
                v-model="state.img"
                ref="uploadFile"
                class="avatar-uploader"
                action="/api/files/upload"
                :show-file-list="false"
                :on-success="handleAvatarSuccessone"
                :disabled="state.predictLoading"
            >
              <el-image v-if="imageUrl" :src="imageUrl" class="preview-image" fit="contain" />
              <div v-else class="uploader-content">
                <el-icon class="upload-icon"><Plus /></el-icon>
                <div class="upload-text">点击上传图片</div>
                <div class="upload-hint">支持 JPG、PNG 格式</div>
              </div>
            </el-upload>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" class="card">
            <div class="image-title">🔥 预测结果</div>
            <el-image
                v-if="predictedImageUrl"
                :src="predictedImageUrl"
                class="preview-image"
                fit="contain"
            />
            <div v-else class="placeholder">
              <el-icon><Picture /></el-icon>
              <span>预测后将在此显示热力图</span>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" class="card doctor-card">
            <div class="image-title">🩺 智能医生</div>
            <div class="chat-container">
              <div class="chat-messages" ref="chatMessagesRef">
                <div v-for="(msg, index) in state.chatMessages" :key="index"
                     :class="['message', msg.role]">
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
        </el-col>
      </el-row>

      <!-- 底部预测结果 -->
      <el-row class="result-section">
        <el-col :span="24">
          <el-card>
            <div class="bottom" v-if="state.predictionResult.label">
              <div class="bottom-row">
                <!-- 左侧：识别结果 + 症状/病因 -->
                <div class="bottom-left">
                  <!-- 紧凑的指标行 -->
                  <div class="bottom-indicators">
                    <div class="indicator-item">
                      <div class="indicator-label">🔍 识别结果</div>
                      <div class="indicator-value disease-name">{{ state.predictionResult.label }}</div>
                    </div>
                    <div class="indicator-divider"></div>
                    <div class="indicator-item">
                      <div class="indicator-label">📊 预测概率</div>
                      <div class="indicator-value probability" :style="{ color: getConfidenceColor(state.predictionResult.confidenceValue) }">
                        {{ state.predictionResult.confidence }}
                      </div>
                    </div>
                    <div class="indicator-divider"></div>
                    <div class="indicator-item">
                      <div class="indicator-label">✅ 可靠性</div>
                      <div class="indicator-value">
                        <el-tag :type="isReliable ? 'success' : 'warning'" size="small" effect="dark">
                          {{ isReliable ? '可靠' : '较低' }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                  <!-- 症状和病因 -->
                  <div class="symptoms-section">
                    <div class="symptoms-title">🌱 症状 &amp; 发病原因</div>
                    <div class="symptoms-content" v-html="symptomsHtml"></div>
                  </div>
                </div>
                <!-- 右侧：知识库建议（防治建议） -->
                <div class="bottom-right">
                  <div class="result-title">
                    📚 知识库建议
                    <span class="source-tag" v-if="knowledgeSource">📖 {{ knowledgeSource }}</span>
                  </div>
                  <div class="treatment-content" v-html="treatmentHtml"></div>
                </div>
              </div>
            </div>
            <div class="bottom placeholder" v-else>
              <div style="width: 100%; text-align: center; color: #909399;">
                <el-icon style="margin-right: 8px; vertical-align: middle;"><Picture /></el-icon>
                <span>预测结果将在这里显示</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts" name="imgPredict">
import { reactive, ref, nextTick, computed, onUnmounted } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { Plus, Picture, Promotion, Loading, CircleCheckFilled } from '@element-plus/icons-vue';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';

const imageUrl = ref('');
const conf = ref(50);
const uploadFile = ref<UploadInstance>();
const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);
const predictedImageUrl = ref('');
const isReliable = ref(false);
const chatMessagesRef = ref<HTMLElement | null>(null);
const showProgressPanel = ref(false);
const startTime = ref<number>(0);
const elapsedTime = ref<string>('0.0');
let timerInterval: any = null;
let stepTimers: any[] = [];

interface ChatMessage {
  role: 'user' | 'doctor';
  content: string;
}

interface ProgressStep {
  label: string;
  desc: string;
  status: 'pending' | 'active' | 'completed';
}

const state = reactive({
  img: '',
  predictionResult: {
    label: '',
    confidence: '',
    confidenceValue: 0,
    allTime: '',
  },
  form: {
    username: '',
    inputImg: '',
    conf: 0.5,
  },
  knowledgeAdvice: '',
  predictLoading: false,
  chatMessages: [] as ChatMessage[],
  userQuestion: '',
  doctorTyping: false,
});

const progressSteps = ref<ProgressStep[]>([
  { label: '图像预处理', desc: '图像尺寸调整、归一化处理', status: 'pending' },
  { label: '模型推理', desc: 'AI神经网络分析病害特征', status: 'pending' },
  { label: '生成热力图', desc: 'Grad-CAM 可视化关注区域', status: 'pending' },
  { label: '检索知识库', desc: '匹配防治建议与专家知识', status: 'pending' },
]);

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
  if (progressSteps.value.every(s => s.status === 'completed')) return '诊断完成';
  return '准备就绪';
});

const formatTooltip = (val: number) => {
  return (val / 100).toFixed(2);
};

const resetProgressSteps = () => {
  progressSteps.value.forEach(step => {
    step.status = 'pending';
  });
};

const startProgressAnimation = () => {
  resetProgressSteps();
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

  progressSteps.value.forEach(step => {
    step.status = 'completed';
  });

  const finalElapsed = (Date.now() - startTime.value) / 1000;
  elapsedTime.value = finalElapsed.toFixed(1);
};

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
  if (response.code === 0) {
    imageUrl.value = URL.createObjectURL(uploadFile.raw!);
    state.img = response.data;
    ElMessage.success('图片上传成功');
  } else {
    ElMessage.error('图片上传失败');
  }
};

const upData = () => {
  if (!state.img) {
    ElMessage.warning('请先上传图片');
    return;
  }

  state.predictLoading = true;
  showProgressPanel.value = true;
  state.form.conf = conf.value / 100;
  state.form.username = userInfos.value.userName;
  state.form.inputImg = state.img;

  state.predictionResult.label = '';
  state.knowledgeAdvice = '';
  predictedImageUrl.value = '';

  startProgressAnimation();

  request.post('/api/flask/predict', state.form).then((res) => {
    if (res.code === 0) {
      try {
        const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;

        if (data.success) {
          state.predictionResult.label = data.disease_name || '未知病害';
          const confidencePercent = (data.confidence * 100).toFixed(2);
          state.predictionResult.confidence = confidencePercent + '%';
          state.predictionResult.confidenceValue = data.confidence;
          isReliable.value = data.is_reliable || false;

          if (data.heatmap_base64) {
            predictedImageUrl.value = data.heatmap_base64;
          }

          if (data.advice) {
            state.knowledgeAdvice = data.advice;
            const initialMessage = `您好！我是智能植物医生 🩺\n\n**诊断结果：**${data.disease_name}\n**置信度：**${(data.confidence * 100).toFixed(2)}%\n\n我已经从知识库中获取了详细的防治建议（见下方"知识库建议"栏）。\n\n您可以问我任何问题，例如：\n• 这个病害的具体症状是什么？\n• 应该如何防治？\n• 有什么预防措施吗？\n\n请问您想了解什么？`;

            state.chatMessages = [{
              role: 'doctor',
              content: initialMessage
            }];
          }

          ElMessage.success('预测成功！');

          saveImageRecord(data).catch(err => {
            console.error('保存图片记录失败:', err);
          });
        } else {
          ElMessage.error(data.error || '预测失败');
        }
      } catch (error) {
        console.error('解析结果时出错:', error);
        ElMessage.error('预测结果解析失败');
      }
    } else {
      ElMessage.error(res.msg || '预测失败');
    }

    stopProgressAnimation();
    setTimeout(() => {
      state.predictLoading = false;
      showProgressPanel.value = false;
    }, 500);
  }).catch((error) => {
    console.error('预测请求失败:', error);
    ElMessage.error('预测请求失败，请检查网络连接');

    stopProgressAnimation();
    setTimeout(() => {
      state.predictLoading = false;
      showProgressPanel.value = false;
    }, 500);
  });
};

const sendToDoctor = async () => {
  if (!state.userQuestion.trim() || !state.predictionResult.label) return;

  const question = state.userQuestion.trim();
  state.userQuestion = '';

  state.chatMessages.push({
    role: 'user',
    content: question
  });

  state.doctorTyping = true;
  scrollToBottom();

  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: question,
        disease_context: state.predictionResult.label
      })
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const result = await response.json();

    if (result.success && result.response) {
      state.chatMessages.push({
        role: 'doctor',
        content: result.response
      });
    } else {
      throw new Error(result.error || '对话失败');
    }
  } catch (error) {
    console.error('询问医生出错:', error);
    state.chatMessages.push({
      role: 'doctor',
      content: '抱歉，医生暂时无法回答，请检查 Flask 服务是否正常运行。'
    });
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

const formatAdvice = (advice: string) => {
  if (!advice) return '';
  return advice
      .replace(/\n/g, '<br/>')
      .replace(/🌱/g, '<span class="emoji">🌱</span>')
      .replace(/🌾/g, '<span class="emoji">🌾</span>')
      .replace(/🧑‍🌾/g, '<span class="emoji">🧑‍🌾</span>')
      .replace(/💊/g, '<span class="emoji">💊</span>')
      .replace(/💡/g, '<span class="emoji">💡</span>')
      .replace(/📚/g, '<span class="emoji">📚</span>');
};

// 将知识库建议拆分为"症状/病因"和"防治建议"两部分
const splitAdvice = (advice: string) => {
  if (!advice) return { symptoms: '', treatment: '' };
  const lines = advice.split('\n');
  const symptomsLines: string[] = [];
  const treatmentLines: string[] = [];
  let currentSection: 'symptoms' | 'treatment' | null = null;
  for (const line of lines) {
    // 先检查防治/建议类（🧑‍🌾 包含 🌾，必须优先匹配）
    if (line.includes('🧑') || line.includes('💊') || line.includes('💡') || line.includes('📚') || line.includes('防治') || line.includes('小贴士')) {
      currentSection = 'treatment';
      treatmentLines.push(line);
    } else if (line.includes('🌱') || line.includes('🌾') || line.includes('症状') || line.includes('病因') || line.includes('发病规律')) {
      currentSection = 'symptoms';
      symptomsLines.push(line);
    } else if (currentSection === 'symptoms') {
      symptomsLines.push(line);
    } else if (currentSection === 'treatment') {
      treatmentLines.push(line);
    }
  }
  return {
    symptoms: symptomsLines.join('\n'),
    treatment: treatmentLines.join('\n')
  };
};

const symptomsHtml = computed(() => {
  const parts = splitAdvice(state.knowledgeAdvice);
  return formatAdvice(parts.symptoms);
});

const treatmentHtml = computed(() => {
  const parts = splitAdvice(state.knowledgeAdvice);
  return formatAdvice(parts.treatment);
});

// 从 advice 文本中提取来源信息
const knowledgeSource = computed(() => {
  if (!state.knowledgeAdvice) return '';
  const firstLine = state.knowledgeAdvice.split('\n')[0];
  const match = firstLine.match(/（来源：([^）]+)）/);
  return match ? match[1] : '';
});

const getConfidenceColor = (value: number) => {
  if (value >= 0.8) return '#67C23A';
  if (value >= 0.5) return '#E6A23C';
  return '#F56C6C';
};

const saveImageRecord = async (predictionData: any) => {
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
      inputImg: state.img,
      outImg: predictedImageUrl.value,
      confidence: JSON.stringify([predictionData.confidence || 0]),
      allTime: elapsedTime.value ? elapsedTime.value + 's' : '0s',
      conf: state.form.conf ? state.form.conf.toString() : '0.5',
      weight: 'default',
      username: userInfos.value.userName || 'unknown',
      startTime: timeStr,
      label: JSON.stringify([predictionData.disease_name]),
      kind: extractCropType(predictionData.disease_name)
    };

    const res = await request.post('/api/imgRecords', recordData);
    if (res.code === 0) {
      console.log('图片检测记录保存成功');
    } else {
      console.error('保存图片记录失败:', res.msg);
    }
  } catch (error) {
    console.error('保存图片记录异常:', error);
  }
};

const extractCropType = (diseaseName: string): string => {
  const cropMap: { [key: string]: string } = {
    '大豆': '大豆', '番茄': '番茄', '玉米': '玉米', '水稻': '水稻',
    '小麦': '小麦', '马铃薯': '马铃薯', '棉花': '棉花', '苹果': '苹果',
    '葡萄': '葡萄', '草莓': '草莓', '花生': '花生', '柑橘': '柑橘',
    'Orange': '柑橘', 'Wheat': '小麦', 'Corn': '玉米', 'Rice': '水稻',
    'Tomato': '番茄', 'Potato': '马铃薯', 'Cotton': '棉花', 'Apple': '苹果',
    'Grape': '葡萄', 'Strawberry': '草莓', 'Soybean': '大豆', 'Peanut': '花生'
  };

  for (const [key, value] of Object.entries(cropMap)) {
    if (diseaseName.includes(key)) {
      return value;
    }
  }
  return '未知作物';
};

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval);
  stepTimers.forEach(timer => clearTimeout(timer));
});
</script>

<style scoped lang="scss">
.system-predict-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  position: relative;

  .system-predict-padding {
    padding: 15px;
    padding-bottom: 0;
    padding-top: 0;
    min-height: calc(100vh - 60px);
    flex: 1;
  }
}

.header {
  width: 100%;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  z-index: 1;
}

// 开始检测按钮 - 放大美化
.predict-button {
  background: linear-gradient(135deg, #409eff 0%, #36a2f1 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35);
  transition: all 0.3s ease;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 40px;
  min-width: 160px;

  .el-icon {
    margin-right: 8px;
    font-size: 18px;
  }

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(64, 158, 255, 0.45);
    background: linear-gradient(135deg, #409eff 0%, #2d8fcf 100%);
  }

  &:active {
    transform: translateY(0);
  }

  &.is-loading {
    background: linear-gradient(135deg, #909399 0%, #76787a 100%);
    box-shadow: none;
  }
}

.progress-panel {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
  z-index: 100;
  position: relative;

  .progress-panel-inner {
    padding: 24px 28px;
  }

  .progress-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      .icon-wrapper {
        width: 48px;
        height: 48px;
        background: rgba(64, 158, 255, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        .pulse-icon {
          font-size: 28px;
          color: #409EFF;
          animation: pulse 1.5s ease-in-out infinite;
        }
      }

      .header-info {
        .progress-title {
          font-size: 20px;
          font-weight: 700;
          color: white;
          display: block;
          margin-bottom: 4px;
        }

        .progress-subtitle {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.6);
        }
      }
    }

    .progress-time-wrapper {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      padding: 8px 16px;
      border-radius: 40px;
      text-align: center;

      .progress-time-label {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
        margin-right: 8px;
      }

      .progress-time-value {
        font-size: 24px;
        font-weight: 700;
        color: #409EFF;
        font-family: 'Courier New', monospace;

        .time-unit {
          font-size: 14px;
          font-weight: 400;
          margin-left: 2px;
        }
      }
    }
  }

  .steps-container {
    margin-bottom: 24px;

    .step-item {
      display: flex;
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .step-indicator {
        position: relative;
        width: 32px;
        margin-right: 16px;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        align-items: center;

        .step-dot {
          width: 32px;
          height: 32px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2;
          transition: all 0.3s ease;

          .check-icon {
            font-size: 20px;
            color: #67C23A;
          }

          .loading-icon {
            font-size: 18px;
            color: #409EFF;
          }

          .pending-dot {
            width: 10px;
            height: 10px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
          }
        }

        .step-line {
          width: 2px;
          height: 40px;
          background: rgba(255, 255, 255, 0.1);
          margin-top: 4px;
          transition: all 0.3s ease;

          &.active {
            background: linear-gradient(180deg, #409EFF 0%, #67C23A 100%);
          }
        }
      }

      .step-content {
        flex: 1;
        padding-bottom: 4px;

        .step-label {
          font-size: 15px;
          font-weight: 600;
          color: white;
          margin-bottom: 4px;
        }

        .step-desc {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.6);
        }
      }

      &.completed {
        .step-label {
          color: #67C23A;
        }
        .step-desc {
          color: rgba(103, 194, 58, 0.7);
        }
        .step-dot {
          background: rgba(103, 194, 58, 0.2);
        }
      }

      &.active {
        .step-label {
          color: #409EFF;
        }
        .step-dot {
          background: rgba(64, 158, 255, 0.2);
          box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
          animation: glow 1.5s ease-in-out infinite;
        }
      }
    }
  }

  .progress-footer {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    .progress-bar-wrapper {
      flex: 1;

      :deep(.el-progress-bar__outer) {
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
      }

      :deep(.el-progress-bar__inner) {
        border-radius: 4px;
        transition: width 0.3s ease;
      }
    }

    .progress-percent {
      font-size: 14px;
      font-weight: 600;
      color: #409EFF;
      min-width: 45px;
      text-align: right;
    }
  }
}

.image-display {
  margin-top: 15px;
  transition: opacity 0.3s ease;

  .card {
    height: 100%;
    background: white;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .image-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 15px;
      padding-bottom: 12px;
      border-bottom: 1px solid #ebeef5;
    }

    .avatar-uploader {
      width: 100%;
      height: 358px;
      border: 2px dashed #d9d9d9;
      border-radius: 12px;
      cursor: pointer;
      overflow: hidden;
      transition: all 0.3s;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #fafafa;

      &:hover {
        border-color: #409EFF;
        background: #f5f9ff;
      }
    }

    .preview-image {
      width: 100%;
      height: 358px;
      object-fit: contain;
    }

    .uploader-content {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      gap: 10px;

      .upload-icon {
        font-size: 48px;
        color: #c0c4cc;
      }

      .upload-text {
        color: #909399;
        font-size: 14px;
      }

      .upload-hint {
        color: #c0c4cc;
        font-size: 12px;
      }
    }

    .placeholder {
      height: 358px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      color: #909399;

      .el-icon {
        font-size: 48px;
      }
    }

    &.doctor-card {
      padding: 0;

      .chat-container {
        height: 358px;
        display: flex;
        flex-direction: column;

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 15px;
          background: #f8f9fa;

          .message {
            margin-bottom: 12px;
            animation: fadeIn 0.3s ease;

            &.user {
              text-align: right;

              .message-content {
                background: #409EFF;
                color: white;
                border-radius: 12px 12px 4px 12px;
                display: inline-block;
                max-width: 85%;
                padding: 10px 14px;
              }
            }

            &.doctor {
              text-align: left;

              .message-content {
                background: white;
                color: #303133;
                border-radius: 12px 12px 12px 4px;
                display: inline-block;
                max-width: 85%;
                padding: 10px 14px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                line-height: 1.6;
                white-space: pre-wrap;

                &.typing {
                  padding: 12px 16px;

                  span {
                    display: inline-block;
                    width: 6px;
                    height: 6px;
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

          &::-webkit-scrollbar {
            width: 6px;
          }

          &::-webkit-scrollbar-thumb {
            background-color: #dcdfe6;
            border-radius: 3px;
          }
        }

        .chat-input {
          padding: 10px;
          background: white;
          border-top: 1px solid #ebeef5;
        }
      }
    }
  }
}

.result-section {
  margin-top: 10px;
  padding: 0;

  :deep(.el-card) {
    background: white;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    margin: 0;

    .el-card__body {
      padding: 0;
    }
  }

  .bottom {
    padding: 20px;
    background: white;
    border-radius: 12px;
    min-height: 140px;

    .bottom-row {
      display: flex;
      gap: 0;

      .bottom-left {
        flex: 0 0 44%;
        display: flex;
        flex-direction: column;
        padding-right: 20px;
        border-right: 1px solid #ebeef5;
      }

      .bottom-right {
        flex: 1;
        padding-left: 20px;
        display: flex;
        flex-direction: column;
      }
    }

    .bottom-indicators {
      display: flex;
      align-items: center;
      padding: 14px 16px;
      background: linear-gradient(135deg, #f0f9ff 0%, #e8f5e9 100%);
      border-radius: 12px;
      margin-bottom: 16px;

      .indicator-item {
        flex: 1;
        text-align: center;

        .indicator-label {
          font-size: 13px;
          color: #909399;
          margin-bottom: 6px;
          font-weight: 500;
        }

        .indicator-value {
          font-weight: 600;

          &.disease-name {
            font-size: 16px;
            color: #303133;
          }

          &.probability {
            font-size: 18px;
            font-weight: 700;
          }
        }
      }

      .indicator-divider {
        width: 1px;
        height: 36px;
        background: #dcdfe6;
        flex-shrink: 0;
      }
    }

    .symptoms-section {
      flex: 1;

      .symptoms-title {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #ebeef5;
      }

      .symptoms-content {
        font-size: 14px;
        line-height: 1.9;
        color: #5a5a5a;
        white-space: normal;
        word-wrap: break-word;
        word-break: break-word;

        :deep(.emoji) {
          font-size: 16px;
          margin-right: 4px;
        }
      }
    }

    .result-title {
      font-size: 15px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px dashed #ebeef5;
      display: flex;
      align-items: center;
      gap: 6px;

      .source-tag {
        font-size: 11px;
        font-weight: 500;
        color: #909399;
        background: linear-gradient(135deg, #f5f7fa, #eef1f6);
        padding: 2px 10px;
        border-radius: 20px;
        margin-left: 4px;
        letter-spacing: 0.5px;
        border: 1px solid #e4e7ed;
        white-space: nowrap;
      }
    }

    .treatment-content {
      font-size: 14px;
      line-height: 1.9;
      color: #5a5a5a;
      white-space: normal;
      word-wrap: break-word;
      word-break: break-word;

      :deep(.emoji) {
        font-size: 16px;
        margin-right: 4px;
      }
    }

    &.placeholder {
      color: #909399;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 80px;

      .el-icon {
        margin-right: 8px;
        font-size: 16px;
      }
    }
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.1);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(64, 158, 255, 0.4);
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
</style>