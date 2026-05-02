<template>
  <div class="detection-records-container">
    <div class="detection-records-wrapper">
      <!-- 顶部统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card img-stat">
          <div class="stat-icon">
            <el-icon><Picture /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ imgTotal }}</div>
            <div class="stat-label">图片检测</div>
          </div>
        </div>
        <div class="stat-card camera-stat">
          <div class="stat-icon">
            <el-icon><Camera /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ cameraTotal }}</div>
            <div class="stat-label">摄像检测</div>
          </div>
        </div>
        <div class="stat-card total-stat">
          <div class="stat-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ imgTotal + cameraTotal }}</div>
            <div class="stat-label">总记录数</div>
          </div>
        </div>
      </div>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
            v-model="searchParams.cropType"
            placeholder="搜索农作物种类"
            style="max-width: 220px"
            clearable
            @clear="loadAllRecords"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchParams.type" placeholder="检测类型" style="width: 140px" clearable @change="loadAllRecords">
          <el-option label="全部" value="" />
          <el-option label="图片检测" value="image" />
          <el-option label="摄像检测" value="camera" />
        </el-select>
        <el-button type="primary" @click="loadAllRecords" :loading="tableData.loading">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>

      <!-- 统一表格 -->
      <div class="table-wrapper">
        <el-table
            :data="paginatedData"
            v-loading="tableData.loading"
            style="width: 100%"
            :row-class-name="tableRowClassName"
        >
          <el-table-column label="序号" width="70" align="center">
            <template #default="scope">
              {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column label="检测类型" width="120" align="center">
            <template #default="scope">
              <el-tag
                  :type="scope.row.recordType === 'image' ? 'success' : 'warning'"
                  size="default"
              >
                <el-icon>
                  <Picture v-if="scope.row.recordType === 'image'" />
                  <Camera v-else />
                </el-icon>
                {{ scope.row.recordType === 'image' ? '图片检测' : '摄像检测' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="cropType" label="农作物种类" min-width="120" align="center" show-overflow-tooltip />
          <el-table-column prop="predictionResult" label="预测结果" min-width="150" align="center" show-overflow-tooltip />
          <el-table-column prop="conf" label="最小阈值" width="100" align="center" />
          <el-table-column prop="allTime" label="总用时" width="100" align="center" />
          <el-table-column prop="startTime" label="识别时间" width="170" align="center" />
          <el-table-column v-if="isAdmin" prop="username" label="识别用户" width="110" align="center" />
          <el-table-column label="操作" width="100" align="center" fixed="right">
            <template #default="scope">
              <el-button
                  size="small"
                  type="danger"
                  link
                  @click="deleteRecord(scope.row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 30, 50]"
              :total="tableData.total"
              layout="total, sizes, prev, pager, next, jumper"
              background
              @size-change="onSizeChange"
              @current-change="onPageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { Picture, Camera, DataAnalysis, Search, Refresh, Delete } from '@element-plus/icons-vue';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

// 判断是否为管理员
const isAdmin = computed(() => userInfos.value.userName === 'admin');

// 统计数据
const imgTotal = ref(0);
const cameraTotal = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

// 搜索条件
const searchParams = reactive({
  cropType: '',
  type: ''
});

// 表格数据
const tableData = reactive({
  data: [],
  total: 0,
  loading: false,
  param: {
    pageNum: 1,
    pageSize: 10
  }
});

// 表格行样式
const tableRowClassName = ({ row, rowIndex }) => {
  if (row.recordType === 'image') {
    return 'image-row';
  }
  return 'camera-row';
};

// 分页数据计算
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return tableData.data.slice(start, end);
});

// 加载所有记录
const loadAllRecords = async () => {
  tableData.loading = true;

  try {
    console.log('开始加载数据，搜索条件:', searchParams);

    const [imgRes, cameraRes] = await Promise.all([
      loadImgRecordsData(),
      loadCameraRecordsData()
    ]);

    console.log('图片检测接口返回:', imgRes);
    console.log('摄像检测接口返回:', cameraRes);

    let allRecords = [];

    if (searchParams.type === '' || searchParams.type === 'image') {
      const imgRecords = (imgRes.records || []).map(item => transformImageRecord(item));
      console.log('图片记录数量:', imgRecords.length);
      allRecords = allRecords.concat(imgRecords);
    }

    if (searchParams.type === '' || searchParams.type === 'camera') {
      const cameraRecords = (cameraRes.records || []).map(item => transformCameraRecord(item));
      console.log('摄像记录数量:', cameraRecords.length);
      allRecords = allRecords.concat(cameraRecords);
    }

    allRecords.sort((a, b) => {
      const timeA = new Date(a.startTime).getTime();
      const timeB = new Date(b.startTime).getTime();
      return timeB - timeA;
    });

    tableData.data = allRecords;
    tableData.total = allRecords.length;
    currentPage.value = 1;

    console.log('最终统计数据 - 图片:', imgTotal.value, '摄像:', cameraTotal.value, '总记录:', allRecords.length);

  } catch (error) {
    console.error('加载数据失败:', error);
    ElMessage.error('加载数据失败');
  } finally {
    tableData.loading = false;
  }
};

// 加载图片检测数据
const loadImgRecordsData = async () => {
  const params = {
    pageNum: 1,
    pageSize: 1000
  };

  if (userInfos.value.userName && userInfos.value.userName !== 'admin') {
    params.search = userInfos.value.userNickname || userInfos.value.userName;
  }

  if (searchParams.cropType) {
    params.search1 = searchParams.cropType;
  }

  console.log('图片检测请求参数:', params);

  const res = await request.get('/api/imgRecords', { params });
  console.log('图片检测接口响应:', res);

  if (res.code === 0) {
    imgTotal.value = res.data?.total || 0;
    console.log('图片检测总数:', imgTotal.value);
    return res.data || { records: [] };
  }
  return { records: [], total: 0 };
};

// 加载摄像检测数据
const loadCameraRecordsData = async () => {
  const params = {
    pageNum: 1,
    pageSize: 1000
  };

  if (userInfos.value.userName && userInfos.value.userName !== 'admin') {
    params.search = userInfos.value.userNickname || userInfos.value.userName;
  }

  if (searchParams.cropType) {
    params.search1 = searchParams.cropType;
  }

  console.log('摄像检测请求参数:', params);

  const res = await request.get('/api/cameraRecords', { params });
  console.log('摄像检测接口响应:', res);

  if (res.code === 0) {
    cameraTotal.value = res.data?.total || 0;
    console.log('摄像检测总数:', cameraTotal.value);
    return res.data || { records: [] };
  }
  return { records: [], total: 0 };
};

// 转换图片记录
const transformImageRecord = (item) => {
  let predictionResult = '-';

  try {
    const labels = JSON.parse(item.label || '[]');
    const confidences = JSON.parse(item.confidence || '[]');

    if (labels.length > 0) {
      predictionResult = labels[0];
    }
  } catch (e) {
    console.error('解析图片记录失败:', e);
  }

  return {
    id: item.id,
    recordType: 'image',
    cropType: item.kind || '-',
    predictionResult: predictionResult,
    weight: item.weight || '-',
    allTime: item.all_time || item.allTime || '-',
    conf: item.conf || '-',
    startTime: item.start_time || item.startTime,
    username: item.username || '-'
  };
};

// 转换摄像记录
const transformCameraRecord = (item) => {
  return {
    id: item.id,
    recordType: 'camera',
    cropType: item.kind || '-',
    predictionResult: '-',
    weight: item.weight || '-',
    allTime: '-',
    conf: item.conf || '-',
    startTime: item.start_time || item.startTime,
    username: item.username || '-'
  };
};

// 重置搜索
const resetSearch = () => {
  searchParams.cropType = '';
  searchParams.type = '';
  currentPage.value = 1;
  loadAllRecords();
};

// 删除记录
const deleteRecord = (row) => {
  const typeText = row.recordType === 'image' ? '图片检测' : '摄像检测';
  ElMessageBox.confirm(`确定要删除该${typeText}记录吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const api = row.recordType === 'image'
          ? `/api/imgRecords/${row.id}`
          : `/api/cameraRecords/${row.id}`;
      const res = await request.delete(api);
      if (res.code === 0) {
        ElMessage.success('删除成功！');
        loadAllRecords();
      } else {
        ElMessage.error(res.msg || '删除失败');
      }
    } catch (error) {
      console.error('删除失败:', error);
      ElMessage.error('网络请求失败');
    }
  }).catch(() => {});
};

// 分页
const onSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
};

const onPageChange = (val) => {
  currentPage.value = val;
};

// 页面加载
onMounted(() => {
  loadAllRecords();
});

</script>

<style scoped lang="scss">
.detection-records-container {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  padding: 20px;

  .detection-records-wrapper {
    height: 100%;
  }
}

// 统计卡片
.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;

  .stat-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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
    }

    .stat-content {
      flex: 1;

      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #303133;
        line-height: 1.2;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 13px;
        color: #909399;
      }
    }

    &.img-stat .stat-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    &.camera-stat .stat-icon {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    &.total-stat .stat-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
  }
}

// 搜索栏
.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

// 表格包装器
.table-wrapper {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  :deep(.el-table) {
    .el-table__row {
      &.image-row {
        background-color: #f8f9fc;
      }
    }
  }
}

// 展开行内容
.expand-content {
  padding: 16px 20px;
  background: #f8f9fc;

  .expand-title {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
    color: #303133;
  }
}

.expand-empty {
  padding: 20px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}

.no-data {
  color: #c0c4cc;
}

// 分页
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

/* ===== 手机端适配（≤768px） ===== */
@media screen and (max-width: 768px) {
  .detection-records-container {
    padding: 12px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stats-cards .stat-card {
    padding: 14px 18px;
  }

  .stats-cards .stat-card .stat-icon {
    width: 44px;
    height: 44px;
    font-size: 22px;
  }

  .stats-cards .stat-card .stat-content .stat-value {
    font-size: 22px;
  }

  .search-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 12px 16px;
  }

  .search-bar .el-input {
    max-width: 100% !important;
  }

  .search-bar .el-select {
    width: 100% !important;
  }

  .search-bar .el-button {
    width: 100%;
    justify-content: center;
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .table-wrapper :deep(.el-table) {
    min-width: 700px;
  }

  .pagination-wrapper {
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
  }

  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }

  .pagination-wrapper :deep(.el-pagination .el-pagination__total) {
    margin-right: 0;
  }
}
</style>