<template>
  <div class="category-vertical-strip">
    <div class="vertical-tabs-list">
      <!-- 全部 分类标签 -->
      <div
        class="v-tab-item"
        :class="{ active: selectedCategoryId === null }"
        @click="$emit('select-category', null)"
        title="全部话术"
      >
        <span class="v-tab-text">全部</span>
        <span class="v-tab-badge" v-if="totalReplyCount > 0">{{ totalReplyCount }}</span>
      </div>

      <!-- 具体分类标签 -->
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="v-tab-item"
        :class="{ active: selectedCategoryId === cat.id }"
        @click="$emit('select-category', cat.id)"
        @contextmenu.prevent="openContextMenu($event, cat)"
        :title="`${cat.name} (${cat.reply_count || 0}条) - 右键编辑/删除`"
      >
        <span class="v-tab-text">{{ cat.name }}</span>
        <span class="v-tab-badge" v-if="cat.reply_count > 0">{{ cat.reply_count }}</span>
      </div>
    </div>

    <!-- 底部添加分类按钮 -->
    <div class="strip-footer">
      <button class="add-cat-btn" @click="$emit('add-category')" title="新增分类" aria-label="新增分类">
        <Plus :size="16" />
      </button>
    </div>

    <!-- 分类右键菜单 -->
    <Teleport to="body">
      <div
        v-if="contextMenu.visible"
        class="context-menu"
        :style="{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }"
        @click.stop
      >
        <div class="menu-item" @click="handleEditCategory">重命名</div>
        <div class="menu-item delete" @click="handleDeleteCategory">删除分类</div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plus } from 'lucide-vue-next'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  selectedCategoryId: {
    type: [Number, null],
    default: null
  }
})

const emit = defineEmits(['select-category', 'add-category', 'edit-category', 'delete-category'])

const totalReplyCount = computed(() => {
  return props.categories.reduce((sum, c) => sum + (c.reply_count || 0), 0)
})

const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  category: null
})

function openContextMenu(event, category) {
  contextMenu.value = {
    visible: true,
    x: Math.min(event.clientX - 100, window.innerWidth - 130),
    y: Math.min(event.clientY, window.innerHeight - 100),
    category
  }
}

function handleEditCategory() {
  const cat = contextMenu.value.category
  contextMenu.value.visible = false
  if (cat) emit('edit-category', cat)
}

function handleDeleteCategory() {
  const cat = contextMenu.value.category
  contextMenu.value.visible = false
  if (cat) emit('delete-category', cat.id)
}

function closeContextMenu() {
  contextMenu.value.visible = false
}

onMounted(() => {
  window.addEventListener('click', closeContextMenu)
})
onUnmounted(() => {
  window.removeEventListener('click', closeContextMenu)
})
</script>

<style scoped>
.category-vertical-strip {
  width: 44px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  flex-shrink: 0;
  user-select: none;
  height: 100%;
}
.vertical-tabs-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
  flex: 1;
}
.vertical-tabs-list::-webkit-scrollbar {
  width: 0;
}
.v-tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 2px;
  gap: 4px;
  cursor: pointer;
  position: relative;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
  color: var(--text-secondary);
  min-height: 48px;
  border-radius: var(--r-control);
}
.v-tab-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.v-tab-item.active {
  background: var(--bg-card);
  color: var(--accent-strong);
}
/* Active state: small surface step with a hairline accent edge,
   not a colored pill. */
.v-tab-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 2px;
  border-radius: 1px;
  background: var(--accent);
}
.v-tab-text {
  writing-mode: vertical-rl;
  letter-spacing: 1px;
  font-size: 12px;
  line-height: 1.2;
  text-orientation: mixed;
}
.v-tab-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1;
  padding: 2px 4px;
  border-radius: 4px;
  background: var(--bg-hover);
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.v-tab-item.active .v-tab-badge {
  color: var(--accent-strong);
  background: var(--accent-wash);
}
.strip-footer {
  padding: 8px 4px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-subtle);
}
.add-cat-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--r-control);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
}
.add-cat-btn:hover {
  background: var(--bg-hover);
  color: var(--accent-strong);
}
.context-menu {
  position: fixed;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--r-control);
  box-shadow: var(--shadow-md);
  padding: 4px;
  z-index: 1000;
  width: 128px;
}
.menu-item {
  padding: 6px 12px;
  font-size: 12.5px;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: 6px;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
}
.menu-item:hover {
  background: var(--bg-hover);
}
.menu-item.delete {
  color: var(--danger);
}
.menu-item.delete:hover {
  background: var(--danger-wash);
  color: var(--danger);
}
</style>