<template>
  <div class="purchase-container">
    <!-- 头部统计区 - 优化间距 -->
    <div class="stats-header">
      <div class="header-content">
        <div class="title-section">
          <el-icon class="cart-icon"><ShoppingCart /></el-icon>
          <h2>🛒 农资采购管理</h2>
          <p class="subtitle">科学采购 · 精准管理 · 降本增效</p>
        </div>
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">采购记录</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ totalAmount.toFixed(2) }}</div>
              <div class="stat-label">采购总额</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalQuantity }}</div>
              <div class="stat-label">采购总量</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索筛选区 - 优化布局 -->
    <div class="search-section">
      <el-card shadow="hover" class="search-card">
        <div class="search-header">
          <div class="search-title">
            <el-icon><Search /></el-icon>
            <span>筛选查询</span>
          </div>
        </div>
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="产品名称">
            <el-input
                v-model="searchForm.search"
                placeholder="请输入产品名称"
                clearable
                prefix-icon="Search"
                style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="供货商">
            <el-input
                v-model="searchForm.supplier"
                placeholder="请输入供货商"
                clearable
                prefix-icon="OfficeBuilding"
                style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="地区">
            <el-input
                v-model="searchForm.region"
                placeholder="请输入地区"
                clearable
                prefix-icon="Location"
                style="width: 160px"
            />
          </el-form-item>
          <el-form-item label="采购人">
            <el-input
                v-model="searchForm.manager"
                placeholder="请输入采购人"
                clearable
                prefix-icon="User"
                style="width: 160px"
            />
          </el-form-item>
          <el-form-item class="search-buttons">
            <el-button type="primary" @click="handleSearch" :loading="loading">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button type="success" @click="openAddDialog">
              <el-icon><Plus /></el-icon>
              新增采购
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 表格区域 - 优化卡片内边距 -->
    <div class="table-section">
      <el-card shadow="hover" class="table-card">
        <div class="table-header">
          <div class="table-title">
            <el-icon><List /></el-icon>
            <span>采购记录列表</span>
          </div>
          <div class="table-stats">
            <span>共 {{ pagination.total }} 条记录</span>
          </div>
        </div>
        <el-table
            :data="tableData"
            v-loading="loading"
            stripe
            style="width: 100%"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266', height: '48px' }"
            :row-style="{ height: '56px' }"
        >
          <el-table-column prop="id" label="ID" width="80" align="center" />
          <el-table-column prop="productName" label="产品名称" min-width="130" align="center">
            <template #default="{ row }">
              <el-tag type="primary" effect="light" size="large">{{ row.productName }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="单价(元)" width="110" align="center">
            <template #default="{ row }">
              <span style="color: #f56c6c; font-weight: 600; font-size: 14px;">¥{{ row.price }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="success" effect="plain" size="large">{{ row.quantity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="总价(元)" width="130" align="center">
            <template #default="{ row }">
              <span style="color: #e6a23c; font-weight: 600; font-size: 14px;">¥{{ (row.price * row.quantity).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="supplier" label="供货商" min-width="130" align="center" />
          <el-table-column prop="region" label="地区" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" type="info">{{ row.region }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="联系电话" width="130" align="center" />
          <el-table-column prop="manager" label="采购人" width="110" align="center" />
          <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip align="center" />
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" type="primary" link @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" link @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 - 优化间距 -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="pagination.pageNum"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 30, 50]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              background
          />
        </div>
      </el-card>
    </div>

    <!-- 新增/编辑对话框 - 优化表单布局 -->
    <el-dialog
        v-model="dialogVisible"
        :title="dialogType === 'add' ? '➕ 新增采购记录' : '✏️ 编辑采购记录'"
        width="700px"
        :close-on-click-modal="false"
        class="purchase-dialog"
    >
      <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="100px"
          class="purchase-form"
      >
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="产品名称" prop="productName">
              <el-input v-model="formData.productName" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价(元)" prop="price">
              <el-input-number
                  v-model="formData.price"
                  :min="0"
                  :precision="2"
                  :step="0.1"
                  controls-position="right"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="采购数量" prop="quantity">
              <el-input-number
                  v-model="formData.quantity"
                  :min="1"
                  :step="1"
                  controls-position="right"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地区" prop="region">
              <el-select v-model="formData.region" placeholder="请选择地区" style="width: 100%">
                <el-option label="华东" value="华东" />
                <el-option label="华北" value="华北" />
                <el-option label="华南" value="华南" />
                <el-option label="华中" value="华中" />
                <el-option label="东北" value="东北" />
                <el-option label="西北" value="西北" />
                <el-option label="西南" value="西南" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="供货商" prop="supplier">
              <el-input v-model="formData.supplier" placeholder="请输入供货商" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="采购人" prop="manager">
          <el-input v-model="formData.manager" placeholder="请输入采购人" />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
              v-model="formData.remark"
              type="textarea"
              :rows="4"
              placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading" size="large">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="purchaseManage">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus';
import {
  ShoppingCart,
  Document,
  Money,
  Box,
  Search,
  Refresh,
  Plus,
  Edit,
  Delete,
  List
} from '@element-plus/icons-vue';
import request from '/@/utils/request';

interface Purchase {
  id?: number;
  productName: string;
  price: number;
  quantity: number;
  supplier: string;
  region: string;
  phone: string;
  manager: string;
  remark?: string;
}

const loading = ref(false);
const submitLoading = ref(false);
const dialogVisible = ref(false);
const dialogType = ref<'add' | 'edit'>('add');
const formRef = ref<FormInstance>();
const tableData = ref<Purchase[]>([]);

const searchForm = reactive({
  search: '',
  supplier: '',
  region: '',
  manager: ''
});

const pagination = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
});

const formData = reactive<Purchase>({
  productName: '',
  price: 0,
  quantity: 1,
  supplier: '',
  region: '',
  phone: '',
  manager: '',
  remark: ''
});

const formRules: FormRules = {
  productName: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  supplier: [{ required: true, message: '请输入供货商', trigger: 'blur' }],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  manager: [{ required: true, message: '请输入采购人', trigger: 'blur' }]
};

// 统计数据
const totalCount = computed(() => pagination.total);
const totalAmount = computed(() => {
  return tableData.value.reduce((sum, item) => sum + item.price * item.quantity, 0);
});
const totalQuantity = computed(() => {
  return tableData.value.reduce((sum, item) => sum + item.quantity, 0);
});

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    const res = await request.get('/api/purchase', {
      params: {
        ...searchForm,
        pageNum: pagination.pageNum,
        pageSize: pagination.pageSize
      }
    });

    if (res.code === 0) {
      tableData.value = res.data.records || [];
      pagination.total = res.data.total || 0;
    } else {
      ElMessage.error(res.msg || '获取数据失败');
    }
  } catch (error) {
    console.error('获取数据失败:', error);
    ElMessage.error('网络请求失败');
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.pageNum = 1;
  fetchData();
};

// 重置
const handleReset = () => {
  searchForm.search = '';
  searchForm.supplier = '';
  searchForm.region = '';
  searchForm.manager = '';
  handleSearch();
};

// 打开新增对话框
const openAddDialog = () => {
  dialogType.value = 'add';
  resetForm();
  dialogVisible.value = true;
};

// 打开编辑对话框
const openEditDialog = (row: Purchase) => {
  dialogType.value = 'edit';
  Object.assign(formData, row);
  dialogVisible.value = true;
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    submitLoading.value = true;
    try {
      const url = '/api/purchase';
      const method = dialogType.value === 'add' ? 'post' : 'put';

      const res = await request[method](url, formData);

      if (res.code === 0) {
        ElMessage.success(dialogType.value === 'add' ? '添加成功' : '修改成功');
        dialogVisible.value = false;
        fetchData();
      } else {
        ElMessage.error(res.msg || '操作失败');
      }
    } catch (error) {
      console.error('提交失败:', error);
      ElMessage.error('网络请求失败');
    } finally {
      submitLoading.value = false;
    }
  });
};

// 删除
const handleDelete = (row: Purchase) => {
  ElMessageBox.confirm(`确定要删除"${row.productName}"的采购记录吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
      .then(async () => {
        try {
          const res = await request.delete(`/api/purchase/${row.id}`);
          if (res.code === 0) {
            ElMessage.success('删除成功');
            fetchData();
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

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    productName: '',
    price: 0,
    quantity: 1,
    supplier: '',
    region: '',
    phone: '',
    manager: '',
    remark: ''
  });
  formRef.value?.clearValidate();
};

// 分页
const handleSizeChange = (val: number) => {
  pagination.pageSize = val;
  fetchData();
};

const handleCurrentChange = (val: number) => {
  pagination.pageNum = val;
  fetchData();
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped lang="scss">
.purchase-container {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  padding: 24px;
}

// 头部统计区 - 优化间距和卡片大小
.stats-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 32px 40px;
  margin-bottom: 24px;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3);

  .header-content {
    .title-section {
      text-align: center;
      color: white;
      margin-bottom: 32px;

      .cart-icon {
        font-size: 56px;
        margin-bottom: 16px;
        opacity: 0.95;
      }

      h2 {
        margin: 0 0 12px 0;
        font-size: 32px;
        font-weight: 600;
        letter-spacing: 1px;
      }

      .subtitle {
        margin: 0;
        font-size: 15px;
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
        padding: 24px 28px;
        display: flex;
        align-items: center;
        gap: 20px;
        transition: all 0.3s ease;
        cursor: pointer;

        &:hover {
          transform: translateY(-6px);
          box-shadow: 0 16px 32px rgba(0, 0, 0, 0.15);
          background: white;
        }

        .stat-icon {
          width: 64px;
          height: 64px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
          color: white;
          flex-shrink: 0;
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #303133;
            margin-bottom: 8px;
            line-height: 1.2;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
            letter-spacing: 0.5px;
          }
        }
      }
    }
  }
}

// 搜索区 - 优化卡片内边距
.search-section {
  margin-bottom: 24px;

  .search-card {
    border-radius: 16px;
    overflow: hidden;

    :deep(.el-card__body) {
      padding: 0;
    }

    .search-header {
      padding: 18px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      .search-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
        font-size: 16px;
        font-weight: 600;

        .el-icon {
          font-size: 20px;
        }
      }
    }

    .search-form {
      padding: 24px 24px 20px 24px;
      background: white;

      :deep(.el-form-item) {
        margin-bottom: 12px;
        margin-right: 20px;
      }

      .search-buttons {
        margin-left: auto;

        :deep(.el-button) {
          padding: 10px 20px;
          margin-left: 12px;
        }
      }
    }
  }
}

// 表格区 - 优化卡片内边距和表格行高
.table-section {
  .table-card {
    border-radius: 16px;
    overflow: hidden;

    :deep(.el-card__body) {
      padding: 0;
    }

    .table-header {
      padding: 18px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      justify-content: space-between;
      align-items: center;

      .table-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
        font-size: 16px;
        font-weight: 600;

        .el-icon {
          font-size: 20px;
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
        font-weight: 600;
      }

      .el-table__body-wrapper td {
        padding: 14px 0;
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: flex-end;
      padding: 20px 24px;
      background: white;
      border-top: 1px solid #ebeef5;
    }
  }
}

// 对话框样式优化
.purchase-dialog {
  :deep(.el-dialog) {
    border-radius: 20px;
    overflow: hidden;
  }

  :deep(.el-dialog__header) {
    padding: 24px 28px;
    margin: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-bottom: none;

    .el-dialog__title {
      color: white;
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.el-dialog__headerbtn) {
    top: 20px;
    right: 20px;

    .el-dialog__close {
      color: white;
      font-size: 20px;

      &:hover {
        color: rgba(255, 255, 255, 0.8);
      }
    }
  }

  :deep(.el-dialog__body) {
    padding: 28px 28px 12px 28px;
  }

  :deep(.el-dialog__footer) {
    padding: 16px 28px 28px 28px;
    border-top: 1px solid #ebeef5;

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }
}

// 表单样式优化
.purchase-form {
  :deep(.el-input-number) {
    width: 100%;
  }

  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #606266;
  }

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }

  :deep(.el-textarea__inner) {
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
    }
  }
}
</style>