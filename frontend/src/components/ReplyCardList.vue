<template>
  <div class="card-list-container">
    <div v-if="replies.length === 0" class="empty-state">
      <Inbox :size="32" class="empty-icon" />
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
        @open-menu="(rect, r) => $emit('open-menu', rect, r)"
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

defineEmits(['send-reply', 'edit-reply', 'delete-reply', 'create-reply', 'open-menu'])
</script>

<style scoped>
.card-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 6px 8px;
  box-sizing: border-box;
}
.card-list-container::-webkit-scrollbar {
  width: 4px;
}
.card-list-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
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
  height: 220px;
  color: var(--text-secondary);
}
.empty-icon {
  margin-bottom: 8px;
  opacity: 0.45;
}
.empty-text {
  font-size: 12.5px;
  margin-bottom: 10px;
}
.empty-add-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 5px;
  font-size: 12px;
  cursor: pointer;
}
</style>
