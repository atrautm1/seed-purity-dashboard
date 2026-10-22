// import { createRouter, createWebHistory } from 'vue-router'
// import ConsensusView from '../views/ConsensusView.vue'
// import AnalysisView from '../views/AnalysisView.vue'

// const routes = [
//   { path: '/', redirect: '/consensus' },
//   { path: '/consensus', name: 'Consensus', component: ConsensusView },
//   { path: '/analysis', name: 'Analysis', component: AnalysisView }
// ]

// export const router = createRouter({
//   history: createWebHistory(),
//   routes
// })

import { createRouter, createWebHistory } from 'vue-router'
import ConsensusView from '../views/ConsensusView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import LoginView from '../views/LoginView.vue'
import LandingView from '../views/LandingView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Landing',
    component: LandingView,
    meta: { requiresAuth: true }
  },
  {
    path: '/consensus',
    name: 'Consensus',
    component: ConsensusView,
    meta: { requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: AnalysisView,
    meta: { requiresAuth: true }
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('auth_token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export { router }
export default router