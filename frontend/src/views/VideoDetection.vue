<template>
  <div class="video-detection">
    <h1 class="page-title">🎬 视频检测</h1>
    <p class="page-subtitle">上传视频进行目标检测，支持 MP4、AVI、MOV 格式</p>
    
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
      v-if="!isProcessing && !result"
    >
      <div class="upload-zone-icon">🎥</div>
      <p class="upload-zone-text">点击或拖拽上传视频</p>
      <p class="upload-zone-hint">支持 MP4、AVI、MOV，最大 100MB</p>
    </div>
    
    <input 
      ref="fileInput"
      type="file" 
      accept="video/*"
      @change="handleFileSelect"
      style="display: none"
    />
    
    <!-- 处理进度 -->
    <div v-if="isProcessing" class="card processing-card">
      <h3 class="processing-title">⏳ 正在处理视频</h3>
      <p class="processing-file">{{ fileName }}</p>
      
      <!-- 上传进度 -->
      <div v-if="uploadProgress < 100" class="progress-section">
        <span class="progress-label">上传中...</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <span class="progress-percent">{{ uploadProgress }}%</span>
      </div>
      
      <!-- 处理中 -->
      <div v-else class="processing-status">
        <div class="spinner"></div>
        <p>服务端正在处理视频，请稍候...</p>
        <p class="processing-hint">（处理时间取决于视频长度）</p>
      </div>
    </div>
    
    <!-- 结果展示 -->
    <div v-if="result" class="result-section">
      <!-- 成功提示 -->
      <div class="message message-success">
        ✅ 视频处理完成！
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-bar">
        <button class="btn btn-secondary" @click="reset">
          🔄 重新上传
        </button>
        <a 
          :href="result.output_url" 
          download 
          class="btn btn-primary"
        >
          📥 下载检测视频
        </a>
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.total_frames }}</div>
          <div class="stat-label">总帧数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.fps }}</div>
          <div class="stat-label">帧率 FPS</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.resolution }}</div>
          <div class="stat-label">分辨率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.total_detections }}</div>
          <div class="stat-label">总检测数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ result.stats.processing_time }}s</div>
          <div class="stat-label">处理时间</div>
        </div>
      </div>
      
      <!-- 视频预览 -->
      <div class="card video-preview">
        <h3 style="margin-bottom: 16px;">🎞️ 视频预览</h3>
        <video 
          :src="result.output_url" 
          controls 
          class="preview-video"
        ></video>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="message message-error">
      ❌ {{ error }}
      <button class="btn btn-secondary" @click="reset" style="margin-left: 16px;">
        重试
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { detectVideo } from '../services/api'

const fileInput = ref(null)
const confidence = ref(0.5)
const isDragover = ref(false)
const isProcessing = ref(false)
const uploadProgress = ref(0)
const fileName = ref('')
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
  if (file && file.type.startsWith('video/')) {
    processFile(file)
  }
}

async function processFile(file) {
  isProcessing.value = true
  uploadProgress.value = 0
  fileName.value = file.name
  error.value = null
  result.value = null
  
  try {
    result.value = await detectVideo(
      file, 
      confidence.value,
      (progress) => {
        uploadProgress.value = progress
      }
    )
  } catch (err) {
    error.value = err.response?.data?.detail || '视频处理失败，请重试'
  } finally {
    isProcessing.value = false
  }
}

function reset() {
  isProcessing.value = false
  uploadProgress.value = 0
  fileName.value = ''
  result.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.video-detection {
  max-width: 1000px;
  margin: 0 auto;
}

.settings-card {
  margin-bottom: 24px;
}

.processing-card {
  text-align: center;
  padding: 48px;
}

.processing-title {
  font-size: 1.25rem;
  margin-bottom: 8px;
}

.processing-file {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-label {
  color: var(--text-secondary);
  min-width: 80px;
}

.progress-percent {
  color: var(--primary-color);
  font-weight: 600;
  min-width: 50px;
}

.processing-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.processing-hint {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.result-section {
  margin-top: 24px;
}

.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.video-preview {
  margin-top: 24px;
}

.preview-video {
  width: 100%;
  border-radius: var(--radius-md);
  background: #000;
}
</style>
