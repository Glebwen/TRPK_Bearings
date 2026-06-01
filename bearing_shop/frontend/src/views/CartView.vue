<template>
  <div>
    <h2 class="mb-4 display-6">🛒 Корзина</h2>

    <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>⚠️ Ошибка!</strong> {{ errorMessage }}
      <button type="button" class="btn-close" @click="errorMessage = ''"></button>
    </div>

    <div class="table-responsive">
      <table class="table table-bordered table-hover shadow-sm bg-white">
        <thead class="table-dark">
          <tr>
            <th>Наименование</th>
            <th>Артикул</th>
            <th>Цена</th>
            <th>Количество</th>
            <th>Сумма</th>
            <th>Действие</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in cartItems" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.article }}</td>
            <td>{{ item.price.toLocaleString() }} руб.</td>
            <td style="width: 150px;">
              <input 
                type="number" 
                v-model.number="item.quantity" 
                @change="validateAndUpdate(item.id, item.quantity)" 
                class="form-control form-control-sm"
                :class="{ 'is-invalid': quantityErrors[item.id] }"
                :min="1"
                :max="item.maxStock">
              <div v-if="quantityErrors[item.id]" class="invalid-feedback">
                {{ quantityErrors[item.id] }}
              </div>
            </td>
            <td>{{ (item.price * item.quantity).toLocaleString() }} руб.</td>
            <td><button @click="removeItemHandler(item.id)" class="btn btn-sm btn-danger">🗑 Удалить</button></td>
          </tr>
          <tr v-if="cartItems.length === 0">
            <td colspan="6" class="text-center text-muted py-4">Ваша корзина пуста</td>
          </tr>
        </tbody>
        <tfoot v-if="cartItems.length > 0" class="table-group-separator">
          <tr class="table-active">
            <th colspan="4" class="text-end fs-5">Итого:</th>
            <th class="fs-5">{{ cartTotal.toLocaleString() }} руб.</th>
            <th></th>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="d-flex justify-content-between gap-3 mt-4">
      <router-link to="/" class="btn btn-outline-secondary btn-lg">← Продолжить выбор</router-link>
      <button @click="goToOrder" class="btn btn-primary btn-lg px-4" :disabled="cartItems.length === 0">
        📋 Оформить заявку
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useCart } from '../composables/useCart'

const router = useRouter()
const { cart, total, updateQuantity, removeItem } = useCart()
const errorMessage = ref('')
const quantityErrors = ref({})

const loadStockQuantities = async () => {
  const cartArray = cartItems.value
  for (const item of cartArray) {
    try {
      const res = await axios.get(`/api/v1/bearings/${item.id}/`)
      item.maxStock = res.data.stock_quantity
    } catch (err) {
      console.error('Ошибка загрузки остатка для', item.article, err)
    }
  }
}

const cartItems = computed(() => {
  let items = []
  if (cart && typeof cart === 'object' && 'value' in cart) {
    items = cart.value || []
  } else if (Array.isArray(cart)) {
    items = cart
  }
  return items.map(item => ({
    ...item,
    maxStock: item.maxStock || Infinity
  }))
})

const cartTotal = computed(() => {
  if (total && typeof total === 'object' && 'value' in total) {
    return total.value || 0
  }
  return typeof total === 'number' ? total : 0
})

const validateAndUpdate = async (id, newQuantity) => {
  quantityErrors.value[id] = null
  errorMessage.value = ''
  
  if (newQuantity <= 0) {
    removeItemHandler(id)
    return
  }
  
  try {
    const res = await axios.get(`/api/v1/bearings/${id}/`)
    const maxStock = res.data.stock_quantity
    
    if (newQuantity > maxStock) {
      quantityErrors.value[id] = `Нельзя заказать больше ${maxStock} шт. (остаток на складе)`
      const currentItem = cartItems.value.find(i => i.id === id)
      if (currentItem) {
        const index = cartItems.value.findIndex(i => i.id === id)
        if (index !== -1 && cart.value && cart.value[index]) {
          cart.value[index].quantity = currentItem.quantity
        }
      }
      return
    }
    
    updateQuantity(id, newQuantity)
    const item = cartItems.value.find(i => i.id === id)
    if (item) {
      item.maxStock = maxStock
    }
  } catch (err) {
    console.error('Ошибка проверки остатка:', err)
    errorMessage.value = 'Не удалось проверить остаток на складе'
  }
}

const updateQuantityHandler = (id, qty) => {
  validateAndUpdate(id, qty)
}

const removeItemHandler = (id) => {
  removeItem(id)
  quantityErrors.value[id] = null
}

const goToOrder = () => {
  if (cartItems.value.length === 0) {
    errorMessage.value = 'Корзина пуста'
    return
  }
  router.push('/order')
}

onMounted(async () => {
  await loadStockQuantities()
})
</script>

<style scoped>
.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  display: block;
  font-size: 0.75rem;
}
</style>