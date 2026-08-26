<template>
  <div class="header-bar">
    <div class="target-badge" :title="targetTitle || '等待微信窗口激活...'">
      <span class="status-dot" :class="{ inactive: !targetTitle }"></span>
      <span class="title-text">{{ targetTitle || '聊天助手' }}</span>
    </div>
    <div class="actions">
      <button class="icon-btn" @click="$emit('open-settings')" title="设置">
        <Settings :size="16" />
      </button>
      <button class="icon-btn" @click="$emit('toggle-collapse')" title="折叠/收起">
        <Minimize2 :size="16" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { Settings, Minimize2 } from 'lucide-vue-next'
defineProps({
  targetTitle: {
    type: String,
    default: ''
  }
})
defineEmits(['open-settings', 'toggle-collapse'])
</script>

<style scoped>
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  height: 42px;
}
.target-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 280px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-color);
  box-shadow: 0 0 6px var(--accent-color);
  flex-shrink: 0;
}
.status-dot.inactive {
  background: #94a3b8;
  box-shadow: none;
}
.title-text {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.actions {
  display: flex;
  gap: 2px;
}
.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn:hover {
  background: var(--border-color);
  color: var(--text-primary);
}
</style>
