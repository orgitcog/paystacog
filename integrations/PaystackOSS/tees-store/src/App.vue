<template>
  <div id="app">
    <router-view></router-view>
  </div>
  <!-- <v-content>
      <router-view></router-view>
    </v-content> -->
</template>

<script>
import Layout from './components/Layout.vue'
import Magazine from './components/Magazine.vue'
import Signup from './components/Signup.vue'
export default {
  name: 'App',
  components: {
    // eslint-disable-next-line vue/no-unused-components
    Signup,
    // eslint-disable-next-line vue/no-unused-components
    Layout,
    // eslint-disable-next-line vue/no-unused-components
    Magazine
  }
}
</script>

<style>
body {
  margin: 0;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
