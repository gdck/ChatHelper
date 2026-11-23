<template>
  <div class="card-list-container">
    <div v-if="replies.length === 0" class="empty-state">
      <Inbox :size="28" class="empty-icon" />
      <p class="empty-text">暂无话术</p>
      <button class="empty-add-btn" @click="$emit('create-reply')">新增话术</button>
    </div>
    <div v-else class="card-list">
      <ReplyCard
        v-for="reply in rankedReplies"
        :key="reply.id"
        :reply="reply"
        @send="(id, mode) => $emit('send-reply', id, mode)"
        @edit="(r) => $emit('edit-reply', r)"
        @delete="(id) => $emit('delete-reply', id)"
        @open-menu="(rect, r) => $emit('open-menu', rect, r)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Inbox } from 'lucide-vue-next'
import ReplyCard from './ReplyCard.vue'

const props = defineProps({
  replies: {
    type: Array,
    default: () => []
  }
})

defineEmits(['send-reply', 'edit-reply', 'delete-reply', 'create-reply', 'open-menu'])

// 标记 use_count 最高的前 3 条为「最常用」，其余保持原顺序
const rankedReplies = computed(() => {
  const top = [...props.replies]
    .filter(r => r.use_count > 0)
    .sort((a, b) => b.use_count - a.use_count)
    .slice(0, 3)
    .map(r => r.id)
  return props.replies.map(r => ({
    ...r,
    __isTop: top.includes(r.id)
  }))
})
</script>

<style scoped>
.card-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  box-sizing: border-box;
}
.card-list {
  display: flex;
  flex-direction: column;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 240px;
  color: var(--text-muted);
  gap: 12px;
}
.empty-icon {
  opacity: 0.5;
}
.empty-text {
  font-size: 13px;
  color: var(--text-secondary);
}
.empty-add-btn {
  background: var(--accent-solid);
  color: #ffffff;
  border: none;
  padding: 7px 16px;
  border-radius: var(--r-control);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--dur-feedback) var(--ease);
}
.empty-add-btn:hover {
  background: var(--accent-hover);
}
</style>