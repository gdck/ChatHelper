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

      <SearchBar
        ref="searchBarRef"
        v-model="searchKeyword"
        @create-reply="handleOpenCreateModal"
      />

      <!-- 主工作区：左侧高密度紧凑话术列表 + 右侧竖向分类导航条 -->
      <div class="main-body-layout">
        <ReplyCardList
          :replies="replies"
          @send-reply="handleSendReply"
          @edit-reply="handleOpenEditModal"
          @delete-reply="handleOpenDeleteReplyConfirm"
          @create-reply="handleOpenCreateModal"
          @open-menu="handleOpenFloatingMenu"
        />

        <CategoryNav
          :categories="categories"
          :selected-category-id="selectedCategoryId"
          @select-category="handleSelectCategory"
          @add-category="handleOpenAddCategoryModal"
          @edit-category="handleOpenEditCategoryModal"
          @delete-category="handleOpenDeleteCategoryConfirm"
        />
      </div>

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
        @data-restored="handleDataRestored"
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

      <!-- 右侧边缘拖拽拉伸调整宽度手柄 -->
      <div
        class="window-resize-handle"
        :class="{ 'is-resizing': isResizing }"
        @pointerdown="handleResizePointerDown"
        title="按住左右拖动调整窗口宽度"
      >
        <div class="resize-indicator-line" />
      </div>

      <!-- 拖拽调节中的实时宽度胶囊气泡 -->
      <transition name="fade-badge">
        <div v-if="isResizing" class="resize-width-badge">
          {{ currentWidth }}px
        </div>
      </transition>
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

// 窗口宽度调整状态
const currentWidth = ref(480)
const isResizing = ref(false)

function handleResizePointerDown(e) {
  if (e.button !== 0) return
  isResizing.value = true
  const startX = e.screenX ?? e.clientX
  const startWidth = currentWidth.value || 480

  const target = e.currentTarget
  if (target && target.setPointerCapture) {
    try {
      target.setPointerCapture(e.pointerId)
    } catch (err) {}
  }

  const onPointerMove = (moveEvent) => {
    if (!isResizing.value) return
    const currentX = moveEvent.screenX ?? moveEvent.clientX
    const deltaX = currentX - startX
    let newWidth = Math.round(startWidth + deltaX)
    if (newWidth < 360) newWidth = 360
    if (newWidth > 800) newWidth = 800

    if (newWidth !== currentWidth.value) {
      currentWidth.value = newWidth
      if (window.pywebview && window.pywebview.api && window.pywebview.api.setSidebarWidth) {
        window.pywebview.api.setSidebarWidth(newWidth, false)
      }
    }
  }

  const onPointerUp = async (upEvent) => {
    isResizing.value = false
    target.removeEventListener('pointermove', onPointerMove)
    target.removeEventListener('pointerup', onPointerUp)
    target.removeEventListener('pointercancel', onPointerUp)
    try {
      if (target && target.releasePointerCapture) {
        target.releasePointerCapture(upEvent.pointerId)
      }
    } catch (err) {}

    // 持久化存储到后端 JSON
    if (window.pywebview && window.pywebview.api && window.pywebview.api.setSidebarWidth) {
      await window.pywebview.api.setSidebarWidth(currentWidth.value, true)
    }
  }

  target.addEventListener('pointermove', onPointerMove)
  target.addEventListener('pointerup', onPointerUp)
  target.addEventListener('pointercancel', onPointerUp)
}

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
      showToast('error', res.error || '发送失败，请确保微信/QQ窗口处于激活状态')
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

watch(isDark, (val) => {
  if (val) {
    document.documentElement.classList.add('dark')
    document.body.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
    document.body.classList.remove('dark')
  }
}, { immediate: true })

async function handleDataRestored() {
  selectedCategoryId.value = null
  searchKeyword.value = ''
  await loadCategories()
  await loadReplies()
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
      if (window.pywebview.api.getSidebarWidth) {
        currentWidth.value = await window.pywebview.api.getSidebarWidth()
      }
    }
  })

  // 周期性轮询兜底，确保跨软件切换窗口时标题100%实时同步
  setInterval(async () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.getTargetTitle) {
      const cur = await window.pywebview.api.getTargetTitle()
      if (cur && cur !== targetTitle.value) {
        targetTitle.value = cur
      }
    }
  }, 400)

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

.main-body-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* 右侧边缘拖拽调整宽度手柄 */
.window-resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 6px;
  height: 100%;
  cursor: ew-resize;
  z-index: 9999;
  user-select: none;
  touch-action: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
}

.window-resize-handle:hover .resize-indicator-line,
.window-resize-handle.is-resizing .resize-indicator-line {
  opacity: 1;
  background: var(--primary-color, #2563eb);
  box-shadow: 0 0 8px rgba(37, 99, 235, 0.4);
}

.resize-indicator-line {
  width: 2px;
  height: 100%;
  background: transparent;
  opacity: 0;
  transition: opacity 0.15s ease, background 0.15s ease;
  border-radius: 1px;
}

.resize-width-badge {
  position: absolute;
  top: 50%;
  right: 18px;
  transform: translateY(-50%);
  background: rgba(15, 23, 42, 0.85);
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 9999px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  pointer-events: none;
  z-index: 10000;
  letter-spacing: 0.5px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.fade-badge-enter-active,
.fade-badge-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-badge-enter-from,
.fade-badge-leave-to {
  opacity: 0;
  transform: translateY(-50%) scale(0.9);
}
</style>
