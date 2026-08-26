<template>
  <div class="reply-card" @dblclick="$emit('send', reply.id, 'paste_only')">
    <div class="card-header">
      <div class="title-row">
        <span class="card-title">{{ reply.title }}</span>
        <span class="use-badge" v-if="reply.use_count > 0">{{ reply.use_count }}次</span>
      </div>
      <div class="tag-row" v-if="reply.tags && reply.tags.length">
        <span v-for="tag in reply.tags" :key="tag" class="tag-badge">{{ tag }}</span>
      </div>
    </div>
    
    <div class="card-content">{{ reply.content }}</div>

    <div class="card-footer">
      <div class="attachments" v-if="reply.attachments && reply.attachments.length">
        <span v-for="(att, idx) in reply.attachments" :key="idx" class="att-chip" :title="att.path">
          📎 {{ att.name || '附件' }}
        </span>
      </div>
      <div class="card-actions">
        <button class="send-btn" @click.stop="$emit('send', reply.id, 'normal')">
          <Send :size="12" />
          <span>发送</span>
        </button>
        <button class="more-btn" @click.stop="toggleMenu">
          <MoreVertical :size="14" />
        </button>
        
        <div class="dropdown-menu" v-if="showMenu" @click.stop>
          <div class="menu-item" @click="emitMode('typewriter')">逐字慢发 (打字机)</div>
          <div class="menu-item" @click="emitMode('repeat3')">连发 3 次</div>
          <div class="menu-item" @click="emitMode('reverse')">倒序发送</div>
          <div class="menu-item" @click="emitMode('paste_only')">仅粘贴不回车</div>
          <hr class="menu-divider" />
          <div class="menu-item" @click="emitAction('edit')">编辑话术</div>
          <div class="menu-item delete" @click="emitAction('delete')">删除话术</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Send, MoreVertical } from 'lucide-vue-next'

const props = defineProps({
  reply: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['send', 'edit', 'delete'])
const showMenu = ref(false)

function toggleMenu() {
  showMenu.value = !showMenu.value
}

function emitMode(mode) {
  showMenu.value = false
  emit('send', props.reply.id, mode)
}

function emitAction(type) {
  showMenu.value = false
  if (type === 'edit') emit('edit', props.reply)
  if (type === 'delete') emit('delete', props.reply.id)
}

function handleGlobalClick() {
  showMenu.value = false
}

onMounted(() => {
  window.addEventListener('click', handleGlobalClick)
})
onUnmounted(() => {
  window.removeEventListener('click', handleGlobalClick)
})
</script>

<style scoped>
.reply-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
  transition: all 0.15s ease;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  position: relative;
}
.reply-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent-color);
}
.card-header {
  margin-bottom: 6px;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-title {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-primary);
}
.use-badge {
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--border-color);
  padding: 1px 6px;
  border-radius: 10px;
}
.tag-row {
  display: flex;
  gap: 4px;
  margin-top: 4px;
  flex-wrap: wrap;
}
.tag-badge {
  font-size: 10.5px;
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-secondary);
  padding: 1px 5px;
  border-radius: 4px;
}
.card-content {
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.45;
  white-space: pre-line;
  max-height: 62px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px dashed var(--border-color);
}
.attachments {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  max-width: 230px;
}
.att-chip {
  font-size: 11px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text-secondary);
  white-space: nowrap;
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
}
.send-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 5px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.send-btn:hover {
  background: var(--accent-hover);
}
.more-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}
.more-btn:hover {
  background: var(--border-color);
  color: var(--text-primary);
}
.dropdown-menu {
  position: absolute;
  right: 0;
  bottom: 30px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: var(--shadow-md);
  padding: 4px 0;
  z-index: 100;
  width: 145px;
}
.menu-item {
  padding: 6px 12px;
  font-size: 12px;
  color: var(--text-primary);
  cursor: pointer;
}
.menu-item:hover {
  background: var(--accent-light);
  color: var(--accent-color);
}
.menu-divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 4px 0;
}
.menu-item.delete {
  color: #ef4444;
}
.menu-item.delete:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
</style>
