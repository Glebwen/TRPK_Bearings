<template>
  <div class="row justify-content-center">
    <div class="col-lg-8">
      <h2 class="mb-4 display-6">📄 Оформление заявки</h2>
      <form @submit.prevent="submitOrder">
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-primary text-white fw-bold">Контактные данные</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label fw-semibold">ФИО *</label>
              <input v-model="form.name" type="text" class="form-control" required>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Организация (опционально)</label>
              <input v-model="form.organization" type="text" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Телефон * (+79xxxxxxxxx)</label>
              <input v-model="form.phone" type="tel" class="form-control" required placeholder="+79123456789">
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Email *</label>
              <input v-model="form.email" type="email" class="form-control" required>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Адрес доставки (опционально)</label>
              <textarea v-model="form.address" rows="2" class="form-control"></textarea>
            </div>
          </div>
        </div>

        <div class="card shadow-sm mb-4">
          <div class="card-header bg-secondary text-white fw-bold">Состав заказа</div>
          <div class="card-body p-0">
            <ul class="list-group list-group-flush">
              <li v-for="item in cartItems" :key="item.id" class="list-group-item d-flex justify-content-between align-items-center">
                {{ item.name }} x {{ item.quantity }}
                <span class="badge bg-primary rounded-pill">{{ (item.price * item.quantity).toLocaleString() }} руб.</span>
              </li>
              <li v-if="cartItems.length === 0" class="list-group-item text-center text-muted">
                Корзина пуста
              </li>
              <li v-if="cartItems.length > 0" class="list-group-item d-flex justify-content-between align-items-center fw-bold bg-light">
                Итого к оплате
                <span class="text-success fs-5">{{ cartTotal.toLocaleString() }} руб.</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="form-check mb-4">
          <input type="checkbox" class="form-check-input" v-model="agree" id="agreeCheck">
          <label class="form-check-label" for="agreeCheck">
            ✔ Я даю согласие на обработку персональных данных
          </label>
        </div>

        <div class="d-flex justify-content-between gap-3">
          <router-link to="/cart" class="btn btn-outline-secondary btn-lg">← Вернуться в корзину</router-link>
          <button type="submit" class="btn btn-success btn-lg px-5" :disabled="!agree || cartItems.length === 0">
            Отправить заявку
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useCart } from '../composables/useCart'

const router = useRouter()
const { cart, total, clearCart } = useCart()
const form = ref({ name: '', organization: '', phone: '', email: '', address: '' })
const agree = ref(false)

const cartItems = computed(() => {
  if (cart && typeof cart === 'object' && 'value' in cart) {
    return cart.value || []
  }
  if (Array.isArray(cart)) {
    return cart
  }
  return []
})

const cartTotal = computed(() => {
  if (total && typeof total === 'object' && 'value' in total) {
    return total.value || 0
  }
  if (typeof total === 'number') {
    return total
  }
  return 0
})

const submitOrder = async () => {
  const cartArray = cartItems.value
  
  if (cartArray.length === 0) {
    alert('Корзина пуста')
    return
  }

  const payload = {
    customer_name: form.value.name,
    customer_organization: form.value.organization,
    customer_phone: form.value.phone,
    customer_email: form.value.email,
    delivery_address: form.value.address,
    items: cartArray.map(i => ({ bearing_id: i.id, quantity: i.quantity }))
  }

  try {
    const res = await axios.post('/api/v1/orders/', payload)
    alert(`✅ Заявка №${res.data.order_number} успешно создана! Статус: ${res.data.status}`)
    clearCart()
    router.push('/')
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.error || 'Проверьте правильность заполнения полей.'
    alert('❌ Ошибка: ' + msg)
  }
}
</script>