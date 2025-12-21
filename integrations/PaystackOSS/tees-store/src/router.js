import Vue from 'vue'
import Router from 'vue-router'
import Layout from './components/Layout.vue'
Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Layout
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: () => import('./components/Receipt.vue')
    },
    {
      path: '/shopping',
      name: 'shopping',
      component: Layout
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('./components/Signup.vue')
    },
    {
      path: '/verify-otp',
      name: 'otp',
      component: () => import('./components/Otp.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./components/Login.vue')
    },
    {
      path: '/*',
      component: Layout
    }
  ]
})
