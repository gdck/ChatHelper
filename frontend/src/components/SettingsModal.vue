<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <span class="modal-title">系统偏好设置</span>
        <button class="close-btn" @click="$emit('close')"><X :size="16" /></button>
      </div>

      <div class="modal-body">
        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">暗黑主题模式</span>
            <span class="setting-desc">切换深色与明亮界面风格</span>
          </div>
          <input type="checkbox" v-model="darkMode" @change="toggleTheme" class="switch-checkbox" />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">粘贴延时补偿 (毫秒)</span>
            <span class="setting-desc">激活窗口后模拟 Ctrl+V 的等待时间</span>
          </div>
          <input type="number" v-model.number="pasteDelay" class="setting-input" />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">回车延时补偿 (毫秒)</span>
            <span class="setting-desc">粘贴内容后模拟 Enter 发送的等待时间</span>
          </div>
          <input type="number" v-model.number="enterDelay" class="setting-input" />
        </div>

        <hr class="divider" />

        <div class="backup-section">
          <span class="section-title">数据库备份与还原</span>
          <div class="backup-buttons">
            <button class="btn backup-btn" @click="handleBackup">
              <Download :size="14" />
              <span>备份当前数据</span>
            </button>
            <button class="btn restore-btn" @click="handleRestore">
              <Upload :size="14" />
              <span>还原数据备份</span>
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn submit" @click="saveSettings">保存配置</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { X, Download, Upload } from 'lucide-vue-next'

const emit = defineEmits(['close', 'theme-changed'])

const darkMode = ref(false)
const pasteDelay = ref(120)
const enterDelay = ref(120)

onMounted(async () => {
  if (window.pywebview && window.pywebview.api) {
    const s = await window.pywebview.api.getSettings()
    darkMode.value = s.dark_mode === '1'
    pasteDelay.value = parseInt(s.paste_delay || '120')
    enterDelay.value = parseInt(s.enter_delay || '120')
  }
})

function toggleTheme() {
  emit('theme-changed', darkMode.value)
}

async function saveSettings() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.saveSetting('dark_mode', darkMode.value ? '1' : '0')
    await window.pywebview.api.saveSetting('paste_delay', String(pasteDelay.value))
    await window.pywebview.api.saveSetting('enter_delay', String(enterDelay.value))
  }
  emit('close')
}

async function handleBackup() {
  alert('备份功能已就绪')
}

async function handleRestore() {
  alert('还原功能已就绪')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
  padding: 16px;
}
.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  width: 100%;
  max-width: 360px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
}
.modal-title {
  font-size: 13.5px;
  font-weight: 600;
}
.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}
.modal-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.setting-label {
  font-size: 12.5px;
  font-weight: 500;
}
.setting-desc {
  font-size: 11px;
  color: var(--text-secondary);
}
.setting-input {
  width: 70px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 8px;
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
  text-align: center;
}
.divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 4px 0;
}
.backup-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}
.backup-buttons {
  display: flex;
  gap: 8px;
}
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  flex: 1;
}
.backup-btn, .restore-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 10px 14px;
  border-top: 1px solid var(--border-color);
}
.btn.submit {
  background: var(--accent-color);
  border: none;
  color: white;
  font-weight: 500;
}
</style>
