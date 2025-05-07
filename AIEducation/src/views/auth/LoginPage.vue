<template>
  <div class="login-container">
    <div class="welcome-text-container">
      <h2 class="welcome-title">
        欢迎使用！<br>
        第一中学智能教育系统！
      </h2>
      </div>

    <div class="login-box-container">
      <el-card class="login-box" shadow="lg">
        <el-tabs v-model="activeTab" class="login-tabs" @tab-click="handleTabClick">
          <el-tab-pane label="账号登录" name="password">
            <div class="tab-content password-content">
              <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top" @submit.prevent="handleLogin" class="login-form">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model.trim="loginForm.username" placeholder="请输入用户名/学号" :prefix-icon="User" clearable size="large" data-testid="username-input" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                  <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password :prefix-icon="Lock" clearable size="large" data-testid="password-input" @keyup.enter="handleLogin" />
                </el-form-item>
                <el-form-item>
                  <div class="form-actions">
                    <el-link type="primary" @click="handleForgotPassword" data-testid="forgot-password-link"> 忘记密码? </el-link>
                  </div>
                </el-form-item>
                <el-form-item class="login-button-item">
                  <el-button type="primary" class="login-button" :loading="loading" @click="handleLogin" size="large" native-type="submit" data-testid="login-button">
                    {{ loading ? '登录中...' : '登 录' }}
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <el-tab-pane label="扫码登录" name="qrcode">
            <div class="tab-content qrcode-content">
               <div class="qr-code-container">
                  <el-skeleton :loading="qrLoading" animated>
                    <template #template>
                      <el-skeleton-item variant="image" style="width: 180px; height: 180px;" />
                    </template>
                    <template #default>
                      <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="登录二维码" class="qr-code-image"/>
                      <div v-else class="qr-code-placeholder">无法加载二维码</div>
                    </template>
                  </el-skeleton>
                  <div v-if="qrStatus === 'expired'" class="qr-code-overlay">
                    <p>二维码已过期</p>
                    <el-button type="primary" plain @click="loadQrCode" :icon="RefreshRight">点击刷新</el-button>
                  </div>
               </div>
              <p class="tab-info-text">请使用 XXX App 扫描二维码登录</p>
              <p v-if="qrStatus === 'scanned'" class="qr-status-text">已扫描，请在App上确认登录</p>
            </div>
          </el-tab-pane>

          <el-tab-pane label="第三方登录" name="thirdparty">
              <div class="tab-content third-party-content">
                <p class="tab-info-text">使用第三方账号快速登录</p>
                <div class="third-party-buttons">
                  <el-button circle size="large" @click="handleThirdPartyLogin('wechat')"> <el-icon :size="24"><ChatDotRound /></el-icon> </el-button>
                  <el-button circle size="large" @click="handleThirdPartyLogin('github')"> <el-icon :size="24"><Platform /></el-icon> </el-button>
                  <el-button circle size="large" @click="handleThirdPartyLogin('qq')"> <el-icon :size="24"><Promotion /></el-icon> </el-button>
                </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <div class="footer">
      </div>
  </div>
</template>

<script setup>
// Script content remains the same as previous version
import { ref, reactive, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  ElForm, ElFormItem, ElInput, ElButton, ElCard, ElLink, ElMessage,
  ElTabs, ElTabPane, ElIcon, ElSkeleton, ElSkeletonItem
} from 'element-plus';
import { User, Lock, RefreshRight, Platform, ChatDotRound, Promotion } from '@element-plus/icons-vue';
import { useAuthStore } from '@/store/auth';

const router = useRouter();
const authStore = useAuthStore();
const loginFormRef = ref(null);
const loading = ref(false);
const activeTab = ref('password');
const loginForm = reactive({ username: '', password: '' });
const qrCodeUrl = ref('');
const qrLoading = ref(false);
const qrStatus = ref('');
let qrPollingInterval = null;
const loginRules = reactive({
  username: [{ required: true, message: '请输入用户名或学号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
});

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const success = await authStore.login({ username: loginForm.username, password: loginForm.password });
        if (!success) ElMessage.error('登录失败，请检查用户名或密码。');
      } catch (error) { console.error('Login component error:', error); ElMessage.error('登录过程中发生错误，请稍后重试。'); }
      finally { loading.value = false; }
    } else { ElMessage.warning('请按要求填写登录信息。'); return false; }
  });
};
const handleForgotPassword = () => router.push({ name: 'ForgotPassword' });
const loadQrCode = async () => {
  console.log('Loading QR Code...'); qrLoading.value = true; qrCodeUrl.value = ''; qrStatus.value = 'loading'; stopQrPolling();
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)); const uniqueId = Date.now();
    qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=login_session_${uniqueId}`;
    qrStatus.value = 'waiting'; startQrPolling(uniqueId);
  } catch (error) { console.error("Failed to load QR code:", error); ElMessage.error("无法加载二维码，请稍后重试。"); qrStatus.value = 'error'; }
  finally { qrLoading.value = false; }
};
const checkQrStatus = async (sessionId) => {
  console.log(`Checking QR status for session ${sessionId}...`);
  try {
    const randomStatus = ['waiting', 'scanned', 'success', 'expired'][Math.floor(Math.random() * 4)];
    const statusFromServer = randomStatus; qrStatus.value = statusFromServer;
    if (statusFromServer === 'success') {
      stopQrPolling(); ElMessage.success("扫码登录成功！"); localStorage.setItem('authToken', 'qr_jwt_token_demo');
      localStorage.setItem('authUser', JSON.stringify({ username: `qr_user_${sessionId}`, name: '扫码用户' }));
      authStore.initializeAuth(); router.push('/app/dashboard');
    } else if (statusFromServer === 'expired') { stopQrPolling(); } else if (statusFromServer === 'error') { stopQrPolling(); ElMessage.error("二维码检查出错。"); }
  } catch (error) { console.error("Error checking QR status:", error); }
};
const startQrPolling = (sessionId) => { stopQrPolling(); qrPollingInterval = setInterval(() => checkQrStatus(sessionId), 3000); };
const stopQrPolling = () => { if (qrPollingInterval) { clearInterval(qrPollingInterval); qrPollingInterval = null; console.log("QR Polling stopped."); } };
const handleThirdPartyLogin = (provider) => { console.log(`Initiating login with ${provider}...`); ElMessage.info(`使用 ${provider} 登录 (功能待实现)`); };
watch(activeTab, (newTab, oldTab) => { if (newTab === 'qrcode') loadQrCode(); else { stopQrPolling(); if (oldTab === 'qrcode') { qrStatus.value = ''; qrCodeUrl.value = ''; } } });
onUnmounted(stopQrPolling);
const handleTabClick = (tab) => console.log('Clicked tab:', tab.props.name);


</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: space-around;
  /* 保持 align-items: center 以确保 login-box-container 垂直居中 */
  align-items: center; /* 还原 */
  min-height: 100vh;
  width: 100%;
  padding: 20px 5%; /* 还原原始 padding */
  box-sizing: border-box;
  background-image: url('@/assets/images/login-bg.jpg'); /* TODO: Replace */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #eef2f7;
  position: relative;
}

/* --- Left Side: Welcome Text --- */
.welcome-text-container {
  flex: 1;
  max-width: 600px;
  text-align: center;
  /* 保持原始的内部 flex 居中，transform 是基于此位置进行偏移 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ffffff; /* White text */
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5); /* Text shadow for readability */
  z-index: 2;
  /* 移除 padding-top，因为我们用 transform 控制位置 */
  margin-left: 15%;
}

.welcome-title {
  font-size: 2.8em;
  font-weight: 600;
  line-height: 1.4;
  margin: 0;
  /* 新增：使用 transform 将标题相对于其原始中心位置向上移动 */
  /* -60px 是一个示例值，您需要根据实际视觉效果调整 */
  transform: translateY(-80px); /* 调整此值使标题顶部与登录框顶部对齐 */
}

/* --- Right Side: Login Box --- */
.login-box-container {
  flex-shrink: 0; /* Prevent login box from shrinking */
  width: 100%;
  max-width: 420px; /* Keep login box width */
  z-index: 2;
  /* 因为父容器 align-items: center，此容器将保持垂直居中 */
}

/* --- 保持登录框及内部其他样式不变 --- */


.login-box {
  width: 100%;
  max-width: none;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  position: relative;
  z-index: 3;
  margin: 0;
  /* --- Font Change Here --- */
  font-family: "Microsoft YaHei", SimHei, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
   :deep(.el-card__body) { padding: 0; }
}

/* Tab Styles */
.login-tabs {
   width: 100%;
   /* min-height removed, let content define height */
}
:deep(.el-tabs__header) { margin-bottom: 0; }
:deep(.el-tabs__nav-wrap) { padding: 0 20px; }
:deep(.el-tabs__nav) { float: none; text-align: center; }
:deep(.el-tabs__item) { font-size: 1.05em; height: 55px; line-height: 55px; font-weight: 500; }
:deep(.el-tabs__content) { }
:deep(.el-tab-pane) { padding: 25px 25px 30px 25px; box-sizing: border-box; }

/* Content within tabs, ensuring consistent height */
.tab-content {
  min-height: 340px; /* Keep min-height for consistent card size */
  display: flex; flex-direction: column; align-items: center;
  justify-content: flex-start; box-sizing: border-box;
}
.password-content { justify-content: center; }
.qrcode-content { justify-content: center; padding-top: 10px; }
.third-party-content { justify-content: center; }

/* Form Styles */
.login-form { padding: 0; width: 100%; }
.el-form-item { margin-bottom: 20px; }
:deep(.el-form-item__label) { color: #606266; line-height: 1.2; margin-bottom: 6px; }
:deep(.el-input__inner) { height: 42px; }
:deep(.el-input) { width: 100%; }
:deep(.el-input__icon) { font-size: 15px; }
.form-actions { width: 100%; display: flex; justify-content: flex-end; align-items: center; margin-top: -15px; margin-bottom: 15px; }
.login-button-item { margin-top: 10px; margin-bottom: 0 !important;}
.login-button { width: 100%; font-size: 1.05em; height: 42px; letter-spacing: 1px; transition: background-color 0.3s ease, transform 0.1s ease; }
.login-button:hover { background-color: var(--el-color-primary-light-3); }
.login-button:active { transform: scale(0.98); }

/* QR & 3rd Party Styles */
.tab-info-text { color: #606266; margin-top: 15px; margin-bottom: 20px; font-size: 0.95em; text-align: center; }
.qr-code-container { width: 180px; height: 180px; margin: 10px auto 0 auto; position: relative; background-color: #f9f9f9; border: 1px solid #eee; display: flex; justify-content: center; align-items: center; flex-shrink: 0; }
.qr-code-image { display: block; width: 100%; height: 100%; }
.qr-code-placeholder { color: #909399; font-size: 0.9em; }
.qr-code-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(255, 255, 255, 0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; color: #606266; }
.qr-code-overlay p { margin-bottom: 15px; font-weight: 500; }
.qr-status-text { color: var(--el-color-success); font-size: 0.9em; margin-top: 10px; }
.third-party-buttons { display: flex; gap: 25px; margin-top: 10px; }

.footer {
  position: absolute; bottom: 20px; left: 0; right: 0;
  text-align: center; color: #fff; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  font-size: 0.9em; z-index: 1;
}
</style>