from django.urls import path
from .views import (
    BearingListView, BearingDetailView, OrderCreateView, OrderStatusView,
    BearingTypeListView, ManufacturerListView, MaterialListView,
    SealTypeListView, PrecisionClassListView, download_document
)
urlpatterns = [
    path('bearings/', BearingListView.as_view(), name='bearing-list'),
    path('bearings/<int:pk>/', BearingDetailView.as_view(), name='bearing-detail'),
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<str:order_number>/', OrderStatusView.as_view(), name='order-status'),
    path('dictionaries/types/', BearingTypeListView.as_view(), name='bearing-types'),
    path('dictionaries/manufacturers/', ManufacturerListView.as_view(), name='manufacturers'),
    path('dictionaries/materials/', MaterialListView.as_view(), name='materials'),
    path('dictionaries/seal-types/', SealTypeListView.as_view(), name='seal-types'),
    path('dictionaries/precision-classes/', PrecisionClassListView.as_view(), name='precision-classes'),
    path('docs/download/<int:doc_id>/', download_document, name='download-document'),
]