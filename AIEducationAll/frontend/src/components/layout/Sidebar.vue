<template>
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical-demo"
      :collapse="isCollapse"
      router
      ><el-menu-item index="/app/dashboard">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>
  
      <el-menu-item index="/app/my-courses">
        <el-icon><Collection /></el-icon>
        <template #title>我的课程</template>
      </el-menu-item>
  
      <el-menu-item index="/app/practice">
        <el-icon><EditPen /></el-icon>
        <template #title>练习中心</template>
      </el-menu-item>
  
      <el-menu-item index="/app/mistake-notebook"> <el-icon><Memo /></el-icon> <template #title>我的错题本</template>
      </el-menu-item>
      </el-menu>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { useRoute } from 'vue-router';
  import {
    DataAnalysis,
    Collection,
    EditPen,
    Memo, // <--- 导入新图标
    // ... 其他需要的图标
  } from '@element-plus/icons-vue';
  
  // (示例) 可能需要 props 来控制菜单折叠状态
  // const props = defineProps({
  //   isCollapse: Boolean
  // });
  
  const route = useRoute();
  const activeMenu = computed(() => route.path); // 高亮当前路由对应的菜单项
  
  // 如果你的侧边栏逻辑更复杂，保持原有逻辑即可，只需添加新的 el-menu-item
  </script>
  
  <style scoped>
  /* 侧边栏样式 */
  .el-menu-vertical-demo:not(.el-menu--collapse) {
    width: 200px;
    min-height: 400px;
  }
  </style>