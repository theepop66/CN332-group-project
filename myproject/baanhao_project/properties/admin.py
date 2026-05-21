from django.contrib import admin
from .models import House, Vehicle

# 1. สร้าง Inline เพื่อให้เพิ่มรถได้ในหน้า "บ้าน" เลย (สะดวกมาก)
class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 1 # จำนวนช่องว่างที่จะโชว์ให้กรอกเพิ่มอัตโนมัติ (default คือ 3 แต่ 1 กำลังสวย)
    fields = ('license_plate', 'brand', 'color') # เลือก field ที่จะโชว์ในตารางย่อย

# 2. ลงทะเบียน House (บ้าน)
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    # หน้าตารางรวม
    list_display = ('house_number', 'house_id', 'get_vehicle_count')
    search_fields = ('house_number', 'house_id') # ค้นหาจากเลขบ้าน
    list_filter = () # ไม่มีตัวกรองแล้ว
    
    # เอา VehicleInline มาแปะไว้ในหน้านี้
    inlines = [VehicleInline]

    # ฟังก์ชันแถม: โชว์จำนวนรถในหน้าตารางรวม
    def get_vehicle_count(self, obj):
        return obj.vehicles.count()
    get_vehicle_count.short_description = 'Vehicles'

# 3. ลงทะเบียน Vehicle (รถ) แยกต่างหากด้วย (เผื่ออยากดู list รถทั้งหมู่บ้าน)
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'color', 'house')
    search_fields = ('license_plate', 'brand')
    list_filter = ('brand',)
    autocomplete_fields = ['house'] # ถ้าบ้านเยอะมาก จะช่วยให้ช่องค้นหาบ้านทำงานเร็วขึ้น