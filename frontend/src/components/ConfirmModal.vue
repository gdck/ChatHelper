<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-dialog">
      <div class="modal-body">
        <div class="icon-wrap" :class="type">
          <AlertTriangle :size="22" />
        </div>
        <div class="content-wrap">
          <span class="confirm-title">{{ title }}</span>
          <p class="confirm-desc">{{ message }}</p>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn cancel" @click="$emit('cancel')">{{ cancelText }}</button>
        <button class="btn confirm" :class="type" @click="$emit('confirm')">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertTriangle } from 'lucide-vue-next'

defineProps({
  title: {
    type: String,
    default: '确认操作'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: '确认删除'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  type: {
    type: String,
    default: 'danger' // 'danger' | 'warning' | 'info'
  }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 700;
  padding: 16px;
}
.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--r-panel);
  width: 100%;
  max-width: 328px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
}
.modal-body {
  padding: 20px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-wrap.danger {
  background: var(--danger-wash);
  color: var(--danger);
}
.icon-wrap.warning {
  background: var(--warning-wash);
  color: var(--warning);
}
.content-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.confirm-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
.confirm-desc {
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.5;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  border-radius: 0 0 var(--r-panel) var(--r-panel);
}
.btn {
  padding: 8px 16px;
  border-radius: var(--r-control);
  font-size: 12.5px;
  cursor: pointer;
  font-weight: 500;
  transition: background var(--dur-feedback) var(--ease),
    border-color var(--dur-feedback) var(--ease);
}
.btn.cancel {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}
.btn.cancel:hover {
  background: var(--bg-hover);
}
.btn.confirm.danger {
  background: var(--danger-strong);
  border: none;
  color: #ffffff;
}
.btn.confirm.danger:hover {
  background: #b33236;
}
</style>
