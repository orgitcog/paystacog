import magazines from '../../data/magazines.json'

const state = {
  magazines: magazines
}

const getters = {
  cartProducts: (state, getters) => {
    return state.magazines
  },

  cartTotalPrice: (state, getters) => {
    return getters.cartProducts.reduce((total, magazine) => {
      return magazine.price
    }, 0)
  }
}

export default {
  namespaced: true,
  state,
  getters
}
