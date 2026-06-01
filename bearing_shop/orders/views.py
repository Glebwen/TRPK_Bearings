from rest_framework import generics, filters
from django.db.models import Q
from .models import (
    Bearing, Order, BearingType, Manufacturer, Material, 
    SealType, PrecisionClass
)
from .serializers import (
    BearingListSerializer, BearingDetailSerializer, 
    OrderCreateSerializer, OrderStatusSerializer,
    BearingTypeSerializer, ManufacturerSerializer,
    MaterialSerializer, SealTypeSerializer, PrecisionClassSerializer
)
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TechnicalDoc

@api_view(['GET'])
def download_document(request, doc_id):
    try:
        doc = get_object_or_404(TechnicalDoc, id=doc_id)
        if doc.file:
            response = FileResponse(doc.file, as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{doc.file_name}"'
            return response
        else:
            return Response({'error': 'Файл не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BearingListView(generics.ListAPIView):
    queryset = Bearing.objects.select_related(
        'stock', 'type', 'precision_class', 'seal_type', 'material', 'manufacturer'
    ).all()
    serializer_class = BearingListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'article']

    def get_queryset(self):
        qs = super().get_queryset()
        type_id = self.request.query_params.get('type_id')
        if type_id:
            qs = qs.filter(type_id=type_id)
        precision_class_id = self.request.query_params.get('precision_class_id')
        if precision_class_id:
            qs = qs.filter(precision_class_id=precision_class_id)
        seal_type_id = self.request.query_params.get('seal_type_id')
        if seal_type_id:
            qs = qs.filter(seal_type_id=seal_type_id)
        material_id = self.request.query_params.get('material_id')
        if material_id:
            qs = qs.filter(material_id=material_id)
        manufacturer_id = self.request.query_params.get('manufacturer_id')
        if manufacturer_id:
            qs = qs.filter(manufacturer_id=manufacturer_id)

        inner_min = self.request.query_params.get('inner_diameter_min')
        inner_max = self.request.query_params.get('inner_diameter_max')
        if inner_min:
            qs = qs.filter(inner_diameter__gte=inner_min)
        if inner_max:
            qs = qs.filter(inner_diameter__lte=inner_max)

        outer_min = self.request.query_params.get('outer_diameter_min')
        outer_max = self.request.query_params.get('outer_diameter_max')
        if outer_min:
            qs = qs.filter(outer_diameter__gte=outer_min)
        if outer_max:
            qs = qs.filter(outer_diameter__lte=outer_max)

        height_min = self.request.query_params.get('height_min')
        height_max = self.request.query_params.get('height_max')
        if height_min:
            qs = qs.filter(height__gte=height_min)
        if height_max:
            qs = qs.filter(height__lte=height_max)

        return qs

class BearingDetailView(generics.RetrieveAPIView):
    queryset = Bearing.objects.prefetch_related('docs').select_related('stock')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_serializer_class(self):
        return BearingDetailSerializer

class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

class OrderStatusView(generics.RetrieveAPIView):
    queryset = Order.objects.select_related('status')
    serializer_class = OrderStatusSerializer
    lookup_field = 'order_number'


class BearingTypeListView(generics.ListAPIView):
    queryset = BearingType.objects.all()
    serializer_class = BearingTypeSerializer

class ManufacturerListView(generics.ListAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class MaterialListView(generics.ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class SealTypeListView(generics.ListAPIView):
    queryset = SealType.objects.all()
    serializer_class = SealTypeSerializer

class PrecisionClassListView(generics.ListAPIView):
    queryset = PrecisionClass.objects.all()
    serializer_class = PrecisionClassSerializer