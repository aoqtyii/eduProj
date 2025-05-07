// 文件: AIEducationAll/frontend/src/services/mistakeNotebook.js

import apiClient from './api'; // 导入配置好的 Axios 实例

/**
 * 获取当前用户的错题本条目列表
 * GET /api/v1/mistake-notebook/
 * @param {object} params - 查询参数
 * @param {string} [params.status] - 按状态过滤 (e.g., 'new', 'reviewed', 'mastered')
 * @param {number} [params.skip=0] - 分页跳过数量
 * @param {number} [params.limit=100] - 每页限制数量
 * @returns {Promise<Array>} 错题条目对象列表 (schemas.MistakeNotebookEntryPublic)，包含嵌套的 question 信息
 */
export const getMistakeEntries = async (params = { skip: 0, limit: 100 }) => {
    try {
        const response = await apiClient.get('/mistake-notebook/', { params }); //
        // 后端返回 List[schemas.MistakeNotebookEntryPublic]
        // 每个对象包含 { id, user_id, question_id, added_at, status, notes, ..., question: { id, question_text, ..., answers: [...] } }
        return response.data;
    } catch (error) {
        console.error('获取错题本列表时出错:', error.response?.data || error.message);
        throw error;
    }
};

/**
 * 更新指定错题条目的状态或笔记
 * PUT /api/v1/mistake-notebook/entry/{entry_id}
 * @param {number} entryId - 错题条目的 ID
 * @param {object} updateData - 更新的数据，匹配 schemas.MistakeNotebookEntryUpdate ({ status?, notes?, last_reviewed_at? })
 * @returns {Promise<Object>} 更新后的错题条目对象 (schemas.MistakeNotebookEntryPublic)
 */
export const updateMistakeEntry = async (entryId, updateData) => {
    if (!entryId) throw new Error("Entry ID is required.");
    try {
        const response = await apiClient.put(`/mistake-notebook/entry/${entryId}`, updateData); //
        return response.data;
    } catch (error) {
        console.error(`更新错题条目 ${entryId} 时出错:`, error.response?.data || error.message);
        throw error;
    }
};

/**
 * 从错题本删除一个条目
 * DELETE /api/v1/mistake-notebook/entry/{entry_id}
 * @param {number} entryId - 错题条目的 ID
 * @returns {Promise<boolean>} 表示删除是否成功 (后端成功返回 204)
 */
export const deleteMistakeEntry = async (entryId) => {
    if (!entryId) throw new Error("Entry ID is required.");
    try {
        await apiClient.delete(`/mistake-notebook/entry/${entryId}`); //
        return true; // 表示成功
    } catch (error) {
        console.error(`删除错题条目 ${entryId} 时出错:`, error.response?.data || error.message);
        // 如果后端返回 404 等，这里会抛出异常
        throw error;
    }
};

/**
 * (可选) 手动将题目添加到错题本
 * POST /api/v1/mistake-notebook/question/{question_id}
 * @param {number} questionId - 要添加的题目 ID
 * @param {string} [notes] - 可选的笔记内容
 * @returns {Promise<Object>} 添加或已存在的错题条目对象 (schemas.MistakeNotebookEntryPublic)
 */
export const addMistakeEntryManually = async (questionId, notes = null) => {
    if (!questionId) throw new Error("Question ID is required.");
    try {
        const payload = notes ? { notes: notes } : {}; // 如果有笔记，则加入请求体
        const response = await apiClient.post(`/mistake-notebook/question/${questionId}`, payload); //
        return response.data;
    } catch (error) {
        console.error(`手动添加题目 ${questionId} 到错题本时出错:`, error.response?.data || error.message);
        throw error;
    }
};