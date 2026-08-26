<template>
  <div class="collapsed-btn" @click="$emit('expand')" title="点击展开聊天助手">
    <Sparkles :size="16" class="icon" />
  </div>
</template>

<script setup>
import { Sparkles } from 'lucide-vue-next'

defineEmits(['expand'])
</script>

<style scoped>
.collapsed-btn {
  width: 28px;
  height: 28px;
  background: #07c160;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  transition: background 0.15s, transform 0.1s;
  box-sizing: border-box;
}

.collapsed-btn:hover {
  background: #06ad56;
  transform: scale(1.05);
}

.collapsed-btn:active {
  transform: scale(0.95);
}

.icon {
  flex-shrink: 0;
}
</style>
