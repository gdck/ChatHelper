<template>
  <div class="card-list-container">
    <div v-if="replies.length === 0" class="empty-state">
      <Inbox :size="36" class="empty-icon" />
      <p class="empty-text">暂无话术内容</p>
      <button class="empty-add-btn" @click="$emit('create-reply')">立即添加</button>
    </div>
    <div v-else class="card-list">
      <ReplyCard
        v-for="reply in replies"
        :key="reply.id"
        :reply="reply"
        @send="(id, mode) => $emit('send-reply', id, mode)"
        @edit="(r) => $emit('edit-reply', r)"
        @delete="(id) => $emit('delete-reply', id)"
      />
    </div>
  </div>
</template>

<script setup>
import { Inbox } from 'lucide-vue-next'
import ReplyCard from './ReplyCard.vue'

defineProps({
  replies: {
    type: Array,
    default: () => []
  }
})

defineEmits(['send-reply', 'edit-reply', 'delete-reply', 'create-reply'])
</script>

<style scoped>
.card-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
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
  height: 260px;
  color: var(--text-secondary);
}
.empty-icon {
  margin-bottom: 10px;
  opacity: 0.5;
}
.empty-text {
  font-size: 13px;
  margin-bottom: 12px;
}
.empty-add-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}
</style>
