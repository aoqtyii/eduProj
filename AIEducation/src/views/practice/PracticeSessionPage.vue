<template>
    <el-container direction="vertical" style="padding: 20px;">
      <el-page-header @back="goBack" style="margin-bottom: 20px;">
        <template #content>
          <span class="text-large font-600 mr-3"> 开始练习: {{ moduleTitle }} </span>
        </template>
      </el-page-header>
  
      <el-main v-loading="loadingQuestions || submitting">
        <el-alert v-if="error" :title="errorTitle" :description="errorMessage" type="error" show-icon :closable="false" style="margin-bottom: 20px;" />
  
        <div v-if="!error && questions.length > 0">
          <el-card v-for="(question, index) in questions" :key="question.id" shadow="never" style="margin-bottom: 20px;">
            <template #header>
              <div class="question-header">
                <strong>问题 {{ index + 1 }}:</strong>
                <span style="margin-left: 10px;">({{ getQuestionTypeText(question.question_type) }})</span>
                 </div>
            </template>
            <div class="question-content">
              <p style="margin-bottom: 15px;">{{ question.question_text }}</p>
  
              <el-radio-group
                v-if="question.question_type === 'multiple_choice'"
                v-model="userAnswers[question.id]"
                 @change="() => markAnswered(question.id)"
              >
                <el-radio
                  v-for="answer in question.answers"
                  :key="answer.id"
                  :label="answer.id"
                  border
                  style="display: block; margin-bottom: 10px;"
                >
                  {{ answer.answer_text }}
                </el-radio>
              </el-radio-group>
  
              <el-input
                v-else-if="['fill_in_blank', 'short_answer', 'coding'].includes(question.question_type)"
                type="textarea"
                :rows="4"
                v-model="userAnswers[question.id]"
                :placeholder="`请输入你的${getQuestionTypeText(question.question_type)}答案`"
                 @input="() => markAnswered(question.id)"
              />
  
               <div v-else>
                  <el-alert type="info" :closable="false" description="暂不支持此题型作答界面。" />
               </div>
  
            </div>
             </el-card>
  
          <el-divider />
  
          <div style="text-align: center;">
             <el-progress
                :percentage="completionPercentage"
                :color="customColors"
                style="margin-bottom: 20px;"
              />
            <el-button
              type="success"
              @click="submitAnswers"
              :loading="submitting"
              :disabled="!allAnswered"
              size="large"
            >
              {{ submitButtonText }}
            </el-button>
            <p v-if="!allAnswered" style="color: #E6A23C; font-size: 12px; margin-top: 5px;">
              请完成所有题目后再提交
            </p>
          </div>
        </div>
         <el-empty v-else-if="!loadingQuestions && !error" description="该模块下暂无题目"></el-empty>
  
      </el-main>
    </el-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { getModuleQuestions, submitSessionAnswers } from '@/services/practice';
  
  const route = useRoute();
  const router = useRouter();
  
  // 从路由参数获取会话 ID
  const sessionId = ref(parseInt(route.params.sessionId, 10));
  // 注意：后端接口是根据 module_id 获取问题，但我们是从 session 开始的。
  // 实践中，你可能需要一个接口 GET /practice/sessions/{sessionId} 来获取 session 详情，包括 module_id 和 module_title
  // 或者，从 PracticeListPage 导航时传递 module_id 和 title 作为查询参数或状态。
  // 这里我们假设可以通过某种方式（例如查询参数）获取 module_id 和 title，或者修改后端接口。
  // 暂时硬编码一个 module_id 和 title 用于演示。
  const moduleId = ref(1); // 假设的 moduleId，需要替换为实际逻辑获取
  const moduleTitle = ref('练习模块'); // 假设的模块标题
  
  const questions = ref([]);
  const userAnswers = ref({}); // { questionId: answerValue }
  const answeredStatus = ref({}); // { questionId: boolean }
  const loadingQuestions = ref(true);
  const submitting = ref(false);
  const error = ref(false);
  const errorTitle = ref('加载失败');
  const errorMessage = ref('');
  
  // --- UI 状态 ---
  // 进度条颜色
  const customColors = [
    { color: '#f56c6c', percentage: 20 },
    { color: '#e6a23c', percentage: 40 },
    { color: '#5cb87a', percentage: 60 },
    { color: '#1989fa', percentage: 80 },
    { color: '#6f7ad3', percentage: 100 },
  ];
  
  // 计算完成度
  const completionPercentage = computed(() => {
    const total = questions.value.length;
    if (total === 0) return 0;
    const answeredCount = Object.values(answeredStatus.value).filter(Boolean).length;
    return Math.round((answeredCount / total) * 100);
  });
  
  // 是否所有题目都已作答
  const allAnswered = computed(() => {
    return questions.value.length > 0 && Object.keys(answeredStatus.value).length === questions.value.length;
  });
  
  // 提交按钮文本
  const submitButtonText = computed(() => {
      return submitting.value ? '正在提交...' : '完成并提交答案';
  });
  
  // 获取题目类型中文名
  const getQuestionTypeText = (type) => {
    const types = {
      'multiple_choice': '单选题',
      'fill_in_blank': '填空题',
      'short_answer': '简答题',
      'coding': '编程题',
    };
    return types[type] || '未知题型';
  };
  
  
  // 加载问题
  onMounted(async () => {
    if (!sessionId.value) {
      error.value = true;
      errorTitle.value = '无效的会话';
      errorMessage.value = '未提供有效的练习会话 ID。';
      loadingQuestions.value = false;
      return;
    }
  
    // -------- 重要: 获取 moduleId 的逻辑 --------
    // 你需要在这里实现获取与 sessionId 关联的 moduleId 的逻辑。
    // 这可能需要一个新的后端接口 GET /api/v1/practice/sessions/{sessionId}
    // 或者在从列表页导航时传递 moduleId。
    // 此处我们使用硬编码的 moduleId = 1 作为示例。
    // -------- 结束: 获取 moduleId 的逻辑 --------
  
    try {
      loadingQuestions.value = true;
      error.value = false;
      const fetchedQuestions = await getModuleQuestions(moduleId.value); // 使用 moduleId 获取问题
      questions.value = fetchedQuestions;
      // 初始化答案和状态对象
      userAnswers.value = {};
      answeredStatus.value = {};
       questions.value.forEach(q => {
         userAnswers.value[q.id] = q.question_type === 'multiple_choice' ? null : ''; // 根据题型初始化
         // 不在此处初始化 answeredStatus，而是在用户输入时标记
       });
    } catch (err) {
      console.error("加载问题失败:", err);
      error.value = true;
      errorTitle.value = '加载问题失败';
      errorMessage.value = err.response?.data?.detail || err.message || '无法连接服务器获取问题。';
      ElMessage.error(errorMessage.value);
    } finally {
      loadingQuestions.value = false;
    }
  });
  
  // 标记题目已作答 (当用户输入或选择时触发)
  const markAnswered = (questionId) => {
      const answer = userAnswers.value[questionId];
      // 检查答案是否非空 (对于文本是trim后非空，对于选择题是非null)
      if ((typeof answer === 'string' && answer.trim() !== '') || (typeof answer === 'number')) {
           answeredStatus.value[questionId] = true;
      } else {
           // 如果用户清空了答案，则标记为未作答
           delete answeredStatus.value[questionId];
           // 强制 Vue 更新响应式对象
           answeredStatus.value = {...answeredStatus.value};
      }
  }
  
  
  // 提交答案
  const submitAnswers = async () => {
    if (!allAnswered.value) {
      ElMessage.warning('请先完成所有题目！');
      return;
    }
  
    ElMessageBox.confirm('确认提交所有答案吗？提交后将无法修改。', '确认提交', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(async () => {
        submitting.value = true;
        error.value = false; // Reset error state before submission
  
        // 准备提交的数据格式 (List[schemas.PracticeAttemptSubmit])
        const attemptsToSubmit = questions.value.map(q => {
          const attempt = {
            question_id: q.id,
            selected_answer_id: null,
            user_answer_text: null,
          };
          if (q.question_type === 'multiple_choice') {
            attempt.selected_answer_id = userAnswers.value[q.id];
          } else {
            attempt.user_answer_text = userAnswers.value[q.id];
          }
          return attempt;
        });
  
        try {
          const result = await submitSessionAnswers(sessionId.value, attemptsToSubmit);
          console.log('提交成功，结果:', result);
          ElMessage.success('答案提交成功！');
          // 跳转到结果页面
          router.push({ name: 'PracticeResults', params: { sessionId: sessionId.value } });
        } catch (err) {
          console.error("提交答案失败:", err);
          error.value = true; // Set error state
          errorTitle.value = '提交失败';
          errorMessage.value = err.response?.data?.detail || err.message || '提交答案时发生错误。';
          ElMessageBox.alert(`提交失败: ${errorMessage.value}`, '错误', {
              confirmButtonText: '确定',
              type: 'error',
          });
        } finally {
          submitting.value = false;
        }
    }).catch(() => {
      // 用户点击了取消
      ElMessage.info('提交已取消');
    });
  };
  
  // 返回上一页
  const goBack = () => {
    // 考虑是否有未保存的更改，如果需要，可以提示用户
    router.back(); // 或 router.push({ name: 'PracticeList' });
  };
  
  </script>
  
  <style scoped>
  .question-header {
    display: flex;
    align-items: center;
  }
  
  .question-content {
    padding: 15px 0;
  }
  
  .el-radio.is-bordered {
      width: 100%; /* 让带边框的单选按钮撑满容器宽度 */
      margin-right: 0; /* 重置 Element Plus 可能添加的右边距 */
      padding-left: 10px; /* 调整内部左边距 */
  }
  
  .el-radio-group {
      width: 100%; /* 确保单选组也撑满 */
  }
  
  .el-main {
      /* 防止内容过多时撑破布局 */
      overflow: auto;
  }
  </style>