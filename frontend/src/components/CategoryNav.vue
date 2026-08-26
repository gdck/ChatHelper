<template>
  <div class="category-nav-container">
    <div class="category-tabs">
      <div
        class="tab-item"
        :class="{ active: selectedCategoryId === null }"
        @click="$emit('select-category', null)"
      >
        <span>全部</span>
        <span class="badge" v-if="totalReplyCount > 0">{{ totalReplyCount }}</span>
      </div>
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="tab-item"
        :class="{ active: selectedCategoryId === cat.id }"
        @click="$emit('select-category', cat.id)"
        @contextmenu.prevent="openContextMenu($event, cat)"
      >
        <span>{{ cat.name }}</span>
        <span class="badge" v-if="cat.reply_count > 0">{{ cat.reply_count }}</span>
      </div>
    </div>
    <button class="add-tab-btn" @click="$emit('add-category')" title="新增分类">
      <Plus :size="14" />
    </button>

    <!-- 分类右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }"
      @click.stop
    >
      <div class="menu-item" @click="handleEditCategory">重命名/编辑</div>
      <div class="menu-item delete" @click="handleDeleteCategory">删除分类</div>
    </div>
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
    x: Math.min(event.clientX, window.innerWidth - 130),
    y: event.clientY,
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
.category-nav-container {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 4px 8px;
  position: relative;
}
.category-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
  overflow-x: auto;
  flex: 1;
  padding-bottom: 2px;
}
.category-tabs::-webkit-scrollbar {
  height: 2px;
}
.tab-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}
.tab-item:hover {
  background: var(--border-color);
  color: var(--text-primary);
}
.tab-item.active {
  background: var(--accent-light);
  color: var(--accent-color);
  font-weight: 600;
}
.badge {
  font-size: 11px;
  padding: 1px 5px;
  border-radius: 10px;
  background: rgba(148, 163, 184, 0.2);
  color: inherit;
}
.tab-item.active .badge {
  background: var(--accent-color);
  color: white;
}
.add-tab-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 5px 6px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.add-tab-btn:hover {
  background: var(--border-color);
  color: var(--text-primary);
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
