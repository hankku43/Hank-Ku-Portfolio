import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        component: () => import('../views/PortfolioHome.vue'),
    },
    {
        path: '/demo/:id',
        component: () => import('../views/ProjectDemo.vue'),
    },
]

export default createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
})
