/**
 * API 服务封装
 */

import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
    baseURL: '/api',
    timeout: 120000, // 2分钟超时（视频处理可能较慢）
})

/**
 * 健康检查
 */
export async function checkHealth() {
    const response = await api.get('/health')
    return response.data
}

/**
 * 获取可用模型列表
 */
export async function getModels() {
    const response = await api.get('/models')
    return response.data
}

/**
 * 图片检测
 * @param {File} file - 图片文件
 * @param {number} confidence - 置信度阈值
 * @returns {Promise} 检测结果
 */
export async function detectImage(file, confidence = 0.5) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('confidence', confidence)

    const response = await api.post('/detect/image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })

    return response.data
}

/**
 * 视频检测
 * @param {File} file - 视频文件
 * @param {number} confidence - 置信度阈值
 * @param {Function} onProgress - 上传进度回调
 * @returns {Promise} 检测结果
 */
export async function detectVideo(file, confidence = 0.5, onProgress = null) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('confidence', confidence)

    const response = await api.post('/detect/video', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress) {
                const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                onProgress(percent)
            }
        }
    })

    return response.data
}

/**
 * 获取任务结果
 * @param {string} taskId - 任务ID
 */
export async function getResult(taskId) {
    const response = await api.get(`/result/${taskId}`)
    return response.data
}

export default api
