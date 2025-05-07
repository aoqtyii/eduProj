<template>
  <div class="dashboard-page" v-loading="loading">
    <el-row :gutter="20" class="core-metrics">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover">
          <div class="metric-item">
            <div class="metric-value">{{ dashboardData?.core_metrics?.average_progress ?? 'N/A' }}%</div>
            <div class="metric-label">平均学习进度</div>
             <el-icon><TrendCharts /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover">
          <div class="metric-item">
             <div class="metric-value">{{ dashboardData?.core_metrics?.overall_accuracy?.toFixed(1) ?? 'N/A' }}%</div>
             <div class="metric-label">练习总准确率</div>
              <el-icon><Aim /></el-icon>
          </div>
        </el-card>
      </el-col>
       <el-col :xs="12" :sm="12" :md="6">
         <el-card shadow="hover">
           <div class="metric-item">
             <div class="metric-value">{{ dashboardData?.core_metrics?.pending_mistakes ?? 'N/A' }}</div>
             <div class="metric-label">待复习错题</div>
              <el-icon><Warning /></el-icon>
           </div>
         </el-card>
       </el-col>
       <el-col :xs="12" :sm="12" :md="6">
         <el-card shadow="hover">
           <div class="metric-item">
             <div class="metric-value">{{ dashboardData?.core_metrics?.active_recommendations ?? 'N/A' }}</div>
             <div class="metric-label">学习建议</div>
              <el-icon><Opportunity /></el-icon>
           </div>
         </el-card>
       </el-col>
    </el-row>

    <el-row :gutter="20" class="main-content equal-height-row">

      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="dashboard-card">
           <template #header>
            <div class="card-header">
              <span>进行中的课程</span>
               <el-button text :icon="MoreFilled" @click="$router.push({ name: 'MyCourses' })">查看全部</el-button>
            </div>
          </template>
          <div class="card-content-wrapper">
              <div v-if="dashboardData?.ongoing_courses_progress?.length > 0">
                 <div class="scrollable-list">
                     <div v-for="course in dashboardData.ongoing_courses_progress" :key="course.course_id" class="course-progress-item">
                       <div class="course-info">
                         <span class="course-title" @click="navigateToCourse(course.course_id)" title="点击查看课程">{{ course.course_title }}</span>
                         <span class="lesson-count">{{ course.completed_lessons }} / {{ course.total_lessons }} 课时</span>
                       </div>
                       <el-progress :percentage="course.progress_percentage" :stroke-width="10" status="success" />
                        <div class="last-accessed" v-if="course.last_accessed_at">
                            上次学习: {{ formatRelativeTime(course.last_accessed_at) }}
                        </div>
                     </div>
                 </div>
               </div>
               <el-empty v-else description="暂无进行中的课程"></el-empty>
           </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
         <el-card shadow="never" class="dashboard-card">
             <template #header>
                <div class="card-header">
                  <span>模块表现</span>
                   <el-button text :icon="MoreFilled" @click="$router.push({ name: 'PracticeList' })">所有练习</el-button>
                </div>
              </template>
               <div class="card-content-wrapper">
                   <div v-if="dashboardData?.practice_performance_by_module?.length > 0" class="module-performance-list scrollable-list">
                      <div v-for="module in dashboardData.practice_performance_by_module.slice(0, 5)" :key="module.module_id" class="module-item"> 
                        <div class="module-title-sessions">
                            <span class="module-title">{{ module.module_title }}</span>
                            <span class="session-count">({{ module.sessions_completed }}次)</span>
                        </div>
                        <el-progress
                          :percentage="module.accuracy ?? 0"
                          :status="getAccuracyStatus(module.accuracy)"
                          :stroke-width="8"
                          :format="() => module.accuracy !== null ? `${module.accuracy.toFixed(1)}%` : 'N/A'"
                          style="margin-top: 5px;"
                        />
                      </div>
                    </div>
                   <el-empty v-else description="暂无模块练习数据"></el-empty>
               </div>
         </el-card>
      </el-col>

       <el-col :xs="24" :sm="12" :md="8">
           <el-card shadow="never" class="dashboard-card">
              <template #header>
                <div class="card-header">
                  <span>学习建议</span>
                   <el-button text :icon="Refresh" @click="fetchDashboardData" title="刷新建议"></el-button>
                </div>
              </template>
               <div class="card-content-wrapper">
                  <div v-if="dashboardData?.active_recommendations?.length > 0">
                     <div class="scrollable-list">
                         <div v-for="rec in dashboardData.active_recommendations" :key="rec.id" class="recommendation-item">
                           <div class="rec-content">
                                <el-icon :size="16" style="margin-right: 5px;"><Guide /></el-icon>
                                <span>{{ rec.reason || rec.related_item_name || '查看详情' }}</span>
                           </div>
                           <div class="rec-actions">
                              <el-button type="primary" link size="small" @click="handleRecommendationClick(rec)">去完成</el-button>
                               <el-button type="info" link size="small" @click="dismissRec(rec.id)" :icon="Close" title="忽略"></el-button>
                           </div>
                         </div>
                      </div>
                  </div>
                  <el-empty v-else description="暂无学习建议"></el-empty>
              </div>
           </el-card>
       </el-col>

       <el-col :xs="24" :sm="12" :md="8">
           <el-card shadow="never" class="dashboard-card">
             <template #header>
               <div class="card-header">
                 <span>近期练习</span>
               </div>
             </template>
              <div class="card-content-wrapper">
                  <div v-if="dashboardData?.practice_performance_summary?.recent_session_scores?.length > 0" >
                      <div class="recent-scores-list scrollable-list">
                           <ul>
                              <li v-for="score in dashboardData.practice_performance_summary.recent_session_scores.slice(0, 5)" :key="score.session_id"> 
                                 <span>{{ formatTimestamp(score.completed_at, 'MM-DD HH:mm') }}</span>
                                 <el-tag :type="getScoreTagType(score.score)" size="small" effect="light">
                                     {{ score.score.toFixed(1) }}%
                                 </el-tag>
                              </li>
                           </ul>
                        </div>
                    </div>
                    <el-empty v-else description="暂无最近练习记录"></el-empty>
              </div>
           </el-card>
       </el-col>

       <el-col :xs="24" :sm="12" :md="8">
           <el-card shadow="never" class="dashboard-card">
             <template #header>
               <div class="card-header">
                 <span>错题本摘要</span>
                  <el-button text :icon="MoreFilled" @click="$router.push({ name: 'MistakeNotebook' })">查看详情</el-button>
               </div>
             </template>
              <div class="card-content-wrapper">
                  <div v-if="dashboardData?.mistake_analysis_summary?.total_mistakes > 0">
                    <div class="mistake-stats">
                        <span>新错题: {{ dashboardData.mistake_analysis_summary.new_mistakes }}</span> |
                        <span>待复习: {{ dashboardData.mistake_analysis_summary.reviewed_mistakes }}</span> |
                        <span>已掌握: {{ dashboardData.mistake_analysis_summary.mastered_mistakes }}</span>
                    </div>
                    <div class="scrollable-list" style="padding-top: 10px;">
                        <div v-if="dashboardData.mistake_analysis_summary?.top_mistake_modules?.length > 0" class="top-mistakes">
                             <strong>高频出错模块:</strong>
                             <ul>
                               <li v-for="mod in dashboardData.mistake_analysis_summary.top_mistake_modules.slice(0, 3)" :key="mod.module_id">
                                 {{ mod.module_title }} ({{ mod.count }}次)
                               </li>
                             </ul>
                         </div>
                         <div v-if="dashboardData.mistake_analysis_summary?.top_mistake_knowledge_points?.length > 0" class="top-mistakes">
                             <strong>高频出错知识点:</strong>
                             <ul>
                               <li v-for="kp in dashboardData.mistake_analysis_summary.top_mistake_knowledge_points.slice(0, 3)" :key="kp.kp_id">
                                 {{ kp.kp_name }} ({{ kp.count }}次)
                               </li>
                             </ul>
                         </div>
                    </div>
                  </div>
                  <el-empty v-else description="错题本是空的，继续努力！"></el-empty>
              </div>
           </el-card>
       </el-col>

       <el-col :xs="24" :sm="12" :md="8">
            <el-card shadow="never" class="dashboard-card">
              <template #header>
                <div class="card-header">
                  <span>近期活动</span>
                </div>
              </template>
               <div class="card-content-wrapper">
                   <div v-if="dashboardData?.recent_activity?.length > 0" >
                        <el-timeline class="recent-activity-timeline scrollable-list">
                         <el-timeline-item
                           v-for="(activity, index) in dashboardData.recent_activity"
                           :key="index"
                           :timestamp="formatTimestamp(activity.timestamp)"
                           placement="top"
                            :icon="getActivityIcon(activity.activity_type)"
                            :type="getActivityColor(activity.activity_type)"
                         >
                           <p>
                             <strong>{{ getActivityTypeText(activity.activity_type) }}:</strong>
                             {{ activity.item_title }}
                             <span v-if="activity.details?.course_title"> ({{ activity.details.course_title }})</span>
                             <span v-if="activity.activity_type === 'practice_completed' && activity.details?.score !== undefined"> - 得分: {{ activity.details.score.toFixed(1) }}%</span>
                           </p>
                         </el-timeline-item>
                       </el-timeline>
                   </div>
                   <el-empty v-else description="暂无活动记录"></el-empty>
               </div>
            </el-card>
       </el-col>

    </el-row>

  </div>
</template>

<script setup>
// Script 部分保持不变
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getStudentAIDashboard, dismissRecommendation } from '@/services/aiAnalysis';
import { MoreFilled, Refresh, Warning, Aim, TrendCharts, Opportunity, Guide, Close, Reading, Finished, DataAnalysis } from '@element-plus/icons-vue';

const loading = ref(false);
const dashboardData = ref(null);
const router = useRouter();

const fetchDashboardData = async () => {
  loading.value = true;
  try {
    dashboardData.value = await getStudentAIDashboard();
  } catch (error) {
    ElMessage.error('加载 Dashboard 数据失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchDashboardData);

const formatTimestamp = (isoString, format = 'YYYY-MM-DD HH:mm') => {
  if (!isoString) return '';
  const date = new Date(isoString);
   if (isNaN(date)) return '';
    if (format === 'YYYY-MM-DD HH:mm') {
        return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).replace(/\//g, '-');
    } else if (format === 'MM-DD HH:mm') {
         return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).replace(/\//g, '-');
    }
    return date.toLocaleString();
};

const formatRelativeTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffSeconds = Math.round((now - date) / 1000);
    const diffMinutes = Math.round(diffSeconds / 60);
    const diffHours = Math.round(diffMinutes / 60);
    const diffDays = Math.round(diffHours / 24);

    if (diffSeconds < 60) return `${diffSeconds} 秒前`;
    if (diffMinutes < 60) return `${diffMinutes} 分钟前`;
    if (diffHours < 24) return `${diffHours} 小时前`;
    if (diffDays === 1) return `昨天`;
    if (diffDays < 7) return `${diffDays} 天前`;
    return formatTimestamp(isoString, 'YYYY-MM-DD');
};

const getActivityTypeText = (type) => {
  const map = {
    'lesson_accessed': '访问课时',
    'practice_completed': '完成练习',
    'mistake_added': '新增错题',
    'recommendation_received': '收到建议',
  };
  return map[type] || type;
};
const getActivityIcon = (type) => {
     switch (type) {
         case 'lesson_accessed': return Reading;
         case 'practice_completed': return Finished;
         case 'mistake_added': return Warning;
         case 'recommendation_received': return Guide;
         default: return DataAnalysis;
     }
}
const getActivityColor = (type) => {
    switch (type) {
        case 'lesson_accessed': return 'primary';
        case 'practice_completed': return 'success';
        case 'mistake_added': return 'warning';
        case 'recommendation_received': return 'info';
        default: '';
    }
}

const getAccuracyStatus = (accuracy) => {
    if (accuracy === null || accuracy === undefined) return '';
    if (accuracy >= 90) return 'success';
    if (accuracy >= 60) return 'warning';
    return 'exception';
};

const getScoreTagType = (score) => {
    if (score === null || score === undefined) return 'info';
    if (score >= 90) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

const navigateToCourse = (courseId) => {
    ElMessage.info('跳转到课程详情页功能待实现');
};

const handleRecommendationClick = (rec) => {
    if (rec.recommendation_type === 'practice_module' && rec.related_item_id) {
         router.push({ name: 'PracticeList' });
         ElMessage.info(`建议练习模块: ${rec.related_item_name}`);
    } else if (rec.recommendation_type === 'knowledge_point' || rec.recommendation_type === 'general_review') {
        router.push({ name: 'MistakeNotebook' });
        ElMessage.info(`建议复习: ${rec.related_item_name || '错题本'}`);
    } else if (rec.recommendation_type === 'lesson' && rec.related_item_id) {
         ElMessage.info('推荐学习课时，请在课程列表中查找');
    }
};

const dismissRec = async (recommendationId) => {
     try {
        await ElMessageBox.confirm('确定要忽略这条学习建议吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        });
        loading.value = true;
        await dismissRecommendation(recommendationId);
        ElMessage.success('建议已忽略');
        await fetchDashboardData();
      } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('操作失败');
            console.error('忽略推荐时出错:', error);
        }
      } finally {
          loading.value = false;
      }
};

</script>

<style lang="scss" scoped>
.dashboard-page {
  padding: 25px;
  background-color: #f9fafb;
}

.core-metrics {
  margin-bottom: 30px;
  .el-card {
      border: none;
      border-radius: 10px;
      transition: all 0.3s ease;
       &:hover {
           transform: translateY(-5px);
           box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
       }
  }
  .metric-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 25px 10px;

     .metric-value {
      font-size: 2.5em;
      font-weight: 600;
      color: var(--el-color-primary);
      margin-bottom: 8px;
      line-height: 1.2;
    }

    .metric-label {
      font-size: 1em;
      color: var(--el-text-color-secondary);
      margin-bottom: 15px;
    }
     .el-icon {
        font-size: 2em;
        color: var(--el-color-info-light-3);
     }
  }
}

/* --- 修改: 主内容区使用 Flex 实现等高 --- */
.main-content.equal-height-row {
  display: flex;
  flex-wrap: wrap; // 允许换行
   & > .el-col { // 直接子元素 col 应用
        margin-bottom: 20px; // 列之间的垂直间距
        display: flex; // 使 col 内部也为 flex 容器
        flex-direction: column; // col 内元素垂直排列
   }
}

.dashboard-card {
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter);
  background-color: #fff;
  overflow: hidden;
  width: 100%; // 卡片宽度占满其 col
  height: 100%; // 卡片高度占满其 col (配合 col 的 display: flex)
  display: flex; // 卡片内部使用 flex
  flex-direction: column; // 卡片内部垂直排列 (Header, Body)

  &:last-child {
    // margin-bottom: 0; // 由 el-col 控制 mb
  }
   .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    font-size: 1.1em; // 减小一点标题
    color: var(--el-text-color-primary);
    padding-bottom: 12px;
    // margin-bottom: 15px; // 移除margin，由 header padding 控制
  }

  // 包裹主要内容的 div
  .card-content-wrapper {
      flex-grow: 1; // 让内容区占据剩余空间
      overflow: hidden; // 隐藏内部溢出，由 scrollable-list 控制滚动
      display: flex; // 使内部内容（如 el-empty 或列表）垂直填充
      flex-direction: column;
       .el-empty { // 让空状态居中
         flex-grow: 1;
         display: flex;
         justify-content: center;
         align-items: center;
       }
  }
  // 内部需要滚动的列表
  .scrollable-list {
      flex-grow: 1; // 占据 card-content-wrapper 的空间
      overflow-y: auto; // 允许垂直滚动
      // padding-right: 5px; // 给滚动条留空间 (可选，美化)

      // 为滚动列表添加细微的滚动条样式 (可选)
      &::-webkit-scrollbar { width: 5px; height: 5px; }
      &::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 5px; }
      &::-webkit-scrollbar-thumb { background: #ccc; border-radius: 5px; }
      &::-webkit-scrollbar-thumb:hover { background: #aaa; }
  }


   :deep(.el-card__body) {
        padding: 15px 20px; // 调整 Body 内边距
        flex-grow: 1; // 让 Body 占据卡片剩余空间
        display: flex; // Body 内部也用 flex
        flex-direction: column;
        overflow: hidden; // 隐藏 Body 自身的溢出
    }
    :deep(.el-card__header) {
        padding: 15px 20px; // 调整 Header 内边距
        border-bottom: 1px solid var(--el-border-color-lighter); // Header 分割线
        flex-shrink: 0; // Header 高度固定
    }
}


h4 {
    margin-bottom: 15px;
    font-weight: 500;
    color: var(--el-text-color-regular);
    font-size: 1.05em;
    flex-shrink: 0; // 标题高度固定
}

.course-progress-item {
  margin-bottom: 18px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--el-border-color-extralight);
  flex-shrink: 0; // 防止被压缩
  &:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }

  .course-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-size: 1em;

    .course-title {
        font-weight: 500;
        color: var(--el-text-color-primary);
        cursor: pointer;
        &:hover { color: var(--el-color-primary); }
        // 限制标题行数 (可选)
        // display: -webkit-box;
        // -webkit-line-clamp: 1;
        // -webkit-box-orient: vertical;
        // overflow: hidden;
    }
    .lesson-count {
        color: var(--el-text-color-secondary);
        font-size: 0.9em;
        white-space: nowrap;
        margin-left: 10px;
    }
  }
  .el-progress {
      margin-bottom: 8px;
      :deep(.el-progress-bar__outer) { background-color: var(--el-color-info-light-8); }
  }
   .last-accessed {
     font-size: 0.85em;
     color: var(--el-text-color-secondary);
     margin-top: 5px;
     text-align: right;
   }
}

/* 练习表现列表样式 */
.module-performance-list {
  .module-item {
    margin-bottom: 15px; // 减小间距
    flex-shrink: 0;
     &:last-child { margin-bottom: 0; }
    .module-title-sessions {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        font-size: 0.95em;
        margin-bottom: 6px;
        .module-title {
            font-weight: 500;
            color: var(--el-text-color-regular);
            margin-right: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 70%;
        }
        .session-count {
            font-size: 0.85em;
            color: var(--el-text-color-secondary);
            flex-shrink: 0;
        }
    }
    :deep(.el-progress--success .el-progress__text) { color: var(--el-color-success-dark-2); font-weight: 500; }
    :deep(.el-progress--warning .el-progress__text) { color: var(--el-color-warning-dark-2); font-weight: 500;}
    :deep(.el-progress--exception .el-progress__text) { color: var(--el-color-danger-dark-2); font-weight: 500;}
    :deep(.el-progress__text) { font-size: 12px !important; }
  }
}

.recent-scores-list {
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    font-size: 0.9em;
    li {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 7px 0; // 调整内边距
      border-bottom: 1px dashed var(--el-border-color-lighter);
      flex-shrink: 0;
       &:last-child { border-bottom: none; }
      span:first-child {
        color: var(--el-text-color-secondary);
        margin-right: 10px;
        font-size: 0.9em;
      }
    }
  }
}


.recent-activity-timeline {
  padding-left: 5px; // 调整内边距
  padding-right: 5px;
  // max-height: 350px; // 移除固定高度，让flex控制
  // overflow-y: auto;

   :deep(.el-timeline-item) {
       padding-bottom: 15px; // 调整时间线项间距
   }
   :deep(.el-timeline-item__node) {
      width: 10px; // 调小节点
      height: 10px;
      left: 0px;
   }
   :deep(.el-timeline-item__icon) {
      font-size: 12px; // 调小图标
      color: #fff;
   }
   :deep(.el-timeline-item__wrapper) {
        padding-left: 22px; // 调整内容缩进
    }
   p {
     font-size: 0.9em; // 调小字体
     line-height: 1.5;
      strong {
        margin-right: 5px;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
   }
    :deep(.el-timeline-item__timestamp) {
        font-size: 0.8em; // 调小时间戳
        color: var(--el-text-color-secondary);
    }
}

.recommendation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0; // 调整内边距
  border-bottom: 1px dashed var(--el-border-color-lighter);
  font-size: 0.9em; // 调小字体
  flex-shrink: 0;
  &:last-child {
    border-bottom: none;
    padding-bottom: 5px;
  }
   .rec-content {
     display: flex;
     align-items: flex-start;
     flex-grow: 1;
     margin-right: 10px;
     line-height: 1.4;
      .el-icon {
         color: var(--el-color-primary);
         margin-top: 3px;
         flex-shrink: 0;
         margin-right: 6px; // 增大图标和文字间距
      }
      span { word-break: break-word; }
   }
    .rec-actions {
     flex-shrink: 0;
     .el-button { margin-left: 5px; }
   }
}

.mistake-stats {
    font-size: 0.9em;
    color: var(--el-text-color-secondary);
    margin-bottom: 15px;
    padding: 10px 15px;
    background-color: var(--el-color-info-light-9);
    border-radius: 6px;
    text-align: center;
    flex-shrink: 0;
     span { margin: 0 10px; }
}
.top-mistakes {
    margin-top: 15px;
    font-size: 0.9em;
    flex-shrink: 0;
     strong {
        display: block;
        margin-bottom: 8px;
        color: var(--el-text-color-regular);
        font-weight: 500;
     }
      ul {
        list-style: none;
        padding-left: 0;
         li {
           margin-bottom: 6px;
           color: var(--el-text-color-secondary);
           display: flex;
           align-items: center;
            &::before {
                content: '•';
                color: var(--el-color-primary-light-3);
                margin-right: 8px;
                font-size: 1.2em;
            }
         }
      }
}

// 响应式调整
@media (max-width: 992px) { // 中等屏幕 - 改为一行两列
     .core-metrics .el-col {
        flex: 0 0 50% !important;
        max-width: 50% !important;
        margin-bottom: 20px;
     }
     // 中等屏幕时，变为一行两列
     .main-content > .el-col {
         flex: 0 0 50% !important;
         max-width: 50% !important;
     }
}

@media (max-width: 768px) { // 小屏幕，保持一行两列或堆叠
    .core-metrics .el-col {
         flex: 0 0 50% !important;
         max-width: 50% !important;
        margin-bottom: 20px;
    }
    // 小屏幕，堆叠
    .main-content > .el-col {
        flex: 0 0 100% !important;
        max-width: 100% !important;
        margin-bottom: 20px; // 统一堆叠间距
    }
     .main-content > .el-col:last-child {
        margin-bottom: 0;
    }
}
@media (max-width: 576px) {
    .dashboard-page {
        padding: 15px;
    }
    .core-metrics .el-col {
         flex: 0 0 100% !important; // 一行一个
         max-width: 100% !important;
     }
}

</style>