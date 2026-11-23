<template>
  <div class="search-container">
    <div class="search-input-wrapper">
      <Search :size="14" class="search-icon" />
      <input
        type="text"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        placeholder="搜索话术、标签、正文"
        class="search-input"
        ref="searchInputRef"
        aria-label="搜索话术"
      />
      <button v-if="modelValue" @click="$emit('update:modelValue', '')" class="clear-btn" aria-label="清空搜索">
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
  padding: 8px 12px;
  gap: 8px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  min-width: 0;
}
.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-muted);
  pointer-events: none;
}
.search-input {
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-control);
  padding: 7px 32px;
  color: var(--text-primary);
  font-size: 12.5px;
  outline: none;
  transition: border-color var(--dur-feedback) var(--ease);
}
.search-input::placeholder {
  color: var(--text-muted);
}
.search-input:focus {
  border-color: var(--accent);
}
.clear-btn {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 4px;
}
.clear-btn:hover {
  color: var(--text-primary);
}
.add-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--accent-solid);
  color: #ffffff;
  border: none;
  padding: 7px 12px;
  border-radius: var(--r-control);
  cursor: pointer;
  font-size: 12.5px;
  font-weight: 500;
  flex-shrink: 0;
  transition: background var(--dur-feedback) var(--ease);
}
.add-btn:hover {
  background: var(--accent-hover);
}
</style>