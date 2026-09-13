import datetime
import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


# =============================================================================
# CATEGORY
# =============================================================================
class Category(models.Model):
    """Medicine category, e.g. Tablet, Syrup, Injection, Ointment."""
    category_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


# =============================================================================
# SUPPLIER
# =============================================================================
class Supplier(models.Model):
    """A medicine supplier / distributor / manufacturer company."""
    supplier_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=12)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gst_number = models.CharField('GST Number', max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:supplier_detail', args=[self.pk])

    @property
    def total_medicines(self):
        return self.medicines.count()


# =============================================================================
# CUSTOMER
# =============================================================================
class Customer(models.Model):
    """A pharmacy walk-in / registered customer."""
    customer_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=12)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:customer_detail', args=[self.pk])

    @property
    def total_purchases(self):
        return self.bills.count()

    @property
    def total_spent(self):
        return self.bills.aggregate(total=models.Sum('grand_total'))['total'] or 0


# =============================================================================
# MEDICINE
# =============================================================================
def medicine_image_path(instance, filename):
    ext = filename.split('.')[-1]
    safe_code = instance.code or 'medicine'
    return f'medicines/{safe_code}_{timezone.now().strftime("%Y%m%d%H%M%S")}.{ext}'


class Medicine(models.Model):
    medicine_id = models.BigAutoField(primary_key=True)
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    name = models.CharField('Medicine Name', max_length=50)
    code = models.CharField('Medicine Code', max_length=10, unique=True)
    batch_number = models.CharField('Batch Number', max_length=30)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                  related_name='medicines')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True,
                                  related_name='medicines')
    manufacturer = models.CharField(max_length=150)

    manufacture_date = models.DateField('Manufacture Date')
    expiry_date = models.DateField('Expiry Date')

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percentage = models.DecimalField('GST (%)', max_digits=5, decimal_places=2, default=5.00)

    quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField('Minimum Stock Level', default=10)
    rack_number = models.CharField('Rack Number', max_length=20, blank=True)

    image = models.ImageField(upload_to=medicine_image_path, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['expiry_date']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f'{self.name} ({self.code})'

    def get_absolute_url(self):
        return reverse('core:medicine_detail', args=[self.pk])

    # ------------------------------------------------------------------
    # SMART EXPIRY LOGIC  (always computed on the fly - never persisted)
    # ------------------------------------------------------------------
    @property
    def days_to_expiry(self):
        """Positive = days remaining. Negative = days since expired."""
        delta = self.expiry_date - timezone.localdate()
        return delta.days

    @property
    def expiry_status(self):
        days = self.days_to_expiry
        if days < 0:
            return 'expired'
        elif days == 0:
            return 'expiring_today'
        elif days == 1:
            return 'expiring_tomorrow'
        elif days <= 7:
            return 'expiring_week'
        elif days <= 30:
            return 'expiring_month'
        return 'safe'

    @property
    def expiry_status_label(self):
        return {
            'expired': 'Expired',
            'expiring_today': 'Expiring Today',
            'expiring_tomorrow': 'Expiring Tomorrow',
            'expiring_week': 'Expiring This Week',
            'expiring_month': 'Expiring This Month',
            'safe': 'Safe',
        }[self.expiry_status]

    @property
    def expiry_badge_class(self):
        return {
            'expired': 'bg-danger',
            'expiring_today': 'bg-danger',
            'expiring_tomorrow': 'bg-warning text-dark',
            'expiring_week': 'bg-warning text-dark',
            'expiring_month': 'bg-info text-dark',
            'safe': 'bg-success',
        }[self.expiry_status]

    @property
    def is_expired(self):
        return self.days_to_expiry < 0

    @property
    def is_sellable(self):
        """Expired or out-of-stock medicines cannot be billed."""
        return not self.is_expired and self.quantity > 0 and self.status == self.STATUS_ACTIVE

    # ------------------------------------------------------------------
    # STOCK LOGIC
    # ------------------------------------------------------------------
    @property
    def stock_status(self):
        if self.quantity <= 0:
            return 'out_of_stock'
        elif self.quantity <= self.minimum_stock:
            return 'low_stock'
        return 'in_stock'

    @property
    def stock_status_label(self):
        return {
            'out_of_stock': 'Out of Stock',
            'low_stock': 'Low Stock',
            'in_stock': 'In Stock',
        }[self.stock_status]

    @property
    def stock_badge_class(self):
        return {
            'out_of_stock': 'bg-danger',
            'low_stock': 'bg-warning text-dark',
            'in_stock': 'bg-success',
        }[self.stock_status]

    @property
    def gst_amount(self):
        return round(self.selling_price * self.gst_percentage / 100, 2)

    @property
    def price_with_gst(self):
        return round(self.selling_price + self.gst_amount, 2)


# =============================================================================
# QUERYSET HELPERS FOR THE SMART EXPIRY ALERT CENTER / DASHBOARD
# =============================================================================
class MedicineQueryHelper:
    """Centralised, dynamic (never persisted) expiry & stock calculations
    used across the Dashboard, Inventory and Expiry Alert Center."""

    @staticmethod
    def today():
        return timezone.localdate()

    @classmethod
    def expired(cls):
        return Medicine.objects.filter(expiry_date__lt=cls.today())

    @classmethod
    def expiring_today(cls):
        return Medicine.objects.filter(expiry_date=cls.today())

    @classmethod
    def expiring_tomorrow(cls):
        return Medicine.objects.filter(expiry_date=cls.today() + datetime.timedelta(days=1))

    @classmethod
    def expiring_within(cls, days):
        return Medicine.objects.filter(
            expiry_date__gte=cls.today(),
            expiry_date__lte=cls.today() + datetime.timedelta(days=days),
        )

    @classmethod
    def safe(cls):
        return Medicine.objects.filter(expiry_date__gt=cls.today() + datetime.timedelta(days=30))

    @classmethod
    def low_stock(cls):
        return Medicine.objects.filter(quantity__gt=0, quantity__lte=models.F('minimum_stock'))

    @classmethod
    def out_of_stock(cls):
        return Medicine.objects.filter(quantity__lte=0)


# =============================================================================
# BILLING
# =============================================================================
def generate_bill_number():
    date_part = timezone.now().strftime('%Y%m%d')
    rand_part = ''.join(random.choices(string.digits, k=4))
    return f'INV-{date_part}-{rand_part}'


class Bill(models.Model):
    bill_id = models.BigAutoField(primary_key=True)
    PAYMENT_CASH = 'cash'
    PAYMENT_CARD = 'card'
    PAYMENT_UPI = 'upi'
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_CARD, 'Card'),
        (PAYMENT_UPI, 'UPI'),
    ]

    STATUS_PAID = 'paid'
    STATUS_PENDING = 'pending'
    STATUS_CHOICES = [
        (STATUS_PAID, 'Paid'),
        (STATUS_PENDING, 'Pending'),
    ]

    bill_number = models.CharField(max_length=30, unique=True, default=generate_bill_number)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='bills')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bills')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PAID)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.bill_number

    def get_absolute_url(self):
        return reverse('core:bill_invoice', args=[self.pk])

    def recalculate_totals(self):
        items = self.items.all()
        subtotal = sum((item.quantity * item.unit_price for item in items), start=0)
        gst_total = sum((item.gst_amount for item in items), start=0)
        discount_amount = round(subtotal * self.discount_percent / 100, 2)
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.gst_amount = gst_total
        self.grand_total = round(subtotal - discount_amount + gst_total, 2)
        self.save(update_fields=['subtotal', 'discount_amount', 'gst_amount', 'grand_total'])


class BillItem(models.Model):
    bill_item_id = models.BigAutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='bill_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ['bill_item_id']

    def __str__(self):
        return f'{self.medicine.name} x {self.quantity}'

    @property
    def line_subtotal(self):
        return round(self.quantity * self.unit_price, 2)

    @property
    def gst_amount(self):
        return round(self.line_subtotal * self.gst_percent / 100, 2)

    @property
    def line_total(self):
        return round(self.line_subtotal + self.gst_amount, 2)


# =============================================================================
# ACTIVITY LOG  (Dashboard "Recent Activities")
# =============================================================================
class ActivityLog(models.Model):
    activity_log_id = models.BigAutoField(primary_key=True)
    ACTION_CHOICES = [
        ('medicine_added', 'Medicine Added'),
        ('medicine_updated', 'Medicine Updated'),
        ('medicine_deleted', 'Medicine Deleted'),
        ('stock_updated', 'Stock Updated'),
        ('supplier_added', 'Supplier Added'),
        ('customer_added', 'Customer Added'),
        ('bill_created', 'Bill Created'),
        ('login', 'User Login'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.get_action_display()} - {self.description}'

    @property
    def icon(self):
        return {
            'medicine_added': 'fa-pills text-success',
            'medicine_updated': 'fa-pen text-primary',
            'medicine_deleted': 'fa-trash text-danger',
            'stock_updated': 'fa-boxes-stacked text-info',
            'supplier_added': 'fa-truck text-warning',
            'customer_added': 'fa-user-plus text-primary',
            'bill_created': 'fa-file-invoice text-success',
            'login': 'fa-right-to-bracket text-secondary',
        }.get(self.action, 'fa-circle-info text-secondary')


def log_activity(user, action, description):
    ActivityLog.objects.create(user=user, action=action, description=description)
