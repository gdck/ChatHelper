<template>
  <div class="collapsed-orb" @click="$emit('expand')" title="点击展开聊天助手">
    <div class="orb-core">
      <Sparkles :size="20" class="orb-icon" />
      <span class="pulse-ring"></span>
    </div>
  </div>
</template>

<script setup>
import { Sparkles } from 'lucide-vue-next'

defineEmits(['expand'])
</script>

<style scoped>
.collapsed-orb {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  cursor: pointer;
  user-select: none;
  overflow: hidden;
}

.orb-core {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #07c160 0%, #05a04e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 16px rgba(7, 193, 96, 0.45), 0 0 0 1.5px rgba(255, 255, 255, 0.35);
  position: relative;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
}

.orb-core:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(7, 193, 96, 0.6), 0 0 0 2px rgba(255, 255, 255, 0.5);
}

.orb-core:active {
  transform: scale(0.92);
}

.orb-icon {
  animation: float 3s ease-in-out infinite;
}

.pulse-ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1.5px solid rgba(7, 193, 96, 0.6);
  animation: pulse 2.4s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
  pointer-events: none;
}

@keyframes pulse {
  0% {
    transform: scale(0.85);
    opacity: 0.9;
  }
  70% {
    transform: scale(1.35);
    opacity: 0;
  }
  100% {
    transform: scale(1.35);
    opacity: 0;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}
</style>
