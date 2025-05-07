<template>
    <div class="forgot-password-container">
      <el-card class="forgot-password-box" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>忘记密码</span>
          </div>
        </template>
  
        <el-form
          ref="resetFormRef"
          :model="resetForm"
          :rules="resetRules"
          label-position="top"
          @submit.prevent="handleResetRequest"
        >
          <p class="info-text">
            请输入与您的账户关联的用户名或邮箱地址。如果账户存在，我们将向您发送密码重置说明。
          </p>
  
          <el-form-item label="用户名或邮箱地址" prop="identifier">
            <el-input
              v-model.trim="resetForm.identifier"
              placeholder="输入用户名或邮箱"
              :prefix-icon="Message"
              clearable
              size="large"
              data-testid="identifier-input"
            />
          </el-form-item>
  
          <el-form-item>
            <el-button
              type="primary"
              class="submit-button"
              :loading="loading"
              @click="handleResetRequest"
              size="large"
              native-type="submit"
              data-testid="submit-button"
            >
              {{ loading ? '处理中...' : '发送重置说明' }}
            </el-button>
          </el-form-item>
  
           <el-form-item>
             <div class="back-to-login">
               <el-link type="primary" @click="goBackToLogin" data-testid="back-to-login-link">
                 返回登录
              </el-link>
             </div>
           </el-form-item>
  
        </el-form>
      </el-card>
       <div class="footer">
         </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElForm, ElFormItem, ElInput, ElButton, ElCard, ElLink, ElMessage } from 'element-plus';
  import { Message } from '@element-plus/icons-vue'; // Using Message icon for email/identifier
  import { requestPasswordReset } from '@/services/auth'; // Import the API service function
  
  // --- Composables ---
  const router = useRouter();
  
  // --- Refs and Reactive State ---
  const resetFormRef = ref(null);
  const loading = ref(false);
  
  // Form data model
  const resetForm = reactive({
    identifier: '', // Can be username or email
  });
  
  // --- Validation Rules ---
  const resetRules = reactive({
    identifier: [
      { required: true, message: '请输入用户名或邮箱地址', trigger: 'blur' },
      // Optional: Add email validation if you only accept emails
      // { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
    ],
  });
  
  // --- Methods ---
  
  /**
   * Handles the password reset request submission.
   */
  const handleResetRequest = async () => {
    if (!resetFormRef.value) return;
  
    await resetFormRef.value.validate(async (valid) => {
      if (valid) {
        loading.value = true;
        try {
          // Call the API service function
          await requestPasswordReset(resetForm.identifier);
  
          // IMPORTANT: Show a generic success message regardless of whether the
          // identifier was actually found, to prevent user enumeration attacks.
          ElMessage.success('请求已提交。如果提供的标识符与账户关联，您将很快收到包含重置说明的邮件或通知。');
  
          // Optional: You might want to clear the form or redirect slightly differently
          // resetForm.identifier = ''; // Clear the form
          // router.push({ name: 'Login' }); // Or redirect back to login after showing message
  
        } catch (error) {
          // Log the technical error, but show a generic message to the user
          console.error('Password reset request failed:', error);
          ElMessage.error('发送请求时遇到问题，请稍后重试。');
        } finally {
          loading.value = false;
        }
      } else {
        ElMessage.warning('请输入有效的用户名或邮箱地址。');
        return false;
      }
    });
  };
  
  /**
   * Navigates the user back to the login page.
   */
  const goBackToLogin = () => {
    router.push({ name: 'Login' });
  };
  
  </script>
  
  <style scoped>
  /* Reuse similar styles from LoginPage for consistency */
  .forgot-password-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(to bottom right, #f0f4f8, #d9e2ec);
    padding: 20px;
    box-sizing: border-box;
  }
  
  .forgot-password-box {
    width: 100%;
    max-width: 450px; /* Can be slightly wider for more text */
    border-radius: 8px;
    background-color: #fff;
  }
  
  .card-header {
    text-align: center;
    font-size: 1.6em;
    font-weight: 600;
    color: #303133;
     padding: 20px 0 10px 0;
  }
  
  .el-form {
    padding: 10px 30px 20px 30px;
  }
  
  .info-text {
    margin-bottom: 20px;
    color: #606266;
    font-size: 0.95em;
    line-height: 1.6;
    text-align: left;
  }
  
  .submit-button {
    width: 100%;
    font-size: 1.1em;
  }
  
  .back-to-login {
    width: 100%;
    text-align: center;
    margin-top: 10px; /* Space above the link */
  }
  
  .footer {
    margin-top: 25px;
    text-align: center;
    color: #a0a3a8;
    font-size: 0.85em;
  }
  </style>