<template>
  <div class="app-wrapper" :class="{ dark: isDark }">
    <HeaderBar
      :target-title="targetTitle"
      @open-settings="showSettingsModal = true"
      @toggle-collapse="handleToggleCollapse"
    />

    <CategoryNav
      :categories="categories"
      :selected-category-id="selectedCategoryId"
      @select-category="handleSelectCategory"
      @add-category="handleAddCategory"
      @edit-category="handleEditCategory"
      @delete-category="handleDeleteCategory"
    />

    <SearchBar
      ref="searchBarRef"
      v-model="searchKeyword"
      @create-reply="handleOpenCreateModal"
    />

    <ReplyCardList
      :replies="replies"
      @send-reply="handleSendReply"
      @edit-reply="handleOpenEditModal"
      @delete-reply="handleDeleteReply"
      @create-reply="handleOpenCreateModal"
    />

    <!-- 新增/编辑话术弹窗 -->
    <ReplyEditModal
      v-if="showReplyModal"
      :initial-data="editingReply"
      :categories="categories"
      :default-category-id="selectedCategoryId"
      @close="showReplyModal = false"
      @save="handleSaveReply"
    />

    <!-- 设置弹窗 -->
    <SettingsModal
      v-if="showSettingsModal"
      @close="showSettingsModal = false"
      @theme-changed="handleThemeChange"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import HeaderBar from './components/HeaderBar.vue'
import CategoryNav from './components/CategoryNav.vue'
import SearchBar from './components/SearchBar.vue'
import ReplyCardList from './components/ReplyCardList.vue'
import ReplyEditModal from './components/ReplyEditModal.vue'
import SettingsModal from './components/SettingsModal.vue'

const isDark = ref(false)
const targetTitle = ref('')
const categories = ref([])
const replies = ref([])
const selectedCategoryId = ref(null)
const searchKeyword = ref('')
const searchBarRef = ref(null)

const showReplyModal = ref(false)
const editingReply = ref(null)
const showSettingsModal = ref(false)

async function loadCategories() {
  if (window.pywebview && window.pywebview.api) {
    categories.value = await window.pywebview.api.getCategories()
  } else {
    // 浏览器开发调试 Mock 数据
    categories.value = [
      { id: 1, name: '常见问答', sort_order: 1, reply_count: 2 },
      { id: 2, name: '售后服务', sort_order: 2, reply_count: 1 },
      { id: 3, name: '报价资料', sort_order: 3, reply_count: 1 }
    ]
  }
}

async function loadReplies() {
  if (window.pywebview && window.pywebview.api) {
    replies.value = await window.pywebview.api.getReplies(
      selectedCategoryId.value,
      searchKeyword.value
    )
  } else {
    replies.value = [
      {
        id: 1,
        category_id: 1,
        title: '问候与介绍',
        content: '您好！祝您{问候语}，很高兴为您服务。今天是{日期}，请问有什么可以帮您？',
        attachments: [],
        tags: ['问候', '高频'],
        use_count: 12
      },
      {
        id: 2,
        category_id: 2,
        title: '退换货说明',
        content: '亲，支持7天无理由退换货，请保持原包装完整并寄回指定网点。',
        attachments: [{ name: '退换货指引.pdf', path: 'C:/docs/guide.pdf' }],
        tags: ['售后'],
        use_count: 5
      }
    ]
  }
}

watch([selectedCategoryId, searchKeyword], () => {
  loadReplies()
})

function handleSelectCategory(catId) {
  selectedCategoryId.value = catId
}

async function handleAddCategory() {
  const name = prompt('请输入新分类名称：')
  if (name && name.trim()) {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.saveCategory({ name: name.trim() })
      await loadCategories()
    }
  }
}

async function handleEditCategory(category) {
  const name = prompt('修改分类名称：', category.name)
  if (name && name.trim()) {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.saveCategory({ id: category.id, name: name.trim(), sort_order: category.sort_order })
      await loadCategories()
    }
  }
}

async function handleDeleteCategory(catId) {
  if (confirm('确认删除该分类？分类下的话术也将被清除！')) {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.deleteCategory(catId)
      if (selectedCategoryId.value === catId) selectedCategoryId.value = null
      await loadCategories()
      await loadReplies()
    }
  }
}

function handleOpenCreateModal() {
  editingReply.value = null
  showReplyModal.value = true
}

function handleOpenEditModal(reply) {
  editingReply.value = reply
  showReplyModal.value = true
}

async function handleSaveReply(formData) {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.saveReply(formData)
    showReplyModal.value = false
    await loadCategories()
    await loadReplies()
  }
}

async function handleDeleteReply(replyId) {
  if (confirm('确认删除该条话术？')) {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.deleteReply(replyId)
      await loadCategories()
      await loadReplies()
    }
  }
}

async function handleSendReply(replyId, mode) {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.sendReply(replyId, mode)
    if (!res.success && res.error) {
      alert(res.error)
    } else {
      await loadReplies()
    }
  } else {
    alert(`[Mock 调试] 触发发送 mode=${mode}, replyId=${replyId}`)
  }
}

function handleToggleCollapse() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.toggleCollapse()
  }
}

function handleThemeChange(dark) {
  isDark.value = dark
}

onMounted(async () => {
  window.addEventListener('target-changed', (e) => {
    targetTitle.value = e.detail || ''
  })

  // 监听 pywebview 就绪
  window.addEventListener('pywebviewready', async () => {
    await loadCategories()
    await loadReplies()
    if (window.pywebview.api) {
      const s = await window.pywebview.api.getSettings()
      isDark.value = s.dark_mode === '1'
    }
  })

  // 浏览器开发模式直接加载
  await loadCategories()
  await loadReplies()
})
</script>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
}
</style>
