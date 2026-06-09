<template>
    <AdminNavbar />
  <div>

    <h2>Импорт товаров</h2>

    <input
      type="file"
      @change="selectFile"
    />

    <button
      class="btn btn-primary mt-3"
      @click="uploadFile"
    >
      Загрузить
    </button>

    <div
      v-if="message"
      class="alert alert-success mt-3"
    >
      {{ message }}
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import AdminNavbar from "../components/AdminNavbar.vue"

const file = ref(null)
const message = ref('')

const selectFile = (event) => {
  file.value = event.target.files[0]
}

const uploadFile = async () => {

  const formData = new FormData()

  formData.append('file', file.value)

  const response = await axios.post(
    'http://127.0.0.1:8000/api/v1/admin/import-xlsx/',
    formData
  )

  message.value = response.data.message
}
</script>