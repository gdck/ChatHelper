<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <span class="modal-title">{{ isEdit ? '编辑话术' : '新增话术' }}</span>
        <button class="close-btn" @click="$emit('close')"><X :size="16" /></button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>所属分类</label>
          <select v-model="form.category_id" class="form-select">
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>话术标题</label>
          <input
            type="text"
            v-model="form.title"
            placeholder="例如：售后退换货指引"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <div class="label-row">
            <label>话术正文</label>
            <div class="variable-chips">
              <span class="var-btn" @click="insertVar('{日期}')">+ {日期}</span>
              <span class="var-btn" @click="insertVar('{时间}')">+ {时间}</span>
              <span class="var-btn" @click="insertVar('{问候语}')">+ {问候语}</span>
              <span class="var-btn" @click="insertVar('{星期}')">+ {星期}</span>
            </div>
          </div>
          <textarea
            ref="contentAreaRef"
            v-model="form.content"
            rows="5"
            placeholder="输入回复内容，支持自动替换上方动态变量..."
            class="form-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <div class="label-row">
            <label>多媒体附件 (支持图片/文档/视频)</label>
            <button class="add-file-btn" @click="chooseFiles">
              <Paperclip :size="13" />
              <span>选择文件</span>
            </button>
          </div>
          <div class="attachments-list" v-if="form.attachments.length">
            <div v-for="(att, idx) in form.attachments" :key="idx" class="att-item">
              <span class="att-name" :title="att.path">{{ att.name }}</span>
              <button class="remove-att-btn" @click="removeAttachment(idx)"><X :size="12" /></button>
            </div>
          </div>
          <div class="empty-att-tip" v-else>暂无附件</div>
        </div>

        <div class="form-group">
          <label>排序序号 (越小越靠前)</label>
          <input type="number" v-model.number="form.sort_order" class="form-input" />
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
import { X, Paperclip } from 'lucide-vue-next'

const props = defineProps({
  initialData: {
    type: Object,
    default: null
  },
  categories: {
    type: Array,
    default: () => []
  },
  defaultCategoryId: {
    type: [Number, null],
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const isEdit = computed(() => !!(props.initialData && props.initialData.id))
const contentAreaRef = ref(null)

const form = reactive({
  id: null,
  category_id: props.defaultCategoryId || (props.categories[0]?.id || 1),
  title: '',
  content: '',
  attachments: [],
  tags: [],
  sort_order: 0
})

onMounted(() => {
  if (props.initialData) {
    form.id = props.initialData.id
    form.category_id = props.initialData.category_id
    form.title = props.initialData.title
    form.content = props.initialData.content
    form.attachments = JSON.parse(JSON.stringify(props.initialData.attachments || []))
    form.tags = JSON.parse(JSON.stringify(props.initialData.tags || []))
    form.sort_order = props.initialData.sort_order || 0
  }
})

function insertVar(varText) {
  form.content += varText
}

async function chooseFiles() {
  if (window.pywebview && window.pywebview.api) {
    const files = await window.pywebview.api.selectFiles()
    if (files && files.length) {
      files.forEach(f => {
        const name = f.split(/[\\/]/).pop()
        form.attachments.push({ name, path: f })
      })
    }
  }
}

function removeAttachment(idx) {
  form.attachments.splice(idx, 1)
}

function handleSubmit() {
  if (!form.title.trim()) {
    alert('请输入话术标题')
    return
  }
  emit('save', { ...form })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
  padding: 16px;
}
.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  width: 100%;
  max-width: 370px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
}
.modal-title {
  font-size: 14px;
  font-weight: 600;
}
.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}
.modal-body {
  padding: 12px 14px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
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
.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.variable-chips {
  display: flex;
  gap: 4px;
}
.var-btn {
  font-size: 10.5px;
  background: var(--accent-light);
  color: var(--accent-color);
  padding: 1px 5px;
  border-radius: 4px;
  cursor: pointer;
}
.form-input, .form-select, .form-textarea {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 10px;
  color: var(--text-primary);
  font-size: 12.5px;
  outline: none;
  transition: border-color 0.15s;
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--accent-color);
}
.form-textarea {
  resize: vertical;
}
.add-file-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
}
.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
}
.att-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-secondary);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11.5px;
}
.att-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
}
.remove-att-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
}
.empty-att-tip {
  font-size: 11px;
  color: var(--text-secondary);
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
  font-size: 12.5px;
  cursor: pointer;
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
  font-weight: 500;
}
</style>
