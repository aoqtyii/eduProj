<template>
    <el-container direction="vertical" style="padding: 20px;">
      <el-header height="auto" style="padding-bottom: 20px;">
        <h1>练习中心</h1>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col v-if="loading" :span="24">
            <el-skeleton :rows="5" animated />
          </el-col>
          <el-col v-else-if="error" :span="24">
             <el-alert
                title="加载练习模块失败"
                type="error"
                :description="error"
                show-icon
                :closable="false"
              />
          </el-col>
           <el-col v-else-if="modules.length === 0" :span="24">
             <el-empty description="暂无可用练习模块"></el-empty>
           </el-col>
          <el-col
            v-for="module in modules"
            :key="module.id"
            :xs="24" :sm="12" :md="8" :lg="6"
            style="margin-bottom: 20px;"
          >
            <el-card shadow="hover" class="practice-card">
              <template #header>
                <div class="card-header">
                  <span>{{ module.title }}</span>
                </div>
              </template>
              <p class="module-description">{{ module.description || '暂无描述' }}</p>
              <template #footer>
                  <el-button
                      type="primary"
                      @click="startPractice(module.id)"
                      :loading="startingSession === module.id"
                   >
                      开始练习
                  </el-button>
               </template>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessage, ElMessageBox } from 'element-plus';
  // Import the API service functions
  import { getPracticeModules, startPracticeSession } from '@/services/practice';
  
  const router = useRouter();
  const modules = ref([]);
  const loading = ref(true);
  const error = ref(null);
  const startingSession = ref(null); // Track which module's session is being started
  
  // Fetch modules when component mounts
  onMounted(async () => {
    try {
      loading.value = true;
      error.value = null;
      modules.value = await getPracticeModules();
    } catch (err) {
      console.error("Failed to load practice modules:", err);
      error.value = err.response?.data?.detail || err.message || '无法连接到服务器。';
      ElMessage.error('加载练习模块列表失败: ' + error.value);
    } finally {
      loading.value = false;
    }
  });
  
  // Function to start a practice session
  const startPractice = async (moduleId) => {
    startingSession.value = moduleId;
    try {
      const session = await startPracticeSession(moduleId);
      console.log('Practice session started:', session);
      // Navigate to the session page with the new session ID
      router.push({ name: 'PracticeSession', params: { sessionId: session.id } });
    } catch (err) {
      console.error(`Failed to start practice session for module ${moduleId}:`, err);
      const errorMsg = err.response?.data?.detail || err.message || '无法开始练习。';
       ElMessageBox.alert(`开始练习失败: ${errorMsg}`, '错误', {
          confirmButtonText: '确定',
          type: 'error',
       });
    } finally {
      startingSession.value = null; // Reset loading state for the button
    }
  };
  </script>
  
  <style scoped>
  .practice-card {
    height: 100%; /* Make cards in a row the same height */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .card-header {
    font-weight: bold;
  }
  
  .module-description {
    font-size: 14px;
    color: #606266;
    margin-bottom: 15px;
    flex-grow: 1; /* Allow description to take up space */
    min-height: 40px; /* Ensure minimum height for alignment */
  }
  
  .el-card__footer {
      padding: 10px 20px;
      border-top: 1px solid #ebeef5;
      box-sizing: border-box;
      text-align: right; /* Align button to the right */
  }
  </style>