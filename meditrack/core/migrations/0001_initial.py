import django.db.models.deletion
from django.conf import settings
import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('contact_person', models.CharField(blank=True, max_length=150)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.TextField(blank=True)),
                ('gst_number', models.CharField(blank=True, max_length=20, verbose_name='GST Number')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Medicine Name')),
                ('code', models.CharField(max_length=30, unique=True, verbose_name='Medicine Code')),
                ('batch_number', models.CharField(max_length=50, verbose_name='Batch Number')),
                ('manufacturer', models.CharField(max_length=150)),
                ('manufacture_date', models.DateField(verbose_name='Manufacture Date')),
                ('expiry_date', models.DateField(verbose_name='Expiry Date')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gst_percentage', models.DecimalField(decimal_places=2, default=5.0, max_digits=5, verbose_name='GST (%)')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('minimum_stock', models.PositiveIntegerField(default=10, verbose_name='Minimum Stock Level')),
                ('rack_number', models.CharField(blank=True, max_length=20, verbose_name='Rack Number')),
                ('image', models.ImageField(blank=True, null=True, upload_to=core.models.medicine_image_path)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medicines', to='core.category')),
                ('supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medicines', to='core.supplier')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='medicine',
            index=models.Index(fields=['expiry_date'], name='core_medici_expiry__b8e6a4_idx'),
        ),
        migrations.AddIndex(
            model_name='medicine',
            index=models.Index(fields=['code'], name='core_medici_code_1c9d3e_idx'),
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_number', models.CharField(default=core.models.generate_bill_number, max_length=30, unique=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('gst_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI')], default='cash', max_length=10)),
                ('payment_status', models.CharField(choices=[('paid', 'Paid'), ('pending', 'Pending')], default='paid', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bills', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bills', to='core.customer')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BillItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gst_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.bill')),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bill_items', to='core.medicine')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('medicine_added', 'Medicine Added'), ('medicine_updated', 'Medicine Updated'), ('medicine_deleted', 'Medicine Deleted'), ('stock_updated', 'Stock Updated'), ('supplier_added', 'Supplier Added'), ('customer_added', 'Customer Added'), ('bill_created', 'Bill Created'), ('login', 'User Login')], max_length=30)),
                ('description', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
