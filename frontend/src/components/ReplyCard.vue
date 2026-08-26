<template>
  <div
    class="reply-compact-row"
    @dblclick="$emit('send', reply.id, 'normal')"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div class="row-left">
      <div class="status-indicator"></div>
      <span class="row-title" :title="reply.title">{{ reply.title }}</span>
      <span v-if="reply.attachments && reply.attachments.length" class="att-badge" title="包含附件">
        📎
      </span>
      <span v-if="reply.tags && reply.tags.length" class="tag-badge">
        {{ reply.tags[0] }}
      </span>
    </div>

    <div class="row-right">
      <span class="use-count" v-if="reply.use_count > 0">{{ reply.use_count }}次</span>
      <button class="send-btn" @click.stop="$emit('send', reply.id, 'normal')" title="直接发送 (Ctrl+V + 回车)">
        <Send :size="11" />
        <span>发送</span>
      </button>
      <button class="more-btn" @click.stop="handleOpenMenu($event)" title="更多发送模式与操作">
        <MoreVertical :size="13" />
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
            <span v-for="tag in reply.tags" :key="tag" class="t-tag">#{{ tag }}</span>
          </div>
          <div class="tooltip-atts" v-if="reply.attachments && reply.attachments.length">
            <span v-for="(att, i) in reply.attachments" :key="i" class="t-att">📎 {{ att.name || '附件' }}</span>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Send, MoreVertical } from 'lucide-vue-next'

const props = defineProps({
  reply: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['send', 'edit', 'delete', 'open-menu'])

const isHovered = ref(false)
const showTooltip = ref(false)
const targetRect = reactive({ top: 0, left: 0, height: 0 })
let hoverTimer = null

function handleMouseEnter(e) {
  isHovered.value = true
  const rect = e.currentTarget.getBoundingClientRect()
  targetRect.top = rect.top
  targetRect.left = rect.left
  targetRect.height = rect.height

  hoverTimer = setTimeout(() => {
    if (isHovered.value) {
      showTooltip.value = true
    }
  }, 450)
}

function handleMouseLeave() {
  isHovered.value = false
  showTooltip.value = false
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
}

const tooltipStyle = computed(() => {
  let top = targetRect.top - 8
  const maxTop = window.innerHeight - 180
  if (top > maxTop) top = maxTop
  if (top < 10) top = 10

  return {
    top: `${top}px`,
    left: '12px',
    maxWidth: '310px'
  }
})

function handleOpenMenu(event) {
  showTooltip.value = false
  const rect = event.currentTarget.getBoundingClientRect()
  emit('open-menu', rect, props.reply)
}
</script>

<style scoped>
.reply-compact-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 10px;
  margin-bottom: 5px;
  height: 36px;
  box-sizing: border-box;
  transition: all 0.12s ease;
  cursor: pointer;
  user-select: none;
}
.reply-compact-row:hover {
  background: var(--bg-primary);
  border-color: var(--accent-color);
  box-shadow: var(--shadow-sm);
}
.row-left {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
  flex: 1;
}
.status-indicator {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent-color);
  flex-shrink: 0;
  opacity: 0.7;
}
.reply-compact-row:hover .status-indicator {
  opacity: 1;
  box-shadow: 0 0 4px var(--accent-color);
}
.row-title {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.att-badge {
  font-size: 11px;
  color: var(--text-secondary);
  flex-shrink: 0;
}
.tag-badge {
  font-size: 10px;
  background: rgba(148, 163, 184, 0.12);
  color: var(--text-secondary);
  padding: 0 4px;
  border-radius: 3px;
  flex-shrink: 0;
  max-width: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-right {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
}
.use-count {
  font-size: 10.5px;
  color: var(--text-secondary);
  opacity: 0.7;
  margin-right: 2px;
}
.send-btn {
  display: flex;
  align-items: center;
  gap: 3px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 3px 7px;
  font-size: 11.5px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.12s;
}
.send-btn:hover {
  background: var(--accent-hover);
}
.more-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 3px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: all 0.12s;
}
.more-btn:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

/* Tooltip 预览卡片 */
.hover-preview-tooltip {
  position: fixed;
  z-index: 1000;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--shadow-md);
  padding: 10px 12px;
  pointer-events: none;
  animation: fadeIn 0.15s ease-out;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border-color);
}
.tooltip-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-color);
}
.tooltip-use {
  font-size: 10.5px;
  color: var(--text-secondary);
}
.tooltip-content {
  font-size: 12px;
  line-height: 1.45;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 140px;
  overflow-y: hidden;
}
.tooltip-footer {
  margin-top: 6px;
  padding-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.tooltip-tags, .tooltip-atts {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.t-tag {
  font-size: 10.5px;
  color: var(--accent-color);
}
.t-att {
  font-size: 10.5px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 1px 4px;
  border-radius: 3px;
}
</style>
