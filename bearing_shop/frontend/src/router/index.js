import { createRouter, createWebHistory } from 'vue-router'
import CatalogView from '../views/CatalogView.vue'
import ProductDetailView from '../views/ProductDetailView.vue'
import CartView from '../views/CartView.vue'
import OrderFormView from '../views/OrderFormView.vue'
import OrdersView from '../views/OrdersView.vue'

const routes = [
  { path: '/', name: 'catalog', component: CatalogView },
  { path: '/product/:id', name: 'product-detail', component: ProductDetailView },
  { path: '/cart', name: 'cart', component: CartView },
  { path: '/order', name: 'order', component: OrderFormView },
  {path: '/orders', name:'orders', component: OrdersView}
]

const router = createRouter({ history: createWebHistory(), routes })
export default router