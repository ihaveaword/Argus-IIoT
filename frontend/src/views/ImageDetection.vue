<template>
  <div class="image-detection">
    <h1 class="page-title">📸 图片检测</h1>
    <p class="page-subtitle">上传图片进行目标检测，支持 JPG、PNG、BMP、WebP 格式</p>
    
    <!-- 置信度设置 -->
    <div class="card settings-card">
      <div class="slider-group">
        <div class="slider-label">
          <span>置信度阈值</span>
          <span class="slider-value">{{ confidence.toFixed(2) }}</span>
        </div>
        <input 
          type="range" 
          v-model.number="confidence"
          min="0.1" 
          max="0.95" 
          step="0.05"
        />
      </div>
    </div>
    
    <!-- 上传区域 -->
    <div 
      class="upload-zone"
      :class="{ dragover: isDragover }"
      @click="triggerUpload"
      @dragover.prevent="isDragover = true"
      @dragleave="isDragover = false"
      @drop.prevent="handleDrop"
      v-if="!originalImage"
    >
      <div class="upload-zone-icon">📤</div>
      <p class="upload-zone-text">点击或拖拽上传图片</p>
      <p class="upload-zone-hint">支持 JPG、PNG、BMP、WebP，最大 10MB</p>
    </div>
    
    <input 
      ref="fileInput"
      type="file" 
      accept="image/*"
      @change="handleFileSelect"
      style="display: none"
    />
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p class="loading-text">正在检测中...</p>
    </div>
    
    <!-- 结果展示 -->
    <div v-if="result" class="result-section">
      <!-- 重新上传按钮 -->
      <div class="action-bar">
        <button class="btn btn-secondary" @click="reset">
          🔄 重新上传
        </button>
        <a 
          :href="result.annotated_image" 
          download="detection_result.jpg" 
          class="btn btn-primary"
        >
          📥 下载结果
        </a>
      </div>
      
      <!-- 图片对比 -->
      <div class="result-grid">
        <div class="result-item">
          <p class="result-label">原始图片</p>
          <img :src="originalImage" class="result-image" alt="原始图片" />
        </div>
        <div class="result-item">
          <p class="result-label">检测结果</p>
          <img :src="result.annotated_image" class="result-image" alt="检测结果" />
        </div>
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.total_objects }}</div>
          <div class="stat-label">检测目标</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.inference_time }}s</div>
          <div class="stat-label">推理时间</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.image_size }}</div>
          <div class="stat-label">图片尺寸</div>
        </div>
      </div>
      
      <!-- 检测列表 -->
      <div v-if="result.detections.length > 0" class="card">
        <h3 style="margin-bottom: 16px;">🎯 检测详情</h3>
        <div class="detection-list">
          <div 
            v-for="(det, index) in result.detections" 
            :key="index"
            class="detection-item"
          >
            <span class="detection-class">{{ det.class }}</span>
            <span class="detection-conf">{{ (det.confidence * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="message message-error">
      ❌ {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { detectImage } from '../services/api'

const fileInput = ref(null)
const confidence = ref(0.5)
const isDragover = ref(false)
const isLoading = ref(false)
const originalImage = ref(null)
const result = ref(null)
const error = ref(null)

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (file) {
    processFile(file)
  }
}

function handleDrop(event) {
  isDragover.value = false
  const file = event.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

async function processFile(file) {
  // 显示原图预览
  originalImage.value = URL.createObjectURL(file)
  isLoading.value = true
  error.value = null
  result.value = null
  
  try {
    result.value = await detectImage(file, confidence.value)
  } catch (err) {
    error.value = err.response?.data?.detail || '检测失败，请重试'
    originalImage.value = null
  } finally {
    isLoading.value = false
  }
}

function reset() {
  originalImage.value = null
  result.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.image-detection {
  max-width: 1000px;
  margin: 0 auto;
}

.settings-card {
  margin-bottom: 24px;
}

.result-section {
  margin-top: 24px;
}

.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.result-item {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 16px;
}
</style>
