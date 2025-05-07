import apiClient from './api';

// 当前用户报名参加课程
// *** 修改点：courseId -> course_id in function argument and payload ***
export const enrollInCourse = async (course_id) => {
    // 后端预期 {"course_id": N}
    try {
        const response = await apiClient.post('/enrollments/', { course_id: course_id });
        // 后端返回创建的报名数据 (schemas.Enrollment)
        return response.data;
    } catch (error) {
        console.error(`报名课程 ${course_id} 时出错:`, error);
        throw error;
    }
};

// 获取当前用户的报名列表 (分页)
export const getMyEnrollments = async (skip = 0, limit = 100) => {
    try {
        const response = await apiClient.get('/enrollments/me', {
            params: { skip, limit }
        });
        // --- 修改点：更新注释说明返回的数据结构 ---
        // 后端返回报名数据列表 ([schemas.EnrollmentPublic])
        // 每个对象现在包含嵌套的 'course' 对象:
        // {
        //   id: ..., user_id: ..., course_id: ..., enrollment_date: ...,
        //   course: { id: ..., title: '...', description: '...' } // <-- 包含课程信息
        // }
        return response.data;
    } catch (error) {
        console.error('获取用户报名列表时出错:', error);
        throw error;
    }
};

// 当前用户取消报名特定课程
// *** 修改点：courseId -> course_id ***
export const unenrollFromCourse = async (course_id) => {
    try {
        // 成功时预期返回 204 No Content
        await apiClient.delete(`/enrollments/course/${course_id}`);
        return true; // 表示成功
    } catch (error) {
        console.error(`取消报名课程 ${course_id} 时出错:`, error);
        throw error;
    }
};