import axios from 'axios';
import { useAuthStore } from '@/store/auth'; // 导入 store 以获取 token

// 创建 Axios 实例
const apiClient = axios.create({
  // 使用环境变量获取基础 URL，并设置默认值为 /api/v1
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1', // *** 修改点：默认值改为 /api/v1 ***
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// 请求拦截器：添加 Authorization 请求头
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.getToken; // 从 store 获取 token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理全局错误 (例如 401 未授权)
apiClient.interceptors.response.use(
  (response) => {
    // 2xx 范围内的状态码会触发该函数
    return response;
  },
  (error) => {
    // 超出 2xx 范围的状态码会触发该函数
    if (error.response) {
      const { status } = error.response;
      if (status === 401) {
        // 未授权：Token 过期或无效
        const authStore = useAuthStore();
        console.error('API 错误: 401 未授权。正在登出。');
        authStore.logout(); // 触发登出操作
        // 可选：重定向到登录页或显示消息
      } else {
        // 处理其他错误 (例如 403 禁止访问, 404 未找到, 500 服务器错误)
        console.error(`API 错误: ${status}`, error.response.data);
      }
    } else if (error.request) {
      // 请求已发出，但未收到响应
      console.error('API 错误: 未收到响应', error.request);
    } else {
      // 设置请求时触发了一个错误
      console.error('API 错误: 请求设置失败', error.message);
    }
    return Promise.reject(error); // 必须拒绝 promise
  }
);

export default apiClient;