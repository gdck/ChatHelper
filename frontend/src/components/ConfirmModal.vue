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
  border: 1px solid var(--border-color);
  border-radius: 10px;
  width: 100%;
  max-width: 320px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
}
.modal-body {
  padding: 18px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-wrap.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
.icon-wrap.warning {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}
.content-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.confirm-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
}
.confirm-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  border-radius: 0 0 10px 10px;
}
.btn {
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
}
.btn.cancel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.btn.confirm.danger {
  background: #ef4444;
  border: none;
  color: white;
}
.btn.confirm.danger:hover {
  background: #dc2626;
}
</style>
