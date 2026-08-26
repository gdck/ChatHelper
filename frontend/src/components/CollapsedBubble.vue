<template>
  <div class="collapsed-container" @click="$emit('expand')" title="点击展开快捷话术助手">
    <div class="pill-body">
      <div class="icon-bubble">
        <Sparkles :size="14" />
      </div>
      <span class="pill-title">快捷话术</span>
      <ChevronRight :size="14" class="arrow-icon" />
    </div>
  </div>
</template>

<script setup>
import { Sparkles, ChevronRight } from 'lucide-vue-next'

defineEmits(['expand'])
</script>

<style scoped>
.collapsed-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  cursor: pointer;
  user-select: none;
  overflow: hidden;
  padding: 2px;
  box-sizing: border-box;
}

.pill-body {
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(135deg, #07c160 0%, #05a350 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px 0 6px;
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(7, 193, 96, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-sizing: border-box;
}

.pill-body:hover {
  transform: scale(1.03);
  box-shadow: 0 6px 18px rgba(7, 193, 96, 0.65);
}

.pill-body:active {
  transform: scale(0.96);
}

.icon-bubble {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pill-title {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.arrow-icon {
  opacity: 0.85;
  transition: transform 0.2s ease;
}

.pill-body:hover .arrow-icon {
  transform: translateX(2px);
  opacity: 1;
}
</style>
