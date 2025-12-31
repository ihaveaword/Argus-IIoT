import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'

// 路由配置
const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('./views/HomeView.vue')
    },
    {
        path: '/image',
        name: 'image',
        component: () => import('./views/ImageDetection.vue')
    },
    {
        path: '/video',
        name: 'video',
        component: () => import('./views/VideoDetection.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 创建应用
const app = createApp(App)
app.use(router)
app.mount('#app')
