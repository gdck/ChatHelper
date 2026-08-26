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
            <span class="setting-label">逐字发送间隔 (毫秒)</span>
            <span class="setting-desc">逐字慢发打字机模式下每个字符的发送等待时间 (默认 500)</span>
          </div>
          <input type="number" v-model.number="typewriterDelay" min="50" step="50" class="setting-input" />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">连发 3 次间隔 (毫秒)</span>
            <span class="setting-desc">连续发送 3 次模式下每轮发送之间的等待时间 (默认 500)</span>
          </div>
          <input type="number" v-model.number="repeatDelay" min="100" step="50" class="setting-input" />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">粘贴延时补偿 (毫秒)</span>
            <span class="setting-desc">激活微信后模拟 Ctrl+V 的前置等待时间 (默认 120)</span>
          </div>
          <input type="number" v-model.number="pasteDelay" min="20" step="20" class="setting-input" />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">回车延时补偿 (毫秒)</span>
            <span class="setting-desc">粘贴内容后模拟 Enter 回车发送的等待时间 (默认 120)</span>
          </div>
          <input type="number" v-model.number="enterDelay" min="20" step="20" class="setting-input" />
        </div>

        <hr class="divider" />

        <div class="backup-section">
          <span class="section-title">数据管理与备份</span>
          <div class="backup-buttons">
            <button class="btn backup-btn" @click="handleBackup">
              <Download :size="14" />
              <span>备份数据</span>
            </button>
            <button class="btn restore-btn" @click="handleRestore">
              <Upload :size="14" />
              <span>还原数据</span>
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

const emit = defineEmits(['close', 'theme-changed', 'toast'])

const darkMode = ref(false)
const typewriterDelay = ref(500)
const repeatDelay = ref(500)
const pasteDelay = ref(120)
const enterDelay = ref(120)

onMounted(async () => {
  if (window.pywebview && window.pywebview.api) {
    const s = await window.pywebview.api.getSettings()
    darkMode.value = s.dark_mode === '1'
    typewriterDelay.value = parseInt(s.typewriter_delay || '500')
    repeatDelay.value = parseInt(s.repeat_delay || '500')
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
    await window.pywebview.api.saveSetting('typewriter_delay', String(typewriterDelay.value))
    await window.pywebview.api.saveSetting('repeat_delay', String(repeatDelay.value))
    await window.pywebview.api.saveSetting('paste_delay', String(pasteDelay.value))
    await window.pywebview.api.saveSetting('enter_delay', String(enterDelay.value))
  }
  emit('toast', { type: 'success', message: '系统设置保存成功' })
  emit('close')
}

async function handleBackup() {
  emit('toast', { type: 'info', message: '已自动备份至本地 chat_helper.db' })
}

async function handleRestore() {
  if (window.pywebview && window.pywebview.api) {
    const files = await window.pywebview.api.selectFiles()
    if (files && files.length) {
      const ok = await window.pywebview.api.restoreDatabase(files[0])
      if (ok) {
        emit('toast', { type: 'success', message: '数据库还原成功，请刷新数据' })
      } else {
        emit('toast', { type: 'error', message: '数据库还原失败，请检查文件格式' })
      }
    }
  }
}
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
  z-index: 600;
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
  max-height: 480px;
  overflow-y: auto;
}
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.setting-label {
  font-size: 12.5px;
  font-weight: 500;
}
.setting-desc {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.3;
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
  font-weight: 500;
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
}
</style>
