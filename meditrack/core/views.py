import datetime
import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CategoryForm, CustomerForm, MedicineForm, SupplierForm
from .models import (
    ActivityLog, Bill, BillItem, Category, Customer, Medicine,
    MedicineQueryHelper, Supplier, log_activity,
)


# =============================================================================
# DASHBOARD
# =============================================================================
@login_required
def dashboard(request):
    today = timezone.localdate()

    total_medicines = Medicine.objects.count()
    total_suppliers = Supplier.objects.count()
    total_customers = Customer.objects.count()

    low_stock_qs = MedicineQueryHelper.low_stock()
    out_of_stock_qs = MedicineQueryHelper.out_of_stock()
    expired_qs = MedicineQueryHelper.expired()
    expiring_today_qs = MedicineQueryHelper.expiring_today()
    expiring_week_qs = MedicineQueryHelper.expiring_within(7)

    # Category-wise stock chart data
    category_data = list(
        Category.objects.annotate(count=Sum('medicines__quantity')).values('name', 'count')
    )

    # Expiry overview chart data
    expiry_chart = {
        'expired': expired_qs.count(),
        'today': expiring_today_qs.count(),
        'week': MedicineQueryHelper.expiring_within(7).count(),
        'month': MedicineQueryHelper.expiring_within(30).count(),
        'safe': MedicineQueryHelper.safe().count(),
    }

    stock_chart = {
        'in_stock': total_medicines - low_stock_qs.count() - out_of_stock_qs.count(),
        'low_stock': low_stock_qs.count(),
        'out_of_stock': out_of_stock_qs.count(),
    }

    recent_activities = ActivityLog.objects.select_related('user')[:10]
    recent_bills = Bill.objects.select_related('customer')[:5]

    context = {
        'total_medicines': total_medicines,
        'total_suppliers': total_suppliers,
        'total_customers': total_customers,
        'low_stock_count': low_stock_qs.count(),
        'out_of_stock_count': out_of_stock_qs.count(),
        'expired_count': expired_qs.count(),
        'expiring_today_count': expiring_today_qs.count(),
        'expiring_week_count': expiring_week_qs.count(),
        'category_data': json.dumps(category_data, default=str),
        'expiry_chart': json.dumps(expiry_chart),
        'stock_chart': json.dumps(stock_chart),
        'recent_activities': recent_activities,
        'recent_bills': recent_bills,
        'today': today,
    }
    return render(request, 'dashboard/dashboard.html', context)


# =============================================================================
# MEDICINE MANAGEMENT (Full CRUD)
# =============================================================================
@login_required
def medicine_list(request):
    medicines = Medicine.objects.select_related('category', 'supplier').all()

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    expiry_status = request.GET.get('expiry_status', '')

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | Q(code__icontains=query) |
            Q(batch_number__icontains=query) | Q(manufacturer__icontains=query)
        )
    if category_id:
        medicines = medicines.filter(category_id=category_id)

    # Filter by dynamically computed properties (evaluate in python since
    # expiry/stock status are not persisted fields).
    medicines = list(medicines)
    if stock_status:
        medicines = [m for m in medicines if m.stock_status == stock_status]
    if expiry_status:
        medicines = [m for m in medicines if m.expiry_status == expiry_status]

    paginator = Paginator(medicines, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'query': query,
        'category_id': category_id,
        'stock_status': stock_status,
        'expiry_status': expiry_status,
    }
    return render(request, 'medicines/list.html', context)


@login_required
def medicine_add(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save()
            log_activity(request.user, 'medicine_added', f'Added medicine "{medicine.name}" ({medicine.code})')
            messages.success(request, f'Medicine "{medicine.name}" added successfully.')
            return redirect('core:medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'medicines/form.html', {'form': form, 'title': 'Add Medicine', 'mode': 'add'})


@login_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            medicine = form.save()
            log_activity(request.user, 'medicine_updated', f'Updated medicine "{medicine.name}" ({medicine.code})')
            messages.success(request, f'Medicine "{medicine.name}" updated successfully.')
            return redirect('core:medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'medicines/form.html',
                  {'form': form, 'title': 'Edit Medicine', 'mode': 'edit', 'medicine': medicine})


@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = medicine.name
        medicine.delete()
        log_activity(request.user, 'medicine_deleted', f'Deleted medicine "{name}"')
        messages.success(request, f'Medicine "{name}" deleted successfully.')
        return redirect('core:medicine_list')
    return redirect('core:medicine_list')


@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine.objects.select_related('category', 'supplier'), pk=pk)
    return render(request, 'medicines/detail.html', {'medicine': medicine})


# =============================================================================
# INVENTORY MANAGEMENT
# =============================================================================
@login_required
def inventory_list(request):
    medicines = Medicine.objects.select_related('category', 'supplier').all()

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    if query:
        medicines = medicines.filter(Q(name__icontains=query) | Q(code__icontains=query))

    medicines = list(medicines)
    if status:
        medicines = [m for m in medicines if m.stock_status == status]

    total_stock_value = sum((m.quantity * m.purchase_price for m in medicines), start=Decimal('0'))

    paginator = Paginator(medicines, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'total_stock_value': total_stock_value,
    }
    context['low_stock_count'] = MedicineQueryHelper.low_stock().count()
    context['out_of_stock_count'] = MedicineQueryHelper.out_of_stock().count()
    context['in_stock_count'] = Medicine.objects.count() - context['low_stock_count'] - context['out_of_stock_count']
    return render(request, 'inventory/list.html', context)


# =============================================================================
# SMART MEDICINE EXPIRY ALERT CENTER
# =============================================================================
@login_required
def expiry_alert_center(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    medicines = Medicine.objects.select_related('category', 'supplier').all()
    if query:
        medicines = medicines.filter(Q(name__icontains=query) | Q(code__icontains=query) |
                                      Q(batch_number__icontains=query))
    medicines = list(medicines)

    counts = {
        'expired': 0, 'expiring_today': 0, 'expiring_tomorrow': 0,
        'expiring_week': 0, 'expiring_month': 0, 'safe': 0,
    }
    for m in medicines:
        counts[m.expiry_status] += 1

    if status:
        medicines = [m for m in medicines if m.expiry_status == status]

    # Sort soonest-to-expire first
    medicines.sort(key=lambda m: m.days_to_expiry)

    paginator = Paginator(medicines, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'counts': counts,
    }
    return render(request, 'expiry/center.html', context)


# =============================================================================
# CATEGORY (used inline from Medicine Management page)
# =============================================================================
@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
        else:
            messages.error(request, 'Could not add category. Please check the name is unique.')
    return redirect(request.META.get('HTTP_REFERER', 'core:medicine_list'))


# =============================================================================
# CUSTOMER MANAGEMENT
# =============================================================================
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        customers = customers.filter(Q(name__icontains=query) | Q(phone__icontains=query) |
                                      Q(email__icontains=query))
    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'customers/list.html', {'page_obj': page_obj, 'query': query})


@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            log_activity(request.user, 'customer_added', f'Added customer "{customer.name}"')
            messages.success(request, f'Customer "{customer.name}" added successfully.')
            return redirect('core:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/form.html', {'form': form, 'title': 'Add Customer', 'mode': 'add'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('core:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/form.html',
                  {'form': form, 'title': 'Edit Customer', 'mode': 'edit', 'customer': customer})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f'Customer "{name}" deleted successfully.')
        return redirect('core:customer_list')
    return redirect('core:customer_list')


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    purchase_history = customer.bills.select_related().prefetch_related('items__medicine').all()
    return render(request, 'customers/detail.html', {'customer': customer, 'purchase_history': purchase_history})


# =============================================================================
# SUPPLIER MANAGEMENT
# =============================================================================
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        suppliers = suppliers.filter(Q(name__icontains=query) | Q(phone__icontains=query) |
                                      Q(email__icontains=query))
    paginator = Paginator(suppliers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'suppliers/list.html', {'page_obj': page_obj, 'query': query})


@login_required
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            log_activity(request.user, 'supplier_added', f'Added supplier "{supplier.name}"')
            messages.success(request, f'Supplier "{supplier.name}" added successfully.')
            return redirect('core:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/form.html', {'form': form, 'title': 'Add Supplier', 'mode': 'add'})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('core:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/form.html',
                  {'form': form, 'title': 'Edit Supplier', 'mode': 'edit', 'supplier': supplier})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{name}" deleted successfully.')
        return redirect('core:supplier_list')
    return redirect('core:supplier_list')


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    medicines = supplier.medicines.all()
    return render(request, 'suppliers/detail.html', {'supplier': supplier, 'medicines': medicines})


# =============================================================================
# BILLING
# =============================================================================
@login_required
def bill_list(request):
    bills = Bill.objects.select_related('customer', 'created_by').all()
    query = request.GET.get('q', '').strip()
    if query:
        bills = bills.filter(Q(bill_number__icontains=query) | Q(customer__name__icontains=query))
    paginator = Paginator(bills, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'billing/list.html', {'page_obj': page_obj, 'query': query})


@login_required
def medicine_search_ajax(request):
    """AJAX endpoint used by the billing screen's live medicine search."""
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        ).select_related('category')[:15]
        for m in medicines:
            results.append({
                'id': m.medicine_id,
                'name': m.name,
                'code': m.code,
                'price': str(m.selling_price),
                'gst': str(m.gst_percentage),
                'quantity_available': m.quantity,
                'expiry_status': m.expiry_status,
                'expiry_label': m.expiry_status_label,
                'is_sellable': m.is_sellable,
                'expiry_date': m.expiry_date.strftime('%d-%m-%Y'),
            })
    return JsonResponse({'results': results})


@login_required
def bill_create(request):
    customers = Customer.objects.filter(is_active=True)

    if request.method == 'POST':
        medicine_ids = request.POST.getlist('medicine_id[]')
        quantities = request.POST.getlist('quantity[]')
        customer_id = request.POST.get('customer') or None
        payment_method = request.POST.get('payment_method', 'cash')
        payment_status = request.POST.get('payment_status', 'paid')
        try:
            discount_percent = Decimal(request.POST.get('discount_percent') or '0')
        except InvalidOperation:
            discount_percent = Decimal('0')

        if not medicine_ids:
            messages.error(request, 'Please add at least one medicine to the bill.')
            return render(request, 'billing/create.html', {'customers': customers})

        errors = []
        line_items = []
        for mid, qty in zip(medicine_ids, quantities):
            try:
                medicine = Medicine.objects.get(pk=mid)
                qty = int(qty)
            except (Medicine.DoesNotExist, ValueError):
                continue

            if qty <= 0:
                continue
            if medicine.is_expired:
                errors.append(f'"{medicine.name}" has expired and cannot be billed.')
                continue
            if qty > medicine.quantity:
                errors.append(f'Only {medicine.quantity} unit(s) of "{medicine.name}" available in stock.')
                continue
            line_items.append((medicine, qty))

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'billing/create.html', {'customers': customers})

        if not line_items:
            messages.error(request, 'No valid medicines were added to the bill.')
            return render(request, 'billing/create.html', {'customers': customers})

        with transaction.atomic():
            bill = Bill.objects.create(
                customer_id=customer_id,
                created_by=request.user,
                payment_method=payment_method,
                payment_status=payment_status,
                discount_percent=discount_percent,
            )
            for medicine, qty in line_items:
                BillItem.objects.create(
                    bill=bill, medicine=medicine, quantity=qty,
                    unit_price=medicine.selling_price, gst_percent=medicine.gst_percentage,
                )
                medicine.quantity -= qty
                medicine.save(update_fields=['quantity'])
            bill.recalculate_totals()
            log_activity(request.user, 'bill_created',
                         f'Created bill {bill.bill_number} - Total ₹{bill.grand_total}')

        messages.success(request, f'Bill {bill.bill_number} generated successfully.')
        return redirect('core:bill_invoice', pk=bill.pk)

    return render(request, 'billing/create.html', {'customers': customers})


@login_required
def bill_invoice(request, pk):
    bill = get_object_or_404(Bill.objects.select_related('customer', 'created_by').prefetch_related('items__medicine'), pk=pk)
    return render(request, 'billing/invoice.html', {'bill': bill})
