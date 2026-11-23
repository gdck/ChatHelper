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
  top: 16px;
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
  padding: 10px 14px;
  border-radius: var(--r-control);
  font-size: 12.5px;
  font-weight: 500;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: var(--shadow-md);
  pointer-events: auto;
  color: #ffffff;
}
.toast-item.success {
  background: var(--accent-solid);
}
.toast-item.error {
  background: var(--danger-strong);
}
.toast-item.warning {
  background: var(--warning);
}
.toast-item.info {
  background: #2b3230;
}
.toast-icon {
  flex-shrink: 0;
}
.toast-text {
  flex: 1;
  word-break: break-word;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 200ms var(--ease), transform 200ms var(--ease);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>