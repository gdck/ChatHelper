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
      <button class="add-cat-btn" @click="$emit('add-category')" title="新增分类">
        <Plus :size="15" />
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
        <div class="menu-item" @click="handleEditCategory">重命名/编辑</div>
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
  width: 38px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
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
  gap: 2px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 6px 0;
  flex: 1;
}
.vertical-tabs-list::-webkit-scrollbar {
  width: 0px;
}
.v-tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 2px;
  cursor: pointer;
  position: relative;
  transition: all 0.15s ease;
  border-right: 2px solid transparent;
  color: var(--text-secondary);
  min-height: 48px;
}
.v-tab-item:hover {
  background: var(--border-color);
  color: var(--text-primary);
}
.v-tab-item.active {
  background: var(--bg-card);
  color: var(--accent-color);
  font-weight: 600;
  border-right: 2px solid var(--accent-color);
}
.v-tab-text {
  writing-mode: vertical-rl;
  letter-spacing: 2px;
  font-size: 11.5px;
  line-height: 1.2;
  text-orientation: mixed;
  margin-bottom: 3px;
}
.v-tab-badge {
  font-size: 9.5px;
  line-height: 1;
  padding: 2px 4px;
  border-radius: 8px;
  background: rgba(148, 163, 184, 0.2);
  color: inherit;
}
.v-tab-item.active .v-tab-badge {
  background: var(--accent-color);
  color: white;
}
.strip-footer {
  padding: 6px 4px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
}
.add-cat-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.add-cat-btn:hover {
  background: var(--border-color);
  color: var(--accent-color);
}
.context-menu {
  position: fixed;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: var(--shadow-md);
  padding: 4px 0;
  z-index: 1000;
  width: 120px;
}
.menu-item {
  padding: 6px 12px;
  font-size: 12px;
  color: var(--text-primary);
  cursor: pointer;
}
.menu-item:hover {
  background: var(--accent-light);
  color: var(--accent-color);
}
.menu-item.delete {
  color: #ef4444;
}
.menu-item.delete:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
</style>
