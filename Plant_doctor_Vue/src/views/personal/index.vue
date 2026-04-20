<template>
  <div class="personal-container">
    <div class="personal-wrapper">
      <div class="content-wrapper">
        <div class="left-section">
          <div class="avatar-card">
            <div class="avatar-wrapper">
              <el-upload
                  class="avatar-uploader"
                  action="http://localhost:9999/files/upload"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
              >
                <img v-if="imageUrl" :src="imageUrl" class="avatar-image" alt="用户头像" />
                <div v-else class="avatar-placeholder">
                  <span>用户头像</span>
                </div>
              </el-upload>
            </div>
            <h3 class="welcome-text">欢迎回来</h3>
            <div class="user-role">{{ displayRole }}</div>
          </div>
        </div>

        <div class="right-section">
          <div class="info-card">
            <h2 class="section-title">个人信息</h2>
            <el-form
                ref="formRef"
                :model="state.form"
                :rules="rules"
                label-width="100px"
                class="info-form"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="账号" prop="username">
                    <el-input v-model="state.form.username" placeholder="请输入账号">
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="密码" prop="password">
                    <el-input
                        v-model="state.form.password"
                        type="password"
                        placeholder="请输入密码"
                        show-password
                    >
                      <template #prefix>
                        <el-icon><Lock /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="姓名" prop="name">
                    <el-input v-model="state.form.name" placeholder="请输入姓名">
                      <template #prefix>
                        <el-icon><UserFilled /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="性别" prop="sex">
                    <el-select v-model="state.form.sex" placeholder="请选择性别">
                      <el-option label="男" value="男" />
                      <el-option label="女" value="女" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Email" prop="email">
                    <el-input v-model="state.form.email" placeholder="请输入Email">
                      <template #prefix>
                        <el-icon><Message /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="手机号码" prop="tel">
                    <el-input v-model="state.form.tel" placeholder="请输入手机号码">
                      <template #prefix>
                        <el-icon><Phone /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item>
                <el-button type="primary" @click="submitForm" :icon="Check" class="submit-button">
                  确认修改
                </el-button>
              </el-form-item>
            </el-form>
          </div>
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
import { Plus, Check, User, Lock, UserFilled, Message, Phone } from '@element-plus/icons-vue';
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
    { required: true, message: '请输入手机号码', trigger: 'blur' }
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
  return role || '';
});

const getTableData = () => {
  request.get('/api/user/' + userInfos.value.userName).then((res) => {
    if (res.code == 0) {
      state.form = res.data;
      imageUrl.value = state.form.avatar;
    } else {
      ElMessage({
        type: 'error',
        message: res.msg,
      });
    }
  });
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
      if (res.data && res.data.avatar) {
        userInfos.value.photo = res.data.avatar;
        Session.set('userInfo', userInfos.value);
      }

      ElMessage.success('修改成功！');
      getTableData();
    } else {
      ElMessage({
        type: 'error',
        message: res.msg,
      });
    }
  });
};

onMounted(() => {
  getTableData();
});
</script>

<style scoped lang="scss">
.personal-container {
  height: calc(100vh - 60px);
  padding-top: 32px;
  background-color: #f5f7fa;
  overflow: hidden;

  .personal-wrapper {
    height: 100%;
    max-width: 1200px;
    margin: 0 auto;

    .content-wrapper {
      height: calc(100% - 32px);
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 32px;

      .left-section {
        .avatar-card {
          background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
          border-radius: 16px;
          padding: 40px 32px;
          text-align: center;
          height: fit-content;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);

          .avatar-wrapper {
            margin-bottom: 24px;

            .avatar-uploader {
              :deep(.el-upload) {
                width: 180px;
                height: 180px;
                margin: 0 auto;
                border-radius: 50%;
                overflow: hidden;
                cursor: pointer;
                transition: all 0.3s ease;
                background: #f5f7fa;
                border: 3px solid #fff;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                display: flex;
                align-items: center;
                justify-content: center;

                &:hover {
                  transform: translateY(-2px);
                  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
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
                justify-content: center;
                align-items: center;
                color: #909399;
                font-size: 16px;
              }
            }
          }

          .welcome-text {
            font-size: 20px;
            color: #2c3e50;
            margin: 0 0 16px;
            font-weight: 600;
          }

          .user-role {
            font-size: 15px;
            color: #409eff;
            font-weight: 500;
            padding: 8px 20px;
            background: rgba(64, 158, 255, 0.1);
            border-radius: 20px;
            display: inline-block;
          }
        }
      }

      .right-section {
        .info-card {
          background: #ffffff;
          border-radius: 16px;
          padding: 40px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);

          .section-title {
            font-size: 24px;
            color: #2c3e50;
            margin: 0 0 32px;
            font-weight: 600;
          }

          .info-form {
            :deep(.el-form-item__label) {
              font-weight: 500;
              color: #2c3e50;
            }

            :deep(.el-input__wrapper) {
              box-shadow: 0 0 0 1px #e4e7ed inset;
              border-radius: 8px;
              padding: 0 12px;
              height: 42px;
              transition: all 0.3s;

              &:hover,
              &.is-focus {
                box-shadow: 0 0 0 1px #409eff inset;
              }

              .el-input__prefix {
                margin-right: 8px;
                color: #909399;
              }
            }

            :deep(.el-select) {
              width: 100%;

              .el-input__wrapper {
                box-shadow: 0 0 0 1px #e4e7ed inset !important;

                &:hover {
                  box-shadow: 0 0 0 1px #409eff inset !important;
                }

                &.is-focus {
                  box-shadow: 0 0 0 1px #409eff inset !important;
                }
              }
            }

            .submit-button {
              padding: 12px 36px;
              font-size: 15px;
              border-radius: 8px;
              background: linear-gradient(135deg, #409eff, #36a2f1);
              border: none;
              transition: all 0.3s ease;
              float: right;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
              }
            }
          }
        }
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .personal-container {
    padding: 16px;

    .personal-wrapper {
      .content-wrapper {
        grid-template-columns: 1fr;
        gap: 24px;

        .info-card {
          padding: 24px;
        }
      }
    }
  }
}
</style>
