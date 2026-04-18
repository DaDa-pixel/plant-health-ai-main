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
          <el-button type="primary" @click="upData" class="predict-button" :loading="state.predictLoading">
            开始预测
          </el-button>
        </div>
      </div>

      <!-- 图片显示区域 -->
      <el-row :gutter="20" class="image-display">
        <!-- 原图展示 -->
        <el-col :span="8">
          <el-card shadow="hover" class="card">
            <div class="image-title">原图片</div>
            <el-upload
                v-model="state.img"
                ref="uploadFile"
                class="avatar-uploader"
                action="/api/files/upload"
                :show-file-list="false"
                :on-success="handleAvatarSuccessone"
            >
              <el-image v-if="imageUrl" :src="imageUrl" class="preview-image" fit="contain" />
              <div v-else class="uploader-content">
                <el-icon class="upload-icon">
                  <Plus />
                </el-icon>
                <div class="upload-text">点击上传图片</div>
              </div>
            </el-upload>
          </el-card>
        </el-col>

        <!-- 预测结果图（热力图） -->
        <el-col :span="8">
          <el-card shadow="hover" class="card">
            <div class="image-title">预测结果</div>
            <el-image
                v-if="predictedImageUrl"
                :src="predictedImageUrl"
                class="preview-image"
                fit="contain"
            />
            <div v-else class="placeholder">
              <el-icon>
                <Picture />
              </el-icon>
              <span>预测后将在此显示热力图</span>
            </div>
          </el-card>
        </el-col>

        <!-- 智能医生对话 -->
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
              <div class="result-column narrow">
                <div class="result-title">🔍 识别结果</div>
                <div class="result-item">
                  <span class="result-value disease-name">{{ state.predictionResult.label }}</span>
                </div>
              </div>
              <div class="result-column narrow">
                <div class="result-title">📊 预测概率</div>
                <div class="result-item">
									<span class="result-value confidence-value" :style="{ color: getConfidenceColor(state.predictionResult.confidenceValue) }">
										{{ state.predictionResult.confidence }}
									</span>
                </div>
              </div>
              <div class="result-column narrow">
                <div class="result-title">✅ 可靠性</div>
                <div class="result-item">
                  <el-tag :type="isReliable ? 'success' : 'warning'" size="default" effect="dark">
                    {{ isReliable ? '可靠' : '较低' }}
                  </el-tag>
                </div>
              </div>
              <div class="result-column wide">
                <div class="result-title">📚 知识库建议</div>
                <div class="result-item advice-wrapper">
                  <div class="advice-content" v-html="formatAdvice(state.knowledgeAdvice)"></div>
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
import { reactive, ref, nextTick } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { Plus, Picture, Promotion } from '@element-plus/icons-vue';
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

interface ChatMessage {
  role: 'user' | 'doctor';
  content: string;
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

const formatTooltip = (val: number) => {
  return (val / 100).toFixed(2);
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
  state.form.conf = conf.value / 100;
  state.form.username = userInfos.value.userName;
  state.form.inputImg = state.img;

  request.post('/api/flask/predict', state.form).then((res) => {
    state.predictLoading = false;

    if (res.code === 0) {
      try {
        const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;

        if (data.success) {
          state.predictionResult.label = data.disease_name || '未知病害';

          const confidencePercent = (data.confidence * 100).toFixed(2);
          state.predictionResult.confidence = confidencePercent + '%';
          state.predictionResult.confidenceValue = data.confidence;

          state.predictionResult.allTime = data.processing_time || '0';

          isReliable.value = data.is_reliable || false;

          if (data.heatmap_base64) {
            predictedImageUrl.value = data.heatmap_base64;
          } else {
            predictedImageUrl.value = '';
          }

          if (data.advice) {
            state.knowledgeAdvice = data.advice;

            const initialMessage = `您好！我是智能植物医生 🩺

**诊断结果：**${data.disease_name}
**置信度：**${(data.confidence * 100).toFixed(2)}%

我已经从知识库中获取了详细的防治建议（见下方"知识库建议"栏）。

您可以问我任何问题，例如：
• 这个病害的具体症状是什么？
• 应该如何防治？
• 有什么预防措施吗？
• 会影响产量吗？

请问您想了解什么？`;

            state.chatMessages = [{
              role: 'doctor',
              content: initialMessage
            }];
          }

          ElMessage.success('预测成功！');
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
  }).catch((error) => {
    state.predictLoading = false;
    console.error('预测请求失败:', error);
    ElMessage.error('预测请求失败，请检查网络连接');
  });
};

const sendToDoctor = async () => {
  if (!state.userQuestion.trim() || !state.predictionResult.label) {
    return;
  }

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
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: question,
        disease_context: state.predictionResult.label
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

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

  let formatted = advice
      .replace(/\n/g, '<br/>')
      .replace(/🌱/g, '<span class="emoji">🌱</span>')
      .replace(/🌾/g, '<span class="emoji">🌾</span>')
      .replace(/🧑‍🌾/g, '<span class="emoji">🧑‍🌾</span>')
      .replace(/💊/g, '<span class="emoji">💊</span>')
      .replace(/💡/g, '<span class="emoji">💡</span>')
      .replace(/📚/g, '<span class="emoji">📚</span>');

  return formatted;
};

const getConfidenceColor = (value: number) => {
  if (value >= 0.8) return '#67C23A';
  if (value >= 0.5) return '#E6A23C';
  return '#F56C6C';
};

</script>

<style scoped lang="scss">
.system-predict-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: #f5f7fa;

  .system-predict-padding {
    padding: 15px;
    padding-bottom: 0;
    padding-top: 0;
    min-height: calc(100vh - 60px);
  }
}

.header {
  width: 100%;
  padding: 10px 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 1px;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: none;
}

.image-display {
  margin-top: 15px;

  .card {
    height: 100%;
    background: white;
    border-radius: 8px;
    box-shadow: none;
    transition: all 0.3s ease;

    &:hover {
      transform: none;
      box-shadow: none;
    }

    .image-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 1px solid #ebeef5;
    }

    .avatar-uploader {
      width: 100%;
      height: 358px;
      border: 1px dashed #d9d9d9;
      border-radius: 4px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: var(--el-transition-duration-fast);
      display: flex;
      justify-content: center;
      align-items: center;

      &:hover {
        border-color: var(--el-color-primary);
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
    }

    .upload-icon {
      font-size: 28px;
      color: #909399;
    }

    .upload-text {
      color: #909399;
      font-size: 14px;
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
        font-size: 28px;
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
    border-radius: 8px;
    box-shadow: none;
    margin: 0;

    .el-card__body {
      padding: 0;
    }
  }

  .bottom {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 20px;
    background: white;
    border-radius: 8px;
    min-height: 140px;

    .result-column {
      padding: 0 15px;
      border-right: 1px solid #ebeef5;

      &:last-child {
        border-right: none;
      }

      &.narrow {
        width: 15%;
        min-width: 120px;
      }

      &.wide {
        width: 55%;
        flex: 1;
      }

      .result-title {
        font-size: 14px;
        color: #606266;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .result-item {
        margin: 5px 0;

        .result-value {
          color: #409EFF;
          font-weight: 500;

          &.disease-name {
            font-size: 18px;
            color: #303133;
            font-weight: 600;
          }

          &.confidence-value {
            font-size: 20px;
            font-weight: 700;
          }
        }

        /* 知识库建议滚动区域 - 修复截断问题 */
        .advice-wrapper {
          width: 100%;
        }

        .advice-content {
          max-height: 200px;
          overflow-y: auto;
          overflow-x: hidden;
          padding-right: 10px;
          font-size: 13px;
          color: #606266;
          line-height: 1.8;
          white-space: normal;
          word-wrap: break-word;
          word-break: break-word;

          /* 自定义滚动条样式 */
          &::-webkit-scrollbar {
            width: 6px;
            height: 6px;
          }

          &::-webkit-scrollbar-track {
            background: #f5f7fa;
            border-radius: 3px;
          }

          &::-webkit-scrollbar-thumb {
            background-color: #c0c4cc;
            border-radius: 3px;

            &:hover {
              background-color: #909399;
            }
          }

          .emoji {
            font-size: 16px;
            margin-right: 4px;
          }

          strong {
            color: #409EFF;
            font-weight: 600;
          }
        }
      }
    }

    &.placeholder {
      color: #909399;
      justify-content: center;
      align-items: center;

      .el-icon {
        margin-right: 8px;
        font-size: 16px;
      }
    }
  }
}

.predict-button {
  background: linear-gradient(45deg, #409eff, #36a2f1);
  border: none;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
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
</style>