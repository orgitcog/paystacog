<template>
  <div class="cart">
    <div class="header">
      <h2>Shopping</h2>
    </div>
    <p class="panel">
      Please add items by clicking the <b> Add button "+"</b> then checkout on the right panel.
    </p>
    <div class="itemlist">
      <div class="itemlist__header">
        <div>Product</div>
        <div>Unit Price</div>
        <div>Quantity</div>
        <div>Sub total</div>
      </div>
      <div class="itemlist__body" v-for="(gift, index) in gifts" :key="index">
        <div class="item__content">
          <div class="item__image">
            <img :src="gift.image" />
          </div>
          <div class="item__description">
            <h4>{{ gift.name }}</h4>
            <span>Size: {{ gift.size }}</span>
            <span>Color: {{ gift.color }}</span>
          </div>
        </div>
        <div class="item__price">
          <span>{{ parseCurrency(gift.price) }}</span>
        </div>
        <div class="item__quantity">
          <div class="qty-wrapper">
            <span title="Remove an item" class="qty-wrapper__button" @click="reduceQuantity(gift.id)"
              >&ndash;</span
            >
            <span title="Add an Item" class="qty-wrapper__value">{{ gift.quantity }}</span>
            <span class="qty-wrapper__button" @click="increaseQuantity(gift.id)"
              >+</span
            >
          </div>
        </div>
        <div>
          {{ calculateUnitTotal(index) }}
        </div>
      </div>
      <button id='btnProceed' @click="toCheckout">
        Proceed
      </button>
    </div>
    <footer class="support">
      <p>
        Need help? Please reach out at <a
        href='mailto:hello@paystack.com?cc=andrew@paystack.com&subject=Paystack Sample Store'>hello@paystack.com</a>
      </p>
      <p>
        Call us on: <a href='tel:+233591566205'> +233 5915 66205 </a>
      </p>
      <p>
        Social:
        <a href="https:///www.twitter.com/paystack"> Twitter</a>
        ||
        <a href="https://www.facebook.com/PaystackHQ/">
          Facebook
        </a>
      </p>
      <address>Paystack Ghana, <br>
        <a href="https://goo.gl/maps/rs11Aig5Lm9hW6898">
           ComUnity_Spaces, <br>
        </a>
        Nikoi St,
        East Legon
      </address>
    </footer>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Cart',
  computed: {
    ...mapGetters('cart', {
      gifts: 'cartProducts'
    })
  },
  methods: {
    increaseQuantity (id) {
      this.$store.commit('cart/incrementGiftQuantity', id)
    },
    reduceQuantity (id) {
      this.$store.commit('cart/decrementGiftQuantity', id)
    },
    calculateUnitTotal (index) {
      return this.parseCurrency(
        this.gifts[index].price * this.gifts[index].quantity
      )
    },
    toCheckout () {
      this.$router.push('/checkout')
    },
    parseCurrency (amount) {
      return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'GHS'
      }).format(amount)
    }
  }
}
</script>

<style lang="scss" scoped>
.cart {
  .header {
    margin-bottom: 40px;
  }
}

footer {
  position: relative;
  left: auto;
  bottom: 0;
}

address {
    position: relative;
    right: 0;
    bottom: 0;
  }
.itemlist {
  margin-bottom: 36px;
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
.panel {
  margin-top: 15px;
  margin-bottom: 10;
  border-radius: 4px;
  padding: 14px;
  padding-top: 24px;
  border-color: #3bb75e !important;
  background-color: #fff;
  border: 1px solid transparent;
  box-shadow: 0 1px 1px;
  box-sizing: border-box;
  display: block;
  width: 60%;
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
#btnProceed {
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
</style>
