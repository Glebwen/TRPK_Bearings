from django.urls import path
from .views import (
    BearingListView, BearingDetailView, OrderCreateView, OrderStatusView,
    BearingTypeListView, ManufacturerListView, MaterialListView,
    SealTypeListView, PrecisionClassListView, download_document, OrdersListView, OrderDetailView, OrderStatusUpdateView, OrderStatusListView, OrderAssignManagerView
)
urlpatterns = [
    # Подшипники
    path('bearings/', BearingListView.as_view(), name='bearing-list'),
    path('bearings/<int:pk>/', BearingDetailView.as_view(), name='bearing-detail'),
    
    # Заказы
    path('orders/list/', OrdersListView.as_view(), name='order-list'),  # GET - список
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),  # POST - создание
    path('orders/detail/<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),  # GET - детали
    path('orders/<str:order_number>/status/', OrderStatusView.as_view(), name='order-status'),  # GET - статус
    path('orders/<str:order_number>/update-status/', OrderStatusUpdateView.as_view(), name='order-update-status'),  # PATCH - обновить статус
    path('orders/<str:order_number>/assign-manager/', OrderAssignManagerView.as_view(), name='order-assign-manager'),
    
    # Справочники
    path('dictionaries/types/', BearingTypeListView.as_view(), name='bearing-types'),
    path('dictionaries/manufacturers/', ManufacturerListView.as_view(), name='manufacturers'),
    path('dictionaries/materials/', MaterialListView.as_view(), name='materials'),
    path('dictionaries/seal-types/', SealTypeListView.as_view(), name='seal-types'),
    path('dictionaries/precision-classes/', PrecisionClassListView.as_view(), name='precision-classes'),
    
    # Документы
    path('docs/download/<int:doc_id>/', download_document, name='download-document'),
    
    # Статусы (если нужен отдельный эндпоинт)
    path('order-statuses/', OrderStatusListView.as_view(), name='order-statuses'),
]