<template>
    <el-container class="default-layout-container">
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="layout-aside">
        <div class="aside-logo">
           <img src="@/assets/images/logo-placeholder.svg" alt="Logo" class="logo-img" v-if="!isCollapsed"/>
           <img src="@/assets/images/logo-small-placeholder.svg" alt="Logo" class="logo-img-small" v-else/>
           <span v-if="!isCollapsed" class="logo-text">智能教育平台</span>
        </div>
  
        <el-scrollbar>
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapsed"
            :collapse-transition="false"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
            class="el-menu-vertical-no-border"
          >
            <el-menu-item index="/app/dashboard">
              <el-icon><House /></el-icon>
              <template #title>仪表盘</template>
            </el-menu-item>
            <el-menu-item index="/app/my-courses"> <el-icon><Reading /></el-icon>
              <template #title>我的课程</template>
            </el-menu-item>
             <el-menu-item index="/app/practice"> <el-icon><EditPen /></el-icon>
              <template #title>练习中心</template>
            </el-menu-item>
             <el-menu-item index="/app/mistake-notebook"> <el-icon><Collection /></el-icon>
              <template #title>错题本</template>
            </el-menu-item>
            <el-menu-item index="/app/ai-analysis"> <el-icon><Collection /></el-icon>
              <template #title>AI智能分析</template>
            </el-menu-item>
            <el-menu-item index="/app/AI-personal"> <el-icon><Collection /></el-icon>
              <template #title>AI个人学习助手</template>
            </el-menu-item>
             <el-menu-item index="/app/labs"> <el-icon><Opportunity /></el-icon>
              <template #title>虚拟实验</template>
            </el-menu-item>
  
             <el-sub-menu index="/app/user"> <template #title>
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </template>
                <el-menu-item index="/app/profile"> <el-icon><Setting /></el-icon>
                  个人资料
                </el-menu-item>
                 <el-menu-item index="/app/settings"> <el-icon><Tools /></el-icon>
                   账户设置
                 </el-menu-item>
             </el-sub-menu>
  
          </el-menu>
        </el-scrollbar>
      </el-aside>
  
      <el-container>
        <el-header class="layout-header">
          <div class="header-left">
             <el-icon class="collapse-icon" @click="toggleSidebar">
               <Expand v-if="isCollapsed" />
               <Fold v-else />
             </el-icon>
             <span>欢迎使用智能教育平台</span>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleUserCommand">
              <span class="el-dropdown-link">
                <el-avatar :size="30" :icon="UserFilled" style="margin-right: 8px; vertical-align: middle;"/>
                {{ userName }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="settings">账户设置</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
  
        <el-main class="layout-main">
          <el-scrollbar> <router-view v-slot="{ Component }">
               <transition name="fade-transform" mode="out-in">
                 <component :is="Component" :key="route.path"/> </transition>
             </router-view>
          </el-scrollbar>
        </el-main>
      </el-container>
    </el-container>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import { useRoute, useRouter, RouterView } from 'vue-router';
  import { useAuthStore } from '@/store/auth';
  import {
    ElContainer, ElHeader, ElAside, ElMain, ElMenu, ElSubMenu, ElMenuItem,
    ElIcon, ElScrollbar, ElDropdown, ElDropdownMenu, ElDropdownItem, ElAvatar,
    ElBadge, ElBreadcrumb, ElBreadcrumbItem // Import components used
  } from 'element-plus';
  import {
    House, Reading, EditPen, Collection, Opportunity, User, Setting, Tools,
    Fold, Expand, ArrowDown, Bell, UserFilled // Import icons used
  } from '@element-plus/icons-vue';
  
  // --- Composables ---
  const route = useRoute(); // Get current route information
  const router = useRouter();
  const authStore = useAuthStore();
  
  // --- State ---
  const isCollapsed = ref(false); // Sidebar collapse state
  
  // --- Computed Properties ---
  const activeMenu = computed(() => {
    // Determine the active menu item based on the current route
    const { path } = route;
    return path; // If menu item index matches route path exactly
  });
  
  const userName = computed(() => {
    // Get username from store, provide fallback
    return authStore.getUser?.name || authStore.getUser?.username || '用户';
  });
  
  // --- Methods ---
  const toggleSidebar = () => {
    isCollapsed.value = !isCollapsed.value;
  };
  
  const handleUserCommand = (command) => {
    switch (command) {
      case 'profile':
        // Navigate to profile page
        router.push({ path: '/app/profile' }); // Adjust route name/path if needed
        break;
      case 'settings':
        // Navigate to settings page
         router.push({ path: '/app/settings' }); // Adjust route name/path if needed
        break;
      case 'logout':
        // Call logout action from store
        authStore.logout();
        break;
      default:
        break;
    }
  };
  
  </script>
  
  <style scoped>
  .default-layout-container {
    height: 100vh; /* Full viewport height */
  }
  
  /* Sidebar Styles */
  .layout-aside {
    background-color: #304156; /* Dark background for sidebar */
    transition: width 0.3s ease;
    overflow-x: hidden; /* Hide horizontal scrollbar during transition */
  }
  
  .aside-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 60px; /* Match header height */
    padding: 0 10px;
    background-color: #2b2f3a; /* Slightly different background for logo area */
    color: #fff;
    white-space: nowrap; /* Prevent text wrapping */
    overflow: hidden;
  }
  .logo-img {
    height: 32px;
    width: 32px;
    margin-right: 12px;
  }
  .logo-img-small {
     height: 32px;
     width: 32px;
  }
  .logo-text {
    font-size: 1.2em;
    font-weight: bold;
  }
  
  .el-menu-vertical-no-border {
    border-right: none; /* Remove default border */
    width: 100% !important; /* Ensure menu takes full width of aside */
  }
  /* Style menu items */
  .el-menu-vertical-no-border .el-menu-item,
  .el-menu-vertical-no-border .el-sub-menu__title {
     height: 50px;
     line-height: 50px;
  }
  .el-menu-vertical-no-border .el-menu-item.is-active {
    background-color: var(--el-color-primary-light-9) !important; /* Element Plus primary light color */
  }
  .el-menu-item [class^=el-icon],
  .el-sub-menu [class^=el-icon] {
    vertical-align: middle;
    margin-right: 5px;
    width: 24px;
    text-align: center;
    font-size: 18px;
  }
  
  
  /* Header Styles */
  .layout-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
    background-color: #fff;
    border-bottom: 1px solid #e6e6e6;
    padding: 0 20px;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    color: #606266;
  }
  .collapse-icon {
    font-size: 22px;
    cursor: pointer;
    margin-right: 15px;
  }
  
  .header-right {
    display: flex;
    align-items: center;
  }
  .el-dropdown-link {
    cursor: pointer;
    display: flex;
    align-items: center;
    color: #303133;
  }
  
  /* Main Content Styles */
  .layout-main {
    background-color: #f0f2f5; /* Light grey background for content area */
    padding: 0; /* Remove default padding */
    /* Allow main content to scroll independently */
    overflow: hidden; /* Prevent main from scrolling, let el-scrollbar handle it */
  }
  /* Ensure scrollbar takes full height */
  .layout-main .el-scrollbar {
    height: calc(100vh - 60px); /* Full height minus header height */
  }
  /* Add padding inside the scrollbar's view */
  :deep(.el-scrollbar__view) {
     padding: 20px;
  }
  
  
  /* Router View Transition Styles */
  .fade-transform-leave-active,
  .fade-transform-enter-active {
    transition: all 0.3s ease-in-out;
  }
  .fade-transform-enter-from {
    opacity: 0;
    transform: translateX(-20px);
  }
  .fade-transform-leave-to {
    opacity: 0;
    transform: translateX(20px);
  }
  </style>