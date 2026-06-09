<template>
    <AdminNavbar />
  <div class="page">

    <h1>Управление изображениями</h1>

    <div class="toolbar">
      <button @click="showModal = true">
        Загрузить изображение
      </button>
    </div>

    <table class="images-table">

      <thead>
        <tr>
          <th>Миниатюра</th>
          <th>Название файла</th>
          <th>Подшипник</th>
          <th>Дата загрузки</th>
          <th></th>
        </tr>
      </thead>

      <tbody>

        <tr
          v-for="item in images"
          :key="item.id"
        >
          <td>
            <img
              :src="item.image_url"
              class="preview"
              alt=""
            />
          </td>

          <td>
            {{ getFileName(item.image_url) }}
          </td>

          <td>
            {{ item.article }} - {{ item.name }}
          </td>

          <td>
            {{ formatDate(item.created_at) }}
          </td>

          <td>
            <button
              class="delete-btn"
              @click="deleteImage(item.id)"
            >
              Удалить
            </button>
          </td>

        </tr>

      </tbody>

    </table>

    <!-- Модальное окно -->

    <div
      v-if="showModal"
      class="modal-overlay"
    >

      <div class="modal">

        <h2>Загрузка изображения</h2>

        <div class="form-group">

          <label>Файл</label>

          <input
            type="file"
            accept=".jpg,.jpeg,.png"
            @change="onFileSelected"
          />

        </div>

        <div class="form-group">

          <label>Наименование подшипника</label>

          <select v-model="selectedBearing">

            <option value="">
              Выберите подшипник
            </option>

            <option
              v-for="bearing in bearings"
              :key="bearing.id"
              :value="bearing.id"
            >
              {{ bearing.article }} - {{ bearing.name }}
            </option>

          </select>

        </div>

        <div class="modal-actions">

          <button @click="uploadImage">
            Привязать
          </button>

          <button @click="showModal = false">
            Отмена
          </button>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

import AdminNavbar from "../components/AdminNavbar.vue"


const images = ref([])
const bearings = ref([])

const showModal = ref(false)

const selectedFile = ref(null)
const selectedBearing = ref("")

const loadImages = async () => {

  const response = await axios.get(
    "http://127.0.0.1:8000/api/v1/admin/images/"
  )

  images.value = response.data
}

const loadBearings = async () => {

  const response = await axios.get(
    "http://127.0.0.1:8000/api/v1/bearings/"
  )

  bearings.value = response.data.results || response.data
}

const onFileSelected = (event) => {

  selectedFile.value = event.target.files[0]
}

const uploadImage = async () => {

  if (!selectedFile.value) {
    alert("Выберите файл")
    return
  }

  if (!selectedBearing.value) {
    alert("Выберите подшипник")
    return
  }

  const formData = new FormData()

  formData.append(
    "image",
    selectedFile.value
  )

  formData.append(
    "bearing_id",
    selectedBearing.value
  )

  await axios.post(
    "http://127.0.0.1:8000/api/v1/admin/images/upload/",
    formData
  )

  showModal.value = false

  selectedFile.value = null
  selectedBearing.value = ""

  await loadImages()
}

const deleteImage = async (id) => {

  if (
    !confirm("Удалить изображение?")
  ) {
    return
  }

  await axios.delete(
    `http://127.0.0.1:8000/api/v1/admin/images/${id}/`
  )

  await loadImages()
}

const getFileName = (url) => {

  if (!url) return ""

  return url.split("/").pop()
}

const formatDate = (date) => {

  return new Date(date)
    .toLocaleString("ru-RU")
}

onMounted(async () => {

  await loadImages()
  await loadBearings()
})
</script>

<style scoped>

.page {
  padding: 24px;
}

.toolbar {
  margin-bottom: 20px;
}

.images-table {
  width: 100%;
  border-collapse: collapse;
}

.images-table th,
.images-table td {
  border: 1px solid #ddd;
  padding: 10px;
}

.preview {
  width: 80px;
  height: 80px;
  object-fit: cover;
}

.delete-btn {
  color: red;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.4);

  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: white;
  padding: 24px;
  width: 450px;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group input,
.form-group select {
  width: 100%;
}

.modal-actions {
  display: flex;
  gap: 10px;
}
</style>