<template>
    <div class="ai-dashboard p-5">
      <el-card class="box-card page-card" shadow="hover"> 
        <template #header>
          <div class="card-header">
            <span><el-icon><DataAnalysis /></el-icon> 智能学习分析</span>
            <el-tag type="success" effect="light" size="small">学生视图</el-tag>
          </div>
        </template>
  
        <div v-if="loading" class="loading-state p-5"> 
          <el-skeleton :rows="8" animated /> 
        </div>
  
        <div v-else-if="error" class="error-state p-5">
          <el-result
            icon="error"
            title="加载失败"
            :sub-title="error"
          >
            <template #extra>
              <el-button type="primary" @click="fetchData">重试</el-button>
            </template>
          </el-result>
        </div>
  
        <div v-else class="dashboard-content">
          <el-row :gutter="24" class="mb-6"> 
            <el-col :xs="24" :sm="12" :md="8">
              <el-card shadow="hover" class="data-card">
                <el-statistic
                  title="整体练习准确率"
                  :value="analysisData.practice_performance_summary?.overall_accuracy ?? 0"
                  suffix="%"
                  :value-style="getStatisticStyle(analysisData.practice_performance_summary?.overall_accuracy)"
                >
                   <template #prefix>
                      <el-icon :size="20" style="margin-right: 5px;"><Aim /></el-icon>
                   </template>
                </el-statistic>
                 <el-progress
                    class="mt-2"
                    :percentage="analysisData.practice_performance_summary?.overall_accuracy ?? 0"
                    :stroke-width="8"
                    :status="getProgressStatus(analysisData.practice_performance_summary?.overall_accuracy)"
                    :show-text="false"
                  />
                <div class="statistic-footer text-sm text-gray-500 mt-1">
                  <span>总尝试: {{ analysisData.practice_performance_summary?.total_questions_attempted ?? 'N/A' }}</span>
                  <el-divider direction="vertical" />
                  <span>总完成: {{ analysisData.practice_performance_summary?.total_sessions_completed ?? 'N/A' }} 次</span>
                </div>
              </el-card>
            </el-col>
  
            <el-col :xs="24" :sm="12" :md="8">
              <el-card shadow="hover" class="data-card">
                 <el-statistic
                    title="错题总数"
                    :value="analysisData.mistake_analysis_summary?.total_mistakes ?? 0"
                 >
                   <template #prefix>
                      <el-icon :size="20" style="margin-right: 5px;"><WarningFilled /></el-icon>
                   </template>
                 </el-statistic>
                 <div class="statistic-footer text-sm text-gray-500 mt-4"> 
                   <span :class="{ 'highlight-new': (analysisData.mistake_analysis_summary?.new_mistakes ?? 0) > 0 }">
                      新错题: {{ analysisData.mistake_analysis_summary?.new_mistakes ?? 0 }}
                   </span>
                   <el-divider direction="vertical" />
                   <span>复习中: {{ analysisData.mistake_analysis_summary?.reviewed_mistakes ?? 0 }}</span>
                   <el-divider direction="vertical" />
                   <span>已掌握: {{ analysisData.mistake_analysis_summary?.mastered_mistakes ?? 0 }}</span>
                 </div>
              </el-card>
            </el-col>
  
            <el-col :xs="24" :sm="24" :md="8"> 
               <el-card shadow="hover" class="data-card recommendation-card">
                 <template #header>
                   <div class="rec-header">
                     <span><el-icon><Opportunity /></el-icon> 学习建议</span>
                     <span class="badge" v-if="activeRecommendations.length > 0">{{ activeRecommendations.length }}</span>
                   </div>
                 </template>
                  <div v-if="activeRecommendations.length > 0" class="rec-body">
                     <el-scrollbar height="100px"> 
                       <el-timeline>
                         <el-timeline-item
                           v-for="rec in activeRecommendations"
                           :key="rec.id"
                           :type="getRecommendationTimelineType(rec.priority)"
                           :hollow="true"
                           size="small"
                         >
                           <div class="rec-content">
                              <span>{{ rec.reason || rec.related_item_name || '通用建议' }}</span>
                              <el-tooltip content="忽略此建议" placement="top">
                                <el-button link type="danger" size="small" @click="dismissRec(rec.id)" class="dismiss-btn">
                                  <el-icon><Close /></el-icon>
                                </el-button>
                              </el-tooltip>
                           </div>
                         </el-timeline-item>
                       </el-timeline>
                     </el-scrollbar>
                  </div>
                  <el-empty v-else description="暂无学习建议" :image-size="60"></el-empty>
               </el-card>
            </el-col>
          </el-row>
  
          <el-divider content-position="left">详细分析</el-divider> 
  
          <el-row :gutter="24">
             <el-col :xs="24" :md="12">
               <el-card shadow="hover" class="chart-card">
                 <template #header>按模块练习准确率 (Top 10 低)</template>
                 <div v-if="moduleAccuracyChartData.labels?.length" class="chart-container" style="height: 300px;"> 
                    <Bar :data="moduleAccuracyChartData" :options="barChartOptions" />
                 </div>
                 <el-empty v-else description="暂无按模块练习数据" :image-size="80"></el-empty>
               </el-card>
             </el-col>
  
              <el-col :xs="24" :md="12">
                 <el-card shadow="hover" class="chart-card">
                   <template #header>错题状态分布</template>
                   <div v-if="mistakeChartData.labels?.length && analysisData.mistake_analysis_summary?.total_mistakes > 0" class="chart-container" style="height: 300px;">
                     <Pie :data="mistakeChartData" :options="pieChartOptions" />
                   </div>
                   <el-empty v-else description="错题本是空的" :image-size="80"></el-empty>
                 </el-card>
              </el-col>
           </el-row>
  
           <el-row :gutter="24" class="mt-6">
              <el-col :span="24">
                <el-card shadow="hover">
                    <template #header>错题模块详情 (按数量排序)</template>
                    <div v-if="analysisData.mistake_analysis_summary?.mistakes_by_module?.length">
                        <el-table :data="topMistakeModules" stripe style="width: 100%" height="280px"> {/* 调整高度 */}
                          <el-table-column type="index" width="50" />
                          <el-table-column prop="module_title" label="练习模块" show-overflow-tooltip />
                          <el-table-column prop="count" label="错题数" width="100" align="center" sortable />
                          <el-table-column label="操作" width="120" align="center">
                            <template #default="scope">
                              <el-button link type="primary" size="small" @click="goToModule(scope.row.module_id)">去练习</el-button>
                            </template>
                          </el-table-column>
                        </el-table>
                    </div>
                    <el-empty v-else description="太棒了，没有模块集中出现错题！" :image-size="80"></el-empty>
                </el-card>
              </el-col>
           </el-row>
  
        </div>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRouter } from 'vue-router'; // 引入 useRouter
  import {
    ElCard, ElRow, ElCol, ElProgress, ElAlert, ElSkeleton, ElEmpty, ElTable,
    ElTableColumn, ElTag, ElButton, ElIcon, ElScrollbar, ElMessage, ElStatistic,
    ElDivider, ElResult, ElTimeline, ElTimelineItem, ElTooltip
  } from 'element-plus';
  import {
      DataAnalysis, Close, Aim, WarningFilled, Opportunity, Star, Check, Refresh // 引入更多图标
  } from '@element-plus/icons-vue';
  import { getStudentAIDashboard, dismissRecommendation } from '@/services/aiAnalysis';
  import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PieController, BarController, Colors } from 'chart.js'; // 引入 Colors
  import { Bar, Pie } from 'vue-chartjs';
  import ChartDataLabels from 'chartjs-plugin-datalabels'; // 引入 datalabels 插件
  
  // 注册 Chart.js 组件和插件
  ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PieController, BarController, Colors, ChartDataLabels); // 注册 Colors 和 DataLabels
  
  const router = useRouter(); // 获取 router 实例
  const loading = ref(true);
  const error = ref(null);
  const analysisData = ref({
    learning_progress: [],
    recent_activity: [],
    practice_performance_summary: {},
    practice_performance_by_module: [],
    mistake_analysis_summary: { mistakes_by_module: [] },
    recommendations: []
  });
  
  // --- 图表配置 ---
  const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                  label += ': ';
              }
              if (context.parsed.y !== null) {
                  label += context.parsed.y + '%'; // 如果是准确率等百分比数据
              } else if (context.parsed !== null && typeof context.parsed === 'number') {
                   label += context.parsed; // 如果是饼图等直接数值
              }
              return label;
          }
        }
      }
    }
  };
  
  const barChartOptions = computed(() => ({
    ...commonChartOptions,
    indexAxis: 'y', // 改为水平柱状图，更适合长标签
    scales: {
      x: {
        beginAtZero: true,
        max: 100, // 准确率最大100
        title: { display: true, text: '准确率 (%)' }
      },
      y: {
         ticks: { autoSkip: false } // 防止标签跳过
      }
    },
    plugins: {
        ...commonChartOptions.plugins,
        datalabels: { // 配置 datalabels
            anchor: 'end',
            align: 'end',
            formatter: (value) => value > 0 ? value + '%' : '', // 只显示大于0的百分比
            color: '#666',
            font: {
                size: 10
            }
        }
    }
  }));
  
  const pieChartOptions = computed(() => ({
    ...commonChartOptions,
     plugins: {
        ...commonChartOptions.plugins,
        datalabels: {
            formatter: (value, ctx) => {
                let sum = 0;
                let dataArr = ctx.chart.data.datasets[0].data;
                dataArr.map(data => { sum += data; });
                let percentage = (value*100 / sum).toFixed(1)+"%";
                return sum === 0 ? '' : percentage; // 如果总数为0则不显示
            },
            color: '#fff',
        }
    }
  }));
  
  
  // --- 计算属性 ---
  const activeRecommendations = computed(() => {
    return analysisData.value.recommendations?.filter(rec => rec.status === 'active') ?? [];
  });
  
  const topMistakeModules = computed(() => {
      // 返回按错题数降序排序的模块列表
      return [...(analysisData.value.mistake_analysis_summary?.mistakes_by_module ?? [])]
              .sort((a, b) => b.count - a.count);
  });
  
  const mistakeChartData = computed(() => {
    const summary = analysisData.value.mistake_analysis_summary;
    if (!summary || summary.total_mistakes === 0) {
      return { labels: [], datasets: [] };
    }
    return {
      labels: ['新错题', '复习中', '已掌握'],
      datasets: [
        {
          label: '错题状态',
          // 使用 Chart.js 内置颜色方案
          // backgroundColor: ['#f56c6c', '#e6a23c', '#67c23a'],
          data: [
            summary.new_mistakes ?? 0,
            summary.reviewed_mistakes ?? 0,
            summary.mastered_mistakes ?? 0
          ],
        },
      ],
    };
  });
  
  const moduleAccuracyChartData = computed(() => {
      const modules = analysisData.value.practice_performance_by_module;
      if (!modules || modules.length === 0) {
          return { labels: [], datasets: [] };
      }
      const sortedModules = [...modules]
          .filter(m => m.accuracy !== null && m.accuracy !== undefined) // 过滤掉没有准确率的数据
          .sort((a, b) => (a.accuracy ?? 101) - (b.accuracy ?? 101)); // 按准确率升序排序 (null放最后)
  
      const displayedModules = sortedModules.slice(0, 10); // 最多显示 10 个
  
      return {
          labels: displayedModules.map(m => m.module_title.length > 15 ? m.module_title.substring(0, 12) + '...' : m.module_title), // 截断长标题
          datasets: [
          {
              label: '模块练习准确率',
              // 使用 Chart.js 内置颜色方案，或根据准确率动态设置
              // backgroundColor: displayedModules.map(m => getBarColor(m.accuracy)),
              borderColor: 'rgba(75, 192, 192, 1)', // 示例边框色
              borderWidth: 1,
              data: displayedModules.map(m => m.accuracy ?? 0),
          },
          ],
      };
  });
  
  
  // --- 方法 ---
  const getStatisticStyle = (value) => {
    if (value === null || value === undefined) return { color: '#909399' }; // Grey
    if (value < 60) return { color: '#f56c6c' }; // Red
    if (value < 85) return { color: '#e6a23c' }; // Orange
    return { color: '#67c23a' }; // Green
  };
  
  const getProgressStatus = (percentage) => {
    if (percentage === null || percentage === undefined) return undefined; // Let ElProgress decide default
    if (percentage < 60) return 'exception';
    if (percentage < 85) return 'warning';
    return 'success';
  };
  
  const getRecommendationTimelineType = (priority) => {
     if (priority === 2) return 'danger';
     if (priority === 1) return 'warning';
     return 'primary'; // 或 'info'
  }
  
  const dismissRec = async (id) => {
    loading.value = true; // 显示加载状态
    try {
      await dismissRecommendation(id);
      // 重新获取数据以更新视图（或者本地移除）
      await fetchData();
      ElMessage.success('建议已忽略');
    } catch (err) {
       console.error("忽略建议失败:", err);
       ElMessage.error('操作失败，请稍后重试');
       error.value = err.response?.data?.detail || err.message || '操作失败'; // 显示错误信息
    } finally {
        loading.value = false;
    }
  }
  
  // 跳转到练习模块
  const goToModule = (moduleId) => {
      // 这里需要根据你的练习流程调整
      // 可能是直接跳转到模块详情页，或者触发开始练习的逻辑
      // 假设直接开始练习会话
      router.push({ name: 'PracticeList' }); // 或者更具体的路由
      console.log("跳转到练习模块:", moduleId);
       ElMessage.info(`准备跳转到练习模块 ${moduleId} (请实现具体跳转逻辑)`);
      // 实际可能需要调用 startPracticeSession API 然后跳转到 session 页面
      // import { startPracticeSession } from '@/services/practice';
      // try {
      //   const session = await startPracticeSession(moduleId);
      //   router.push({ name: 'PracticeSession', params: { sessionId: session.id } });
      // } catch (err) { ElMessage.error('开始练习失败'); }
  }
  
  const fetchData = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await getStudentAIDashboard();
      analysisData.value = response;
    } catch (err) {
      console.error("加载 AI 分析数据失败:", err);
      error.value = err.response?.data?.detail || err.message || '无法连接到服务器';
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(fetchData);
  
  </script>
  
  <style scoped>
  .ai-dashboard {
    background-color: #f5f7fa; /* 页面背景色 */
    min-height: calc(100vh - 60px); /* 减去可能的 header 高度 */
  }
  
  .page-card {
    border: none; /* 移除卡片边框 */
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.1rem; /* 稍大标题 */
    font-weight: 600; /* 加粗 */
    color: #303133;
  }
  .card-header .el-icon {
    margin-right: 8px;
    vertical-align: middle; /* 图标垂直居中 */
  }
  .card-header .el-tag {
      margin-left: 10px;
  }
  
  .data-card {
    height: 100%; /* 让卡片在行内高度一致 */
    display: flex;
    flex-direction: column;
  }
  /* 确保 el-statistic 标题和数值正确显示 */
  .data-card :deep(.el-statistic__head) {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px; /* 增加标题和数值间距 */
  }
  .data-card :deep(.el-statistic__content) {
    font-size: 24px; /* 增大数值字体 */
    font-weight: bold;
  }
  
  .statistic-footer {
    margin-top: auto; /* 将脚注推到底部 */
    padding-top: 10px; /* 增加与上面内容的间距 */
    color: #909399;
    font-size: 13px; /* 稍小字体 */
    border-top: 1px solid #ebeef5; /* 添加细分割线 */
  }
  .statistic-footer .el-divider--vertical {
    margin: 0 8px; /* 调整分隔符间距 */
  }
  .highlight-new {
      color: var(--el-color-danger); /* 突出显示新错题 */
      font-weight: bold;
  }
  
  .recommendation-card .rec-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1rem; /* 调整建议标题大小 */
    font-weight: normal;
  }
  .recommendation-card .badge {
    background-color: var(--el-color-danger);
    color: white;
    border-radius: 10px;
    padding: 0 6px;
    font-size: 12px;
    height: 18px;
    line-height: 18px;
  }
  .recommendation-card .rec-body {
    padding: 5px 0; /* 调整建议列表内边距 */
  }
  
  .recommendation-card .el-timeline {
     padding-left: 5px; /* 调整时间线左边距 */
  }
  .recommendation-card .el-timeline-item {
      padding-bottom: 8px; /* 调整时间线项间距 */
  }
  .recommendation-card :deep(.el-timeline-item__content) {
      font-size: 13px; /* 调整建议文本大小 */
      line-height: 1.4;
  }
  .recommendation-card .rec-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
  }
  .recommendation-card .dismiss-btn {
      margin-left: 10px;
      opacity: 0.7;
      transition: opacity 0.2s;
  }
  .recommendation-card .rec-content:hover .dismiss-btn {
      opacity: 1;
  }
  
  
  .chart-card {
    height: 380px; /* 固定图表卡片高度 */
    display: flex;
    flex-direction: column;
  }
  .chart-card .chart-container {
    flex-grow: 1; /* 让图表容器填充剩余空间 */
    position: relative; /* Chart.js 需要相对定位 */
  }
  .chart-card :deep(.el-card__body) {
     flex-grow: 1;
     display: flex;
     flex-direction: column;
  }
  
  
  .mb-6 {
    margin-bottom: 2rem; /* 32px */
  }
  .mt-6 {
    margin-top: 2rem; /* 32px */
  }
  .mt-4 {
    margin-top: 1rem; /* 16px */
  }
  .mt-2 {
    margin-top: 0.5rem; /* 8px */
  }
  .mt-1 {
    margin-top: 0.25rem; /* 4px */
  }
  .p-5 {
      padding: 1.5rem; /* 24px */
  }
  
  /* 响应式调整 (示例) */
  @media (max-width: 768px) {
    .el-col {
      margin-bottom: 1.5rem; /* 在小屏幕上增加列间距 */
    }
    .chart-card {
      height: auto; /* 小屏幕上取消固定高度 */
    }
    .chart-card .chart-container {
       height: 250px; /* 小屏幕上给个固定高度 */
    }
  }
  </style>