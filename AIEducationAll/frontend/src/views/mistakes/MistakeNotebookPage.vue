<template>
    <div class="mistake-notebook-page">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>我的错题本</span>
            <div class="filters">
               <el-select
                 v-model="filters.status"
                 placeholder="按状态筛选"
                 clearable
                 @change="handleStatusChange"
                 style="width: 150px;"
               >
                 <el-option label="全部" value=""></el-option>
                 <el-option label="新题" value="new"></el-option>
                 <el-option label="已复习" value="reviewed"></el-option>
                 <el-option label="已掌握" value="mastered"></el-option>
               </el-select>
            </div>
          </div>
        </template>
  
        <el-table :data="entries" v-loading="loading" style="width: 100%">
          <el-table-column type="expand">
            <template #default="props">
              <div class="question-details">
                <p><strong>题目详情:</strong></p>
                <div v-html="props.row.question?.question_text || '无题目文本'"></div>
                <div v-if="props.row.question?.question_type === 'multiple_choice' && props.row.question.answers?.length">
                  <p style="margin-top: 10px;"><strong>选项:</strong></p>
                  <ul>
                    <li v-for="answer in props.row.question.answers" :key="answer.id" :class="{ 'correct-answer': answer.is_correct }">
                      {{ answer.answer_text }} <el-tag v-if="answer.is_correct" type="success" size="small" effect="dark">正确</el-tag>
                    </li>
                  </ul>
                </div>
                 <div v-if="props.row.question?.explanation">
                   <p style="margin-top: 10px;"><strong>解析:</strong></p>
                   <div v-html="props.row.question.explanation"></div>
                 </div>
              </div>
            </template>
          </el-table-column>
  
          <el-table-column prop="question.question_text" label="题目 (缩略)" min-width="250">
             <template #default="scope">
                <div class="truncated-text" :title="scope.row.question?.question_text">
                  {{ scope.row.question?.question_text || 'N/A' }}
                </div>
             </template>
          </el-table-column>
  
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ formatStatus(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
  
          <el-table-column prop="added_at" label="添加时间" width="180">
             <template #default="scope">
               {{ formatDateTime(scope.row.added_at) }}
             </template>
          </el-table-column>
  
          <el-table-column prop="notes" label="笔记" min-width="150">
             <template #default="scope">
                <div class="truncated-text" :title="scope.row.notes">
                  {{ scope.row.notes || '-' }}
                </div>
             </template>
          </el-table-column>
  
          <el-table-column label="操作" fixed="right" width="260">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="openNotesDialog(scope.row)">
                {{ scope.row.notes ? '编辑笔记' : '添加笔记' }}
              </el-button>
               <el-dropdown @command="(command) => handleStatusUpdate(scope.row.id, command)" style="margin-left: 10px;">
                  <el-button link type="primary" size="small">
                    更新状态<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="new" :disabled="scope.row.status === 'new'">标记为新题</el-dropdown-item>
                      <el-dropdown-item command="reviewed" :disabled="scope.row.status === 'reviewed'">标记为已复习</el-dropdown-item>
                      <el-dropdown-item command="mastered" :disabled="scope.row.status === 'mastered'">标记为已掌握</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              <el-button link type="danger" size="small" @click="handleDeleteEntry(scope.row.id)" style="margin-left: 10px;">
                移除
              </el-button>
            </template>
          </el-table-column>
  
          <template #empty>
              <el-empty description="错题本是空的，去练习中心挑战一下吧！" />
          </template>
        </el-table>
  
        <el-pagination
          v-if="pagination.total > 0"
          style="margin-top: 20px;"
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
  
        <el-dialog
          v-model="notesDialogVisible"
          :title="currentEntry ? (currentEntry.notes ? '编辑笔记' : '添加笔记') : '笔记'"
          width="500px"
          @close="resetCurrentEntry"
        >
          <el-input
            v-if="currentEntry"
            v-model="currentEntryNotes"
            type="textarea"
            :rows="5"
            placeholder="请输入笔记内容..."
          />
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="notesDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveNotes" :loading="notesSaving">
                保存
              </el-button>
            </span>
          </template>
        </el-dialog>
  
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, watch } from 'vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { ArrowDown } from '@element-plus/icons-vue';
  // 导入 API 服务函数
  import { getMistakeEntries, updateMistakeEntry, deleteMistakeEntry } from '@/services/mistakeNotebook'; //
  
  // --- 响应式状态 ---
  const entries = ref([]); // 错题条目列表
  const loading = ref(true); // 表格加载状态
  const error = ref(null); // 错误信息
  const pagination = reactive({
    currentPage: 1,
    pageSize: 10,
    total: 0,
  });
  const filters = reactive({
    status: '', // 筛选状态，空字符串表示全部
  });
  const notesDialogVisible = ref(false); // 笔记对话框可见性
  const currentEntry = ref(null); // 当前正在编辑笔记的条目
  const currentEntryNotes = ref(''); // 当前编辑的笔记内容
  const notesSaving = ref(false); // 笔记保存加载状态
  
  // --- 方法 ---
  
  // 获取错题数据
  const fetchEntries = async () => {
    loading.value = true;
    error.value = null;
    try {
      const params = {
        skip: (pagination.currentPage - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        status: filters.status || undefined, // 如果为空则不传 status 参数
      };
      const response = await getMistakeEntries(params); // 调用 API 获取数据
      // 注意：后端返回的数据可能不是分页对象，而是列表本身。我们需要根据列表长度判断总数（如果后端不返回总数）
      // 假设后端 API 不直接返回总数，这里只是一个前端分页展示
      entries.value = response; //
      // TODO: 后端最好能返回总条目数以便正确分页，这里暂时模拟总数
      // pagination.total = response.totalCount; // 假设后端返回 totalCount
       if (pagination.currentPage === 1 && response.length < pagination.pageSize) {
         pagination.total = response.length; // 如果第一页数据少于页大小，假设这就是总数
       } else if (response.length === 0 && pagination.currentPage > 1) {
          // 如果当前页没有数据，可能需要回到上一页或将总数设置为已知最大值
          // pagination.total = (pagination.currentPage - 1) * pagination.pageSize;
          // 更好的方法是后端直接返回 total
          pagination.total = entries.value.length; // 临时处理
       } else {
          // 无法确定总数，可能需要显示更多或由后端提供
          pagination.total = entries.value.length + (response.length === pagination.pageSize ? pagination.pageSize : 0); // 估算
       }
  
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '加载错题数据失败';
      ElMessage.error(error.value);
      entries.value = [];
      pagination.total = 0;
    } finally {
      loading.value = false;
    }
  };
  
  // 页面大小改变
  const handleSizeChange = (newSize) => {
    pagination.pageSize = newSize;
    pagination.currentPage = 1; // 回到第一页
    fetchEntries();
  };
  
  // 当前页改变
  const handlePageChange = (newPage) => {
    pagination.currentPage = newPage;
    fetchEntries();
  };
  
  // 状态筛选改变
  const handleStatusChange = () => {
    pagination.currentPage = 1; // 回到第一页
    fetchEntries();
  };
  
  // 打开笔记对话框
  const openNotesDialog = (entry) => {
    currentEntry.value = entry;
    currentEntryNotes.value = entry.notes || ''; // 加载现有笔记
    notesDialogVisible.value = true;
  };
  
  // 重置当前编辑条目
  const resetCurrentEntry = () => {
      currentEntry.value = null;
      currentEntryNotes.value = '';
  }
  
  // 保存笔记
  const saveNotes = async () => {
    if (!currentEntry.value) return;
    notesSaving.value = true;
    try {
      const updatedData = { notes: currentEntryNotes.value };
      const updatedEntry = await updateMistakeEntry(currentEntry.value.id, updatedData); //
      // 更新表格中的数据
      const index = entries.value.findIndex(e => e.id === updatedEntry.id);
      if (index !== -1) {
        // 直接更新可能不会触发响应式更新，如果 response_model 包含 question，需要注意
        // entries.value[index] = updatedEntry;
        // 仅更新笔记字段更安全
         entries.value[index].notes = updatedEntry.notes;
      }
      ElMessage.success('笔记已保存');
      notesDialogVisible.value = false;
    } catch (err) {
      ElMessage.error('保存笔记失败');
    } finally {
      notesSaving.value = false;
    }
  };
  
  // 更新状态
  const handleStatusUpdate = async (entryId, newStatus) => {
     try {
       loading.value = true; // 可以用表格 loading 或单独的 loading 状态
       const updatedEntry = await updateMistakeEntry(entryId, { status: newStatus, last_reviewed_at: newStatus !== 'new' ? new Date().toISOString() : undefined }); // 如果不是 new，更新复习时间
       // 更新表格中的数据
       const index = entries.value.findIndex(e => e.id === updatedEntry.id);
       if (index !== -1) {
         entries.value[index].status = updatedEntry.status;
         entries.value[index].last_reviewed_at = updatedEntry.last_reviewed_at;
       }
       ElMessage.success(`状态已更新为 ${formatStatus(newStatus)}`);
     } catch (err) {
       ElMessage.error('更新状态失败');
     } finally {
        loading.value = false;
     }
  };
  
  
  // 删除条目
  const handleDeleteEntry = (entryId) => {
    ElMessageBox.confirm(
      '确定要从错题本中移除这个题目吗？',
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(async () => {
      try {
        loading.value = true;
        await deleteMistakeEntry(entryId); //
        ElMessage.success('错题已移除');
        // 刷新列表
        fetchEntries(); // 重新获取当前页数据
        // 或者从本地列表移除
        // entries.value = entries.value.filter(e => e.id !== entryId);
        // pagination.total -= 1; // 如果本地管理 total
      } catch (err) {
        ElMessage.error('移除失败');
      } finally {
         loading.value = false;
      }
    }).catch(() => {
      // 用户取消
    });
  };
  
  // --- 辅助函数 ---
  // 格式化状态显示文本
  const formatStatus = (status) => {
    switch (status) {
      case 'new': return '新题';
      case 'reviewed': return '已复习';
      case 'mastered': return '已掌握';
      default: return status;
    }
  };
  
  // 获取状态标签类型
  const getStatusTagType = (status) => {
    switch (status) {
      case 'new': return ''; // 默认
      case 'reviewed': return 'warning';
      case 'mastered': return 'success';
      default: return 'info';
    }
  };
  
  // 格式化日期时间
  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return '-';
    try {
      return new Date(dateTimeString).toLocaleString('zh-CN');
    } catch (e) {
      return dateTimeString; // 返回原始字符串如果格式化失败
    }
  };
  
  
  // --- 生命周期钩子 ---
  onMounted(() => {
    fetchEntries(); // 组件挂载时获取数据
  });
  
  </script>
  
  <style scoped lang="scss">
  .mistake-notebook-page {
    padding: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .filters {
    /* 样式留空，可根据需要添加 */
  }
  
  .question-details {
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 4px;
    margin: 10px;
  
    ul {
      padding-left: 20px;
      margin-top: 5px;
    }
    li {
      margin-bottom: 5px;
    }
    .correct-answer {
      font-weight: bold;
      color: #67C23A; // Element Plus success color
    }
    // 确保 v-html 渲染的内容换行正常
    :deep(div) {
        white-space: pre-wrap; /* 保留换行符 */
        word-wrap: break-word; /* 允许长单词换行 */
    }
  }
  
  .truncated-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* 覆盖默认的链接按钮下划线 (如果需要) */
  .el-button.is-link {
      text-decoration: none;
  }
  </style>