<template>
    <div class="lesson-view-page">
      <el-breadcrumb separator="/" style="margin-bottom: 20px;">
        <el-breadcrumb-item :to="{ name: 'MyCourses' }">我的课程</el-breadcrumb-item>
        <el-breadcrumb-item>{{ course?.title || `课程 ${props.courseId}` }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ lesson?.title || '加载中...' }}</el-breadcrumb-item>
      </el-breadcrumb>
  
      <el-card v-if="loading" shadow="never">
         <el-skeleton :rows="8" animated />
      </el-card>
  
      <el-card v-else-if="error" shadow="never">
          <el-alert type="error" :title="'加载课时内容失败: ' + error" :closable="false" />
       </el-card>
  
      <el-card v-else-if="lesson && course" shadow="never">
        <template #header>
          <div class="lesson-header">
            <h2>{{ lesson.title }}</h2>
            <el-tag v-if="progress?.completed" type="success" size="small">已完成</el-tag>
          </div>
        </template>
  
        <div class="lesson-content" v-html="lesson.content || '暂无内容'"></div>
  
        <template #footer>
          <div class="lesson-footer">
            <el-button
              :icon="ArrowLeft"
              @click="navigateToLesson(previousLessonId)"
              :disabled="!previousLessonId || navigationLoading"
              :loading="navigationLoading && loadingDirection === 'prev'"
            >
              上一课时
            </el-button>
            <el-button
              @click="markAsComplete"
              type="success"
              :loading="completeLoading"
              :disabled="progress?.completed || navigationLoading"
            >
              {{ progress?.completed ? '已完成' : '标记为已完成' }}
            </el-button>
            <el-button
              @click="navigateToLesson(nextLessonId)"
              :disabled="!nextLessonId || navigationLoading"
              :loading="navigationLoading && loadingDirection === 'next'"
            >
              下一课时 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
      </el-card>
  
      <el-alert v-else title="未找到课时信息" type="warning" show-icon :closable="false" />
  
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessage } from 'element-plus';
  import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue';
  // 服务函数
  import { getLessonById, getLessonsByCourse } from '@/services/lesson'; //
  import { updateLessonProgress } from '@/services/progress'; //
  import { getCourseById } from '@/services/course'; // 获取课程信息
  // 假设后端 progress 接口会返回进度信息，或者需要单独获取
  // import { getLessonProgress } from '@/services/progress'; // 可能需要这个
  
  const route = useRoute();
  const router = useRouter();
  
  // 从路由参数获取 Props
  const props = defineProps({
    courseId: {
      type: [String, Number],
      required: true,
    },
    lessonId: {
      type: [String, Number],
      required: true,
    },
  });
  
  // 响应式状态
  const course = ref(null); // 存储课程信息 { id, title, ... }
  const lesson = ref(null); // 存储当前课时信息 { id, title, content, order, course_id, ... }
  const progress = ref(null); // 存储当前课时的进度 { completed, score, ... }
  const courseLessons = ref([]); // 存储当前课程的所有课时列表
  const loading = ref(true); // 整体加载状态
  const error = ref(null); // 错误信息
  const completeLoading = ref(false); // “标记完成”按钮加载状态
  const navigationLoading = ref(false); // 课时导航加载状态
  const loadingDirection = ref(''); // 'prev' or 'next'
  
  // 计算属性：获取当前课时在列表中的索引
  const currentLessonIndex = computed(() => {
    if (!lesson.value || courseLessons.value.length === 0) {
      return -1;
    }
    // 需要比较 ID，因为 lessonId prop 可能是字符串
    return courseLessons.value.findIndex(l => l.id === Number(props.lessonId));
  });
  
  // 计算属性：获取上一课时的 ID
  const previousLessonId = computed(() => {
    if (currentLessonIndex.value > 0) {
      return courseLessons.value[currentLessonIndex.value - 1].id;
    }
    return null;
  });
  
  // 计算属性：获取下一课时的 ID
  const nextLessonId = computed(() => {
    if (currentLessonIndex.value !== -1 && currentLessonIndex.value < courseLessons.value.length - 1) {
      return courseLessons.value[currentLessonIndex.value + 1].id;
    }
    return null;
  });
  
  
  // 获取数据的核心函数
  const fetchData = async (cId, lId) => {
    loading.value = true;
    navigationLoading.value = false; // 重置导航加载状态
    error.value = null;
    lesson.value = null;
    course.value = null; // 重置课程信息
    progress.value = null; // 重置进度
    // courseLessons.value = []; // 考虑是否每次都重新获取整个列表
  
    try {
      // 并行获取课程信息、当前课时信息、课程所有课时列表 (用于导航)
      const [courseData, lessonData, allLessonsData] = await Promise.all([
        getCourseById(cId), // 获取课程信息
        getLessonById(lId), // 获取当前课时详情
        // 优化：如果列表不常变，可以考虑缓存或只获取一次
        courseLessons.value.length === 0 ? getLessonsByCourse(cId, 0, 1000) : Promise.resolve(courseLessons.value) // 获取所有课时用于导航
      ]);
  
      course.value = courseData;
      lesson.value = lessonData;
      // 如果 courseLessons 被重新获取了，更新它
      if(Array.isArray(allLessonsData)) {
          courseLessons.value = allLessonsData;
      }
  
  
      // 记录访问进度 (即使失败也不阻塞页面加载)
      try {
        // 后端 update_or_create_progress 会处理记录创建和 last_accessed_at 更新
        // 调用接口，后端返回的是包含当前状态的 Progress 对象
        const progressData = await updateLessonProgress(lId, {}); //
        progress.value = progressData; // 更新本地进度状态
        console.log(`已记录访问并获取进度 for lesson ${lId}`, progressData);
      } catch (progressError) {
        console.warn(`记录课时 ${lId} 访问进度失败:`, progressError);
        // 这里可以选择不提示用户，因为核心功能是显示课时内容
      }
  
    } catch (err) {
      console.error(`加载课程 ${cId} 或课时 ${lId} 失败:`, err);
      error.value = err.response?.data?.detail || err.message || '加载数据时发生未知错误';
      ElMessage.error(`加载失败: ${error.value}`);
    } finally {
      loading.value = false;
    }
  };
  
  // 标记为完成的逻辑
  const markAsComplete = async () => {
    if (!lesson.value || progress.value?.completed) return; // 如果已完成，则不执行
    completeLoading.value = true;
    try {
      // 调用接口标记为完成，并获取更新后的进度
      const updatedProgress = await updateLessonProgress(props.lessonId, { completed: true }); //
      progress.value = updatedProgress; // 更新本地进度状态
      ElMessage.success('课时已标记为完成！');
      // 可选：如果标记完成后自动进入下一课时
      // if (nextLessonId.value) {
      //   navigateToLesson(nextLessonId.value);
      // }
    } catch (err) {
       console.error(`标记课时 ${props.lessonId} 为完成失败:`, err);
       const completeError = err.response?.data?.detail || err.message || '未知错误';
       ElMessage.error(`标记完成失败: ${completeError}`);
    } finally {
       completeLoading.value = false;
    }
  };
  
  // 导航到其他课时
  const navigateToLesson = (targetLessonId) => {
    if (!targetLessonId || navigationLoading.value) return;
  
    // 设置加载方向用于按钮 loading 状态
    loadingDirection.value = targetLessonId < props.lessonId ? 'prev' : 'next';
    navigationLoading.value = true; // 开始导航加载
  
    router.push({
      name: 'LessonView',
      params: { courseId: props.courseId, lessonId: targetLessonId }
    });
    // fetchData 会在 watch 中被触发，无需手动调用
    // navigationLoading 会在 fetchData 开始时重置
  };
  
  // 组件挂载时获取初始数据
  onMounted(() => {
    fetchData(props.courseId, props.lessonId);
  });
  
  // 监听路由参数变化，以便在课时之间导航时重新加载数据
  watch(
    () => props.lessonId, // 只监听 lessonId 通常足够，因为 courseId 在同一课程内不变
    (newLessonId, oldLessonId) => {
      if (newLessonId && newLessonId !== oldLessonId) {
         fetchData(props.courseId, newLessonId);
      }
    }
  );
  
  </script>
  
  <style scoped lang="scss">
  .lesson-view-page {
    padding: 20px;
  }
  
  .lesson-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    h2 {
      margin: 0;
    }
  }
  
  .lesson-content {
    // 为渲染后的 HTML 内容添加基础样式
    line-height: 1.6;
    margin-bottom: 20px; // 与底部导航的间距
  
    // 如果使用 v-html，可能需要针对特定标签进行样式调整
    // 例如：限制图片大小、代码块样式等
    :deep(img) {
      max-width: 100%;
      height: auto;
      display: block;
      margin: 1em 0;
    }
    :deep(pre) {
      background-color: #f5f5f5;
      padding: 1em;
      border-radius: 4px;
      overflow-x: auto;
    }
    :deep(code) {
       font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
    }
  }
  
  .lesson-footer {
    display: flex;
    justify-content: space-between; // 将按钮分布在两端和中间
    align-items: center;
  }
  </style>