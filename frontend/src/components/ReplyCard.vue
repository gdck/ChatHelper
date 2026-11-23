<template>
  <div
    class="reply-compact-row"
    :class="{ 'is-top': isTopUsed }"
    @dblclick="$emit('send', reply.id, 'paste_only')"
    @contextmenu.prevent="handleRightClick($event)"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    title="双击仅粘贴到输入框不回车，右键弹出快捷动作菜单"
  >
    <div class="row-left">
      <Paperclip v-if="reply.attachments && reply.attachments.length" :size="13" class="att-icon" />
      <span class="row-title" :title="reply.title">{{ reply.title }}</span>
      <span v-if="isTopUsed" class="top-marker">最常用</span>
      <span v-if="reply.tags && reply.tags.length" class="tag-badge">{{ reply.tags[0] }}</span>
    </div>

    <div class="row-right">
      <span class="use-count" v-if="reply.use_count > 0">{{ reply.use_count }}</span>
      <button class="send-btn" @click.stop="$emit('send', reply.id, 'normal')" title="直接发送 (Ctrl+V + 回车)">
        <Send :size="11" />
        <span>发送</span>
      </button>
      <button
        ref="moreBtnRef"
        class="more-btn"
        @click.stop="handleOpenMenu"
        title="更多发送模式与操作"
        aria-label="更多操作"
      >
        <MoreVertical :size="14" />
      </button>
    </div>

    <!-- 悬浮完整内容预览 Tooltip -->
    <Teleport to="body">
      <div
        v-if="showTooltip"
        class="hover-preview-tooltip"
        :style="tooltipStyle"
      >
        <div class="tooltip-header">
          <span class="tooltip-title">{{ reply.title }}</span>
          <span class="tooltip-use" v-if="reply.use_count > 0">已用 {{ reply.use_count }} 次</span>
        </div>
        <div class="tooltip-content">{{ reply.content }}</div>
        <div class="tooltip-footer" v-if="(reply.tags && reply.tags.length) || (reply.attachments && reply.attachments.length)">
          <div class="tooltip-tags" v-if="reply.tags && reply.tags.length">
            <span v-for="tag in reply.tags" :key="tag" class="t-tag">{{ tag }}</span>
          </div>
          <div class="tooltip-atts" v-if="reply.attachments && reply.attachments.length">
            <span v-for="(att, i) in reply.attachments" :key="i" class="t-att">
              <Paperclip :size="11" />
              {{ att.name || '附件' }}
            </span>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Send, MoreVertical, Paperclip } from 'lucide-vue-next'

const props = defineProps({
  reply: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['send', 'edit', 'delete', 'open-menu'])

const moreBtnRef = ref(null)
const isHovered = ref(false)
const showTooltip = ref(false)
const targetRect = reactive({ top: 0, bottom: 0, left: 0, right: 0, height: 0 })
let hoverTimer = null

// 最常用：按 use_count 排序的前 3 条，作为列表里唯一的强调点
const isTopUsed = computed(() => {
  if (!props.reply.use_count) return false
  // 由列表在渲染时通过 data 属性传入排名，避免在此访问兄弟节点
  return props.reply.__isTop === true
})

function handleMouseEnter(e) {
  isHovered.value = true
  const rect = e.currentTarget.getBoundingClientRect()
  targetRect.top = rect.top
  targetRect.bottom = rect.bottom
  targetRect.left = rect.left
  targetRect.right = rect.right
  targetRect.height = rect.height

  hoverTimer = setTimeout(() => {
    if (isHovered.value) {
      showTooltip.value = true
    }
  }, 350)
}

function handleMouseLeave() {
  isHovered.value = false
  showTooltip.value = false
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
}

// 智能上下避让计算
const tooltipStyle = computed(() => {
  const vh = window.innerHeight
  const showBelow = targetRect.top < vh * 0.52

  if (showBelow) {
    return {
      top: `${targetRect.bottom + 8}px`,
      left: '12px',
      right: '56px',
      maxHeight: `${Math.max(100, vh - targetRect.bottom - 24)}px`
    }
  } else {
    return {
      bottom: `${vh - targetRect.top + 8}px`,
      left: '12px',
      right: '56px',
      maxHeight: `${Math.max(100, targetRect.top - 24)}px`
    }
  }
})

function getAnchorRect() {
  if (moreBtnRef.value) {
    return moreBtnRef.value.getBoundingClientRect()
  }
  return {
    left: targetRect.right - 24,
    right: targetRect.right,
    top: targetRect.top,
    bottom: targetRect.bottom,
    width: 24,
    height: targetRect.height
  }
}

function handleRightClick() {
  showTooltip.value = false
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
  emit('open-menu', getAnchorRect(), props.reply)
}

function handleOpenMenu() {
  showTooltip.value = false
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
  emit('open-menu', getAnchorRect(), props.reply)
}
</script>

<style scoped>
.reply-compact-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-card);
  padding: 8px 12px;
  margin-bottom: 4px;
  min-height: 44px;
  box-sizing: border-box;
  transition: background var(--dur-feedback) var(--ease),
    border-color var(--dur-feedback) var(--ease);
  cursor: pointer;
  user-select: none;
}
.reply-compact-row:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}
.row-left {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}
.att-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}
.row-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
/* Moment: 最常用 — the one place color earns its keep in the list */
.top-marker {
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1;
  padding: 3px 5px;
  border-radius: 4px;
  background: var(--accent-wash);
  color: var(--accent-strong);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.tag-badge {
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
  max-width: 64px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  flex-shrink: 0;
}
.use-count {
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  margin-right: 4px;
}
.send-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--accent-solid);
  color: #ffffff;
  border: none;
  border-radius: var(--r-control);
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--dur-feedback) var(--ease);
}
.send-btn:hover {
  background: var(--accent-hover);
}
.more-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--r-control);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
}
.more-btn:hover {
  background: var(--bg-active);
  color: var(--text-primary);
}

/* ---- Tooltip ---- */
.hover-preview-tooltip {
  position: fixed;
  z-index: 10000;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--r-card);
  box-shadow: var(--shadow-md);
  padding: 12px 14px;
  pointer-events: none;
  animation: fadeIn var(--dur-enter) var(--ease);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-sizing: border-box;
  color: var(--text-primary);
  overflow-y: auto;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
}
.tooltip-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tooltip-use {
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--text-muted);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.tooltip-content {
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}
.tooltip-footer {
  margin-top: 8px;
  padding-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px solid var(--border-subtle);
}
.tooltip-tags,
.tooltip-atts {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.t-tag {
  font-size: 11px;
  color: var(--accent-strong);
}
.t-att {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}
</style>