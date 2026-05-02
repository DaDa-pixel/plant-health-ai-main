<template>
  <div class="knowledge-base-container">
    <!-- 头部搜索区 -->
    <div class="search-header">
      <div class="header-content">
        <div class="title-section">
          <el-icon class="book-icon"><Reading /></el-icon>
          <h2>📚 病虫害知识库</h2>
          <p class="subtitle">权威知识 · 科学防治 · 精准指导</p>
        </div>
        <div class="search-section">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索病害名称、症状、作物类型..."
            clearable
            size="large"
            @keyup.enter="handleSearch"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="handleSearch" :loading="loading">
                搜索
              </el-button>
            </template>
          </el-input>
          <div class="quick-tags">
            <el-tag
              v-for="tag in quickTags"
              :key="tag"
              size="small"
              effect="plain"
              @click="searchByTag(tag)"
              class="quick-tag"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar" v-if="searchResults.length > 0">
      <div class="stat-item">
        <el-icon><Document /></el-icon>
        <span>共找到 <strong>{{ totalCount }}</strong> 条结果</span>
      </div>
      <div class="stat-item" v-if="searchKeyword">
        <el-icon><Search /></el-icon>
        <span>关键词：<strong>{{ searchKeyword }}</strong></span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 搜索无结果 -->
    <div v-else-if="hasSearched && searchResults.length === 0" class="empty-state">
      <el-icon class="empty-icon"><DocumentDelete /></el-icon>
      <h3>未找到相关结果</h3>
      <p>请尝试其他关键词，或点击上方快速标签浏览</p>
    </div>

    <!-- 初始推荐（未搜索时） -->
    <div v-else-if="!hasSearched" class="recommend-section">
      <div class="recommend-header">
        <div class="recommend-title">
          <el-icon class="fire-icon"><DataAnalysis /></el-icon>
          <h3>🌱 热门病害推荐</h3>
        </div>
        <p class="recommend-desc">点击了解常见病害的症状与防治方法</p>
      </div>
      <div class="recommend-cards">
        <div
          v-for="(item, index) in recommendList"
          :key="index"
          class="recommend-card"
          @click="showDetail(item)"
          :style="{ '--card-delay': index * 0.1 + 's' }"
        >
          <div class="card-badge">{{ index + 1 }}</div>
          <div class="card-icon-wrapper">
            <el-icon class="card-icon" :class="iconClass(index)"><Warning /></el-icon>
          </div>
          <h4 class="card-name">{{ item.disease_name }}</h4>
          <p class="card-preview">{{ truncateText(item.symptoms, 40) }}</p>
          <div class="card-footer">
            <span class="card-tag" v-if="item.crop_type">{{ item.crop_type }}</span>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-else class="results-container">
      <transition-group name="fade" tag="div" class="cards-grid">
        <div
          v-for="(item, index) in searchResults"
          :key="index"
          class="disease-card"
          @click="showDetail(item)"
        >
          <div class="card-header">
            <div class="disease-name">
              <el-icon class="name-icon"><Warning /></el-icon>
              <h3>{{ item.disease_name }}</h3>
            </div>
            <el-tag size="small" type="warning" effect="dark">查看详情</el-tag>
          </div>

          <div class="card-body">
            <div class="info-section">
              <div class="section-title">
                <el-icon><View /></el-icon>
                <span>主要症状</span>
              </div>
              <p class="section-content">{{ truncateText(item.symptoms, 80) }}</p>
            </div>

            <div class="info-section">
              <div class="section-title">
                <el-icon><QuestionFilled /></el-icon>
                <span>发病原因</span>
              </div>
              <p class="section-content">{{ truncateText(item.cause, 80) }}</p>
            </div>

            <div class="info-section">
              <div class="section-title">
                <el-icon><CircleCheck /></el-icon>
                <span>防治方法</span>
              </div>
              <p class="section-content">{{ truncateText(item.treatment, 80) }}</p>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      width="70%"
      :close-on-click-modal="false"
      class="detail-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <el-icon class="dialog-icon"><Reading /></el-icon>
          <span>{{ currentDetail?.disease_name || '病害详情' }}</span>
        </div>
      </template>

      <div v-if="currentDetail" class="detail-content">
        <div class="detail-section">
          <div class="section-header">
            <el-icon><View /></el-icon>
            <h4>病害症状</h4>
          </div>
          <div class="section-body">{{ currentDetail.symptoms || '暂无数据' }}</div>
        </div>

        <div class="detail-section">
          <div class="section-header">
            <el-icon><QuestionFilled /></el-icon>
            <h4>发病原因</h4>
          </div>
          <div class="section-body">{{ currentDetail.cause || '暂无数据' }}</div>
        </div>

        <div class="detail-section">
          <div class="section-header">
            <el-icon><CircleCheck /></el-icon>
            <h4>防治方法</h4>
          </div>
          <div class="section-body treatment-text">{{ currentDetail.treatment || '暂无数据' }}</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="infoDisease">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Reading,
  Search,
  Document,
  DocumentDelete,
  Warning,
  View,
  QuestionFilled,
  CircleCheck,
  DataAnalysis,
  ArrowRight
} from '@element-plus/icons-vue';
import request from '/@/utils/request';

interface DiseaseInfo {
  disease_name: string;
  symptoms: string;
  cause: string;
  treatment: string;
  crop_type?: string;
}

const searchKeyword = ref('');
const loading = ref(false);
const searchResults = ref<DiseaseInfo[]>([]);
const detailVisible = ref(false);
const currentDetail = ref<DiseaseInfo | null>(null);
const hasSearched = ref(false);
const recommendList = ref<DiseaseInfo[]>([]);

const quickTags = ['番茄', '玉米', '水稻', '小麦', '白粉病', '锈病', '蚜虫'];

const totalCount = computed(() => searchResults.value.length);

// 热门推荐图标样式轮换
const iconClass = (index: number) => {
  const classes = ['icon-red', 'icon-orange', 'icon-blue', 'icon-green', 'icon-purple', 'icon-teal'];
  return classes[index % classes.length];
};

// 加载推荐数据
const loadRecommendations = async () => {
  try {
    // 用多个热门关键词搜索，合并结果作为推荐
    const keywords = ['番茄', '玉米', '水稻', '小麦'];
    const allResults: DiseaseInfo[] = [];
    const seen = new Set<string>();

    for (const keyword of keywords) {
      const res = await request.post('/api/flask/knowledge/search', { keyword });
      if (res.code === 0 && res.data.success && res.data.results) {
        for (const item of res.data.results) {
          if (!seen.has(item.disease_name)) {
            seen.add(item.disease_name);
            allResults.push(item);
          }
        }
      }
    }

    recommendList.value = allResults.slice(0, 6);
  } catch (error) {
    console.warn('加载推荐数据失败:', error);
    recommendList.value = [];
  }
};

// 搜索处理
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }

  hasSearched.value = true;
  loading.value = true;

  try {
    const response = await request.post('/api/flask/knowledge/search', {
      keyword: searchKeyword.value.trim()
    });

    if (response.code === 0 && response.data.success) {
      searchResults.value = response.data.results || [];

      if (searchResults.value.length === 0) {
        ElMessage.info('未找到相关结果，请尝试其他关键词');
      }
    } else {
      ElMessage.error(response.msg || '搜索失败');
      searchResults.value = [];
    }
  } catch (error) {
    console.error('搜索失败:', error);
    ElMessage.error('搜索失败，请检查网络连接');
    searchResults.value = [];
  } finally {
    loading.value = false;
  }
};

// 快速标签搜索
const searchByTag = (tag: string) => {
  searchKeyword.value = tag;
  handleSearch();
};

// 显示详情
const showDetail = (item: DiseaseInfo) => {
  currentDetail.value = item;
  detailVisible.value = true;
};

// 截断文本
const truncateText = (text: string, maxLength: number) => {
  if (!text) return '暂无数据';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// 页面加载时自动获取推荐数据
onMounted(() => {
  loadRecommendations();
});
</script>

<style scoped lang="scss">
.knowledge-base-container {
  width: 100%;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  overflow-y: auto;
}

// 头部搜索区
.search-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 30px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

  .header-content {
    max-width: 1200px;
    margin: 0 auto;

    .title-section {
      text-align: center;
      margin-bottom: 30px;
      color: white;

      .book-icon {
        font-size: 48px;
        margin-bottom: 12px;
        opacity: 0.9;
      }

      h2 {
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 600;
      }

      .subtitle {
        margin: 0;
        font-size: 14px;
        opacity: 0.85;
      }
    }

    .search-section {
      max-width: 700px;
      margin: 0 auto;

      .search-input {
        :deep(.el-input__wrapper) {
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
      }

      .quick-tags {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 16px;
        flex-wrap: wrap;

        .quick-tag {
          cursor: pointer;
          transition: all 0.3s ease;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
          }
        }
      }
    }
  }
}

// 统计栏
.stats-bar {
  display: flex;
  gap: 24px;
  padding: 16px 30px;
  background: white;
  border-bottom: 1px solid #ebeef5;

  .stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #606266;

    .el-icon {
      color: #667eea;
    }

    strong {
      color: #667eea;
      font-weight: 600;
    }
  }
}

// 加载状态
.loading-container {
  padding: 40px 30px;
  background: white;
  margin: 20px 30px;
  border-radius: 12px;
}

// 空状态
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;

  .empty-icon {
    font-size: 80px;
    margin-bottom: 20px;
    opacity: 0.5;
  }

  h3 {
    margin: 0 0 12px 0;
    font-size: 20px;
    color: #606266;
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}

// 推荐区域
.recommend-section {
  padding: 30px;
  flex: 1;

  .recommend-header {
    text-align: center;
    margin-bottom: 28px;

    .recommend-title {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 8px;

      .fire-icon {
        font-size: 28px;
        color: #f56c6c;
      }

      h3 {
        margin: 0;
        font-size: 22px;
        color: #303133;
        font-weight: 600;
      }
    }

    .recommend-desc {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }

  .recommend-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .recommend-card {
    background: white;
    border-radius: 16px;
    padding: 24px 20px 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
    animation: cardFadeIn 0.6s ease both;
    animation-delay: var(--card-delay, 0s);

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #667eea, #764ba2);
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    &:hover {
      transform: translateY(-6px);
      box-shadow: 0 12px 32px rgba(102, 126, 234, 0.18);
      border-color: #667eea;

      &::before {
        opacity: 1;
      }

      .card-arrow {
        transform: translateX(4px);
        opacity: 1;
      }
    }

    .card-badge {
      position: absolute;
      top: 10px;
      right: 14px;
      font-size: 12px;
      font-weight: 700;
      color: #c0c4cc;
      opacity: 0.4;
    }

    .card-icon-wrapper {
      display: flex;
      justify-content: center;
      margin-bottom: 14px;

      .card-icon {
        font-size: 36px;
        padding: 12px;
        border-radius: 14px;

        &.icon-red { color: #f56c6c; background: #fef0f0; }
        &.icon-orange { color: #e6a23c; background: #fdf6ec; }
        &.icon-blue { color: #409eff; background: #ecf5ff; }
        &.icon-green { color: #67c23a; background: #f0f9eb; }
        &.icon-purple { color: #9b59b6; background: #f3eaf9; }
        &.icon-teal { color: #00bcd4; background: #e0f7fa; }
      }
    }

    .card-name {
      margin: 0 0 10px 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      text-align: center;
    }

    .card-preview {
      margin: 0 0 16px 0;
      font-size: 13px;
      color: #909399;
      line-height: 1.5;
      text-align: center;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .card-footer {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;

      .card-tag {
        font-size: 12px;
        padding: 2px 10px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 20px;
        font-weight: 500;
      }

      .card-arrow {
        font-size: 16px;
        color: #667eea;
        opacity: 0.5;
        transition: all 0.3s ease;
      }
    }
  }
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 结果容器
.results-container {
  flex: 1;
  padding: 30px;
  overflow-y: auto;

  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }
}

// 病害卡片
.disease-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
    border-color: #667eea;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f0f0;

    .disease-name {
      display: flex;
      align-items: center;
      gap: 8px;

      .name-icon {
        font-size: 20px;
        color: #f56c6c;
      }

      h3 {
        margin: 0;
        font-size: 18px;
        color: #303133;
        font-weight: 600;
      }
    }
  }

  .card-body {
    .info-section {
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      .section-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #667eea;
        font-weight: 600;
        margin-bottom: 6px;

        .el-icon {
          font-size: 14px;
        }
      }

      .section-content {
        margin: 0;
        font-size: 13px;
        color: #606266;
        line-height: 1.6;
      }
    }
  }
}

// 详情对话框
.detail-dialog {
  :deep(.el-dialog__header) {
    padding: 20px 24px;
    border-bottom: 2px solid #f0f0f0;
  }

  :deep(.el-dialog__body) {
    padding: 24px;
    max-height: 60vh;
    overflow-y: auto;
  }

  .dialog-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 20px;
    font-weight: 600;
    color: #303133;

    .dialog-icon {
      font-size: 28px;
      color: #667eea;
    }
  }

  .detail-content {
    .detail-section {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }

      .section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #f0f0f0;

        .el-icon {
          font-size: 20px;
          color: #667eea;
        }

        h4 {
          margin: 0;
          font-size: 16px;
          color: #303133;
          font-weight: 600;
        }
      }

      .section-body {
        font-size: 14px;
        color: #606266;
        line-height: 1.8;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;

        &.treatment-text {
          white-space: pre-wrap;
        }
      }
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: all 0.4s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* ===== 手机端适配（≤768px） ===== */
@media screen and (max-width: 768px) {
  .knowledge-base-container {
    height: auto;
    overflow-y: visible;
  }

  .search-header {
    padding: 24px 16px;
  }

  .search-header .header-content .title-section {
    margin-bottom: 20px;
  }

  .search-header .header-content .title-section h2 {
    font-size: 20px;
  }

  .search-header .header-content .title-section .subtitle {
    font-size: 12px;
  }

  .search-header .header-content .search-section .search-input :deep(.el-input__wrapper) {
    border-radius: 8px;
  }

  .search-header .header-content .search-section .quick-tags {
    gap: 6px;
  }

  .stats-bar {
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px;
  }

  .recommend-section {
    padding: 16px;
  }

  .recommend-section .recommend-header .recommend-title h3 {
    font-size: 18px;
  }

  .recommend-section .recommend-cards {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .recommend-section .recommend-card {
    padding: 18px 16px 16px;
  }

  .results-container {
    padding: 16px;
  }

  .results-container .cards-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .disease-card {
    padding: 16px;
  }

  .disease-card .card-header .disease-name h3 {
    font-size: 15px;
  }

  .detail-dialog {
    width: 92% !important;
    max-width: 92% !important;
  }

  .detail-dialog :deep(.el-dialog__body) {
    padding: 16px;
    max-height: 55vh;
  }

  .detail-dialog .dialog-header {
    font-size: 16px;
  }

  .detail-dialog .detail-content .detail-section .section-header h4 {
    font-size: 14px;
  }

  .detail-dialog .detail-content .detail-section .section-body {
    font-size: 13px;
    padding: 10px;
  }
}
</style>