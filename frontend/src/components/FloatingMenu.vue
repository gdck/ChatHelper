<template>
  <div v-if="visible" class="floating-menu-overlay" @click.self="$emit('close')">
    <div
      class="floating-menu"
      :style="menuStyle"
      @click.stop
    >
      <div class="menu-item" @click="handleSelectMode('typewriter')">
        <Sparkles :size="13" class="menu-icon text-green" />
        <span>逐字慢发 (打字机)</span>
      </div>
      <div class="menu-item" @click="handleSelectMode('repeat3')">
        <Repeat :size="13" class="menu-icon text-blue" />
        <span>连发 3 次</span>
      </div>
      <div class="menu-item" @click="handleSelectMode('reverse')">
        <ArrowLeftRight :size="13" class="menu-icon text-purple" />
        <span>倒序发送</span>
      </div>
      <div class="menu-item" @click="handleSelectMode('paste_only')">
        <ClipboardCopy :size="13" class="menu-icon text-orange" />
        <span>仅粘贴不回车</span>
      </div>
      
      <hr class="menu-divider" />

      <div class="menu-item" @click="handleAction('edit')">
        <Edit3 :size="13" class="menu-icon" />
        <span>编辑话术</span>
      </div>
      <div class="menu-item delete" @click="handleAction('delete')">
        <Trash2 :size="13" class="menu-icon text-red" />
        <span>删除话术</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Sparkles,
  Repeat,
  ArrowLeftRight,
  ClipboardCopy,
  Edit3,
  Trash2
} from 'lucide-vue-next'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  anchorRect: {
    type: Object,
    default: null
  },
  reply: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'select-mode', 'action'])

const menuStyle = computed(() => {
  if (!props.anchorRect) {
    return { top: '50%', left: '50%' }
  }

  const menuWidth = 160
  const menuHeight = 220
  const winHeight = window.innerHeight
  const winWidth = window.innerWidth
  const rect = props.anchorRect

  // 水平定位：默认右对齐到按钮，且不超出屏幕
  let left = rect.right - menuWidth
  if (left < 8) left = 8
  if (left + menuWidth > winWidth - 8) left = winWidth - menuWidth - 8

  // 垂直定位：根据屏幕可用空间自动向上或向下弹出（避免被顶部 Header/底部边缘遮挡）
  let top
  if (rect.bottom + menuHeight + 8 <= winHeight) {
    // 空间充裕，向下展开
    top = rect.bottom + 4
  } else if (rect.top - menuHeight - 8 >= 0) {
    // 空间不足，向上展开
    top = rect.top - menuHeight - 4
  } else {
    // 居中适配
    top = Math.max(8, winHeight - menuHeight - 8)
  }

  return {
    top: `${top}px`,
    left: `${left}px`
  }
})

function handleSelectMode(mode) {
  if (props.reply) {
    emit('select-mode', props.reply.id, mode)
  }
  emit('close')
}

function handleAction(action) {
  if (props.reply) {
    emit('action', action, props.reply)
  }
  emit('close')
}
</script>

<style scoped>
.floating-menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: transparent;
}

.floating-menu {
  position: fixed;
  width: 160px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
  padding: 5px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  animation: popIn 0.16s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.94);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.12s ease;
}

.menu-item:hover {
  background: var(--accent-light);
  color: var(--accent-color);
}

.menu-icon {
  flex-shrink: 0;
  opacity: 0.85;
}

.menu-item:hover .menu-icon {
  opacity: 1;
}

.text-green { color: #07c160; }
.text-blue { color: #3b82f6; }
.text-purple { color: #8b5cf6; }
.text-orange { color: #f97316; }
.text-red { color: #ef4444; }

.menu-divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 4px 0;
}

.menu-item.delete {
  color: #ef4444;
}

.menu-item.delete:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
</style>
