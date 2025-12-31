<template>
  <div class="architecture-audit">
    <div class="header">
      <h1>🏗️ Architecture Audit Tool</h1>
      <p class="subtitle">Comprehensive microservices architecture analysis and consistency audit</p>
    </div>

    <div class="audit-form">
      <h2>Scan Repository</h2>
      <div class="form-group">
        <label for="repoPath">Repository Path:</label>
        <input
          id="repoPath"
          v-model="repoPath"
          type="text"
          placeholder="e.g., /home/runner/work/Argus-IIoT/Argus-IIoT"
          class="input-field"
        />
      </div>
      <button @click="scanRepository" :disabled="loading || !repoPath" class="btn-primary">
        <span v-if="loading">🔄 Scanning...</span>
        <span v-else>🔍 Scan Repository</span>
      </button>
    </div>

    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>

    <div v-if="scanResult" class="scan-result">
      <h2>✅ Scan Completed</h2>
      <div class="result-card">
        <div class="result-info">
          <p><strong>Audit ID:</strong> {{ scanResult.audit_id }}</p>
          <p><strong>Directory:</strong> {{ scanResult.directory }}</p>
          <p><strong>Timestamp:</strong> {{ scanResult.timestamp }}</p>
        </div>
        <div class="result-summary">
          <div class="stat-item">
            <span class="stat-value">{{ scanResult.summary.architecture_patterns }}</span>
            <span class="stat-label">Architecture Patterns</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ scanResult.summary.api_endpoints }}</span>
            <span class="stat-label">API Endpoints</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ scanResult.summary.tech_stack_items }}</span>
            <span class="stat-label">Technology Items</span>
          </div>
        </div>
        <button @click="viewReport(scanResult.audit_id)" class="btn-view-report">
          📊 View Interactive Report
        </button>
      </div>
    </div>

    <div class="audits-list" v-if="audits.length > 0">
      <h2>📋 Previous Audits</h2>
      <div class="audits-container">
        <div v-for="audit in audits" :key="audit.id" class="audit-item">
          <div class="audit-info">
            <p class="audit-id">{{ audit.id }}</p>
            <p class="audit-dir">{{ audit.directory }}</p>
            <p class="audit-time">{{ formatDate(audit.timestamp) }}</p>
          </div>
          <div class="audit-actions">
            <span :class="['status', audit.status]">{{ audit.status }}</span>
            <button v-if="audit.status === 'completed'" @click="viewReport(audit.id)" class="btn-small">
              View Report
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2>🎯 Features</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🏛️</div>
          <h3>Architecture Patterns</h3>
          <p>Automatically detect MVC, Hexagonal, Clean Architecture, DDD, and more</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔌</div>
          <h3>API Analysis</h3>
          <p>Analyze REST, gRPC, GraphQL APIs and generate contract consistency reports</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🛠️</div>
          <h3>Technology Stack</h3>
          <p>Review databases, message queues, caches, and framework choices</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📝</div>
          <h3>ADR Templates</h3>
          <p>Generate Architecture Decision Records templates for documentation</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '../services/api';

export default {
  name: 'ArchitectureAudit',
  setup() {
    const repoPath = ref('/home/runner/work/Argus-IIoT/Argus-IIoT');
    const loading = ref(false);
    const error = ref('');
    const scanResult = ref(null);
    const audits = ref([]);

    const scanRepository = async () => {
      loading.value = true;
      error.value = '';
      scanResult.value = null;

      try {
        const response = await api.post('/audit/scan', {
          directory_path: repoPath.value
        });

        if (response.data.success) {
          scanResult.value = response.data;
          loadAudits(); // Refresh audits list
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to scan repository';
      } finally {
        loading.value = false;
      }
    };

    const viewReport = (auditId) => {
      // Open report in new tab
      const reportUrl = `${api.defaults.baseURL}/audit/report/${auditId}`;
      window.open(reportUrl, '_blank');
    };

    const loadAudits = async () => {
      try {
        const response = await api.get('/audit/audits');
        if (response.data.success) {
          audits.value = response.data.audits.reverse(); // Most recent first
        }
      } catch (err) {
        console.error('Failed to load audits:', err);
      }
    };

    const formatDate = (timestamp) => {
      if (!timestamp) return '';
      return new Date(timestamp).toLocaleString();
    };

    onMounted(() => {
      loadAudits();
    });

    return {
      repoPath,
      loading,
      error,
      scanResult,
      audits,
      scanRepository,
      viewReport,
      formatDate
    };
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
}

.header h1 {
  color: #667eea;
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.audit-form {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.audit-form h2 {
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 30px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
  font-weight: 500;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  border-left: 4px solid #c33;
}

.scan-result {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.scan-result h2 {
  color: #4caf50;
  margin-bottom: 20px;
}

.result-card {
  border: 2px solid #e0e0e0;
  padding: 20px;
  border-radius: 8px;
}

.result-info {
  margin-bottom: 20px;
}

.result-info p {
  margin: 8px 0;
  color: #666;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  display: block;
  color: #666;
  font-size: 0.9rem;
}

.btn-view-report {
  background: #667eea;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 15px;
  transition: background 0.3s;
}

.btn-view-report:hover {
  background: #764ba2;
}

.audits-list {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.audits-list h2 {
  color: #333;
  margin-bottom: 20px;
}

.audits-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.audit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: border-color 0.3s;
}

.audit-item:hover {
  border-color: #667eea;
}

.audit-info {
  flex: 1;
}

.audit-id {
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.audit-dir {
  color: #666;
  font-size: 0.9rem;
  font-family: monospace;
  margin-bottom: 3px;
}

.audit-time {
  color: #999;
  font-size: 0.85rem;
}

.audit-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status.completed {
  background: #d4edda;
  color: #155724;
}

.status.failed {
  background: #f8d7da;
  color: #721c24;
}

.btn-small {
  background: #667eea;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.btn-small:hover {
  background: #764ba2;
}

.features-section {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.features-section h2 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  text-align: center;
  padding: 25px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  transition: all 0.3s;
}

.feature-card:hover {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #333;
  margin-bottom: 10px;
  font-size: 1.2rem;
}

.feature-card p {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
}
</style>
