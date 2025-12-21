<template>
  <div class="cart">
    <div class="title">
      <h1>Paystack Gift Store</h1>
    </div>
    <div class="header">
      <h3>Please enter the OTP sent to your phone</h3>
    </div>
    <div class="form-item">
      <label> It may take up to 2 minutes to receive it. </label>
      <input v-model="otp" />
    </div>
    <div class="form-item">
      <button :disabled="!isNumberValid" @click="submitOTP">Verify</button>
    </div>
    <div class="form-item">
      <a id="resend-link" style="display: none" @click="resendOTP">
        OTP expired, resend OTP?</a>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    otp: '',
    loading: false
  }),
  props: {
    source: String,
    snack: Function
  },
  computed: {
    isNumberValid () {
      const regex = /^[0-9]*$/
      return this.otp && this.otp.length === 6 && regex.test(this.otp)
    }
  },
  created () {
    setTimeout(
      function () { document.getElementById('resend-link').style = 'cursor: pointer; display: block' }, 90000)
  },
  methods: {
    submitOTP () {
      this.loading = true
      const data = {
        otp: this.otp
      }
      // this.$router.push('/shopping')
      this.$http
        .post('/verify-otp.json', JSON.stringify(data))
        .then((resp) => {
          this.loading = false
          if (!resp.data) {
            // this.snack(resp.data.message, 'error')
            return
          }
          this.$router.push('/login')
        })
        .catch((err) => {
          this.loading = false
          //   this.snack('A network error occured', 'error')
          alert('We run into an error. Please check the credentials. ' + err)
        })
    },
    resendOTP () {
      this.$http
        .post('/resend-otp.json', localStorage.getItem('shopper'))
        .then((resp) => {
          this.loading = false
          if (!resp.data) {
            // this.snack(resp.data.message, 'error')
            alert('We run into an error. Please reachout to admin')
            return
          }
          alert('OTP sent. Please check your phone.')
          var link = document.getElementById('resend-link')
          link.style.display = 'none'
          link.style.textDecoration = 'underline'
        })
        .catch((err) => {
          this.loading = false
          //  TODO: Please tell them to apply for a new OTP.
          alert('We run into an error. Please check the credentials. ' + err)
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
