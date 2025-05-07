// 文件: AIEducationAll/frontend/src/services/dashboard.js

import apiClient from './api'; // 导入配置好的 Axios 实例

/**
 * 获取学生 Dashboard 的摘要数据。
 * 后端应返回类似课程进度、最近活动等数据。
 */
export const getStudentDashboardData = async () => {
  try {
    // API 端点保持不变
    const response = await apiClient.get('/dashboard/student');

    // 更新后的预期响应结构示例:
    // {
    //   enrolled_courses_progress: [
    //     { course_id: 1, course_title: 'Python入门', total_lessons: 10, completed_lessons: 5, progress_percentage: 50 },
    //     { course_id: 2, course_title: 'Web开发基础', total_lessons: 8, completed_lessons: 8, progress_percentage: 100 }
    //   ],
    //   recent_activity: [
    //     { activity_type: 'lesson_accessed', item_id: 3, item_title: '循环语句', timestamp: '2025-04-26T10:30:00Z', course_title: 'Python入门' },
    //     { activity_type: 'lesson_completed', item_id: 8, item_title: 'CSS 基础', timestamp: '2025-04-25T15:00:00Z', course_title: 'Web开发基础' }
    //   ]
    //   // ... 其他可能的字段
    // }
    return response.data;
  } catch (error) {
    console.error('获取学生 Dashboard 数据时出错:', error);
    throw error; // 重新抛出错误，由组件处理
  }
};