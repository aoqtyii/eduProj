import apiClient from './api';

// 为课程创建新课时
export const createLesson = async (lessonData) => {
    // lessonData 应匹配后端的 LessonCreate schema: {title, content?, order?, course_id}
    try {
        const response = await apiClient.post('/lessons/', lessonData);
        // 后端返回创建的课时数据 (schemas.Lesson)
        return response.data;
    } catch (error) {
        console.error('创建课时时出错:', error);
        throw error;
    }
};

// 获取特定课程的课时列表 (分页)
// *** 修改点：courseId -> course_id ***
export const getLessonsByCourse = async (course_id, skip = 0, limit = 100) => {
    try {
        const response = await apiClient.get(`/lessons/by_course/${course_id}`, {
            params: { skip, limit }
        });
        // 后端返回课时数据列表 ([schemas.Lesson])
        return response.data;
    } catch (error) {
        console.error(`获取课程 ${course_id} 的课时列表时出错:`, error);
        throw error;
    }
};

// 获取特定课时详情
// *** 修改点：lessonId -> lesson_id ***
export const getLessonById = async (lesson_id) => {
    try {
        const response = await apiClient.get(`/lessons/${lesson_id}`);
        // 后端返回课时数据 (schemas.Lesson)
        return response.data;
    } catch (error) {
        console.error(`获取课时 ${lesson_id} 时出错:`, error);
        throw error;
    }
};

// 更新课时
// *** 修改点：lessonId -> lesson_id ***
export const updateLesson = async (lesson_id, updateData) => {
    // updateData 应匹配后端的 LessonUpdate schema: {title?, content?, order?}
    try {
        const response = await apiClient.put(`/lessons/${lesson_id}`, updateData);
        // 后端返回更新后的课时数据 (schemas.Lesson)
        return response.data;
    } catch (error) {
        console.error(`更新课时 ${lesson_id} 时出错:`, error);
        throw error;
    }
};

// 删除课时
// *** 修改点：lessonId -> lesson_id ***
export const deleteLesson = async (lesson_id) => {
    try {
        // 成功时预期返回 204 No Content
        await apiClient.delete(`/lessons/${lesson_id}`);
        return true; // 表示成功
    } catch (error) {
        console.error(`删除课时 ${lesson_id} 时出错:`, error);
        throw error;
    }
};