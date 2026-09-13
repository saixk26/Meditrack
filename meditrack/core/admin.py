from django.contrib import admin
from .models import ActivityLog, Bill, BillItem, Category, Customer, Medicine, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'is_active')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('is_active',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('is_active',)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'batch_number', 'category', 'supplier',
                     'expiry_date', 'quantity', 'minimum_stock', 'status')
    search_fields = ('name', 'code', 'batch_number')
    list_filter = ('status', 'category', 'supplier')
    date_hierarchy = 'expiry_date'


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'customer', 'grand_total', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('bill_number',)
    list_filter = ('payment_method', 'payment_status')
    inlines = [BillItemInline]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'description', 'user', 'timestamp')
    list_filter = ('action',)
