import { createRouter, createWebHistory } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useAuthStore } from '@/store/auth' // Import auth store

// Define Routes with Lazy Loading
const routes = [
  // Routes for unauthenticated users (using AuthLayout)
  {
    path: '/',
    component: AuthLayout, // Use layout for grouping
    children: [
      {
        path: 'login',
        name: 'Login',
        // Lazy load the component
        component: () => import('@/views/auth/LoginPage.vue'),
        meta: { requiresGuest: true } // Only accessible if not logged in
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('@/views/auth/ForgotPasswordPage.vue'), // Placeholder
        meta: { requiresGuest: true }
      },
       // Redirect root path to login if not logged in, or dashboard if logged in
      {
        path: '',
        redirect: '/login'
      }
    ]
  },

  // --- 修改点：在 DefaultLayout 的 children 中添加 "MyCourses" 路由 ---
  {
    path: '/app', // 认证后路由的前缀
    component: DefaultLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardPage.vue'),
      },
      // --- 新增路由 ---
      {
        path: 'my-courses', // 定义路径
        name: 'MyCourses', // 路由名称
        // 懒加载 "我的课程" 页面组件
        component: () => import('@/views/courses/MyCoursesPage.vue'),
        meta: { title: '我的课程' } // 可选：为页面添加标题元信息
      },
      {
        // Example: /app/course/1/lesson/3
        path: 'course/:courseId/lesson/:lessonId',
        name: 'LessonView',
        component: () => import('@/views/lessons/LessonViewPage.vue'),
        props: true, // Pass route params (courseId, lessonId) as props to the component
        meta: { title: '学习课时' } // Optional page title
      },
      // --- 添加练习中心路由 ---
      {
        path: 'practice', // 练习中心主页，列出模块
        name: 'PracticeList',
        component: () => import('@/views/practice/PracticeListPage.vue'),
        meta: { title: '练习中心' }
      },
      {
        // 动态路由，匹配具体的练习会话
        // 用户通过 PracticeListPage 点击模块 -> 调用 startPracticeSession -> 获取 session_id -> 跳转到此路由
        path: 'practice/session/:sessionId',
        name: 'PracticeSession',
        component: () => import('@/views/practice/PracticeSessionPage.vue'),
        props: true, // 将路由参数 (:sessionId) 作为 props 传递给组件
        meta: { title: '开始练习' }
      },
      {
        // 显示练习会话结果的路由
        path: 'practice/session/:sessionId/results',
        name: 'PracticeResults',
        component: () => import('@/views/practice/PracticeResultsPage.vue'),
        props: true, // 将路由参数 (:sessionId) 作为 props 传递给组件
        meta: { title: '练习结果' }
      },
      {
        path: 'mistake-notebook', // 定义路径
        name: 'MistakeNotebook', // 路由名称
        // 懒加载错题本页面组件
        component: () => import('@/views/mistakes/MistakeNotebookPage.vue'),
        meta: { title: '我的错题本' } // 页面标题
      },
      {
        path: 'ai-analysis', // 定义路径
        name: 'StudentAIDashboard', // 路由名称
        // 懒加载 AI 分析 Dashboard 页面组件
        component: () => import('@/views/analysis/StudentAIDashboard.vue'),
        meta: { title: '智能分析' } // 页面标题
      },
      // --- 结束添加练习中心路由 ---
      // --- 结束新增 ---
      // {
      //   path: 'profile',
      //   name: 'Profile',
      //   component: () => import('@/views/profile/ProfilePage.vue'),
      // },
      {
        path: '', // /app 路径重定向到 Dashboard
        redirect: { name: 'Dashboard' }
      }
    ]
  }

  // Catch-all 404 route (optional)
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue') }
];

// Create Router Instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Use HTML5 history mode
  routes,
});

// Navigation Guard (Authentication Check)
router.beforeEach((to, from, next) => {
  // IMPORTANT: Initialize Pinia store correctly BEFORE guard runs.
  // This might require adjusting where/how the store is imported or ensuring Pinia is fully initialized.
  // In simpler setups, directly importing here might work, but be cautious in complex apps.
  const authStore = useAuthStore(); // Get auth store instance

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);
  const isAuthenticated = authStore.isAuthenticated; // Check if user is logged in (based on token/state)

  if (requiresAuth && !isAuthenticated) {
    // If route requires login and user is not logged in, redirect to login
    console.log('Navigation Guard: Requires auth, not authenticated. Redirecting to login.');
    next({ name: 'Login', query: { redirect: to.fullPath } }); // Pass redirect query
  } else if (requiresGuest && isAuthenticated) {
    // If route is for guests (like login) and user is logged in, redirect to dashboard
    console.log('Navigation Guard: Requires guest, but authenticated. Redirecting to dashboard.');
    next({ name: 'Dashboard' });
  } else {
    // Otherwise, allow navigation
    console.log('Navigation Guard: Proceeding.');
    next();
  }
});

export default router;