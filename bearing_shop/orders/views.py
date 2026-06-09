from rest_framework import generics, filters
from django.db.models import Q
from .models import (
    Order,
    OrderStatus,
    Bearing,
    BearingStock,
    BearingType,
    PrecisionClass,
    SealType,
    Material,
    Manufacturer
)
from .serializers import (
    BearingListSerializer, BearingDetailSerializer, 
    OrderCreateSerializer, OrderStatusSerializer,
    BearingTypeSerializer, ManufacturerSerializer,
    MaterialSerializer, SealTypeSerializer, PrecisionClassSerializer, OrderDetailSerializer, OrderListSerializer,
    OrderStatusUpdateSerializer, OrderStatusSimpleSerializer, OrderAssignManagerSerializer, BearingImageSerializer
)
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from rest_framework import status
from .models import TechnicalDoc
from rest_framework.views import APIView
import openpyxl

from .models import BearingStock

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

#Для менеджера
class OrdersListView(generics.ListAPIView):
    """Список всех заявок (для менеджера)"""
    serializer_class = OrderListSerializer
    filter_backends = []
    
    def get_queryset(self):
        queryset = Order.objects.select_related('customer', 'status').annotate(
            items_count=Count('items'),
            total_quantity=Sum('items__quantity')
        ).order_by('-created_at')
        
        # Фильтрация
        status_id = self.request.query_params.get('status_id')
        if status_id:
            queryset = queryset.filter(status_id=status_id)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        customer_email = self.request.query_params.get('customer_email')
        if customer_email:
            queryset = queryset.filter(customer__email__icontains=customer_email)
        
        order_number = self.request.query_params.get('order_number')
        if order_number:
            queryset = queryset.filter(order_number__icontains=order_number)
        
        return queryset


class OrderDetailView(generics.RetrieveAPIView):
    """Детальная информация о заявке"""
    queryset = Order.objects.prefetch_related(
        'items__bearing', 
        'history__old_status', 
        'history__new_status',
        'customer'
    )
    serializer_class = OrderDetailSerializer
    lookup_field = 'order_number'


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Обновление статуса заявки"""
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    lookup_field = 'order_number'
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'order_number': instance.order_number,
            'status': instance.status.name,
            'message': 'Статус успешно обновлён'
        })

class OrderStatusListView(generics.ListAPIView):
    """Список всех статусов заявок"""
    queryset = OrderStatus.objects.all()
    serializer_class = OrderStatusSimpleSerializer

class OrderAssignManagerView(generics.UpdateAPIView):
    """Назначение менеджера на заявку"""
    queryset = Order.objects.all()
    serializer_class = OrderAssignManagerSerializer
    lookup_field = 'order_number'
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        manager_name = instance.manager.get_full_name() or instance.manager.username if instance.manager else None
        
        return Response({
            'order_number': instance.order_number,
            'manager': {
                'id': instance.manager.id if instance.manager else None,
                'name': manager_name
            },
            'message': 'Менеджер успешно назначен'
        })

class ImportXlsxView(APIView):

    def post(self, request):

        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "Файл не выбран"},
                status=400
            )

        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for row in sheet.iter_rows(min_row=2, values_only=True):
            print("ROW =", row)

            try:

                article = str(row[0]).strip() if row[0] else None
                name = str(row[1]).strip() if row[1] else None

                if not article or not name:
                    skipped_count += 1
                    continue

                type_name = str(row[2]).strip()
                inner_diameter = int(row[3] or 1)
                outer_diameter = int(row[4] or 1)
                height = int(row[5] or 1)

                precision_code = int(row[6] or 0)

                seal_name = str(row[7]).strip()
                material_name = str(row[8]).strip()
                manufacturer_name = str(row[9]).strip()

                price = float(row[10] or 0)
                stock_quantity = int(row[11] or 0)


                bearing_type, _ = BearingType.objects.get_or_create(
                    name=type_name
                )

                precision, _ = PrecisionClass.objects.get_or_create(
                    code=precision_code
                )

                seal, _ = SealType.objects.get_or_create(
                    name=seal_name
                )

                material, _ = Material.objects.get_or_create(
                    name=material_name
                )

                manufacturer, _ = Manufacturer.objects.get_or_create(
                    name=manufacturer_name
                )


                bearing, created = Bearing.objects.get_or_create(
                    article=article,
                    defaults={
                        "name": name,
                        "type": bearing_type,
                        "inner_diameter": inner_diameter,
                        "outer_diameter": outer_diameter,
                        "height": height,
                        "precision_class": precision,
                        "seal_type": seal,
                        "material": material,
                        "manufacturer": manufacturer,
                    }
                )

                if created:

                    created_count += 1

                else:

                    bearing.name = name
                    bearing.type = bearing_type
                    bearing.inner_diameter = inner_diameter
                    bearing.outer_diameter = outer_diameter
                    bearing.height = height
                    bearing.precision_class = precision
                    bearing.seal_type = seal
                    bearing.material = material
                    bearing.manufacturer = manufacturer

                    bearing.save()

                    updated_count += 1

                BearingStock.objects.update_or_create(
                    bearing=bearing,
                    defaults={
                        "price": price,
                        "stock_quantity": stock_quantity
                    }
                )

            except Exception as e:

                print(
                    f"Ошибка импорта строки {row}: {e}"
                )

                skipped_count += 1

        return Response({
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count
        })

class BearingImageListView(generics.ListAPIView):

    serializer_class = BearingImageSerializer

    def get_queryset(self):

        return Bearing.objects.filter(
            image__isnull=False
        ).exclude(
            image=""
        )
        
class UploadBearingImageView(APIView):

    def post(self, request):

        bearing_id = request.data.get("bearing_id")
        image = request.FILES.get("image")

        if not bearing_id:
            return Response(
                {"error": "Не выбран подшипник"},
                status=400
            )

        if not image:
            return Response(
                {"error": "Файл не выбран"},
                status=400
            )

        bearing = get_object_or_404(
            Bearing,
            id=bearing_id
        )

        bearing.image = image
        bearing.save()

        return Response({
            "message": "Изображение загружено"
        })
        
class DeleteBearingImageView(APIView):

    def delete(self, request, pk):

        bearing = get_object_or_404(
            Bearing,
            pk=pk
        )

        if bearing.image:
            bearing.image.delete()

        bearing.image = None
        bearing.save()

        return Response({
            "message": "Изображение удалено"
        })