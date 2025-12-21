<template>
  <div class="cart">
    <div class="title">
      <h1>Paystack Gift Store</h1>
    </div>
    <div class="header">
      <h2>Sign Up</h2>
    </div>
    <div class="form-item">
      <label>Name</label>
      <input type="text" v-model="name" placeholder="Jane Doe" />
    </div>
    <div class="form-item">
      <label>Mobile Money number</label>
      <input v-model="momo" placeholder="Ex: 0240974010" />
    </div>
    <div class="form-item">
      <label>Password</label>
      <input type="password" v-model="password" />
    </div>
    <div class="form-item">
      <button :disabled="!isNumberValid || !isNameValid" @click="signup">Sign Up</button>
    </div>
    <div class="form-item">
      Already have an account?
      <router-link :to="{name: 'login'}">Login here</router-link>
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
      return (
        this.momo &&
        this.momo.length === 10 &&
        regex.test(this.momo) && this.password.length >= 7
      )
    },
    isNameValid () {
      const regex = /^[a-z][a-z '-.,]{0,31}$|^$/i
      return this.name && regex.test(this.name)
    }
  },
  methods: {
    signup () {
      this.loading = true
      const data = {
        name: this.name,
        momo: this.momo,
        password: this.password
      }
      // this.$router.push('/shopping')
      this.$http
        .post('/signup.json', JSON.stringify(data))
        .then((resp) => {
          this.loading = false
          if (!resp.data) {
            // this.snack(resp.data.message, 'error')
            return
          }
          localStorage.setItem('shopper', JSON.stringify(resp.data.momo))
          this.$router.push('/verify-otp')
        })
        .catch(() => {
          this.loading = false
          // this.snack('A network error occured', 'error')
          alert('We run into an error. Please check your inputs & try again.')
        })
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
  padding: 10px;
  width: 50%;
  .title {
    margin-top: 50px;
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

.itemlist {
  &__header,
  &__body {
    display: grid;
    grid-template-columns: 300px repeat(3, 1fr);
    grid-gap: 12px;
  }

  &__header {
    margin-bottom: 36px;
    font-size: 18px;
    font-weight: 500;
  }

  &__body {
    margin-bottom: 32px;
  }

  button {
    border: none;
    font-size: 16px;
    padding: 8px;
    font-weight: 400;
    cursor: pointer;
  }
}

.item {
  &__content {
    display: flex;
  }

  &__image {
    flex: 0 1 120px;
    img {
      width: 100px;
      border-radius: 8px;
    }
  }

  &__description {
    flex: 1 1 auto;
    h4 {
      margin: 0;
      line-height: 1;
    }
    span {
      display: block;
    }
  }

  &__quantity {
    display: flex;
  }

  &__price {
    flex: 0 1 auto;
  }
}

.qty-wrapper {
  border: 1px solid #efefef;
  height: fit-content;

  &__value {
    width: 70px;
    height: 20px;
    margin: 0 auto;
    display: inline-block;
    vertical-align: middle;
    text-align: center;
    cursor: default;
  }

  &__button {
    width: 20px;
    height: 20px;
    background: #f2f2f2;
    border-radius: 4px;
    font-weight: 600;
    padding: 8px 5px 8px 5px;
    border: 1px solid #f5f3f3;
    display: inline-block;
    vertical-align: middle;
    text-align: center;
    cursor: pointer;
  }
}
</style>
