<template>
  <div class="layout">
    <div class="layout__left">
      <Cart />
    </div>
    <div :hidden="true" class="layout__right">
      <Receipt />
    </div>
    <!-- <Magazine /> -->
  </div>
</template>

<script>
import Cart from './Cart.vue'
import { mapGetters } from 'vuex'
import Receipt from './Receipt.vue'
// import Magazine from './Magazine.vue'
export default {
  name: 'Layout',
  components: {
    Cart,
    Receipt
  },
  computed: {
    ...mapGetters('cart', {
      selected: 'cartTotalPrice'
    }),
    isValidTotal () {
      return this.selected.toFixed(2) >= 1.99
    }
  },
  mounted: function () {
    if (!localStorage.getItem('shopper')) {
      this.$router.push('/login')
    }
    // End session after 10 minutes.
    setTimeout(this.endSession, 600000)
  },
  methods: {
    endSession () {
      alert('Your session has expired. We\'re logging you out.')
      localStorage.removeItem('shopper')
      this.$router.push('/login')
    }
  }
}
</script>

<style lang="scss" scoped>
 $light-gray: #fbfbfb;

  .layout {
    display: flex;

    &__left {
      width: 99vw;
      padding: 32px;
      background: $light-gray;
    }

    &__right {
      width: 30vw;
      height: 80vh;
      padding: 32px;
    }
  }
</style>
