// AIEducationAll/frontend/src/services/practice.js
import apiClient from './api'; // 导入配置好的 Axios 实例

/**
 * 获取可用的练习模块列表
 * GET /api/v1/practice/modules/
 * @param {number} skip - 分页跳过数量
 * @param {number} limit - 每页限制数量
 * @returns {Promise<Array>} 练习模块对象列表 (schemas.PracticeModule)
 */
export const getPracticeModules = async (skip = 0, limit = 100) => {
    try {
        const response = await apiClient.get('/practice/modules/', {
            params: { skip, limit }
        });
        // Expected backend response: List[schemas.PracticeModule]
        // Example: [{id: 1, title: '模块1', description: '...', course_id: null, ...}, ...]
        return response.data;
    } catch (error) {
        console.error('获取练习模块列表时出错:', error.response?.data || error.message);
        throw error;
    }
};

/**
 * 获取指定模块的所有问题（包括选项）
 * GET /api/v1/practice/modules/{module_id}/questions
 * @param {number} moduleId - 练习模块的 ID
 * @returns {Promise<Array>} 问题对象列表 (schemas.PracticeQuestionWithOptions)
 */
export const getModuleQuestions = async (moduleId) => {
    if (!moduleId) throw new Error("Module ID is required.");
    try {
        const response = await apiClient.get(`/practice/modules/${moduleId}/questions`);
        // Expected backend response: List[schemas.PracticeQuestionWithOptions]
        // Example: [{id: 1, module_id: 1, question_text: '?', type: 'mc', answers: [{id: 1, text: 'A', correct: false}, ...]}, ...]
        return response.data;
    } catch (error) {
        console.error(`获取模块 ${moduleId} 的问题时出错:`, error.response?.data || error.message);
        throw error;
    }
};

/**
 * 开始一个新的练习会话
 * POST /api/v1/practice/sessions/
 * @param {number} moduleId - 要开始练习的模块 ID
 * @returns {Promise<Object>} 创建的练习会话对象 (schemas.PracticeSession)
 */
export const startPracticeSession = async (moduleId) => {
     if (!moduleId) throw new Error("Module ID is required to start a session.");
    try {
        // Request body: { module_id: moduleId }
        const response = await apiClient.post('/practice/sessions/', { module_id: moduleId });
        // Expected backend response: schemas.PracticeSession
        // Example: {id: 123, user_id: 1, module_id: 1, started_at: '...', status: 'in_progress', ...}
        return response.data;
    } catch (error) {
        console.error(`开始模块 ${moduleId} 的练习会话时出错:`, error.response?.data || error.message);
        throw error;
    }
};

/**
 * 提交练习会话的答案
 * POST /api/v1/practice/sessions/{session_id}/submit
 * @param {number} sessionId - 练习会话的 ID
 * @param {Array<Object>} attempts - 用户提交的答案列表，每个对象应匹配 schemas.PracticeAttemptSubmit ({question_id, selected_answer_id?, user_answer_text?})
 * @returns {Promise<Object>} 会话结果对象 (schemas.PracticeSessionResult)
 */
export const submitSessionAnswers = async (sessionId, attempts) => {
    if (!sessionId) throw new Error("Session ID is required.");
    if (!Array.isArray(attempts)) throw new Error("Attempts must be an array.");
    try {
        // Request body: attempts (List[schemas.PracticeAttemptSubmit])
        const response = await apiClient.post(`/practice/sessions/${sessionId}/submit`, attempts);
        // Expected backend response: schemas.PracticeSessionResult
        // Example: {id: 123, ..., status: 'completed', score: 80.0, attempts: [{id: 1, q_id: 1, sel_ans_id: 2, correct: true, question: {...}}, ...]}
        return response.data;
    } catch (error) {
        console.error(`提交会话 ${sessionId} 的答案时出错:`, error.response?.data || error.message);
        throw error;
    }
};

/**
 * 获取指定练习会话的结果
 * GET /api/v1/practice/sessions/{session_id}/results
 * @param {number} sessionId - 练习会话的 ID
 * @returns {Promise<Object>} 会话结果对象 (schemas.PracticeSessionResult)
 */
export const getSessionResults = async (sessionId) => {
    if (!sessionId) throw new Error("Session ID is required.");
    try {
        const response = await apiClient.get(`/practice/sessions/${sessionId}/results`);
         // Expected backend response: schemas.PracticeSessionResult (same as submit)
        return response.data;
    } catch (error) {
        console.error(`获取会话 ${sessionId} 的结果时出错:`, error.response?.data || error.message);
        throw error;
    }
};