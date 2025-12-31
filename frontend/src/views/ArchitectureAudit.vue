<template>
  <div class="architecture-audit">
    <div class="header">
      <h1>🏗️ 架构一致性审计</h1>
      <p>全面分析微服务架构的模式、API契约、服务拓扑和技术栈</p>
    </div>

    <div class="audit-section">
      <div class="card">
        <h2>🚀 快速开始</h2>
        <p>分析当前仓库的架构，生成完整的审计报告</p>
        
        <button 
          @click="analyzeLocalRepository" 
          :disabled="loading"
          class="btn-primary"
        >
          {{ loading ? '分析中...' : '分析本地仓库' }}
        </button>

        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>正在分析架构模式、API契约和服务依赖关系...</p>
        </div>
      </div>

      <div v-if="result" class="result-section">
        <div class="card success-card">
          <h2>✅ 分析完成</h2>
          
          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-value">{{ result.summary.total_repositories }}</div>
              <div class="stat-label">仓库数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ result.summary.total_services }}</div>
              <div class="stat-label">服务数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ result.summary.total_endpoints }}</div>
              <div class="stat-label">API端点</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ result.summary.tech_stack_items }}</div>
              <div class="stat-label">技术栈组件</div>
            </div>
            <div class="stat-box" :class="{'alert-danger': result.summary.circular_dependencies > 0}">
              <div class="stat-value">{{ result.summary.circular_dependencies }}</div>
              <div class="stat-label">循环依赖</div>
            </div>
            <div class="stat-box" :class="{'alert-warning': result.summary.bottlenecks > 0}">
              <div class="stat-value">{{ result.summary.bottlenecks }}</div>
              <div class="stat-label">性能瓶颈</div>
            </div>
          </div>

          <div class="reports">
            <h3>📊 生成的报告</h3>
            <div class="report-links">
              <a :href="getFullUrl(result.report.html_url)" target="_blank" class="report-link">
                📄 查看完整HTML报告
              </a>
              <a :href="getFullUrl(result.report.topology_svg_url)" target="_blank" class="report-link">
                🕸️ 服务拓扑图 (SVG)
              </a>
              <a :href="getFullUrl(result.report.patterns_svg_url)" target="_blank" class="report-link">
                📈 架构模式分布图 (SVG)
              </a>
            </div>
          </div>

          <div v-if="result.details && result.details.repositories.length > 0" class="details">
            <h3>🔍 仓库详情</h3>
            <div v-for="repo in result.details.repositories" :key="repo.name" class="repo-card">
              <h4>📦 {{ repo.name }}</h4>
              <p><strong>架构模式:</strong> 
                <span v-for="pattern in repo.patterns" :key="pattern" class="badge">{{ pattern }}</span>
              </p>
              <p><strong>服务:</strong> {{ repo.services.join(', ') || '无' }}</p>
              <p><strong>API端点:</strong> {{ repo.api_endpoints }}</p>
              <p><strong>技术栈:</strong> {{ repo.tech_stack }} 项</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-message">
        <h3>❌ 错误</h3>
        <p>{{ error }}</p>
      </div>
    </div>

    <div class="info-section">
      <div class="card">
        <h2>📖 功能说明</h2>
        <div class="features">
          <div class="feature">
            <h3>🏛️ 架构模式识别</h3>
            <p>自动识别MVC、Hexagonal、Clean Architecture、DDD等架构模式</p>
          </div>
          <div class="feature">
            <h3>🔌 API契约分析</h3>
            <p>分析REST、gRPC、GraphQL接口，检测破坏性变更</p>
          </div>
          <div class="feature">
            <h3>🕸️ 服务拓扑</h3>
            <p>绘制完整的服务调用关系，标注循环依赖和性能瓶颈</p>
          </div>
          <div class="feature">
            <h3>🛠️ 技术栈审计</h3>
            <p>审查数据库、消息队列、缓存等技术选型，提供标准化建议</p>
          </div>
          <div class="feature">
            <h3>📝 ADR模板</h3>
            <p>提供架构决策记录模板，统一技术文档规范</p>
          </div>
          <div class="feature">
            <h3>📊 交互式报告</h3>
            <p>生成包含代码跳转链接和SVG图表的HTML报告</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ArchitectureAudit',
  data() {
    return {
      loading: false,
      result: null,
      error: null,
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    };
  },
  methods: {
    async analyzeLocalRepository() {
      this.loading = true;
      this.error = null;
      this.result = null;

      try {
        const response = await axios.post(`${this.apiBaseUrl}/api/architecture/analyze-local`);
        this.result = response.data;
      } catch (err) {
        this.error = err.response?.data?.detail || err.message || '分析失败';
        console.error('Error analyzing repository:', err);
      } finally {
        this.loading = false;
      }
    },
    getFullUrl(path) {
      if (path.startsWith('http')) {
        return path;
      }
      return `${this.apiBaseUrl}${path}`;
    }
  }
};
</script>

<style scoped>
.architecture-audit {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card h2 {
  color: #667eea;
  margin-bottom: 15px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 40px;
  font-size: 1.1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 20px;
  font-weight: bold;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  margin-top: 30px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.stat-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-box.alert-danger {
  background: #ffebee;
  border: 2px solid #f44336;
}

.stat-box.alert-warning {
  background: #fff3e0;
  border: 2px solid #ff9800;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #667eea;
}

.stat-box.alert-danger .stat-value {
  color: #f44336;
}

.stat-box.alert-warning .stat-value {
  color: #ff9800;
}

.stat-label {
  color: #666;
  margin-top: 5px;
  font-size: 0.9rem;
}

.reports {
  margin-top: 30px;
}

.reports h3 {
  color: #764ba2;
  margin-bottom: 15px;
}

.report-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.report-link {
  display: block;
  padding: 15px 20px;
  background: white;
  border: 2px solid #667eea;
  border-radius: 8px;
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s;
}

.report-link:hover {
  background: #667eea;
  color: white;
  transform: translateX(5px);
}

.details {
  margin-top: 30px;
}

.details h3 {
  color: #764ba2;
  margin-bottom: 15px;
}

.repo-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #667eea;
}

.repo-card h4 {
  color: #667eea;
  margin-bottom: 10px;
}

.badge {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  margin-right: 5px;
}

.error-message {
  background: #ffebee;
  border: 2px solid #f44336;
  border-radius: 8px;
  padding: 20px;
  color: #c62828;
}

.info-section {
  margin-top: 40px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.feature {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.feature h3 {
  color: #667eea;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.feature p {
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 1.8rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
