<template>
    <el-container direction="vertical" style="padding: 20px;">
      <el-page-header @back="goBack" style="margin-bottom: 20px;">
         <template #content>
          <span class="text-large font-600 mr-3"> 练习结果: {{ results?.module?.title || '...' }} </span>
        </template>
      </el-page-header>
  
      <el-main v-loading="loading">
        <el-alert v-if="error" title="加载结果失败" :description="errorMessage" type="error" show-icon :closable="false" style="margin-bottom: 20px;" />
  
        <div v-if="results && !error">
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <el-descriptions title="练习总结" :column="2" border>
              <el-descriptions-item label="练习模块">{{ results.module?.title || '未知模块' }}</el-descriptions-item>
              <el-descriptions-item label="最终得分">
                <el-tag :type="results.score >= 60 ? 'success' : 'danger'" size="large">
                  {{ results.score != null ? results.score.toFixed(1) : 'N/A' }} 分
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ formatDateTime(results.started_at) }}</el-descriptions-item>
              <el-descriptions-item label="完成时间">{{ formatDateTime(results.completed_at) }}</el-descriptions-item>
               <el-descriptions-item label="题目总数">{{ results.attempts?.length || 0 }}</el-descriptions-item>
               <el-descriptions-item label="答对题数">
                  {{ correctCount }} / {{ results.attempts?.length || 0 }}
               </el-descriptions-item>
            </el-descriptions>
          </el-card>
  
          <el-collapse v-model="activeCollapseItems">
            <el-collapse-item
              v-for="(attempt, index) in results.attempts"
              :key="attempt.id"
              :name="attempt.question_id"
            >
               <template #title>
                  <div :class="['attempt-title', attempt.is_correct ? 'correct' : 'incorrect']">
                      问题 {{ index + 1 }}: {{ attempt.question?.question_text.substring(0, 50) }}...
                      <el-icon class="status-icon">
                          <CircleCheckFilled v-if="attempt.is_correct" />
                          <CircleCloseFilled v-else />
                      </el-icon>
                  </div>
               </template>
  
               <div class="attempt-details">
                 <p><strong>题目:</strong> {{ attempt.question?.question_text }}</p>
  
                 <div v-if="attempt.question?.question_type === 'multiple_choice'">
                     <p><strong>你的选择:</strong></p>
                     <el-radio-group :model-value="attempt.selected_answer_id" disabled>
                         <el-radio
                             v-for="ans in attempt.question?.answers"
                             :key="ans.id"
                             :label="ans.id"
                             border
                             :class="getAnswerClass(ans, attempt)"
                             style="display: block; margin-bottom: 10px;"
                         >
                             {{ ans.answer_text }}
                             <el-icon v-if="ans.is_correct"><Select /></el-icon>
                             <el-icon v-if="!ans.is_correct && ans.id === attempt.selected_answer_id"><Close /></el-icon>
                         </el-radio>
                     </el-radio-group>
                 </div>
                 <div v-else>
                     <p><strong>你的答案:</strong></p>
                     <el-input type="textarea" :model-value="attempt.user_answer_text || '未作答'" :rows="3" readonly disabled />
                     <p v-if="attempt.is_correct === false && getCorrectAnswerText(attempt.question)">
                        <strong>参考答案:</strong> {{ getCorrectAnswerText(attempt.question) }}
                      </p>
                      <p v-else-if="attempt.is_correct === null">
                         <el-tag type="info">此题型暂不支持自动判分</el-tag>
                      </p>
  
                 </div>
  
                 <p style="margin-top: 10px;">
                      <strong>结果:</strong>
                      <el-tag :type="attempt.is_correct ? 'success' : (attempt.is_correct === false ? 'danger' : 'info')">
                         {{ attempt.is_correct ? '正确' : (attempt.is_correct === false ? '错误' : '未评分') }}
                      </el-tag>
                  </p>
                 <p v-if="attempt.question?.explanation" style="margin-top: 10px; background-color: #f4f4f5; padding: 10px; border-radius: 4px;">
                   <strong>解析:</strong> {{ attempt.question.explanation }}
                 </p>
                  <p v-if="attempt.feedback" style="margin-top: 10px; color: #e6a23c;">
                   <strong>反馈:</strong> {{ attempt.feedback }}
                 </p>
               </div>
            </el-collapse-item>
          </el-collapse>
  
          <el-divider />
           <div style="text-align: center;">
               <el-button type="primary" @click="goBack">返回练习中心</el-button>
                <el-button v-if="results?.module_id" @click="retryPractice" :loading="retrying">
                  再做一次
                </el-button>
           </div>
  
        </div>
         <el-empty v-else-if="!loading && !error" description="未能加载练习结果"></el-empty>
      </el-main>
    </el-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessage } from 'element-plus';
  import { CircleCheckFilled, CircleCloseFilled, Select, Close } from '@element-plus/icons-vue';
  import { getSessionResults, startPracticeSession } from '@/services/practice';
  
  const route = useRoute();
  const router = useRouter();
  const sessionId = ref(parseInt(route.params.sessionId, 10));
  const results = ref(null);
  const loading = ref(true);
  const error = ref(false);
  const errorMessage = ref('');
  const activeCollapseItems = ref([]); // 控制展开哪些题目详情
  const retrying = ref(false);
  
  // 加载结果
  onMounted(async () => {
    if (!sessionId.value) {
      error.value = true;
      errorMessage.value = '无效的会话 ID。';
      loading.value = false;
      return;
    }
    try {
      loading.value = true;
      error.value = false;
      results.value = await getSessionResults(sessionId.value);
      // 默认展开所有错误的题目
      activeCollapseItems.value = results.value?.attempts
          ?.filter(a => a.is_correct === false)
          ?.map(a => a.question_id) || [];
    } catch (err) {
      console.error("加载练习结果失败:", err);
      error.value = true;
      errorMessage.value = err.response?.data?.detail || err.message || '无法连接服务器获取结果。';
      ElMessage.error(errorMessage.value);
    } finally {
      loading.value = false;
    }
  });
  
  // 计算答对题数
  const correctCount = computed(() => {
      return results.value?.attempts?.filter(a => a.is_correct === true).length || 0;
  });
  
  
  // 格式化日期时间
  const formatDateTime = (isoString) => {
    if (!isoString) return 'N/A';
    try {
      return new Date(isoString).toLocaleString('zh-CN');
    } catch (e) {
      return isoString; // Return original if parsing fails
    }
  };
  
  // 获取选择题选项的样式类
  const getAnswerClass = (answer, attempt) => {
    const classes = [];
    if (answer.is_correct) {
      classes.push('correct-answer');
    }
    if (answer.id === attempt.selected_answer_id && !answer.is_correct) {
       classes.push('wrong-selection');
    }
     if (answer.id === attempt.selected_answer_id) {
       classes.push('selected-answer'); // 标记用户的选择
     }
    return classes.join(' ');
  };
  
  // 获取非选择题的正确答案文本 (如果提供)
  const getCorrectAnswerText = (question) => {
      if (!question || !question.answers || question.question_type === 'multiple_choice') {
          return null;
      }
      // 假设非选择题的正确答案也存储在 answers 数组中，且 is_correct 为 true
      const correctAnswer = question.answers.find(ans => ans.is_correct);
      return correctAnswer ? correctAnswer.answer_text : null;
  };
  
  
  // 再做一次
  const retryPractice = async () => {
      if (!results.value?.module_id) return;
      retrying.value = true;
       try {
          const newSession = await startPracticeSession(results.value.module_id);
          router.push({ name: 'PracticeSession', params: { sessionId: newSession.id } });
        } catch (err) {
          console.error(`Failed to restart practice session for module ${results.value.module_id}:`, err);
          ElMessage.error('无法重新开始练习: ' + (err.response?.data?.detail || err.message));
        } finally {
          retrying.value = false;
        }
  }
  
  // 返回
  const goBack = () => {
    router.push({ name: 'PracticeList' });
  };
  </script>
  
  <style scoped>
  .attempt-title {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 500;
  }
  
  .attempt-title.correct {
      color: #67C23A;
  }
  
  .attempt-title.incorrect {
       color: #F56C6C;
  }
  
  .status-icon {
      font-size: 1.2em;
      margin-left: 10px;
  }
  
  .attempt-details {
    padding: 15px;
    font-size: 14px;
    line-height: 1.6;
    border-top: 1px solid #eee; /* Add a separator */
    margin-top: 10px;
  }
  
  .attempt-details strong {
      color: #303133;
      margin-right: 5px;
  }
  
  /* 高亮正确答案 */
  .el-radio.correct-answer {
    /* border-color: #67C23A !important; */
    background-color: #f0f9eb;
  }

  
  /* 标记错误选择 */
  .el-radio.wrong-selection {
    border-color: #f56c6c !important;
    background-color: #fef0f0;
  }
  .el-radio.wrong-selection .el-radio__label {
    color: #f56c6c !important;
  }
  /* .el-radio.wrong-selection .el-radio__inner {
     border-color: #f56c6c;
  } */
  
  /* 使得 radio 边框不被覆盖 */
  .el-radio.is-bordered {
      position: relative; /* Ensure icons are positioned correctly */
  }
  
  .el-radio .el-icon {
      margin-left: 5px;
      vertical-align: middle;
  }
  .el-radio.correct-answer .el-icon-select {
      color: #67C23A;
  }
  .el-radio.wrong-selection .el-icon-close {
       color: #F56C6C;
  }
  
  </style>