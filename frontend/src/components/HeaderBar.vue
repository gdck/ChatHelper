<template>
  <div class="header-bar">
    <div class="target-badge" :title="targetTitle || '未检测到聊天窗口'">
      <span class="status-dot" :class="{ inactive: !targetTitle }"></span>
      <span class="title-text">{{ targetTitle || '聊天助手' }}</span>
    </div>
    <div class="actions">
      <button class="icon-btn" @click="$emit('open-settings')" title="设置" aria-label="设置">
        <Settings :size="16" />
      </button>
      <button class="icon-btn" @click="$emit('toggle-collapse')" title="折叠" aria-label="折叠面板">
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
  border-bottom: 1px solid var(--border-subtle);
  height: 44px;
  flex-shrink: 0;
}
.target-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 280px;
  min-width: 0;
}
/* Signature: live dock-status dot. Solid green = locked on target,
   gray = idle. One color moment in the chrome, no glow. */
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  transition: background var(--dur-feedback) var(--ease);
}
.status-dot.inactive {
  background: var(--text-muted);
}
.title-text {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.actions {
  display: flex;
  gap: 4px;
}
.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--r-control);
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>