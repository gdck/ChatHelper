<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <span class="modal-title">系统偏好设置</span>
        <button class="close-btn" @click="$emit('close')"><X :size="16" /></button>
      </div>

      <div class="modal-body">
        <!-- 界面风格 -->
        <div class="setting-item">
          <div class="setting-info">
            <span class="setting-label">暗黑主题模式</span>
            <span class="setting-desc">切换深色与明亮界面风格</span>
          </div>
          <input type="checkbox" v-model="darkMode" @change="toggleTheme" class="switch-checkbox" />
        </div>

        <hr class="divider" />

        <!-- 支持的 IM 聊天软件复选 -->
        <div class="im-section">
          <div class="section-header">
            <span class="section-title">支持的聊天软件 (吸附目标)</span>
            <span class="section-desc">勾选需要自动吸附跟随的客户端</span>
          </div>
          <div class="im-grid">
            <label
              v-for="im in imList"
              :key="im.key"
              class="im-card"
              :class="{ active: selectedIms.includes(im.key) }"
            >
              <input
                type="checkbox"
                :value="im.key"
                v-model="selectedIms"
                class="im-checkbox"
              />
              <span class="im-name">{{ im.name }}</span>
            </label>
          </div>
        </div>

        <hr class="divider" />

        <!-- 数据管理与备份 -->
        <div class="backup-section">
          <span class="section-title">数据管理与备份 (JSON)</span>
          <div class="backup-buttons">
            <button class="btn backup-btn" @click="handleBackup">
              <Download :size="14" />
              <span>备份导出</span>
            </button>
            <button class="btn restore-btn" @click="handleRestore">
              <Upload :size="14" />
              <span>还原覆盖</span>
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

const emit = defineEmits(['close', 'theme-changed', 'toast', 'data-restored'])

const darkMode = ref(false)
const selectedIms = ref(['wechat', 'wxwork', 'qq', 'tim', 'dingtalk', 'aliworkbench'])

const imList = [
  { key: 'wechat', name: '微信' },
  { key: 'wxwork', name: '企业微信' },
  { key: 'qq', name: 'QQ' },
  { key: 'tim', name: 'TIM' },
  { key: 'dingtalk', name: '钉钉' },
  { key: 'aliworkbench', name: '千牛' },
]

onMounted(async () => {
  if (window.pywebview && window.pywebview.api) {
    const s = await window.pywebview.api.getSettings()
    darkMode.value = s.dark_mode === '1'
    if (s.supported_ims) {
      try {
        const parsed = JSON.parse(s.supported_ims)
        if (Array.isArray(parsed)) {
          selectedIms.value = parsed
        }
      } catch (e) {
        console.error('Failed to parse supported_ims', e)
      }
    }
  }
})

function toggleTheme() {
  emit('theme-changed', darkMode.value)
}

async function saveSettings() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.saveSetting('dark_mode', darkMode.value ? '1' : '0')
    await window.pywebview.api.saveSetting('supported_ims', JSON.stringify(selectedIms.value))
  }
  emit('toast', { type: 'success', message: '系统设置保存成功' })
  emit('close')
}

async function handleBackup() {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.backupData()
    if (res.success) {
      emit('toast', { type: 'success', message: res.message || '备份导出完成' })
    } else if (!res.cancelled) {
      emit('toast', { type: 'error', message: res.error || '备份导出失败' })
    }
  } else {
    emit('toast', { type: 'info', message: '已模拟备份导出成功 (Mock)' })
  }
}

async function handleRestore() {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.restoreData()
    if (res.success) {
      emit('toast', { type: 'success', message: res.message || '数据还原完成' })
      emit('data-restored')
    } else if (!res.cancelled) {
      emit('toast', { type: 'error', message: res.error || res.message || '数据还原失败，请检查 JSON 格式' })
    }
  } else {
    emit('toast', { type: 'success', message: '数据还原成功 (Mock)' })
    emit('data-restored')
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
  border: 1px solid var(--border-default);
  border-radius: var(--r-panel);
  width: 100%;
  max-width: 368px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}
.modal-title {
  font-size: 14px;
  font-weight: 500;
}
.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
}
.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.modal-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 480px;
  overflow-y: auto;
}
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.setting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.setting-label {
  font-size: 13px;
  font-weight: 500;
}
.setting-desc {
  font-size: 11.5px;
  color: var(--text-secondary);
  line-height: 1.4;
}
.divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 0;
}
.im-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.section-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.section-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
.section-desc {
  font-size: 11.5px;
  color: var(--text-secondary);
}
.im-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 4px;
}
.im-card {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-control);
  cursor: pointer;
  transition: border-color var(--dur-feedback) var(--ease),
    background var(--dur-feedback) var(--ease);
  user-select: none;
}
.im-card:hover {
  border-color: var(--border-strong);
}
.im-card.active {
  background: var(--accent-wash);
  border-color: var(--accent);
}
.im-checkbox {
  accent-color: var(--accent-solid);
  cursor: pointer;
}
.im-name {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
}
.backup-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  padding: 8px 16px;
  border-radius: var(--r-control);
  font-size: 12.5px;
  cursor: pointer;
  flex: 1;
  font-weight: 500;
  transition: background var(--dur-feedback) var(--ease),
    border-color var(--dur-feedback) var(--ease);
}
.backup-btn, .restore-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
}
.backup-btn:hover, .restore-btn:hover {
  border-color: var(--border-strong);
  background: var(--bg-hover);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}
.btn.submit {
  background: var(--accent-solid);
  border: none;
  color: #ffffff;
}
.btn.submit:hover {
  background: var(--accent-hover);
}
</style>
