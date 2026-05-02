<template>
  <div class="personal-container">
    <div class="personal-wrapper">
      <div class="content-wrapper">
        <!-- 左侧卡片：头像与角色 -->
        <div class="left-section">
          <div class="avatar-card">
            <!-- 顶部渐变装饰 -->
            <div class="card-top-decoration"></div>

            <div class="avatar-wrapper">
              <el-upload
                class="avatar-uploader"
                action="/api/files/upload"
                :show-file-list="false"
                :on-success="handleAvatarSuccess"
              >
                <div class="avatar-inner">
                  <img v-if="imageUrl" :src="imageUrl" class="avatar-image" alt="用户头像" />
                  <div v-else class="avatar-placeholder">
                    <el-icon :size="40"><Camera /></el-icon>
                    <span>上传头像</span>
                  </div>
                </div>
              </el-upload>
            </div>

            <h3 class="welcome-text">{{ greeting }}，{{ state.form.name || '用户' }}</h3>

            <div class="user-role">
              <el-tag :type="roleTagType" effect="plain" size="large" round>
                {{ displayRole }}
              </el-tag>
            </div>

            <div class="divider"></div>

            <div class="stats-info">
              <div class="stat-item">
                <el-icon class="stat-icon"><Key /></el-icon>
                <div class="stat-content">
                  <span class="stat-label">用户 ID</span>
                  <span class="stat-value">{{ state.form.id || '--' }}</span>
                </div>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon time"><Clock /></el-icon>
                <div class="stat-content">
                  <span class="stat-label">加入时间</span>
                  <span class="stat-value">{{ formatDate(state.form.createTime) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧卡片：表单信息 -->
        <div class="right-section">
          <div class="info-card">
            <div class="card-header">
              <div class="header-left">
                <el-icon class="header-icon"><Edit /></el-icon>
                <div class="header-text">
                  <h2 class="section-title">个人信息</h2>
                  <p class="section-desc">管理您的账户信息和个人资料</p>
                </div>
              </div>
            </div>

            <el-form
              ref="formRef"
              :model="state.form"
              :rules="rules"
              label-width="90px"
              class="info-form"
            >
              <el-row :gutter="32">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="账号" prop="username">
                    <el-input v-model="state.form.username" placeholder="请输入账号" clearable>
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="密码" prop="password">
                    <el-input
                      v-model="state.form.password"
                      type="password"
                      placeholder="请输入密码"
                      show-password
                      clearable
                    >
                      <template #prefix>
                        <el-icon><Lock /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="32">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="姓名" prop="name">
                    <el-input v-model="state.form.name" placeholder="请输入姓名" clearable>
                      <template #prefix>
                        <el-icon><UserFilled /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="性别" prop="sex">
                    <el-select v-model="state.form.sex" placeholder="请选择性别" clearable>
                      <el-option label="男" value="男" />
                      <el-option label="女" value="女" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="32">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="state.form.email" placeholder="请输入邮箱" clearable>
                      <template #prefix>
                        <el-icon><Message /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="手机号" prop="tel">
                    <el-input v-model="state.form.tel" placeholder="请输入手机号码" clearable>
                      <template #prefix>
                        <el-icon><Phone /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item>
                <div class="form-actions">
                  <el-button @click="resetForm" :icon="RefreshRight" plain round>
                    重置
                  </el-button>
                  <el-button type="primary" @click="submitForm" :icon="Check" round class="submit-btn">
                    保存修改
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>

      <!-- 页脚信息 -->
      <div class="page-footer">
        <div class="footer-links">
          <span class="footer-link">服务状态</span>
          <span class="divider-dot">·</span>
          <span class="footer-link">开放平台协议</span>
          <span class="divider-dot">·</span>
          <span class="footer-link">隐私政策</span>
          <span class="divider-dot">·</span>
          <span class="footer-text">浙ICP备2023025841号</span>
          <span class="divider-dot">·</span>
          <span class="footer-text">浙公网安备 33010502011812 号</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="personal">
import { reactive, ref, onMounted, computed } from 'vue';
import type { FormInstance } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import {
  Check, User, Lock, UserFilled, Message, Phone, Camera, RefreshRight,
  Key, Clock, Edit
} from '@element-plus/icons-vue';
import { Session } from '/@/utils/storage';

const imageUrl = ref('');
const formRef = ref<FormInstance>();

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  sex: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  tel: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
};

const handleAvatarSuccess = (response: any) => {
  if (response.code === 0) {
    imageUrl.value = response.data;
    state.form.avatar = response.data;
    userInfos.value.photo = response.data;
    Session.set('userInfo', userInfos.value);
    ElMessage.success('头像上传成功');
  } else {
    ElMessage.error('头像上传失败');
  }
};

const state = reactive({
  form: {} as any,
});

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

const displayRole = computed(() => {
  const role = state.form.role;
  if (role === 'admin') return '管理员';
  if (role === 'common') return '普通用户';
  if (role === 'others') return '其他用户';
  return role || '访客';
});

const roleTagType = computed(() => {
  const role = state.form.role;
  if (role === 'admin') return 'danger';
  if (role === 'common') return 'primary';
  if (role === 'others') return 'warning';
  return 'info';
});

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return '早上好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '--';
  const date = new Date(dateStr);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
};

const getTableData = () => {
  request.get('/api/user/' + userInfos.value.userName).then((res) => {
    if (res.code == 0) {
      state.form = res.data;
      imageUrl.value = state.form.avatar;
    } else {
      ElMessage.error(res.msg);
    }
  });
};

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
    getTableData();
    ElMessage.info('已重置为最新信息');
  }
};

const submitForm = async () => {
  if (!formRef.value) return;
  await formRef.value.validate((valid) => {
    if (valid) {
      upData();
    } else {
      ElMessage.error('请完善必填信息');
    }
  });
};

const upData = () => {
  request.post('/api/user/update', state.form).then((res) => {
    if (res.code == 0) {
      ElMessage.success('修改成功！');
      getTableData();
    } else {
      ElMessage.error(res.msg);
    }
  });
};

onMounted(() => {
  getTableData();
});
</script>

<style scoped lang="scss">
.personal-container {
  min-height: calc(100vh - 60px);
  padding: 40px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e8ecf1 100%);

  .personal-wrapper {
    max-width: 1200px;
    margin: 0 auto;

    .content-wrapper {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 36px;
      align-items: start;

      @media (max-width: 1000px) {
        grid-template-columns: 1fr;
        gap: 28px;
      }
    }

    // ========== 页脚 ==========
    .page-footer {
      margin-top: 48px;
      padding-top: 24px;
      border-top: 1px solid #e5e7eb;
      text-align: center;

      .footer-links {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        gap: 4px 12px;
        font-size: 13px;
        color: #9ca3af;
        line-height: 1.8;

        .footer-link {
          color: #6b7280;
          cursor: pointer;
          transition: color 0.2s;

          &:hover {
            color: #409eff;
          }
        }

        .divider-dot {
          color: #d1d5db;
          user-select: none;
        }

        .footer-text {
          color: #9ca3af;
        }
      }
    }
  }
}

// ========== 左侧头像卡片 ==========
.left-section {
  .avatar-card {
    background: #fff;
    border-radius: 20px;
    padding: 0;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
    overflow: hidden;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.1);
    }

    .card-top-decoration {
      height: 88px;
      background: linear-gradient(135deg, #409eff, #66b1ff);

      &::after {
        content: '';
        display: block;
        height: 24px;
        background: #fff;
        border-radius: 0 0 50% 50% / 0 0 24px 24px;
      }
    }

    .avatar-wrapper {
      margin-top: -44px;
      margin-bottom: 20px;
      position: relative;
      z-index: 1;

      .avatar-uploader {
        :deep(.el-upload) {
          width: 100px;
          height: 100px;
          border-radius: 50%;
          overflow: hidden;
          cursor: pointer;
          border: 4px solid #fff;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto;
          background: #f0f2f5;

          &:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 24px rgba(64, 158, 255, 0.25);
          }
        }

        .avatar-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .avatar-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
          color: #909399;
          font-size: 12px;
          width: 100%;
          height: 100%;
        }
      }
    }

    .welcome-text {
      font-size: 20px;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 14px;
      padding: 0 20px;
    }

    .user-role {
      margin-bottom: 20px;

      :deep(.el-tag) {
        padding: 6px 18px;
        font-size: 13px;
        font-weight: 500;
      }
    }

    .divider {
      height: 1px;
      background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
      margin: 0 24px 20px;
    }

    .stats-info {
      padding: 0 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 10px;

      .stat-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        background: #f8fafc;
        border-radius: 12px;
        transition: all 0.2s;

        &:hover {
          background: #f1f5f9;
        }

        .stat-icon {
          width: 38px;
          height: 38px;
          border-radius: 10px;
          background: linear-gradient(135deg, #409eff, #66b1ff);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          flex-shrink: 0;

          &.time {
            background: linear-gradient(135deg, #67c23a, #85ce61);
          }
        }

        .stat-content {
          text-align: left;
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 2px;

          .stat-label {
            font-size: 12px;
            color: #9ca3af;
          }

          .stat-value {
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
          }
        }
      }
    }
  }
}

// ========== 右侧表单卡片 ==========
.right-section {
  .info-card {
    background: #fff;
    border-radius: 20px;
    padding: 36px 32px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
    transition: box-shadow 0.3s;

    &:hover {
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    }

    .card-header {
      margin-bottom: 32px;
      padding-bottom: 20px;
      border-bottom: 1px solid #f1f5f9;

      .header-left {
        display: flex;
        align-items: center;
        gap: 14px;

        .header-icon {
          width: 48px;
          height: 48px;
          border-radius: 14px;
          background: linear-gradient(135deg, #409eff, #66b1ff);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
        }

        .header-text {
          .section-title {
            font-size: 22px;
            font-weight: 600;
            color: #111827;
            margin: 0 0 4px;
          }

          .section-desc {
            font-size: 13px;
            color: #9ca3af;
            margin: 0;
          }
        }
      }
    }

    .info-form {
      :deep(.el-row) {
        margin-bottom: 22px;

        &:last-of-type {
          margin-bottom: 28px;
        }
      }

      :deep(.el-form-item) {
        margin-bottom: 0;
      }

      :deep(.el-form-item__label) {
        font-weight: 500;
        color: #374151;
        font-size: 14px;
        padding-bottom: 4px;
      }

      :deep(.el-input__wrapper) {
        border-radius: 12px;
        box-shadow: 0 0 0 1px #e5e7eb inset;
        background: #fafafa;
        padding: 0 14px;
        height: 44px;
        transition: all 0.2s;

        &:hover {
          box-shadow: 0 0 0 1px #cbd5e1 inset;
          background: #fff;
        }

        &.is-focus {
          box-shadow: 0 0 0 2px #409eff inset !important;
          background: #fff;
        }

        .el-input__prefix {
          color: #9ca3af;
          margin-right: 10px;
        }
      }

      :deep(.el-select) {
        width: 100%;

        .el-input__wrapper {
          border-radius: 12px;
        }
      }

      .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 14px;
        padding-top: 20px;
        border-top: 1px solid #f1f5f9;

        .el-button {
          padding: 12px 28px;
          font-weight: 500;
          font-size: 14px;
          border-radius: 24px;
        }

        .submit-btn {
          background: linear-gradient(135deg, #409eff, #2b7fd9);
          border: none;
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(64, 158, 255, 0.4);
          }
        }
      }
    }
  }
}

// ========== 响应式 ==========
@media (max-width: 768px) {
  .personal-container {
    padding: 20px 16px;
  }

  .right-section .info-card {
    padding: 24px 20px;

    .card-header {
      margin-bottom: 24px;
    }

    .info-form {
      :deep(.el-form-item__label) {
        padding-bottom: 0;
      }

      .form-actions {
        flex-direction: column-reverse;

        .el-button {
          width: 100%;
          justify-content: center;
        }
      }
    }
  }

  .left-section .avatar-card {
    .card-top-decoration {
      height: 64px;
    }
  }

  .personal-wrapper .page-footer {
    margin-top: 32px;
    padding-top: 16px;

    .footer-links {
      font-size: 12px;
      gap: 4px 8px;
    }
  }
}
</style>
