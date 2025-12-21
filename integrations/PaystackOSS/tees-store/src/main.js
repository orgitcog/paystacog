import Vue from 'vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import router from './router'
import axios from 'axios'
import App from './App.vue'
import store from './store'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.config.productionTip = false

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

const instance = axios.create({
  baseURL: 'https://pstk-itc-mobile-money.herokuapp.com/',
  // withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': ''
  }
})

Vue.prototype.$http = instance

new Vue({
  store,
  router,
  render: h => h(App)
}).$mount('#app')
