<template>
  <TransitionGroup name="toast" tag="div" class="toast-container">
    <div
      v-for="item in toasts"
      :key="item.id"
      class="toast-item"
      :class="item.type"
    >
      <CheckCircle2 v-if="item.type === 'success'" :size="16" class="toast-icon" />
      <AlertCircle v-else-if="item.type === 'error'" :size="16" class="toast-icon" />
      <AlertTriangle v-else-if="item.type === 'warning'" :size="16" class="toast-icon" />
      <Info v-else :size="16" class="toast-icon" />
      <span class="toast-text">{{ item.message }}</span>
    </div>
  </TransitionGroup>
</template>

<script setup>
import { CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-vue-next'

defineProps({
  toasts: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 9999;
  pointer-events: none;
  width: 90%;
  max-width: 320px;
}
.toast-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 500;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
  pointer-events: auto;
}
.toast-item.success {
  background: rgba(7, 193, 96, 0.92);
  color: white;
}
.toast-item.error {
  background: rgba(239, 68, 68, 0.92);
  color: white;
}
.toast-item.warning {
  background: rgba(245, 158, 11, 0.92);
  color: white;
}
.toast-item.info {
  background: rgba(30, 41, 59, 0.92);
  color: white;
}
.toast-icon {
  flex-shrink: 0;
}
.toast-text {
  flex: 1;
  word-break: break-all;
}

/* 动效 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-12px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-12px) scale(0.95);
}
</style>
