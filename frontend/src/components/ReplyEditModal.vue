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
          <label>话术标题 <span class="required">*</span></label>
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
            placeholder="输入回复内容，点击上方插入动态变量..."
            class="form-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <div class="label-row">
            <label>多媒体附件 (支持多图片/文档/视频)</label>
            <button class="add-file-btn" @click="chooseFiles">
              <Paperclip :size="13" />
              <span>选择文件</span>
            </button>
          </div>
          <div class="attachments-list" v-if="form.attachments.length">
            <div v-for="(att, idx) in form.attachments" :key="idx" class="att-item">
              <Paperclip :size="12" class="att-icon" />
              <span class="att-name" :title="att.path">{{ att.name }}</span>
              <button class="remove-att-btn" @click="removeAttachment(idx)" aria-label="移除附件">
                <X :size="12" />
              </button>
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
        <button class="btn submit" @click="handleSubmit">保存话术</button>
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

const emit = defineEmits(['close', 'save', 'toast'])

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
    emit('toast', { type: 'warning', message: '请输入话术标题' })
    return
  }
  emit('save', { ...form })
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
  z-index: 500;
  padding: 16px;
}
.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--r-panel);
  width: 100%;
  max-width: 376px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}
.modal-title {
  font-size: 14px;
  font-weight: 500;
}
.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background var(--dur-feedback) var(--ease),
    color var(--dur-feedback) var(--ease);
}
.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.modal-body {
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-secondary);
}
.required {
  color: var(--danger);
}
.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.variable-chips {
  display: flex;
  gap: 6px;
}
.var-btn {
  font-size: 11px;
  font-family: var(--font-mono);
  background: var(--accent-wash);
  color: var(--accent-strong);
  padding: 3px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background var(--dur-feedback) var(--ease);
}
.var-btn:hover {
  background: var(--accent-light);
}
.form-input, .form-select, .form-textarea {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r-control);
  padding: 8px 10px;
  color: var(--text-primary);
  font-size: 12.5px;
  outline: none;
  transition: border-color var(--dur-feedback) var(--ease);
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--accent);
}
.form-textarea {
  resize: vertical;
  line-height: 1.6;
}
.add-file-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  padding: 4px 8px;
  border-radius: var(--r-control);
  font-size: 11.5px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: border-color var(--dur-feedback) var(--ease),
    background var(--dur-feedback) var(--ease);
}
.add-file-btn:hover {
  border-color: var(--border-strong);
  background: var(--bg-hover);
}
.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
}
.att-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 6px 10px;
  border-radius: var(--r-control);
  font-size: 12px;
}
.att-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}
.att-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
  flex: 1;
  min-width: 0;
}
.remove-att-btn {
  background: transparent;
  border: none;
  color: var(--danger);
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.remove-att-btn:hover {
  background: var(--danger-wash);
}
.empty-att-tip {
  font-size: 11.5px;
  color: var(--text-muted);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}
.btn {
  padding: 8px 16px;
  border-radius: var(--r-control);
  font-size: 12.5px;
  cursor: pointer;
  font-weight: 500;
  transition: background var(--dur-feedback) var(--ease),
    border-color var(--dur-feedback) var(--ease);
}
.btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
}
.btn.cancel:hover {
  border-color: var(--border-strong);
  background: var(--bg-hover);
}
.btn.submit {
  background: var(--accent-solid);
  border: none;
  color: #ffffff;
}
.btn.submit:hover {
  background: var(--accent-hover);
}
</style>
