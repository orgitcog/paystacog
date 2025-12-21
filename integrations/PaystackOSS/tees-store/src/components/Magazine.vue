<template>
  <div class="cart">
    <div class="header">
      <h2>Daily Savings Plan</h2>
    </div>
    <div class="itemlist">
      <div class="itemlist__header">
        <div>Product</div>
        <div>Description</div>
        <div>Price</div>
      </div>
      <div class="itemlist__body" v-for="(magazine, index) in magazines" :key="index">
        <div class="item__content">
          <div class="item__image">
            <img :src="magazine.image" />
          </div>
          <div class="item__description">
            <h4>{{ magazine.name }}</h4>
          </div>
        </div>
        <div class="item__content">
          <div class="item__description">
            <h4>{{ magazine.description }}</h4>
          </div>
        </div>
        <div class="item__price">
          <span>{{ parseCurrency(magazine.price) }}</span>
        </div>
        <div>
          <div class="receipt">
            <div class="item__checkout">
              <div class="form-item">
                <label>Mobile Money number</label>
                <input v-model="momo" />
              </div>
              <button @click="makePayment">Subscribe</button>
            </div>
          </div>
          <!-- {{ calculateUnitTotal(index) }} -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Magazine',
  data () {
    return {
      momo: '',
      loading: false
    }
  },
  computed: {
    ...mapGetters('magazine', {
      magazines: 'cartProducts',
      price: 'cartTotalPrice'
    }),
    total () {
      return this.price
    }
  },
  methods: {
    parseCurrency (amount) {
      return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'GHS'
      }).format(amount)
    },
    makePayment () {
      const data = {
        email: this.email,
        amount: 2.0,
        refNo: this.randomRef(),
        phone: this.momoFormat(),
        frequency: 1,
        startDate: '2020-07-27',
        endDate: '2020-08-27',
        network: 'MTN'
      }

      this.$http.post('/mandates.json', JSON.stringify(data)).then((resp) => {
        // TODO: Create Instruction box or show success message.
        // console.log(resp.data)
        alert('Transaction Successful')
      })
      // console.log('paid' + this.price)
    },
    momoFormat () {
      if (this.momo.charAt(0) === '0') {
        return this.momo.replace('0', '233')
      } else {
        return this.momo
      }
    },
    randomRef () {
      return (
        'PYSTCK-SUB ' +
        ((Math.random() * (10024 - 1024) + 1024) * 10000).toFixed(0)
      )
    }
  }
}
</script>
<style lang="scss" scoped>
$gray: #f2f5f7;
.cart {
  .header {
    margin-bottom: 50px;
  }
}
.receipt {
  display: flex;
  flex-direction: column;

  &__form {
    width: 100%;
    margin-bottom: 48px;
  }

  .header {
    margin-bottom: 50px;
  }

  &__items {
    border-top: 1px dashed #ececec;
    padding-top: 30px;
    margin-bottom: 30px;
  }
}
.receipt-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;

  span:first-child {
    margin-right: 24px;
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
  &__checkout {
    button {
      width: 100%;
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
.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 24px;

  label {
    margin-bottom: 8px;
    font-weight: 500;
  }

  input,
  textarea {
    font-size: 14px;
    color: #737575;
    padding: 10px;
    border: 1px solid $gray;
    box-sizing: border-box;
    box-shadow: 0px 1px 1px rgba(0, 0, 0, 0.03);
    border-radius: 6px;

    &:focus {
      border: 1px solid rgba(130, 130, 130, 0.2);
      outline: none;
    }
  }

  textarea {
    height: 80px;
    resize: none;
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
