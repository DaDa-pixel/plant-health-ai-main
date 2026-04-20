<template>
  <div class="chat-container">
    <!-- 头部 -->
    <div class="chat-header">
      <div class="header-content">
        <div class="header-left">
          <el-icon class="robot-icon" :class="{ 'pulse': loading }"><ChatDotRound /></el-icon>
          <div class="header-info">
            <h3 class="chat-title">👨‍⚕️ 植物医生-老张</h3>
            <p class="status-text">{{ statusText }}</p>
          </div>
        </div>
        <div class="header-right">
          <el-button @click="clearChat" :disabled="messages.length <= 1" size="small">
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
        </div>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messageContainer">
      <!-- 欢迎卡片 -->
      <div v-if="messages.length === 1" class="welcome-card">
        <div class="welcome-icon">
          <el-icon><ChatLineSquare /></el-icon>
        </div>
        <h3>您好！我是植物医生老张 👋</h3>
        <p>种地几十年，有啥病虫害问题尽管问，我给您支支招！</p>
      </div>

      <!-- 消息列表 -->
      <div v-for="(message, index) in messages.slice(1)" :key="index"
           :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']">
        <div class="message-content">
          <div class="avatar">
            <el-icon v-if="message.role === 'user'"><User /></el-icon>
            <el-icon v-else><ChatDotRound /></el-icon>
          </div>
          <div class="text-wrapper">
            <div class="text" v-html="formatMessage(message.content)"></div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>

      <!-- 加载动画 -->
      <div v-if="loading" class="message assistant-message">
        <div class="message-content">
          <div class="avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="text-wrapper">
            <div class="text typing-bubble">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 建议问题 -->
    <div class="suggested-questions" v-if="messages.length === 1">
      <div class="suggested-title">💡 猜你想问</div>
      <div class="suggested-list">
        <div v-for="(question, index) in suggestedQuestions"
             :key="index"
             class="suggested-item"
             @click="selectQuestion(question)">
          {{ question }}
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="3"
        placeholder="请输入您的问题...（Shift+Enter换行，Enter发送）"
        @keydown.enter.exact.prevent="sendMessage"
        :disabled="!isModelAvailable || loading"
        resize="none"
      />
      <div class="input-actions">
        <div class="input-tips">
          <el-tag size="small" :type="isModelAvailable ? 'success' : 'danger'" effect="plain">
            {{ isModelAvailable ? '✅ 模型已就绪' : '⚠️ 模型未连接' }}
          </el-tag>
        </div>
        <el-button
          type="primary"
          :loading="loading"
          @click="sendMessage"
          :disabled="!userInput.trim() || !isModelAvailable"
          class="send-btn"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { ChatDotRound, Delete, User, Promotion, ChatLineSquare } from '@element-plus/icons-vue'

export default {
  name: 'SmartChat',
  components: {
    ChatDotRound,
    Delete,
    User,
    Promotion,
    ChatLineSquare
  },
  data() {
    return {
      messages: [{
        role: 'assistant',
        content: '你好，我是植物医生老张，种地几十年了，有啥问题尽管问！',
        timestamp: Date.now()
      }],
      userInput: '',
      loading: false,
      isModelAvailable: false,
      statusText: '正在检查模型状态...',
      suggestedQuestions: [
        '如何防治水稻病害？',
        '玉米常见病虫害有哪些？',
        '小麦生长周期是多少天？',
        '如何提高农作物产量？',
        '农药使用注意事项有哪些？',
        '农作物施肥的最佳时间？',
        '如何识别植物病害症状？'
      ]
    }
  },
  mounted() {
    this.checkModelStatus()
  },
  methods: {
    // 检查模型状态
    async checkModelStatus() {
      try {
        const response = await axios.get('http://localhost:5000/health')
        if (response.data) {
          this.isModelAvailable = response.data.llm_available || false
          this.statusText = this.isModelAvailable
            ? '✅ 在线 - 随时为您服务'
            : '⚠️ Ollama服务未启动，请运行 ollama serve'
        }
      } catch (error) {
        this.isModelAvailable = false
        this.statusText = '❌ Flask服务未启动'
        console.error('检查模型状态失败:', error)
      }
    },

    // 选择建议问题
    selectQuestion(question) {
      this.userInput = question
      this.sendMessage()
    },

    // 发送消息
    async sendMessage() {
      if (!this.userInput.trim() || this.loading || !this.isModelAvailable) return

      const userMessage = this.userInput.trim()

      // 添加用户消息
      this.messages.push({
        role: 'user',
        content: userMessage,
        timestamp: Date.now()
      })

      this.userInput = ''
      this.loading = true
      this.scrollToBottom()

      try {
        const response = await axios.post('http://localhost:5000/chat', {
          message: userMessage,
          disease_context: null // 独立助手模式，不设置病害上下文
        })

        if (response.data.success && response.data.response) {
          this.messages.push({
            role: 'assistant',
            content: response.data.response,
            timestamp: Date.now()
          })
        } else {
          throw new Error(response.data.error || '对话失败')
        }
      } catch (error) {
        this.$message.error('发送消息失败，请检查Flask和Ollama服务是否启动')
        console.error('Error:', error)

        // 添加错误提示消息
        this.messages.push({
          role: 'assistant',
          content: '哎呀，老张这会儿有点忙不过来。请确保以下服务已启动：\n\n1. Flask服务: python flask_api.py\n2. Ollama服务: ollama serve\n\n启动后老张就能继续给您解答啦！',
          timestamp: Date.now()
        })
      } finally {
        this.loading = false
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },

    // 清空对话
    clearChat() {
      this.messages = [{
        role: 'assistant',
        content: '你好，我是植物医生老张，种地几十年了，有啥问题尽管问！',
        timestamp: Date.now()
      }]
      this.$message.success('对话已清空')
    },

    // 滚动到底部
    scrollToBottom() {
      const container = this.$refs.messageContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },

    // 格式化消息内容
    formatMessage(content) {
      if (!content) return ''

      return content
        .replace(/\n/g, '<br/>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
    },

    // 格式化时间
    formatTime(timestamp) {
      const date = new Date(timestamp)
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 头部样式 */
.chat-header {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.robot-icon {
  font-size: 36px;
  color: #667eea;
}

.robot-icon.pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chat-title {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.status-text {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.header-right .el-button {
  border-radius: 8px;
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 欢迎卡片 */
.welcome-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  max-width: 600px;
  margin: 40px auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  animation: fadeIn 0.5s ease;
}

.welcome-icon {
  font-size: 60px;
  color: #667eea;
  margin-bottom: 16px;
}

.welcome-card h3 {
  margin: 0 0 12px 0;
  font-size: 22px;
  color: #303133;
}

.welcome-card p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

/* 消息样式 */
.message {
  margin-bottom: 20px;
  opacity: 0;
  transform: translateY(20px);
  animation: messageAppear 0.3s ease forwards;
  display: flex;
}

@keyframes messageAppear {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.message-content {
  display: flex;
  align-items: flex-start;
  max-width: 75%;
  gap: 10px;
}

.user-message {
  justify-content: flex-end;
}

.user-message .message-content {
  flex-direction: row-reverse;
}

.assistant-message .message-content {
  justify-content: flex-start;
}

.avatar {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-message .avatar {
  background: linear-gradient(135deg, #409EFF 0%, #36a2f1 100%);
  color: white;
}

.assistant-message .avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.text-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: calc(100% - 48px);
}

.text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
  word-wrap: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-message .text {
  background: linear-gradient(135deg, #409EFF 0%, #36a2f1 100%);
  color: white;
  border-top-right-radius: 4px;
}

.assistant-message .text {
  background: rgba(255, 255, 255, 0.95);
  color: #303133;
  border-top-left-radius: 4px;
}

.text code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.message-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  text-align: right;
  padding: 0 4px;
}

.assistant-message .message-time {
  color: rgba(0, 0, 0, 0.4);
  text-align: left;
}

/* 打字动画 */
.typing-bubble {
  padding: 16px 20px !important;
  display: flex;
  gap: 6px;
  align-items: center;
}

.typing-bubble span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite;
}

.typing-bubble span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-bubble span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
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

/* 建议问题 */
.suggested-questions {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.suggested-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  font-weight: 500;
}

.suggested-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggested-item {
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  font-size: 13px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggested-item:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

/* 输入区域 */
.chat-input {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 2px solid #e4e7ed;
  padding: 12px;
  font-size: 14px;
  resize: none;
  transition: all 0.3s ease;
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-input :deep(.el-textarea__inner:disabled) {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.send-btn {
  min-width: 100px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.send-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:active {
  transform: translateY(0);
}
</style>
