// AIEducationAll/frontend/src/services/aiAnalysis.js
import apiClient from './api';

/**
 * 获取当前学生的 AI 分析统计数据 Dashboard (增强版)
 * GET /api/v1/ai-analysis/student/dashboard
 * @returns {Promise<Object>} 学生 AI 分析数据 (StudentAIDashboardData Schema)
 */
export const getStudentAIDashboard = async () => { // 函数名可以更新以反映内容
    try {
        const response = await apiClient.get('/ai-analysis/student/dashboard');
        // 后端现在返回 StudentAIDashboardData 结构的数据
        // { core_metrics: {...}, ongoing_courses_progress: [...], recent_activity: [...], ... }
        return response.data;
    } catch (error) {
        console.error('获取学生 AI Dashboard 数据时出错:', error.response?.data || error.message);
        throw error;
    }
};

/**
 * 获取当前学生的学习推荐
 * GET /api/v1/ai-analysis/student/recommendations
 * @param {number} limit - 获取推荐的数量
 * @returns {Promise<Array>} 推荐对象列表 (schemas.Recommendation)
 */
export const getRecommendations = async (limit = 5) => {
    try {
        const response = await apiClient.get('/ai-analysis/student/recommendations', {
            params: { limit }
        });
        // Backend returns List[schemas.Recommendation]
        return response.data;
    } catch (error) {
        console.error('获取学习推荐时出错:', error.response?.data || error.message);
        throw error;
    }
};

/**
 * 用户忽略一条推荐
 * PUT /api/v1/ai-analysis/student/recommendations/{recommendation_id}/dismiss
 * @param {number} recommendationId - 要忽略的推荐 ID
 * @returns {Promise<Object>} 更新后的推荐对象 (status='dismissed')
 */
export const dismissRecommendation = async (recommendationId) => {
     if (!recommendationId) throw new Error("Recommendation ID is required.");
    try {
        const response = await apiClient.put(`/ai-analysis/student/recommendations/${recommendationId}/dismiss`);
        return response.data;
    } catch (error) {
        console.error(`忽略推荐 ${recommendationId} 时出错:`, error.response?.data || error.message);
        throw error;
    }
};