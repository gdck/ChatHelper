<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <span class="modal-title">{{ isEdit ? '编辑分类' : '新建分类' }}</span>
        <button class="close-btn" @click="$emit('close')"><X :size="15" /></button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>分类名称 <span class="required">*</span></label>
          <input
            ref="inputRef"
            type="text"
            v-model="form.name"
            placeholder="例如：售后常见问答、售前促单..."
            class="form-input"
            @keydown.enter="handleSubmit"
          />
        </div>

        <div class="form-group">
          <label>显示顺序 (数字越小越靠前)</label>
          <input
            type="number"
            v-model.number="form.sort_order"
            class="form-input"
            @keydown.enter="handleSubmit"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn cancel" @click="$emit('close')">取消</button>
        <button class="btn submit" @click="handleSubmit">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  category: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])
const isEdit = computed(() => !!(props.category && props.category.id))
const inputRef = ref(null)

const form = reactive({
  id: props.category ? props.category.id : null,
  name: props.category ? props.category.name : '',
  sort_order: props.category ? props.category.sort_order : 0
})

onMounted(() => {
  inputRef.value?.focus()
})

function handleSubmit() {
  if (!form.name.trim()) return
  emit('save', {
    id: form.id,
    name: form.name.trim(),
    sort_order: form.sort_order || 0
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 600;
  padding: 16px;
}
.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  width: 100%;
  max-width: 320px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
}
.modal-title {
  font-size: 13.5px;
  font-weight: 600;
}
.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}
.modal-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.form-group label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}
.required {
  color: #ef4444;
}
.form-input {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 10px;
  color: var(--text-primary);
  font-size: 12.5px;
  outline: none;
  transition: border-color 0.15s;
}
.form-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px var(--accent-light);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid var(--border-color);
}
.btn {
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
}
.btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.btn.submit {
  background: var(--accent-color);
  border: none;
  color: white;
}
.btn.submit:hover {
  background: var(--accent-hover);
}
</style>
