<template>
  <div>
    <h2 class="mb-4 display-6">🛒 Корзина</h2>

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
            <td style="width: 120px;">
              <input type="number" v-model.number="item.quantity" @change="updateQuantityHandler(item.id, item.quantity)" class="form-control form-control-sm">
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
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="d-flex justify-content-between gap-3 mt-4">
      <router-link to="/" class="btn btn-outline-secondary btn-lg">← Продолжить выбор</router-link>
      <button @click="goToOrder" class="btn btn-primary btn-lg px-4" :disabled="cartItems.length === 0">Оформить заявку</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../composables/useCart'

const router = useRouter()
const { cart, total, updateQuantity, removeItem } = useCart()

// Получаем массив корзины (если cart это ref)
const cartItems = computed(() => {
  if (cart && typeof cart === 'object' && 'value' in cart) {
    return cart.value || []
  }
  return Array.isArray(cart) ? cart : []
})

const cartTotal = computed(() => {
  if (total && typeof total === 'object' && 'value' in total) {
    return total.value || 0
  }
  return typeof total === 'number' ? total : 0
})

const updateQuantityHandler = (id, qty) => {
  updateQuantity(id, qty)
}

const removeItemHandler = (id) => {
  removeItem(id)
}

const goToOrder = () => router.push('/order')
</script>