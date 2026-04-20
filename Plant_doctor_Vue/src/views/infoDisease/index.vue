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
    <div class="stats-bar" v-if="!loading && searchResults.length >= 0">
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

    <!-- 空状态 -->
    <div v-else-if="searchResults.length === 0 && !loading" class="empty-state">
      <el-icon class="empty-icon"><DocumentDelete /></el-icon>
      <h3>暂无数据</h3>
      <p>输入关键词搜索病虫害知识，或点击上方快速标签</p>
    </div>

    <!-- 结果列表 -->
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
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Reading,
  Search,
  Document,
  DocumentDelete,
  Warning,
  View,
  QuestionFilled,
  CircleCheck
} from '@element-plus/icons-vue';
import request from '/@/utils/request';

interface DiseaseInfo {
  disease_name: string;
  symptoms: string;
  cause: string;
  treatment: string;
}

const searchKeyword = ref('');
const loading = ref(false);
const searchResults = ref<DiseaseInfo[]>([]);
const detailVisible = ref(false);
const currentDetail = ref<DiseaseInfo | null>(null);

const quickTags = ['番茄', '玉米', '水稻', '小麦', '白粉病', '锈病', '蚜虫'];

const totalCount = computed(() => searchResults.value.length);

// 搜索处理
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }

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
</style>