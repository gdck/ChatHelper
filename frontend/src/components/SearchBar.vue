<template>
  <div class="search-container">
    <div class="search-input-wrapper">
      <Search :size="14" class="search-icon" />
      <input
        type="text"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        placeholder="搜索话术/标签/正文 (Alt+Space)"
        class="search-input"
        ref="searchInputRef"
      />
      <button v-if="modelValue" @click="$emit('update:modelValue', '')" class="clear-btn">
        <X :size="13" />
      </button>
    </div>
    <button @click="$emit('create-reply')" class="add-btn" title="新增话术">
      <Plus :size="15" />
      <span>新增</span>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, X, Plus } from 'lucide-vue-next'

defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue', 'create-reply'])

const searchInputRef = ref(null)

defineExpose({
  focus: () => searchInputRef.value?.focus()
})
</script>

<style scoped>
.search-container {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  gap: 8px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}
.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 8px;
  color: var(--text-secondary);
  pointer-events: none;
}
.search-input {
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 5px 26px 5px 28px;
  color: var(--text-primary);
  font-size: 12.5px;
  outline: none;
  transition: all 0.15s;
}
.search-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px var(--accent-light);
}
.clear-btn {
  position: absolute;
  right: 6px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
}
.add-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12.5px;
  font-weight: 500;
  flex-shrink: 0;
  transition: background 0.15s;
}
.add-btn:hover {
  background: var(--accent-hover);
}
</style>
