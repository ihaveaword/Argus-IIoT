<template>
  <div class="app">
    <!-- 页头 -->
    <header class="header">
      <div class="container header-content">
        <div class="logo">
          <span class="logo-icon">👁️</span>
          <span class="logo-text">Argus-IIoT</span>
        </div>
        
        <nav class="nav">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            🏠 首页
          </router-link>
          <router-link to="/image" class="nav-link" :class="{ active: $route.path === '/image' }">
            📸 图片检测
          </router-link>
          <router-link to="/video" class="nav-link" :class="{ active: $route.path === '/video' }">
            🎬 视频检测
          </router-link>
        </nav>
      </div>
    </header>
    
    <!-- 主内容 -->
    <main class="main">
      <div class="container">
        <router-view />
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>Argus-IIoT · 轻量级边缘云协同目标检测系统</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// App 组件
</script>

<style scoped>
.footer {
  padding: 24px 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.875rem;
  border-top: 1px solid var(--border-color);
}
</style>
