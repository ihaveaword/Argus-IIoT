<template>
  <div class="home">
    <h1 class="page-title">🎯 Argus-IIoT 平台</h1>
    <p class="page-subtitle">目标检测 + 微服务架构审计 · 一站式 IIoT 解决方案</p>
    
    <!-- 状态卡片 -->
    <div class="status-card" :class="{ 'status-online': isOnline, 'status-offline': !isOnline }">
      <span class="status-dot"></span>
      <span>{{ isOnline ? '服务在线' : '服务离线' }}</span>
      <span v-if="deviceInfo" class="device-info">· 设备: {{ deviceInfo }}</span>
    </div>
    
    <!-- 功能卡片 -->
    <div class="feature-grid">
      <router-link to="/image" class="card feature-card">
        <div class="card-header">
          <div class="card-icon">📸</div>
          <h2 class="card-title">图片检测</h2>
        </div>
        <p class="feature-desc">上传图片，自动识别并标注目标物体，支持 JPG、PNG、BMP 等格式</p>
        <div class="feature-tags">
          <span class="tag">实时推理</span>
          <span class="tag">结果下载</span>
        </div>
      </router-link>
      
      <router-link to="/video" class="card feature-card">
        <div class="card-header">
          <div class="card-icon">🎬</div>
          <h2 class="card-title">视频检测</h2>
        </div>
        <p class="feature-desc">上传视频文件，逐帧进行目标检测，输出标注后的视频</p>
        <div class="feature-tags">
          <span class="tag">逐帧处理</span>
          <span class="tag">视频导出</span>
        </div>
      </router-link>
      
      <router-link to="/audit" class="card feature-card">
        <div class="card-header">
          <div class="card-icon">🏗️</div>
          <h2 class="card-title">架构审计</h2>
        </div>
        <p class="feature-desc">全面扫描微服务架构，生成交互式报告，包含模式识别和技术栈分析</p>
        <div class="feature-tags">
          <span class="tag">架构分析</span>
          <span class="tag">API审计</span>
        </div>
      </router-link>
    </div>
    
    <!-- 使用说明 -->
    <div class="card info-card">
      <h3 class="info-title">💡 快速开始</h3>
      <div class="steps">
        <div class="step">
          <span class="step-num">1</span>
          <span>选择「图片检测」或「视频检测」功能</span>
        </div>
        <div class="step">
          <span class="step-num">2</span>
          <span>上传需要检测的文件</span>
        </div>
        <div class="step">
          <span class="step-num">3</span>
          <span>调整置信度阈值（可选）</span>
        </div>
        <div class="step">
          <span class="step-num">4</span>
          <span>查看检测结果并下载</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { checkHealth } from '../services/api'

const isOnline = ref(false)
const deviceInfo = ref('')

onMounted(async () => {
  try {
    const health = await checkHealth()
    isOnline.value = health.status === 'healthy'
    deviceInfo.value = health.device?.toUpperCase() || ''
  } catch (error) {
    isOnline.value = false
  }
})
</script>

<style scoped>
.home {
  max-width: 900px;
  margin: 0 auto;
}

.status-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  margin-bottom: 32px;
}

.status-online {
  background: rgba(72, 187, 120, 0.15);
  color: var(--success);
}

.status-offline {
  background: rgba(252, 129, 129, 0.15);
  color: var(--error);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.device-info {
  color: var(--text-muted);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  text-decoration: none;
  color: inherit;
}

.feature-desc {
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.6;
}

.feature-tags {
  display: flex;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  background: var(--bg-input);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.info-card {
  background: var(--bg-card);
}

.info-title {
  font-size: 1.125rem;
  margin-bottom: 20px;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: 50%;
  font-size: 0.875rem;
  font-weight: 600;
}
</style>
