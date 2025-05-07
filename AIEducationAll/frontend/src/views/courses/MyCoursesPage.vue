<template>
  <div class="my-courses-page">
    <el-row :gutter="20">
      <el-col v-if="loading" :span="24">
        <el-skeleton :rows="5" animated />
      </el-col>
      <el-col v-else-if="error" :span="24">
        <el-alert type="error" :title="'加载我的课程失败: ' + error" :closable="false" />
      </el-col>
      <el-col v-else-if="enrolledCourses.length === 0" :span="24">
        <el-empty description="您还没有报名任何课程" />
      </el-col>
      <el-col v-for="enrollment in enrolledCourses" :key="enrollment.id" :xs="24" :sm="12" :md="8" :lg="6" class="course-col">
        <el-card class="course-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ enrollment.course?.title || '课程标题加载中...' }}</span>
              </div>
          </template>
          <div class="course-description">
            {{ enrollment.course?.description || '暂无描述' }}
          </div>
          <template #footer>
            <div class="card-footer">
              <el-button
                type="primary"
                :icon="Document"
                @click="startOrContinueLearning(enrollment.course_id)"
                :loading="startLearningLoading[enrollment.course_id]"
              >
                开始学习
              </el-button>
              <el-button
                type="danger"
                plain
                :icon="Close"
                @click="confirmUnenroll(enrollment.course_id, enrollment.course?.title)"
                :loading="unenrollLoading[enrollment.course_id]"
              >
                取消报名
              </el-button>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Document, Close } from '@element-plus/icons-vue';
// 假设您有这些基于提供文件的服务函数
import { getMyEnrollments, unenrollFromCourse } from '@/services/enrollment'; //
import { getLessonsByCourse } from '@/services/lesson'; // 需要这个来查找第一节课

const router = useRouter();
const enrolledCourses = ref([]); // 存储报名数据 { id, user_id, course_id, enrollment_date, course: { id, title, description } }
const loading = ref(true); // 加载状态
const error = ref(null); // 错误信息
const startLearningLoading = reactive({}); // 每个课程“开始学习”按钮的加载状态
const unenrollLoading = reactive({}); // 每个课程“取消报名”按钮的加载状态

// 组件挂载时获取已报名课程
onMounted(async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await getMyEnrollments(); // 获取 EnrollmentPublic 列表
    enrolledCourses.value = response; //
  } catch (err) {
    console.error("加载已报名课程失败:", err);
    error.value = err.response?.data?.detail || err.message || '未知错误';
    ElMessage.error(`加载我的课程失败: ${error.value}`);
  } finally {
    loading.value = false;
  }
});

// --- 开始学习逻辑 ---
const startOrContinueLearning = async (courseId) => {
  if (!courseId) return;
  startLearningLoading[courseId] = true;
  try {
    // 1. 获取课程的课时列表以找到第一节课
    //    仅获取第一个课时 (limit=1, skip=0)
    const lessons = await getLessonsByCourse(courseId, 0, 1); //

    if (!lessons || lessons.length === 0) {
      ElMessage.warning('该课程还没有课时内容。');
      return;
    }

    // 2. 获取第一节课 (后端按 'order' 字段，然后按 'id' 排序)
    const firstLesson = lessons[0]; //

    // 3. 导航到课时视图页面
    router.push({
      name: 'LessonView', // 使用在 router/index.js 中定义的路由名称
      params: { courseId: courseId, lessonId: firstLesson.id } // 传递课程ID和课时ID
    });

  } catch (err) {
    console.error(`开始学习课程 ${courseId} 失败:`, err);
    ElMessage.error('无法开始学习，请稍后重试。');
    error.value = err.response?.data?.detail || err.message || '获取课时失败';
  } finally {
    startLearningLoading[courseId] = false;
  }
};

// --- 取消报名逻辑 ---
const confirmUnenroll = (courseId, courseTitle) => {
  ElMessageBox.confirm(
    `您确定要取消报名课程 "${courseTitle || courseId}" 吗？您的学习进度将会丢失。`, // 确认提示信息
    '确认取消报名', // 提示框标题
    {
      confirmButtonText: '确定取消', // 确认按钮文字
      cancelButtonText: '再想想', // 取消按钮文字
      type: 'warning', // 提示类型
    }
  ).then(async () => {
    // 用户点击确认
    await handleUnenroll(courseId);
  }).catch(() => {
    // 用户点击取消或关闭提示框
    ElMessage.info('取消操作已撤销');
  });
};

const handleUnenroll = async (courseId) => {
  if (!courseId) return;
  unenrollLoading[courseId] = true;
  try {
    await unenrollFromCourse(courseId); // 调用取消报名接口
    ElMessage.success('成功取消报名！');
    // 刷新课程列表
    enrolledCourses.value = enrolledCourses.value.filter(e => e.course_id !== courseId);
  } catch (err) {
    console.error(`取消报名课程 ${courseId} 失败:`, err);
    const unenrollError = err.response?.data?.detail || err.message || '未知错误';
    ElMessage.error(`取消报名失败: ${unenrollError}`);
  } finally {
    unenrollLoading[courseId] = false;
  }
};
</script>

<style scoped lang="scss">
.my-courses-page {
  padding: 20px; // 页面内边距
}

.course-col {
  margin-bottom: 20px; // 卡片之间的垂直间距
}

.course-card {
  height: 100%; // 使同一行的卡片高度一致
  display: flex;
  flex-direction: column; // 垂直排列卡片内容

  .card-header {
    font-weight: bold; // 卡片标题加粗
  }

  .course-description {
    flex-grow: 1; // 让描述区域占据可用空间
    color: #606266; // 描述文字颜色
    font-size: 14px; // 描述文字大小
    margin-bottom: 15px; // 与底部的间距
    // 可选：限制描述行数
    display: -webkit-box;
    -webkit-line-clamp: 3; // 最多显示3行
    -webkit-box-orient: vertical;
    overflow: hidden; // 隐藏溢出部分
    text-overflow: ellipsis; // 显示省略号
    min-height: 63px; // 大约3行文字的高度
  }

  .card-footer {
    display: flex;
    justify-content: space-between; // 按钮两端对齐
    align-items: center; // 垂直居中对齐
  }
}

// 确保 Element Plus 组件样式正确加载 (如果需要覆盖)
</style>