<template>
  <div v-if="visible" class="floating-menu-overlay" @click.self="$emit('close')">
    <div
      class="floating-menu"
      :style="menuStyle"
      @click.stop
    >
      <div class="menu-item" @click="handleSelectMode('typewriter')">
        <Sparkles :size="14" class="menu-icon" />
        <span>逐字慢发</span>
      </div>
      <div class="menu-item" @click="handleSelectMode('repeat3')">
        <Repeat :size="14" class="menu-icon" />
        <span>连发 3 次</span>
      </div>
      <div class="menu-item" @click="handleSelectMode('reverse')">
        <ArrowLeftRight :size="14" class="menu-icon" />
        <span>倒序发送</span>
      </div>
      <div class="menu-item" @click="handleSelectMode('paste_only')">
        <ClipboardCopy :size="14" class="menu-icon" />
        <span>仅粘贴不回车</span>
      </div>

      <hr class="menu-divider" />

      <div class="menu-item" @click="handleAction('edit')">
        <Edit3 :size="14" class="menu-icon" />
        <span>编辑话术</span>
      </div>
      <div class="menu-item delete" @click="handleAction('delete')">
        <Trash2 :size="14" class="menu-icon" />
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

  const menuWidth = 168
  const menuHeight = 224
  const winHeight = window.innerHeight
  const winWidth = window.innerWidth
  const rect = props.anchorRect

  // 水平定位
  let left
  if (rect.width === 0) {
    left = rect.left
  } else {
    left = rect.right - menuWidth
  }
  if (left < 8) left = 8
  if (left + menuWidth > winWidth - 8) left = winWidth - menuWidth - 8

  // 垂直定位：自动避让上下边缘
  let top
  if (rect.bottom + menuHeight + 8 <= winHeight) {
    top = rect.bottom + 4
  } else if (rect.top - menuHeight - 8 >= 0) {
    top = rect.top - menuHeight - 4
  } else {
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
  width: 168px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--r-card);
  box-shadow: var(--shadow-md);
  padding: 4px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  animation: popIn var(--dur-enter) var(--ease);
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  font-size: 12.5px;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
}

.menu-item:hover {
  background: var(--bg-hover);
  color: var(--accent-strong);
}

.menu-icon {
  flex-shrink: 0;
  color: var(--text-muted);
  transition: color var(--dur-feedback) var(--ease);
}
.menu-item:hover .menu-icon {
  color: var(--accent-strong);
}

.menu-divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 4px 0;
}

.menu-item.delete {
  color: var(--danger);
}
.menu-item.delete .menu-icon {
  color: var(--danger);
}
.menu-item.delete:hover {
  background: var(--danger-wash);
  color: var(--danger);
}
.menu-item.delete:hover .menu-icon {
  color: var(--danger);
}
</style>