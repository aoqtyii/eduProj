import apiClient from './api';

// 更新 (或创建) 课时进度
// *** 修改点：lessonId -> lesson_id ***
export const updateLessonProgress = async (lesson_id, progressData) => {
    // progressData 应匹配后端的 ProgressUpdate schema: {completed?, score?}
    try {
        const response = await apiClient.post(`/progress/lesson/${lesson_id}`, progressData);
        // 后端返回更新/创建的进度数据 (schemas.Progress)
        return response.data;
    } catch (error) {
        console.error(`更新课时 ${lesson_id} 进度时出错:`, error);
        throw error;
    }
};

// 如果需要，添加其他与进度相关的 API 调用 (例如 GET /progress/lesson/{lesson_id})