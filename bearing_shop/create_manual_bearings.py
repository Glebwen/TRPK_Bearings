import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bearing_shop.settings')
import django
django.setup()

from orders.models import (
    Bearing, BearingStock, Manufacturer, BearingType,
    PrecisionClass, SealType, Material
)

# ========== 1. СПРАВОЧНИКИ ==========

# Производители
hbb, _ = Manufacturer.objects.get_or_create(name='HBB')
skf, _ = Manufacturer.objects.get_or_create(name='SKF')
fag, _ = Manufacturer.objects.get_or_create(name='FAG')
nsk, _ = Manufacturer.objects.get_or_create(name='NSK')

# Типы подшипников
ball, _ = BearingType.objects.get_or_create(name='шариковый')
roller, _ = BearingType.objects.get_or_create(name='роликовый')
needle, _ = BearingType.objects.get_or_create(name='игольчатый')
radial, _ = BearingType.objects.get_or_create(name='радиальный')
thrust, _ = BearingType.objects.get_or_create(name='упорный')
radial_thrust, _ = BearingType.objects.get_or_create(name='радиально-упорный')

# Классы точности (используем коды 0,4,5,6)
prec_0, _ = PrecisionClass.objects.get_or_create(code=0, defaults={'description': 'Обычный класс'})
prec_4, _ = PrecisionClass.objects.get_or_create(code=4, defaults={'description': 'Особо высокой точности'})
prec_5, _ = PrecisionClass.objects.get_or_create(code=5, defaults={'description': 'Высокой точности'})
prec_6, _ = PrecisionClass.objects.get_or_create(code=6, defaults={'description': 'Повышенной точности'})

# Типы уплотнений
open_seal, _ = SealType.objects.get_or_create(name='открытый')
metal_shields, _ = SealType.objects.get_or_create(name='металлические шайбы')
rubber_seals, _ = SealType.objects.get_or_create(name='резиновые шайбы')

# Материалы
steel, _ = Material.objects.get_or_create(name='подшипниковая сталь')
stainless, _ = Material.objects.get_or_create(name='нержавеющая сталь')
ceramic, _ = Material.objects.get_or_create(name='керамика')

print("✓ Справочники созданы/проверены")

# ========== 2. ФУНКЦИЯ ==========

def create_bearing(article, name, bearing_type, inner_d, outer_d, height, precision, seal, material, manufacturer, price, stock):
    bearing, created = Bearing.objects.update_or_create(
        article=article,
        defaults={
            'name': name,
            'type': bearing_type,
            'inner_diameter': inner_d,
            'outer_diameter': outer_d,
            'height': height,
            'precision_class': precision,
            'seal_type': seal,
            'material': material,
            'manufacturer': manufacturer,
            'image_url': '',
        }
    )
    BearingStock.objects.update_or_create(
        bearing=bearing,
        defaults={'price': price, 'stock_quantity': stock}
    )
    print(f"{'✓ СОЗДАН' if created else '• ОБНОВЛЁН'}: {article}")

# ========== 3. ДОБАВЛЕНИЕ 10 ПОДШИПНИКОВ ==========

print("\n=== ДОБАВЛЕНИЕ ПОДШИПНИКОВ ===\n")

# 1. SKF - глубокий шариковый подшипник, открытый, сталь, обычный класс
create_bearing(
    article='6205-2Z/C3',
    name='Радиальный шариковый подшипник 6205-2Z/C3 SKF',
    bearing_type=radial,
    inner_d=25, outer_d=52, height=15,
    precision=prec_0,
    seal=metal_shields,
    material=steel,
    manufacturer=skf,
    price=450,
    stock=25
)

# 2. FAG - роликовый конический подшипник, открытый, сталь, повышенная точность
create_bearing(
    article='30208-A',
    name='Роликовый конический подшипник 30208-A FAG',
    bearing_type=roller,
    inner_d=40, outer_d=80, height=18,
    precision=prec_6,
    seal=open_seal,
    material=steel,
    manufacturer=fag,
    price=1890,
    stock=12
)

# 3. NSK - упорный шариковый подшипник, открытый, сталь, высокая точность
create_bearing(
    article='51108',
    name='Упорный шариковый подшипник 51108 NSK',
    bearing_type=thrust,
    inner_d=40, outer_d=60, height=13,
    precision=prec_5,
    seal=open_seal,
    material=steel,
    manufacturer=nsk,
    price=1250,
    stock=8
)

# 4. HBB - игольчатый подшипник, открытый, сталь, обычный класс
create_bearing(
    article='NK-30/20',
    name='Игольчатый подшипник NK 30/20 HBB',
    bearing_type=needle,
    inner_d=30, outer_d=38, height=20,
    precision=prec_0,
    seal=open_seal,
    material=steel,
    manufacturer=hbb,
    price=560,
    stock=15
)

# 5. SKF - радиально-упорный, резиновые уплотнения, нержавеющая сталь, высокая точность
create_bearing(
    article='7206-B-2RZP5',
    name='Радиально-упорный подшипник 7206-B-2RZP5 SKF нерж.',
    bearing_type=radial_thrust,
    inner_d=30, outer_d=62, height=16,
    precision=prec_5,
    seal=rubber_seals,
    material=stainless,
    manufacturer=skf,
    price=3450,
    stock=7
)

# 6. FAG - упорный роликовый, открытый, сталь, особо высокая точность
create_bearing(
    article='81212-TV-P4',
    name='Упорный роликовый подшипник 81212-TV-P4 FAG',
    bearing_type=thrust,
    inner_d=60, outer_d=95, height=26,
    precision=prec_4,
    seal=open_seal,
    material=steel,
    manufacturer=fag,
    price=8900,
    stock=3
)

# 7. NSK - радиальный, металлические шайбы, керамика, повышенная точность
create_bearing(
    article='6004-2Z-HC5',
    name='Радиальный подшипник с керамическими шарами 6004-2Z-HC5 NSK',
    bearing_type=radial,
    inner_d=20, outer_d=42, height=12,
    precision=prec_6,
    seal=metal_shields,
    material=ceramic,
    manufacturer=nsk,
    price=2750,
    stock=4
)

# 8. HBB - радиально-упорный, резиновые уплотнения, сталь, обычный класс
create_bearing(
    article='7005CTA-2RZ',
    name='Радиально-упорный подшипник 7005CTA-2RZ HBB',
    bearing_type=radial_thrust,
    inner_d=25, outer_d=47, height=12,
    precision=prec_0,
    seal=rubber_seals,
    material=steel,
    manufacturer=hbb,
    price=2850,
    stock=18
)

# 9. FAG - игольчатый с резиновыми уплотнениями, нержавеющая сталь
create_bearing(
    article='RNA-6904-2RS',
    name='Игольчатый подшипник RNA 6904-2RS FAG нерж.',
    bearing_type=needle,
    inner_d=25, outer_d=37, height=30,
    precision=prec_5,
    seal=rubber_seals,
    material=stainless,
    manufacturer=fag,
    price=4200,
    stock=6
)

# 10. NSK - шариковый радиальный, открытый, керамика, особо высокая точность
create_bearing(
    article='6208/HC5P4',
    name='Радиальный шариковый подшипник с керамикой 6208/HC5P4 NSK',
    bearing_type=radial,
    inner_d=40, outer_d=80, height=18,
    precision=prec_4,
    seal=open_seal,
    material=ceramic,
    manufacturer=nsk,
    price=18500,
    stock=2
)

print("\n=== ДОБАВЛЕНО 10 РАЗНООБРАЗНЫХ ПОДШИПНИКОВ ===\n")

# Выводим список для проверки
print("Список добавленных подшипников:\n")
bearings = Bearing.objects.all().order_by('id')
for b in bearings:
    print(f"  - {b.article} | {b.name} | {b.type.name} | {b.manufacturer.name} | {b.stock.price} руб. | остаток: {b.stock.stock_quantity}")