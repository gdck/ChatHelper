<template>
  <div class="collapsed-btn" @click="$emit('expand')" title="展开聊天助手">
    <MessageSquare :size="15" class="icon" />
    <span class="bubble-dot"></span>
  </div>
</template>

<script setup>
import { MessageSquare } from 'lucide-vue-next'

defineEmits(['expand'])
</script>

<style scoped>
.collapsed-btn {
  width: 32px;
  height: 32px;
  background: var(--accent-solid);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--r-control);
  cursor: pointer;
  box-shadow: var(--shadow-md);
  transition: background var(--dur-feedback) var(--ease);
  box-sizing: border-box;
  position: relative;
}
.collapsed-btn:hover {
  background: var(--accent-hover);
}
.collapsed-btn:active {
  transform: scale(0.96);
}
.icon {
  flex-shrink: 0;
}
/* 折叠态也保留签名：贴在图标角的实时状态点 */
.bubble-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ffffff;
  opacity: 0.9;
}
</style>