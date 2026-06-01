<template>
  <div>
    <h1 class="mb-4 display-5">Каталог подшипников</h1>


    <div class="card shadow-sm mb-5">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-2">
            <label class="form-label fw-semibold">Тип</label>
            <select v-model="filters.type_id" class="form-select">
              <option :value="null">Все типы</option>
              <option v-for="t in dictionaries.types" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-semibold">Производитель</label>
            <select v-model="filters.manufacturer_id" class="form-select">
              <option :value="null">Все производители</option>
              <option v-for="m in dictionaries.manufacturers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-semibold">Материал</label>
            <select v-model="filters.material_id" class="form-select">
              <option :value="null">Все материалы</option>
              <option v-for="m in dictionaries.materials" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-semibold">Уплотнение</label>
            <select v-model="filters.seal_type_id" class="form-select">
              <option :value="null">Все типы</option>
              <option v-for="s in dictionaries.seal_types" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-semibold">Класс точности</label>
            <select v-model="filters.precision_class_id" class="form-select">
              <option :value="null">Все классы</option>
              <option v-for="p in dictionaries.precision_classes" :key="p.id" :value="p.id">{{ p.code }}</option>
            </select>
          </div>
        </div>

        <div class="row g-3 align-items-end mt-2">

          <div class="col-md-2">
            <label class="form-label fw-semibold">Внутр. диам. (мм)</label>
            <div class="d-flex gap-2">
              <input type="number" v-model.number="filters.inner_diameter_min" class="form-control" placeholder="от">
              <input type="number" v-model.number="filters.inner_diameter_max" class="form-control" placeholder="до">
            </div>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-semibold">Наруж. диам. (мм)</label>
            <div class="d-flex gap-2">
              <input type="number" v-model.number="filters.outer_diameter_min" class="form-control" placeholder="от">
              <input type="number" v-model.number="filters.outer_diameter_max" class="form-control" placeholder="до">
            </div>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-semibold">Высота (мм)</label>
            <div class="d-flex gap-2">
              <input type="number" v-model.number="filters.height_min" class="form-control" placeholder="от">
              <input type="number" v-model.number="filters.height_max" class="form-control" placeholder="до">
            </div>
          </div>

          <div class="col-md-4">
            <label class="form-label fw-semibold">🔍 Поиск по названию</label>
            <input v-model="search" class="form-control" placeholder="Начните вводить..." @keyup.enter="applyFilters">
          </div>

          <div class="col-md-2">
            <button @click="applyFilters" class="btn btn-primary w-100 fw-semibold mb-2">Показать</button>
            <button @click="resetFilters" class="btn btn-outline-secondary w-100">Сбросить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="p in products" :key="p.id" class="col">
        <div class="card h-100 shadow-sm border-0 rounded-4 overflow-hidden">
          <img :src="p.image || 'https://placehold.co/400x200?text=Нет+фото'" class="card-img-top" style="height: 200px; object-fit: contain; background: #f8f9fa;">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ p.name }}</h5>
            <p class="card-text text-secondary">
              <span class="badge bg-secondary me-1">{{ p.article }}</span><br>
              <span class="badge bg-info me-1">{{ p.type_name }}</span>
              <span class="badge bg-light text-dark">{{ p.manufacturer_name }}</span><br>
              💰 <strong>{{ p.price.toLocaleString() }} руб.</strong><br>
              📦 Остаток: {{ p.stock_quantity }} шт.
            </p>
            <router-link :to="'/product/' + p.id" class="btn btn-sm btn-outline-primary w-100 mt-2">📖 Подробнее</router-link>
          </div>
        </div>
      </div>
      <div v-if="products.length === 0" class="col-12 text-center text-muted py-5">
        <h3>Нет товаров по выбранным критериям</h3>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { useCart } from '../composables/useCart'

const { addToCart } = useCart()

const products = ref([])
const search = ref('')
const filters = reactive({
  type_id: null,
  manufacturer_id: null,
  material_id: null,
  seal_type_id: null,
  precision_class_id: null,
  inner_diameter_min: null,
  inner_diameter_max: null,
  outer_diameter_min: null,
  outer_diameter_max: null,
  height_min: null,
  height_max: null
})
const quantities = ref({})

const dictionaries = ref({
  types: [],
  manufacturers: [],
  materials: [],
  seal_types: [],
  precision_classes: []
})

const loadDictionaries = async () => {
  try {
    const typesRes = await axios.get('/api/v1/dictionaries/types/')
    dictionaries.value.types = typesRes.data
    
    const manufacturersRes = await axios.get('/api/v1/dictionaries/manufacturers/')
    dictionaries.value.manufacturers = manufacturersRes.data
    
    const materialsRes = await axios.get('/api/v1/dictionaries/materials/')
    dictionaries.value.materials = materialsRes.data
    
    const sealTypesRes = await axios.get('/api/v1/dictionaries/seal-types/')
    dictionaries.value.seal_types = sealTypesRes.data
    
    const precisionRes = await axios.get('/api/v1/dictionaries/precision-classes/')
    dictionaries.value.precision_classes = precisionRes.data
  } catch (err) {
    console.error('Ошибка загрузки справочников:', err)
  }
}

const loadProducts = async () => {
  try {
    const params = {
      search: search.value,
      ...filters
    }
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined || params[key] === '') {
        delete params[key]
      }
    })
    const res = await axios.get('/api/v1/bearings/', { params })
    products.value = res.data
    products.value.forEach(p => {
      if (!quantities.value[p.id]) quantities.value[p.id] = 1
    })
  } catch (err) {
    console.error('Ошибка загрузки товаров:', err)
  }
}

const applyFilters = () => {
  loadProducts()
}

const resetFilters = () => {
  filters.type_id = null
  filters.manufacturer_id = null
  filters.material_id = null
  filters.seal_type_id = null
  filters.precision_class_id = null
  filters.inner_diameter_min = null
  filters.inner_diameter_max = null
  filters.outer_diameter_min = null
  filters.outer_diameter_max = null
  filters.height_min = null
  filters.height_max = null
  search.value = ''
  loadProducts()
}

onMounted(async () => {
  await loadDictionaries()
  await loadProducts()
})
</script>