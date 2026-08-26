<template>
  <div class="app-wrapper" :class="{ dark: isDark, 'is-collapsed': isCollapsed }">
    <!-- 折叠模式下的微型悬浮微标 -->
    <CollapsedBubble
      v-if="isCollapsed"
      @expand="handleToggleCollapse"
    />

    <!-- 展开模式下的完整功能面板 -->
    <template v-else>
      <!-- 全局 Toast 提示 -->
      <Toast :toasts="toasts" />

      <HeaderBar
        :target-title="targetTitle"
        @open-settings="showSettingsModal = true"
        @toggle-collapse="handleToggleCollapse"
      />

      <CategoryNav
        :categories="categories"
        :selected-category-id="selectedCategoryId"
        @select-category="handleSelectCategory"
        @add-category="handleOpenAddCategoryModal"
        @edit-category="handleOpenEditCategoryModal"
        @delete-category="handleOpenDeleteCategoryConfirm"
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
        @delete-reply="handleOpenDeleteReplyConfirm"
        @create-reply="handleOpenCreateModal"
        @open-menu="handleOpenFloatingMenu"
      />

      <!-- 全局悬浮动作菜单（智能防遮挡） -->
      <FloatingMenu
        :visible="floatingMenu.visible"
        :anchor-rect="floatingMenu.anchorRect"
        :reply="floatingMenu.reply"
        @close="floatingMenu.visible = false"
        @select-mode="handleSendReply"
        @action="handleFloatingMenuAction"
      />

      <!-- 新增/编辑分类弹窗 -->
      <CategoryModal
        v-if="showCategoryModal"
        :category="editingCategory"
        @close="showCategoryModal = false"
        @save="handleSaveCategory"
      />

      <!-- 新增/编辑话术弹窗 -->
      <ReplyEditModal
        v-if="showReplyModal"
        :initial-data="editingReply"
        :categories="categories"
        :default-category-id="selectedCategoryId"
        @close="showReplyModal = false"
        @save="handleSaveReply"
        @toast="triggerToast"
      />

      <!-- 设置弹窗 -->
      <SettingsModal
        v-if="showSettingsModal"
        @close="showSettingsModal = false"
        @theme-changed="handleThemeChange"
        @toast="triggerToast"
      />

      <!-- 通用二次确认删除弹窗 -->
      <ConfirmModal
        v-if="confirmDialog.visible"
        :title="confirmDialog.title"
        :message="confirmDialog.message"
        :confirm-text="confirmDialog.confirmText"
        :type="confirmDialog.type"
        @confirm="handleConfirmAction"
        @cancel="confirmDialog.visible = false"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import CollapsedBubble from './components/CollapsedBubble.vue'
import Toast from './components/Toast.vue'
import HeaderBar from './components/HeaderBar.vue'
import CategoryNav from './components/CategoryNav.vue'
import SearchBar from './components/SearchBar.vue'
import ReplyCardList from './components/ReplyCardList.vue'
import FloatingMenu from './components/FloatingMenu.vue'
import CategoryModal from './components/CategoryModal.vue'
import ReplyEditModal from './components/ReplyEditModal.vue'
import SettingsModal from './components/SettingsModal.vue'
import ConfirmModal from './components/ConfirmModal.vue'

const isDark = ref(false)
const isCollapsed = ref(false)
const targetTitle = ref('')
const categories = ref([])
const replies = ref([])
const selectedCategoryId = ref(null)
const searchKeyword = ref('')
const searchBarRef = ref(null)

// 悬浮菜单状态
const floatingMenu = reactive({
  visible: false,
  anchorRect: null,
  reply: null
})

function handleOpenFloatingMenu(rect, reply) {
  floatingMenu.anchorRect = rect
  floatingMenu.reply = reply
  floatingMenu.visible = true
}

function handleFloatingMenuAction(action, reply) {
  if (action === 'edit') {
    handleOpenEditModal(reply)
  } else if (action === 'delete') {
    handleOpenDeleteReplyConfirm(reply.id)
  }
}

// 弹窗状态
const showCategoryModal = ref(false)
const editingCategory = ref(null)

const showReplyModal = ref(false)
const editingReply = ref(null)

const showSettingsModal = ref(false)

// Toast 状态
const toasts = ref([])
let toastIdCounter = 0

function showToast(type, message) {
  const id = ++toastIdCounter
  toasts.value.push({ id, type, message })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 2600)
}

function triggerToast(data) {
  showToast(data.type || 'info', data.message || '')
}

// 确认弹窗状态
const confirmDialog = reactive({
  visible: false,
  title: '确认删除',
  message: '',
  confirmText: '确认删除',
  type: 'danger',
  action: null
})

function openConfirmDialog(title, message, action, confirmText = '确认删除', type = 'danger') {
  confirmDialog.title = title
  confirmDialog.message = message
  confirmDialog.action = action
  confirmDialog.confirmText = confirmText
  confirmDialog.type = type
  confirmDialog.visible = true
}

async function handleConfirmAction() {
  if (confirmDialog.action) {
    await confirmDialog.action()
  }
  confirmDialog.visible = false
}

async function loadCategories() {
  if (window.pywebview && window.pywebview.api) {
    categories.value = await window.pywebview.api.getCategories()
  } else {
    categories.value = [
      { id: 1, name: '常用问候', sort_order: 1, reply_count: 1 },
      { id: 2, name: '售后服务', sort_order: 2, reply_count: 1 },
      { id: 3, name: '产品与报价', sort_order: 3, reply_count: 1 }
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
        title: '7天退换货政策',
        content: '亲，支持7天无理由退换货，请保持原包装完整并寄回指定网点。',
        attachments: [{ name: '退换货指引.pdf', path: 'C:/docs/guide.pdf' }],
        tags: ['售后', '政策'],
        use_count: 8
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

// 分类管理
function handleOpenAddCategoryModal() {
  editingCategory.value = null
  showCategoryModal.value = true
}

function handleOpenEditCategoryModal(category) {
  editingCategory.value = category
  showCategoryModal.value = true
}

async function handleSaveCategory(data) {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.saveCategory(data)
    if (res.success) {
      showToast('success', data.id ? '分类已更新' : '分类创建成功')
      showCategoryModal.value = false
      await loadCategories()
    } else {
      showToast('error', res.error || '保存分类失败')
    }
  } else {
    showToast('success', '分类保存成功 (Mock)')
    showCategoryModal.value = false
  }
}

function handleOpenDeleteCategoryConfirm(catId) {
  openConfirmDialog(
    '删除分类',
    '确认删除该分类？该分类下的所有话术将被同步删除，无法恢复！',
    async () => {
      if (window.pywebview && window.pywebview.api) {
        await window.pywebview.api.deleteCategory(catId)
        if (selectedCategoryId.value === catId) selectedCategoryId.value = null
        showToast('success', '分类及话术已删除')
        await loadCategories()
        await loadReplies()
      }
    }
  )
}

// 话术管理
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
    const res = await window.pywebview.api.saveReply(formData)
    if (res.success) {
      showToast('success', formData.id ? '话术已更新' : '话术创建成功')
      showReplyModal.value = false
      await loadCategories()
      await loadReplies()
    } else {
      showToast('error', res.error || '保存话术失败')
    }
  } else {
    showToast('success', '话术保存成功 (Mock)')
    showReplyModal.value = false
  }
}

function handleOpenDeleteReplyConfirm(replyId) {
  openConfirmDialog(
    '删除话术',
    '确认删除该条话术内容？删除后不可撤销。',
    async () => {
      if (window.pywebview && window.pywebview.api) {
        await window.pywebview.api.deleteReply(replyId)
        showToast('success', '话术已删除')
        await loadCategories()
        await loadReplies()
      }
    }
  )
}

// 快捷发送
async function handleSendReply(replyId, mode) {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.sendReply(replyId, mode)
    if (!res.success) {
      showToast('error', res.error || '发送失败，请确保微信窗口处于激活状态')
    } else {
      showToast('success', '发送指令已执行')
      await loadReplies()
    }
  } else {
    showToast('success', `[Mock 调试] 触发发送 mode=${mode}`)
  }
}

async function handleToggleCollapse() {
  if (window.pywebview && window.pywebview.api) {
    const state = await window.pywebview.api.toggleCollapse()
    isCollapsed.value = state
  } else {
    isCollapsed.value = !isCollapsed.value
  }
}

function handleThemeChange(dark) {
  isDark.value = dark
}

onMounted(async () => {
  window.addEventListener('target-changed', (e) => {
    targetTitle.value = e.detail || ''
  })

  window.addEventListener('collapse-changed', (e) => {
    isCollapsed.value = !!e.detail
  })

  window.addEventListener('pywebviewready', async () => {
    await loadCategories()
    await loadReplies()
    if (window.pywebview.api) {
      const s = await window.pywebview.api.getSettings()
      isDark.value = s.dark_mode === '1'
      if (window.pywebview.api.getCollapseState) {
        isCollapsed.value = await window.pywebview.api.getCollapseState()
      }
      if (window.pywebview.api.getTargetTitle) {
        targetTitle.value = await window.pywebview.api.getTargetTitle()
      }
    }
  })

  await loadCategories()
  await loadReplies()

  // 建立 250ms 实时标题心跳同步，确保聊天对象切换时标题秒级响应
  setInterval(async () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.getTargetTitle) {
      try {
        const t = await window.pywebview.api.getTargetTitle()
        if (t !== targetTitle.value) {
          targetTitle.value = t
        }
      } catch (e) {}
    }
  }, 250)
})
</script>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-color);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: var(--text-primary);
  position: relative;
  overflow: hidden;
}

.app-wrapper.is-collapsed {
  background: transparent !important;
  border-left: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
}
</style>
