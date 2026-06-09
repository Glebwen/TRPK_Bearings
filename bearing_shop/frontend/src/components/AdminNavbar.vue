<template>
  <nav class="admin-navbar">

    <RouterLink to="/admin/import">
      Импорт товаров
    </RouterLink>

    <RouterLink to="/admin/images">
      Изображения
    </RouterLink>

    <RouterLink to="/admin/docs">
      Документация
    </RouterLink>

    <RouterLink to="/login">
      Выйти
    </RouterLink>

  </nav>
</template>

<style scoped>
.admin-navbar {
  display: flex;
  gap: 20px;
  padding: 16px;
  background: #2c3e50;
}

.admin-navbar a {
  color: white;
  text-decoration: none;
}
</style>