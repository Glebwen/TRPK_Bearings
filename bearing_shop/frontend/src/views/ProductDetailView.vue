<template>
  <div v-if="product" class="row g-5">
    <div class="col-md-5 text-center">
      <img :src="product.image || 'https://placehold.co/500x400?text=Нет+фото'" class="img-fluid rounded-4 shadow" style="max-height: 400px; object-fit: contain;">
    </div>
    <div class="col-md-7">
      <h1 class="display-6 fw-bold">{{ product.name }}</h1>
      <p class="badge bg-dark fs-6 mt-2">{{ product.article }}</p>

      <table class="table table-bordered mt-4 bg-white">
        <tr><th style="width: 40%">Тип</th><td>{{ product.type_name }}</td></tr>
        <tr><th>Внутренний диаметр</th><td>{{ product.inner_diameter }} мм</td></tr>
        <tr><th>Наружный диаметр</th><td>{{ product.outer_diameter }} мм</td></tr>
        <tr><th>Высота</th><td>{{ product.height }} мм</td></tr>
        <tr><th>Материал</th><td>{{ product.material_name || 'подшипниковая сталь' }}</td></tr>
        <tr><th>Класс точности</th><td>{{ product.precision_class_code }}</td></tr>
      </table>

      <div class="alert alert-primary d-flex justify-content-between align-items-center">
        <span class="fs-3 fw-bold">{{ product.price.toLocaleString() }} руб.</span>
        <span class="badge bg-success fs-6">в наличии: {{ product.stock_quantity }} шт.</span>
      </div>

      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
        <strong>⚠️ Ошибка!</strong> {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <div class="row g-2 mt-3">
        <div class="col-4">
          <input 
            type="number" 
            v-model.number="quantity" 
            :min="minQuantity" 
            :max="product.stock_quantity" 
            class="form-control form-control-lg"
            :class="{ 'is-invalid': quantityError }"
            @input="validateQuantity">
        </div>
        <div class="col-8">
          <button 
            @click="addToCartHandler" 
            class="btn btn-success btn-lg w-100"
            :disabled="!canAddToCart">
            🛒 Добавить в корзину
          </button>
        </div>
      </div>
      <div class="mt-3">
        <router-link to="/" class="btn btn-outline-secondary w-100">← Назад в каталог</router-link>
      </div>

      <div v-if="product.docs && product.docs.length" class="mt-5">
        <h4 class="mb-3">📄 Техническая документация</h4>
        <div class="list-group">
          <div v-for="doc in product.docs" :key="doc.id" class="list-group-item d-flex justify-content-between align-items-center">
            <span>{{ doc.file_name }}</span>
            <button @click="downloadFile(doc)" class="btn btn-sm btn-primary">
              ⬇️ Скачать
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center py-5">
    <div class="spinner-border text-primary" role="status"></div>
    <p class="mt-2">Загрузка...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useCart } from '../composables/useCart'

const route = useRoute()
const { addToCart } = useCart()
const product = ref(null)
const quantity = ref(0)
const errorMessage = ref('')
const quantityError = ref(false)

const minQuantity = computed(() => 0)

const canAddToCart = computed(() => {
  return product.value && 
         quantity.value > 0 && 
         quantity.value <= product.value.stock_quantity &&
         product.value.stock_quantity > 0
})

const validateQuantity = () => {
  quantityError.value = false
  errorMessage.value = ''
  
  if (quantity.value < 0) {
    quantity.value = 0
  }
  
  if (product.value && quantity.value > product.value.stock_quantity) {
    quantityError.value = true
    errorMessage.value = `Нельзя добавить больше ${product.value.stock_quantity} шт. (остаток на складе)`
  }
}

const addToCartHandler = () => {
  if (!product.value) return
  
  if (product.value.stock_quantity <= 0) {
    errorMessage.value = 'Товар отсутствует на складе. Добавление в корзину невозможно.'
    return
  }
  
  if (quantity.value <= 0) {
    errorMessage.value = 'Укажите количество больше 0'
    return
  }
  
  if (quantity.value > product.value.stock_quantity) {
    errorMessage.value = `Нельзя добавить больше ${product.value.stock_quantity} шт. (остаток на складе)`
    return
  }
  
  addToCart(product.value, quantity.value)
  errorMessage.value = ''
  
  const successMsg = document.createElement('div')
  successMsg.className = 'alert alert-success alert-dismissible fade show mt-3'
  successMsg.innerHTML = `
    <strong>✓ Успешно!</strong> Товар добавлен в корзину (${quantity.value} шт.)
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `
  document.querySelector('.alert-primary')?.insertAdjacentElement('afterend', successMsg)
  
  setTimeout(() => {
    successMsg.remove()
  }, 3000)
}

const downloadFile = async (doc) => {
  try {
    let fileUrl = doc.file_url || doc.file
    
    if (!fileUrl) {
      alert('URL файла не найден')
      return
    }
    
    if (fileUrl.startsWith('/')) {
      fileUrl = `http://localhost:8000${fileUrl}`
    }
    
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = doc.file_name || 'document'
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    console.error('Ошибка скачивания:', err)
    alert('Не удалось скачать файл. Попробуйте позже.')
  }
}

watch(quantity, () => {
  validateQuantity()
})

onMounted(async () => {
  try {
    const res = await axios.get(`/api/v1/bearings/${route.params.id}/`)
    product.value = res.data
    
    if (product.value.stock_quantity > 0) {
      quantity.value = 1
    } else {
      quantity.value = 0
    }
  } catch (err) {
    console.error(err)
    alert('Не удалось загрузить товар')
  }
})
</script>

<style scoped>
.list-group-item {
  transition: all 0.2s ease;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.btn-primary {
  min-width: 100px;
}
</style>
