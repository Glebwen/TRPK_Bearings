import { ref, computed } from 'vue'

const cart = ref([])

export function useCart() {
  const total = computed(() => {
    return cart.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  const loadCart = () => {
    const saved = localStorage.getItem('cart')
    if (saved) {
      try {
        cart.value = JSON.parse(saved)
      } catch (e) {
        console.warn('Ошибка загрузки корзины', e)
        cart.value = []
      }
    }
  }

  const saveCart = () => {
    localStorage.setItem('cart', JSON.stringify(cart.value))
  }

  const addToCart = (product, quantity) => {
    const existingIndex = cart.value.findIndex(item => item.id === product.id)
    
    if (existingIndex !== -1) {

      cart.value[existingIndex].quantity += quantity
    } else {
      cart.value.push({
        id: product.id,
        article: product.article,
        name: product.name,
        price: product.price,
        image_url: product.image_url || '',
        quantity: quantity
      })
    }
    saveCart()
  }

  const updateQuantity = (productId, quantity) => {
    const item = cart.value.find(i => i.id === productId)
    if (item) {
      if (quantity <= 0) {
        cart.value = cart.value.filter(i => i.id !== productId)
      } else {
        item.quantity = quantity
      }
      saveCart()
    }
  }

  const removeItem = (productId) => {
    cart.value = cart.value.filter(i => i.id !== productId)
    saveCart()
  }

  const clearCart = () => {
    cart.value = []
    localStorage.removeItem('cart')
  }

  loadCart()

  return { cart, total, addToCart, updateQuantity, removeItem, clearCart }
}