<template>
  <div class="cart">
    <div class="title">
      <h1>Paystack Gift Store</h1>
    </div>
    <div class="header">
      <h2>Login</h2>
    </div>
    <div class="form-item">
      <label>Mobile Money number</label>
      <input v-model="momo" />
    </div>
    <div class="form-item">
      <label>Password</label>
      <input type="password" v-model="password" />
    </div>
    <div class="form-item">
      <button :disabled="!isNumberValid || !isPasswordGood" @click="login">Login</button>
    </div>
    <div class="form-item">
      Don't have an account?
      <router-link :to="{name: 'signup'}">Sign up here</router-link>
    </div>
  </div>
</template>
<script>
export default {
  data: () => ({
    name: '',
    password: '',
    momo: '',
    loading: false,
    auth: {}
  }),
  props: {
    source: String,
    snack: Function
  },
  computed: {
    isNumberValid () {
      const regex = /^[0]{1}[0-9]*$/
      return this.momo && this.momo.length === 10 && regex.test(this.momo)
    },
    isPasswordGood () {
      return this.password.length >= 7
    }
  },
  methods: {
    login () {
      this.loading = true
      const data = {
        momo: this.momo,
        password: this.password
      }
      // this.$router.push('/shopping')
      this.$http
        .post('/login.json', JSON.stringify(data))
        .then((resp) => {
          this.loading = false
          if (!resp.data) {
            // this.snack(resp.data.message, 'error')
            alert('Invalid Credentials. Please check your inputs and try again.')
            return
          }
          localStorage.setItem('shopper', JSON.stringify(resp.data))
          this.$router.push('/shopping')
        })
        .catch(() => {
          this.loading = false
          //   this.snack('A network error occured', 'error')
          alert('We run into an error. Please check your credentials. ')
        })
    },
    momoFormat () {
      if (this.momo.charAt(0) === '0') {
        return this.momo.replace('0', '+233')
      } else {
        return this.momo
      }
    }
  }
}
</script>

<style lang="scss" scoped>
$gray: #f2f5f7;
.cart {
  display: flex;
  flex-direction: column;
  margin: auto;
  width: 50%;
  .title {
    margin-top: 50px;
  }
  .header {
  }
  .form-item {
    display: flex;
    flex-direction: column;
    margin-bottom: 24px;

    label {
      margin-bottom: 8px;
      font-weight: 500;
    }

    input {
      font-size: 14px;
      color: #737575;
      padding: 10px;
      width: 50%;
      border: 1px solid $gray;
      box-sizing: border-box;
      box-shadow: 0px 1px 1px rgba(0, 0, 0, 0.03);
      border-radius: 6px;

      &:focus {
        border: 1px solid rgba(130, 130, 130, 0.2);
        outline: none;
      }
    }
    button {
      width: 50%;
      background: #3bb75e;
      color: white;
      border-radius: 5px;
      border: none;
      font-size: 14px;
      font-weight: 500;
      text-transform: uppercase;
      height: 36px;
      padding-left: 10px;
      padding-right: 10px;
      cursor: pointer;

      &:disabled {
        background-color: rgba(59, 183, 94, 0.65);
        cursor: default;
      }

      &:focus {
        outline: none;
      }
    }
  }
}
</style>
