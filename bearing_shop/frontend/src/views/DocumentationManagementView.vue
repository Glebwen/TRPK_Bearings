<script setup>
import AdminNavbar from "../components/AdminNavbar.vue"
</script>

<template>
  <AdminNavbar />

  <div class="page">

    <h1>Управление документацией</h1>

    <div class="toolbar">
      <button>
        Загрузить документацию
      </button>
    </div>

    <table class="docs-table">

      <thead>
        <tr>
          <th>Название файла</th>
          <th>Тип</th>
          <th>Подшипник</th>
          <th>Дата загрузки</th>
          <th></th>
        </tr>
      </thead>

      <tbody>

        <tr>
          <td>catalog.pdf</td>
          <td>PDF</td>
          <td>100BAR10STYN/P4SUL</td>
          <td>09.06.2026 12:00</td>

          <td>
            <button class="delete-btn">
              Удалить
            </button>
          </td>
        </tr>

        <tr>
          <td>drawing.pdf</td>
          <td>PDF</td>
          <td>200BARBAR</td>
          <td>09.06.2026 12:15</td>

          <td>
            <button class="delete-btn">
              Удалить
            </button>
          </td>
        </tr>

      </tbody>

    </table>

  </div>
</template>

<style scoped>

.page {
  padding: 24px;
}

.toolbar {
  margin-bottom: 20px;
}

.docs-table {
  width: 100%;
  border-collapse: collapse;
}

.docs-table th,
.docs-table td {
  border: 1px solid #ddd;
  padding: 10px;
}

.delete-btn {
  color: red;
}

</style>