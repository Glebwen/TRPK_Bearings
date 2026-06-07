<template>
  <div class="orders-container">
    <!-- Заголовок -->
    <div class="page-header">
      <h1 class="page-title">Управление заявками</h1>
      <div class="header-actions">
        <button class="btn-refresh" @click="fetchOrders">
          <span class="refresh-icon">🔄</span> Обновить
        </button>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filters-card">
      <div class="filters-grid">
        <div class="filter-group">
          <label>Статус</label>
          <select v-model="filters.status_id" class="filter-select" @change="applyFilters">
            <option value="">Все статусы</option>
            <option v-for="status in statuses" :key="status.id" :value="status.id">
              {{ status.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Email клиента</label>
          <input 
            type="text" 
            v-model="filters.customer_email" 
            placeholder="Поиск по email"
            class="filter-input"
            @input="applyFiltersDebounced"
          >
        </div>

        <div class="filter-group">
          <label>Номер заявки</label>
          <input 
            type="text" 
            v-model="filters.order_number" 
            placeholder="B000001"
            class="filter-input"
            @input="applyFiltersDebounced"
          >
        </div>

        <div class="filter-group">
          <label>Дата с</label>
          <input type="date" v-model="filters.date_from" class="filter-input" @change="applyFilters">
        </div>

        <div class="filter-group">
          <label>Дата по</label>
          <input type="date" v-model="filters.date_to" class="filter-input" @change="applyFilters">
        </div>

        <div class="filter-group filter-actions">
          <button class="btn-clear" @click="clearFilters">Сбросить</button>
        </div>
      </div>
    </div>

    <!-- Таблица заявок -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="orders-table">
          <thead>
            <tr>
              <th>№ заявки</th>
              <th>Клиент</th>
              <th>Email</th>
              <th>Статус</th>
              <th>Сумма</th>
              <th>Товаров</th>
              <th>Кол-во</th>
              <th>Дата создания</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.order_number">
              <td class="order-number">{{ order.order_number }}</td>
              <td>{{ order.customer_name }}</td>
              <td>{{ order.customer_email }}</td>
              <td>
                <span :class="['status-badge', getStatusClass(order.status_name)]">
                  {{ order.status_name }}
                </span>
              </td>
              <td class="price-cell">{{ formatPrice(order.total_amount) }} ₽</td>
              <td class="center">{{ order.items_count }}</td>
              <td class="center">{{ order.total_quantity }}</td>
              <td>{{ formatDate(order.created_at) }}</td>
              <td class="actions-cell">
                <button class="btn-view" @click="viewOrderDetail(order.order_number)">
                  Подробнее
                </button>
              </td>
            </tr>
            <tr v-if="orders.length === 0 && !loading">
              <td colspan="9" class="empty-state">
                <div class="empty-icon">📋</div>
                <p>Заявок не найдено</p>
              </td>
            </tr>
            <tr v-if="loading">
              <td colspan="9" class="loading-state">
                <div class="spinner"></div>
                <p>Загрузка заявок...</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Пагинация -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1" 
          @click="changePage(currentPage - 1)"
        >
          ←
        </button>
        <div class="page-numbers">
          <button 
            v-for="page in displayedPages" 
            :key="page"
            :class="['page-btn', { active: page === currentPage }]"
            @click="changePage(page)"
          >
            {{ page }}
          </button>
        </div>
        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages" 
          @click="changePage(currentPage + 1)"
        >
          →
        </button>
      </div>
    </div>

    <!-- Модальное окно деталей заявки -->
    <div v-if="selectedOrder" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Заявка {{ selectedOrder.order_number }}</h2>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <!-- Информация о клиенте -->
          <div class="info-section">
            <h3>Информация о клиенте</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">ФИО:</span>
                <span>{{ selectedOrder.customer.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">Организация:</span>
                <span>{{ selectedOrder.customer.organization || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Телефон:</span>
                <span>{{ selectedOrder.customer.phone }}</span>
              </div>
              <div class="info-item">
                <span class="label">Email:</span>
                <span>{{ selectedOrder.customer.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">Адрес доставки:</span>
                <span>{{ selectedOrder.delivery_address || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Статус (с возможностью изменения) -->
          <div class="info-section">
            <h3>Статус заявки</h3>
            <div class="status-update">
              <div class="current-status">
                <span class="status-label">Текущий статус:</span>
                <span :class="['status-badge', getStatusClass(selectedOrder.status_name)]">
                  {{ selectedOrder.status_name }}
                </span>
              </div>
              <div class="status-change">
                <select v-model="newStatusId" class="status-select" @change="updateStatus">
                  <option value="">Изменить статус</option>
                  <option v-for="status in statuses" :key="status.id" :value="status.id">
                    {{ status.name }}
                  </option>
                </select>
                <button 
                  v-if="newStatusId" 
                  class="btn-confirm" 
                  @click="confirmStatusChange"
                  :disabled="updatingStatus"
                >
                  {{ updatingStatus ? 'Сохранение...' : 'Подтвердить' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Товары -->
          <div class="info-section">
            <h3>Состав заявки</h3>
            <table class="items-table">
              <thead>
                <tr>
                  <th>Артикул</th>
                  <th>Наименование</th>
                  <th>Количество</th>
                  <th>Цена</th>
                  <th>Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in selectedOrder.items" :key="item.id">
                  <td>{{ item.bearing_article }}</td>
                  <td>{{ item.bearing_name }}</td>
                  <td class="center">{{ item.quantity }}</td>
                  <td class="price-cell">{{ formatPrice(item.price_at_order) }} ₽</td>
                  <td class="price-cell">{{ formatPrice(item.quantity * item.price_at_order) }} ₽</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="4" class="total-label">Итого:</td>
                  <td class="total-price">{{ formatPrice(selectedOrder.total_amount) }} ₽</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'OrdersManagement',
  setup() {
    // Состояние
    const orders = ref([])
    const statuses = ref([])
    const loading = ref(false)
    const updatingStatus = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const selectedOrder = ref(null)
    const newStatusId = ref('')

    // Фильтры
    const filters = reactive({
      status_id: '',
      customer_email: '',
      order_number: '',
      date_from: '',
      date_to: ''
    })

    // API базовый URL
    const API_BASE_URL = 'http://localhost:8000/api/v1' // Замените на ваш URL

    // Методы
    const fetchOrders = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          ...filters
        }
        // Удаляем пустые параметры
        Object.keys(params).forEach(key => {
          if (!params[key]) delete params[key]
        })

        const response = await axios.get(`${API_BASE_URL}/orders/list/`, { params })
        
        // Если API возвращает пагинированный ответ
        if (response.data.results) {
          orders.value = response.data.results
          totalPages.value = Math.ceil(response.data.count / 20)
        } else {
          orders.value = response.data
          totalPages.value = 1
        }
      } catch (error) {
        console.error('Ошибка при загрузке заявок:', error)
        alert('Не удалось загрузить заявки')
      } finally {
        loading.value = false
      }
    }

    const fetchStatuses = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/order-statuses/`)
        statuses.value = response.data
      } catch (error) {
        console.error('Ошибка при загрузке статусов:', error)
      }
    }

    const viewOrderDetail = async (orderNumber) => {
      try {
        const response = await axios.get(`${API_BASE_URL}/orders/detail/${orderNumber}/`)
        selectedOrder.value = response.data
        newStatusId.value = ''
      } catch (error) {
        console.error('Ошибка при загрузке деталей заявки:', error)
        alert('Не удалось загрузить детали заявки')
      }
    }

    const confirmStatusChange = () => {
      if (confirm(`Изменить статус с "${selectedOrder.value.status_name}" на "${getStatusName(newStatusId.value)}"?`)) {
        updateStatus()
      }
    }

    const updateStatus = async () => {
      if (!newStatusId.value || !selectedOrder.value) return

      updatingStatus.value = true
      try {
        await axios.patch(`${API_BASE_URL}/orders/${selectedOrder.value.order_number}/update-status/`, {
          status_id: parseInt(newStatusId.value)
        })
        
        // Обновляем статус в текущем выбранном заказе
        const newStatus = statuses.value.find(s => s.id === parseInt(newStatusId.value))
        if (newStatus) {
          selectedOrder.value.status_name = newStatus.name
        }
        
        alert('Статус успешно обновлён')
        newStatusId.value = ''
        
        // Обновляем список заявок
        await fetchOrders()
      } catch (error) {
        console.error('Ошибка при обновлении статуса:', error)
        alert('Не удалось обновить статус')
      } finally {
        updatingStatus.value = false
      }
    }

    const getStatusName = (statusId) => {
      const status = statuses.value.find(s => s.id === parseInt(statusId))
      return status ? status.name : ''
    }

    const closeModal = () => {
      selectedOrder.value = null
      newStatusId.value = ''
    }

    const applyFilters = () => {
      currentPage.value = 1
      fetchOrders()
    }

    let debounceTimeout
    const applyFiltersDebounced = () => {
      clearTimeout(debounceTimeout)
      debounceTimeout = setTimeout(() => {
        applyFilters()
      }, 500)
    }

    const clearFilters = () => {
      filters.status_id = ''
      filters.customer_email = ''
      filters.order_number = ''
      filters.date_from = ''
      filters.date_to = ''
      applyFilters()
    }

    const changePage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchOrders()
    }

    const formatPrice = (price) => {
      return new Intl.NumberFormat('ru-RU').format(price)
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU')
    }

    const getStatusClass = (statusName) => {
      const classes = {
        'Принята': 'status-new',
        'В обработке': 'status-processing',
        'Отгружена': 'status-shipped',
        'Отменена': 'status-cancelled'
      }
      return classes[statusName] || 'status-default'
    }

    const displayedPages = computed(() => {
      const delta = 2
      const range = []
      const rangeWithDots = []
      let l

      for (let i = 1; i <= totalPages.value; i++) {
        if (i === 1 || i === totalPages.value || (i >= currentPage.value - delta && i <= currentPage.value + delta)) {
          range.push(i)
        }
      }

      range.forEach((i) => {
        if (l) {
          if (i - l === 2) {
            rangeWithDots.push(l + 1)
          } else if (i - l !== 1) {
            rangeWithDots.push('...')
          }
        }
        rangeWithDots.push(i)
        l = i
      })

      return rangeWithDots
    })

    onMounted(() => {
      fetchStatuses()
      fetchOrders()
    })

    return {
      orders,
      statuses,
      loading,
      updatingStatus,
      currentPage,
      totalPages,
      selectedOrder,
      newStatusId,
      filters,
      fetchOrders,
      viewOrderDetail,
      updateStatus,
      confirmStatusChange,
      closeModal,
      applyFilters,
      applyFiltersDebounced,
      clearFilters,
      changePage,
      formatPrice,
      formatDate,
      getStatusClass,
      displayedPages
    }
  }
}
</script>

<style scoped>
.orders-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.btn-refresh {
  padding: 8px 16px;
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background-color: #edf2f7;
}

.filters-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 6px;
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.btn-clear {
  padding: 8px 16px;
  background-color: #edf2f7;
  border: none;
  border-radius: 8px;
  color: #4a5568;
  cursor: pointer;
  font-size: 14px;
}

.btn-clear:hover {
  background-color: #e2e8f0;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table thead {
  background-color: #f7fafc;
  border-bottom: 2px solid #e2e8f0;
}

.orders-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.orders-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #edf2f7;
  color: #4a5568;
  font-size: 14px;
}

.orders-table tbody tr {
  transition: background-color 0.2s;
}

.orders-table tbody tr:hover {
  background-color: #f7fafc;
}

.order-number {
  font-weight: 600;
  color: #2b6cb0;
}

.center {
  text-align: center;
}

.price-cell {
  font-weight: 500;
  color: #2d3748;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-new {
  background-color: #fefcbf;
  color: #975a16;
}

.status-processing {
  background-color: #bee3f8;
  color: #2c5282;
}

.status-shipped {
  background-color: #c6f6d5;
  color: #22543d;
}

.status-cancelled {
  background-color: #fed7d7;
  color: #742a2a;
}

.status-default {
  background-color: #e2e8f0;
  color: #4a5568;
}

.actions-cell {
  text-align: center;
}

.btn-view {
  padding: 4px 12px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s;
}

.btn-view:hover {
  background-color: #3182ce;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 60px !important;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 4px solid #e2e8f0;
  border-top-color: #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 20px;
  border-top: 1px solid #e2e8f0;
}

.page-btn {
  padding: 8px 12px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 36px;
}

.page-btn:hover:not(:disabled) {
  background-color: #edf2f7;
}

.page-btn.active {
  background-color: #4299e1;
  color: white;
  border-color: #4299e1;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1a202c;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #a0aec0;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #4a5568;
}

.modal-body {
  padding: 24px;
}

.info-section {
  margin-bottom: 32px;
}

.info-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  gap: 8px;
}

.info-item .label {
  font-weight: 500;
  color: #718096;
  min-width: 100px;
}

.status-update {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.current-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-label {
  font-weight: 500;
  color: #4a5568;
}

.status-change {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  min-width: 200px;
}

.btn-confirm {
  padding: 8px 20px;
  background-color: #48bb78;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-confirm:hover:not(:disabled) {
  background-color: #38a169;
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
}

.items-table th {
  text-align: left;
  padding: 10px 12px;
  background-color: #f7fafc;
  font-weight: 600;
  font-size: 14px;
}

.items-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #edf2f7;
}

.items-table tfoot td {
  font-weight: 600;
  padding-top: 16px;
}

.total-label {
  text-align: right;
  font-weight: 600;
}

.total-price {
  font-weight: 700;
  font-size: 18px;
  color: #2b6cb0;
}
</style>