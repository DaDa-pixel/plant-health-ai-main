<template>
  <div class="greenhouse-container">
    <div class="greenhouse-wrapper">
      <!-- 头部统计区 -->
      <div class="stats-header">
        <div class="header-content">
          <div class="title-section">
            <el-icon class="header-icon"><OfficeBuilding /></el-icon>
            <h2>🌿 温室智能管理</h2>
            <p class="subtitle">环境监测 · 数据管理 · 智能决策</p>
          </div>
          <div class="stats-cards">
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><List /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ state.tableData.total }}</div>
                <div class="stat-label">温室总数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon><Sunny /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ uniqueCropTypes }}</div>
                <div class="stat-label">作物种类</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ uniqueManagers }}</div>
                <div class="stat-label">管理人员</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索筛选区 -->
      <div class="search-section">
        <el-card shadow="hover" class="search-card">
          <div class="search-header">
            <div class="search-title">
              <el-icon><Search /></el-icon>
              <span>数据筛选</span>
            </div>
          </div>
          <div class="search-body">
            <el-form :inline="true" :model="state.tableData.param" class="filter-form">
              <el-form-item label="温室名称">
                <el-input
                    v-model="state.tableData.param.search"
                    placeholder="请输入温室名称"
                    clearable
                    style="width: 180px"
                    @clear="handleSearch"
                />
              </el-form-item>
              <el-form-item label="作物类型">
                <el-input
                    v-model="state.tableData.param.cropType"
                    placeholder="请输入作物类型"
                    clearable
                    style="width: 160px"
                    @clear="handleSearch"
                />
              </el-form-item>
              <el-form-item label="生长状态">
                <el-select
                    v-model="state.tableData.param.growthStatus"
                    placeholder="请选择生长状态"
                    clearable
                    style="width: 140px"
                    @change="handleSearch"
                >
                  <el-option label="幼苗期" value="幼苗期" />
                  <el-option label="生长期" value="生长期" />
                  <el-option label="开花期" value="开花期" />
                  <el-option label="结果期" value="结果期" />
                  <el-option label="成熟期" value="成熟期" />
                </el-select>
              </el-form-item>
              <el-form-item label="负责人">
                <el-input
                    v-model="state.tableData.param.manager"
                    placeholder="请输入负责人"
                    clearable
                    style="width: 150px"
                    @clear="handleSearch"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSearch" :loading="state.tableData.loading">
                  <el-icon><Search /></el-icon>
                  查询
                </el-button>
                <el-button @click="handleReset">
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
                <el-button type="success" @click="onOpenAddGreenhouse('add')">
                  <el-icon><Plus /></el-icon>
                  添加温室
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>

      <!-- 表格区域 -->
      <div class="table-section">
        <el-card shadow="hover" class="table-card">
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <span>温室数据列表</span>
            </div>
            <div class="table-stats">
              <span>共 {{ state.tableData.total }} 条记录</span>
            </div>
          </div>

          <el-table
              :data="state.tableData.data"
              v-loading="state.tableData.loading"
              stripe
              style="width: 100%"
              border
          >
            <el-table-column prop="num" label="序号" width="70" align="center" fixed="left" />
            <el-table-column prop="greenhouseName" label="温室名称" min-width="120" align="center">
              <template #default="{ row }">
                <el-tag type="primary" effect="light" size="large">{{ row.greenhouseName }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cropType" label="作物类型" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag type="success" effect="plain">{{ row.cropType }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量(株)" width="100" align="center">
              <template #default="{ row }">
                <span class="quantity-value">{{ row.quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="growthStatus" label="生长状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.growthStatus)" effect="dark" size="small">
                  {{ row.growthStatus }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="temperature" label="温度(℃)" width="100" align="center">
              <template #default="{ row }">
                <span :class="getTempClass(row.temperature)">{{ row.temperature }}°C</span>
              </template>
            </el-table-column>
            <el-table-column prop="airHumidity" label="空气湿度(%)" width="120" align="center">
              <template #default="{ row }">
                <div class="humidity-display">
                  <el-progress
                      :percentage="row.airHumidity"
                      :stroke-width="6"
                      :color="getHumidityColor(row.airHumidity)"
                      :show-text="false"
                      style="width: 70px; display: inline-block;"
                  />
                  <span class="humidity-value">{{ row.airHumidity }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="soilHumidity" label="土壤湿度(%)" width="120" align="center">
              <template #default="{ row }">
                <div class="humidity-display">
                  <el-progress
                      :percentage="row.soilHumidity"
                      :stroke-width="6"
                      :color="getHumidityColor(row.soilHumidity)"
                      :show-text="false"
                      style="width: 70px; display: inline-block;"
                  />
                  <span class="humidity-value">{{ row.soilHumidity }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="co2Concentration" label="CO₂浓度" width="110" align="center">
              <template #default="{ row }">
                <span>{{ row.co2Concentration }} ppm</span>
              </template>
            </el-table-column>
            <el-table-column prop="soilPh" label="土壤pH" width="90" align="center">
              <template #default="{ row }">
                <span :class="getPhClass(row.soilPh)">{{ row.soilPh }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="lightIntensity" label="光照强度" width="110" align="center">
              <template #default="{ row }">
                <span>{{ row.lightIntensity }} lux</span>
              </template>
            </el-table-column>
            <el-table-column prop="manager" label="负责人" width="100" align="center">
              <template #default="{ row }">
                <span class="manager-name">{{ row.manager }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="recordTime" label="记录时间" width="170" align="center">
              <template #default="{ row }">
                <span class="record-time">{{ formatDate(row.recordTime) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right" align="center">
              <template #default="scope">
                <el-button size="small" type="primary" link @click="onOpenEditGreenhouse('edit', scope.row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" link @click="onRowDel(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页器 -->
          <div class="pagination-wrapper">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 30, 50]"
                :total="state.tableData.total"
                layout="total, sizes, prev, pager, next, jumper"
                background
                @size-change="onHandleSizeChange"
                @current-change="onHandleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </div>
    <GreenhouseDialog ref="greenhouseDialogRef" @refresh="getTableData" />
  </div>
</template>

<script setup>
import { defineAsyncComponent, reactive, onMounted, ref, computed } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import {
  OfficeBuilding, List, Sunny, User, Search, Refresh, Plus, Edit, Delete
} from '@element-plus/icons-vue';
import request from '/@/utils/request';

// 引入组件
const GreenhouseDialog = defineAsyncComponent(() => import('./dialog.vue'));

// 定义变量内容
const greenhouseDialogRef = ref();
const currentPage = ref(1);
const pageSize = ref(10);

const state = reactive({
  tableData: {
    data: [],
    total: 0,
    loading: false,
    param: {
      search: '',
      cropType: '',
      growthStatus: '',
      manager: '',
      recordTime: '',
    },
  },
});

// 统计计算 - 从当前表格数据中统计
const uniqueCropTypes = computed(() => {
  const types = new Set();
  state.tableData.data.forEach(item => {
    if (item.cropType) types.add(item.cropType);
  });
  return types.size;
});

const uniqueManagers = computed(() => {
  const managers = new Set();
  state.tableData.data.forEach(item => {
    if (item.manager) managers.add(item.manager);
  });
  return managers.size;
});

// 获取表格数据
const getTableData = async () => {
  state.tableData.loading = true;
  try {
    const res = await request.get('/api/greenhouse', {
      params: {
        ...state.tableData.param,
        pageNum: currentPage.value,
        pageSize: pageSize.value,
      },
    });

    if (res.code === 0) {
      const records = res.data.records || [];
      // 计算正确的序号（基于分页）
      state.tableData.data = records.map((item, index) => ({
        ...item,
        num: (currentPage.value - 1) * pageSize.value + index + 1
      }));
      state.tableData.total = res.data.total || 0;
    } else {
      ElMessage.error(res.msg || '获取数据失败');
      state.tableData.data = [];
      state.tableData.total = 0;
    }
  } catch (error) {
    console.error('获取数据失败:', error);
    ElMessage.error('网络请求失败');
    state.tableData.data = [];
    state.tableData.total = 0;
  } finally {
    state.tableData.loading = false;
  }
};

// 搜索
const handleSearch = () => {
  currentPage.value = 1;
  getTableData();
};

// 重置
const handleReset = () => {
  state.tableData.param.search = '';
  state.tableData.param.cropType = '';
  state.tableData.param.growthStatus = '';
  state.tableData.param.manager = '';
  currentPage.value = 1;
  getTableData();
};

// 打开新增温室弹窗
const onOpenAddGreenhouse = (type) => {
  greenhouseDialogRef.value.openDialog(type);
};

// 打开修改温室弹窗
const onOpenEditGreenhouse = (type, row) => {
  greenhouseDialogRef.value.openDialog(type, row);
};

// 删除温室
const onRowDel = (row) => {
  ElMessageBox.confirm(`确定要删除温室"${row.greenhouseName}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(async () => {
        try {
          const res = await request.delete('/api/greenhouse/' + row.id);
          if (res.code === 0) {
            ElMessage.success('删除成功！');
            getTableData();
          } else {
            ElMessage.error(res.msg || '删除失败');
          }
        } catch (error) {
          console.error('删除失败:', error);
          ElMessage.error('网络请求失败');
        }
      })
      .catch(() => {});
};

// 分页改变 - 每页条数变化
const onHandleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  getTableData();
};

// 分页改变 - 当前页变化
const onHandleCurrentChange = (val) => {
  currentPage.value = val;
  getTableData();
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
};

// 获取状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    '幼苗期': 'info',
    '生长期': 'primary',
    '开花期': 'warning',
    '结果期': 'success',
    '成熟期': 'danger'
  };
  return statusMap[status] || 'info';
};

// 温度样式类
const getTempClass = (temp) => {
  if (temp > 35 || temp < 10) return 'temp-warning';
  if (temp > 30 || temp < 15) return 'temp-caution';
  return 'temp-normal';
};

// 湿度颜色
const getHumidityColor = (humidity) => {
  if (humidity >= 60 && humidity <= 80) return '#67C23A';
  if (humidity >= 40 && humidity < 60) return '#E6A23C';
  return '#F56C6C';
};

// pH值样式类
const getPhClass = (ph) => {
  if (ph >= 6.0 && ph <= 7.5) return 'ph-normal';
  return 'ph-warning';
};

// 页面加载时
onMounted(() => {
  getTableData();
});
</script>

<style scoped lang="scss">
.greenhouse-container {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  padding: 20px;

  .greenhouse-wrapper {
    height: 100%;
  }
}

// 头部统计区
.stats-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 28px 36px;
  margin-bottom: 24px;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3);

  .header-content {
    .title-section {
      text-align: center;
      color: white;
      margin-bottom: 28px;

      .header-icon {
        font-size: 48px;
        margin-bottom: 12px;
        opacity: 0.95;
      }

      h2 {
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: 1px;
      }

      .subtitle {
        margin: 0;
        font-size: 14px;
        opacity: 0.9;
      }
    }

    .stats-cards {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;

      .stat-card {
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.3s ease;
        cursor: pointer;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
          background: white;
        }

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          color: white;
          flex-shrink: 0;
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #303133;
            margin-bottom: 4px;
            line-height: 1.2;
          }

          .stat-label {
            font-size: 13px;
            color: #909399;
            letter-spacing: 0.5px;
          }
        }
      }
    }
  }
}

// 搜索区
.search-section {
  margin-bottom: 20px;

  .search-card {
    border-radius: 16px;
    overflow: hidden;

    :deep(.el-card__body) {
      padding: 0;
    }

    .search-header {
      padding: 14px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

      .search-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
        font-size: 15px;
        font-weight: 600;

        .el-icon {
          font-size: 18px;
        }
      }
    }

    .search-body {
      padding: 20px 24px;
      background: white;

      .filter-form {
        :deep(.el-form-item) {
          margin-bottom: 0;
          margin-right: 16px;
        }
      }
    }
  }
}

// 表格区
.table-section {
  .table-card {
    border-radius: 16px;
    overflow: hidden;

    :deep(.el-card__body) {
      padding: 0;
    }

    .table-header {
      padding: 14px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      justify-content: space-between;
      align-items: center;

      .table-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
        font-size: 15px;
        font-weight: 600;

        .el-icon {
          font-size: 18px;
        }
      }

      .table-stats {
        color: rgba(255, 255, 255, 0.9);
        font-size: 13px;
      }
    }

    :deep(.el-table) {
      margin: 0;

      .el-table__header-wrapper th {
        background-color: #f8f9fc !important;
      }

      .el-table__body-wrapper td {
        padding: 12px 0;
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: flex-end;
      padding: 16px 24px;
      background: white;
      border-top: 1px solid #ebeef5;
    }
  }
}

// 数值样式
.quantity-value {
  font-size: 16px;
  font-weight: 600;
  color: #409EFF;
}

.manager-name {
  font-weight: 500;
  color: #606266;
}

.record-time {
  font-size: 12px;
  color: #909399;
}

.humidity-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .humidity-value {
    font-size: 13px;
    font-weight: 500;
  }
}

// 温度样式
.temp-normal {
  color: #67C23A;
  font-weight: 500;
}

.temp-caution {
  color: #E6A23C;
  font-weight: 500;
}

.temp-warning {
  color: #F56C6C;
  font-weight: 600;
}

// pH样式
.ph-normal {
  color: #67C23A;
  font-weight: 500;
}

.ph-warning {
  color: #F56C6C;
  font-weight: 500;
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