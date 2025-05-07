import apiClient from './api';

// 创建新课程
export const createCourse = async (courseData) => {
    // courseData 应匹配后端的 CourseCreate schema: {title, description?}
    try {
        const response = await apiClient.post('/courses/', courseData);
        // 后端返回创建的课程数据 (schemas.Course)
        return response.data;
    } catch (error) {
        console.error('创建课程时出错:', error);
        throw error;
    }
};

// 获取课程列表 (分页)
export const getCourses = async (skip = 0, limit = 100) => {
    try {
        const response = await apiClient.get('/courses/', {
            params: { skip, limit }
        });
        // 后端返回课程数据列表 ([schemas.Course])
        return response.data;
    } catch (error) {
        console.error('获取课程列表时出错:', error);
        throw error;
    }
};

// 获取特定课程详情
// *** 修改点：courseId -> course_id ***
export const getCourseById = async (course_id) => {
    try {
        const response = await apiClient.get(`/courses/${course_id}`);
        // 后端返回课程数据 (schemas.Course)
        return response.data;
    } catch (error) {
        console.error(`获取课程 ${course_id} 时出错:`, error);
        throw error;
    }
};

// 更新课程
// *** 修改点：courseId -> course_id ***
export const updateCourse = async (course_id, updateData) => {
    // updateData 应匹配后端的 CourseUpdate schema: {title?, description?}
    try {
        const response = await apiClient.put(`/courses/${course_id}`, updateData);
        // 后端返回更新后的课程数据 (schemas.Course)
        return response.data;
    } catch (error) {
        console.error(`更新课程 ${course_id} 时出错:`, error);
        throw error;
    }
};

// 删除课程
// *** 修改点：courseId -> course_id ***
export const deleteCourse = async (course_id) => {
    try {
        // 成功时预期返回 204 No Content
        await apiClient.delete(`/courses/${course_id}`);
        return true; // 表示成功
    } catch (error) {
        console.error(`删除课程 ${course_id} 时出错:`, error);
        throw error;
    }
};