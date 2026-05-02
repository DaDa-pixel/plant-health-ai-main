<template>
  <div class="login-container">
    <div class="bg-bubbles">
      <li v-for="n in 10" :key="n"></li>
    </div>

    <div class="login-box animate__animated animate__fadeIn">
      <!-- 顶部品牌标识 -->
      <div class="brand-header">
        <div class="brand-icon">
          <span class="brand-icon-text">🌾</span>
        </div>
      </div>

      <div class="title">
        <h2>基于神经网络的农作物病害识别和智能咨询系统</h2>
        <p class="subtitle">智慧农业 · AI 智能诊断 · 科学种植</p>
      </div>

      <el-form :model="ruleForm" :rules="registerRules" ref="ruleFormRef">
        <el-form-item prop="username">
          <el-input v-model="ruleForm.username" placeholder="请输入用户名" prefix-icon="User" class="custom-input" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="ruleForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password class="custom-input" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="login-btn" @click="submitForm(ruleFormRef)"> 登录 </el-button>
        </el-form-item>
      </el-form>

      <div class="options">
        <router-link to="/register">注册账号</router-link>
        <span class="divider-line">|</span>
        <a href="#">忘记密码</a>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive, computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { initFrontEndControlRoutes } from '/@/router/frontEnd';
import { initBackEndControlRoutes } from '/@/router/backEnd';
import { Session } from '/@/utils/storage';
import { formatAxis } from '/@/utils/formatTime';
import { NextLoading } from '/@/utils/loading';
import type { FormInstance, FormRules } from 'element-plus';
import request from '/@/utils/request';

// 定义变量内容
const { t } = useI18n();
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const route = useRoute();
const router = useRouter();
const formSize = ref('default');
const ruleFormRef = ref<FormInstance>();

/*
* 定义全局变量，等价Vue2中的data() return。
*/
const ruleForm = reactive({
  username: '',
  password: '',
});

/*
* 校验规则。
*/
const registerRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在3-20个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在3-20个字符', trigger: 'blur' },
  ],
});

/*
* 提交后的方法。
*/
// 时间获取
const currentTime = computed(() => {
  return formatAxis(new Date());
});
// 登录
const onSignIn = async () => {
  // 存储 token 到浏览器缓存
  Session.set('token', Math.random().toString(36).substr(0));
  // 模拟数据，对接接口时，记得删除多余代码及对应依赖的引入。用于 `/src/stores/userInfo.ts` 中不同用户登录判断（模拟数据）
  Cookies.set('userName', ruleForm.username);
  if (!themeConfig.value.isRequestRoutes) {
    // 前端控制路由，2、请注意执行顺序
    const isNoPower = await initFrontEndControlRoutes();
    signInSuccess(isNoPower);
  } else {
    // 模拟后端控制路由，isRequestRoutes 为 true，则开启后端控制路由
    // 添加完动态路由，再进行 router 跳转，否则可能报错 No match found for location with path "/"
    const isNoPower = await initBackEndControlRoutes();
    // 执行完 initBackEndControlRoutes，再执行 signInSuccess
    signInSuccess(isNoPower);
  }
};
// 登录成功后的跳转
const signInSuccess = (isNoPower: boolean | undefined) => {
  if (isNoPower) {
    ElMessage.warning('抱歉，您没有登录权限');
    Session.clear();
  } else {
    // 初始化登录成功时间问候语
    let currentTimeInfo = currentTime.value;
    // 登录成功，跳到转首页
    // 如果是复制粘贴的路径，非首页/登录页，那么登录成功后重定向到对应的路径中
    if (route.query?.redirect) {
      router.push({
        path: <string>route.query?.redirect,
        query: Object.keys(<string>route.query?.params).length > 0 ? JSON.parse(<string>route.query?.params) : '',
      });
    } else {
      router.push('/');
    }
    // 登录成功提示
    const signInText = t('message.signInText');
    ElMessage.success(`${currentTimeInfo}，${signInText}`);
    // 添加 loading，防止第一次进入界面时出现短暂空白
    NextLoading.start();
  }
};
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate((valid) => {
    if (valid) {
      request.post('/api/user/login', ruleForm).then((res) => {
        console.log(res);
        if (res.code == 0) {
          Cookies.set('role', res.data.role); //  设置角色
          //登录成功
          onSignIn();
        } else {
          ElMessage({
            type: 'error',
            message: res.msg,
          });
        }
      });
    } else {
      console.log('error submit!');
      ElMessage.error('请完善必填信息');
    }
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('/bg1.png');
  background-position: center;
  background-repeat: no-repeat;
  background-size: 100% 100%;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-box {
  position: relative;
  z-index: 2;
  width: 460px;
  padding: 40px 50px 50px;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transform: translateY(20px);
  animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}

/* ========== 品牌标识 ========== */
.brand-header {
  text-align: center;
  margin-bottom: 24px;
}

.brand-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(67, 233, 123, 0.3);
  animation: floatIcon 3s ease-in-out infinite;
}

.brand-icon-text {
  font-size: 32px;
  line-height: 1;
}

@keyframes floatIcon {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* ========== 标题 ========== */
.title {
  text-align: center;
  margin-bottom: 32px;
}

.title h2 {
  font-size: 22px;
  color: #1a2332;
  margin: 0 auto 10px;
  font-weight: 700;
  line-height: 1.5;
  max-width: 380px;
}

.subtitle {
  font-size: 13px;
  color: #7f8c8d;
  letter-spacing: 3px;
  margin: 0;
  background: linear-gradient(135deg, #2f80ed, #56ccf2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 500;
}

/* ========== 输入框 ========== */
:deep(.custom-input .el-input__wrapper) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  padding: 14px 16px;
  height: 48px;
  background: #f8fafc;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  background: #fff;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(47, 128, 237, 0.2);
  border-color: #2f80ed;
  background: #fff;
}

:deep(.custom-input .el-input__prefix) {
  font-size: 16px;
  color: #9ca3af;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

/* ========== 登录按钮 ========== */
.login-btn {
  width: 100%;
  padding: 14px 0;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2f80ed 0%, #56ccf2 100%);
  border: none;
  margin-top: 6px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.login-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(47, 128, 237, 0.35);
}

.login-btn:active {
  transform: translateY(0);
}

/* ========== 选项链接 ========== */
.options {
  margin-top: 28px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
}

.options a {
  color: #2f80ed;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  font-weight: 500;
  padding: 4px 6px;
}

.divider-line {
  color: #ddd;
  margin: 0 14px;
  font-size: 14px;
}

.options a:hover {
  color: #56ccf2;
  text-decoration: none;
  background: rgba(47, 128, 237, 0.06);
  border-radius: 6px;
}

/* ========== 背景气泡动画 ========== */
.bg-bubbles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
  pointer-events: none;
}

.bg-bubbles li {
  position: absolute;
  list-style: none;
  display: block;
  width: 40px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.12);
  bottom: -160px;
  animation: square 25s infinite;
  transition-timing-function: linear;
  border-radius: 50%;
}

.bg-bubbles li:nth-child(1) {
  left: 10%;
  width: 80px;
  height: 80px;
  animation-delay: 0s;
}

.bg-bubbles li:nth-child(2) {
  left: 20%;
  width: 90px;
  height: 90px;
  animation-delay: 2s;
  animation-duration: 17s;
}

.bg-bubbles li:nth-child(3) {
  left: 25%;
  animation-delay: 4s;
}

.bg-bubbles li:nth-child(4) {
  left: 40%;
  width: 60px;
  height: 60px;
  animation-duration: 22s;
}

.bg-bubbles li:nth-child(5) {
  left: 70%;
  width: 120px;
  height: 120px;
}

.bg-bubbles li:nth-child(6) {
  left: 80%;
  width: 90px;
  height: 90px;
  animation-delay: 3s;
}

.bg-bubbles li:nth-child(7) {
  left: 32%;
  width: 60px;
  height: 60px;
  animation-delay: 7s;
}

.bg-bubbles li:nth-child(8) {
  left: 55%;
  width: 20px;
  height: 20px;
  animation-delay: 15s;
  animation-duration: 40s;
}

.bg-bubbles li:nth-child(9) {
  left: 25%;
  width: 10px;
  height: 10px;
  animation-delay: 2s;
  animation-duration: 40s;
}

.bg-bubbles li:nth-child(10) {
  left: 90%;
  width: 160px;
  height: 160px;
  animation-delay: 11s;
}

@keyframes square {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(-1000px) rotate(600deg);
    opacity: 0;
  }
}

/* ========== 入场动画 ========== */
@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* ========== 表单项入场 ========== */
:deep(.el-form-item) {
  opacity: 0;
}

:deep(.el-form-item:nth-child(1)) {
  transform: translateX(-30px);
  animation: fadeInItem 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
}

:deep(.el-form-item:nth-child(2)) {
  transform: translateX(30px);
  animation: fadeInItem 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.35s forwards;
}

:deep(.el-form-item:nth-child(3)) {
  animation: fadeInItem 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.5s forwards;
}

@keyframes fadeInItem {
  from {
    transform: translateX(-30px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

:deep(.el-form-item:nth-child(2)) {
  animation-name: fadeInItemRight;
}

@keyframes fadeInItemRight {
  from {
    transform: translateX(30px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .login-box {
    width: 92%;
    padding: 30px 24px 40px;
  }

  .title h2 {
    font-size: 18px;
  }

  .subtitle {
    font-size: 12px;
    letter-spacing: 2px;
  }

  .brand-icon {
    width: 52px;
    height: 52px;
  }

  .brand-icon-text {
    font-size: 26px;
  }
}
</style>
