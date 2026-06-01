from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
import re

class BearingType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тип подшипника")
    class Meta:
        verbose_name_plural = "Типы подшипников"
    def __str__(self): return self.name

class PrecisionClass(models.Model):
    code = models.SmallIntegerField(unique=True, verbose_name="Код класса")
    description = models.CharField(max_length=100, blank=True, verbose_name="Описание")
    class Meta:
        verbose_name_plural = "Классы точности"
    def __str__(self): return str(self.code)

class SealType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тип уплотнения")
    class Meta:
        verbose_name_plural = "Типы уплотнений"
    def __str__(self): return self.name

class Material(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Материал")
    class Meta:
        verbose_name_plural = "Материалы"
    def __str__(self): return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Производитель")
    class Meta:
        verbose_name_plural = "Производители"
    def __str__(self): return self.name

class OrderStatus(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Статус заявки")
    class Meta:
        verbose_name_plural = "Статусы заявок"
    def __str__(self): return self.name

class Bearing(models.Model):
    article = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    type = models.ForeignKey(BearingType, on_delete=models.PROTECT, verbose_name="Тип")
    inner_diameter = models.IntegerField(verbose_name="Внутренний диаметр (мм)", validators=[MinValueValidator(1)])
    outer_diameter = models.IntegerField(verbose_name="Наружный диаметр (мм)", validators=[MinValueValidator(1)])
    height = models.IntegerField(verbose_name="Высота (мм)", validators=[MinValueValidator(1)])
    precision_class = models.ForeignKey(PrecisionClass, on_delete=models.PROTECT, verbose_name="Класс точности")
    seal_type = models.ForeignKey(SealType, on_delete=models.PROTECT, verbose_name="Тип уплотнения")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name="Материал")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Производитель")
    image = models.ImageField(upload_to='bearings/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    class Meta:
        verbose_name_plural = "Подшипники"
    def __str__(self): return f"{self.article} - {self.name}"

class BearingStock(models.Model):
    bearing = models.OneToOneField(Bearing, on_delete=models.CASCADE, related_name='stock', verbose_name="Подшипник")
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    class Meta:
        verbose_name_plural = "Остатки и цены"

class TechnicalDoc(models.Model):
    bearing = models.ForeignKey(Bearing, on_delete=models.CASCADE, related_name='docs', verbose_name="Подшипник")
    file_name = models.CharField(max_length=255, verbose_name="Имя файла")
    file = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="Файл документации")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    class Meta:
        verbose_name_plural = "Техническая документация"

class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name="ФИО")
    organization = models.CharField(max_length=255, blank=True, null=True, verbose_name="Организация")
    phone = models.CharField(max_length=20, validators=[RegexValidator(r'^\+79\d{9}$', message='Формат +79xxxxxxxxx')], verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Email")
    class Meta:
        verbose_name_plural = "Клиенты"
    def __str__(self): return f"{self.name} ({self.email})"

class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Номер заявки")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="Клиент")
    delivery_address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, default=1, verbose_name="Статус")  # 1 = "Принята"
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Итоговая сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    class Meta:
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        if not self.order_number:
            last = Order.objects.order_by('id').last()
            new_id = last.id + 1 if last else 1
            self.order_number = f"B{new_id:06d}"
        super().save(*args, **kwargs)
    def __str__(self): return f"Заявка {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заявка")
    bearing = models.ForeignKey(Bearing, on_delete=models.PROTECT, verbose_name="Подшипник")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Количество")
    price_at_order = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена на момент заказа")
    class Meta:
        verbose_name_plural = "Позиции заявок"
    @property
    def total(self): return self.quantity * self.price_at_order

class StatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history', verbose_name="Заявка")
    old_status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, null=True, blank=True, related_name='+', verbose_name="Старый статус")
    new_status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name='+', verbose_name="Новый статус")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")
    class Meta:
        verbose_name_plural = "История статусов"
        ordering = ['-changed_at']

class EmailNotification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications', verbose_name="Заявка")
    recipient_email = models.EmailField(verbose_name="Email получателя")
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Текст письма")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    class Meta:
        verbose_name_plural = "Email уведомления"