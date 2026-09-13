import datetime

from django import forms
from django.utils import timezone

from .models import Category, Customer, Medicine, Supplier


def _text(placeholder, extra_class=''):
    return forms.TextInput(attrs={'class': f'form-control {extra_class}'.strip(), 'placeholder': placeholder})


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'code', 'batch_number', 'category', 'supplier', 'manufacturer',
            'manufacture_date', 'expiry_date', 'purchase_price', 'selling_price',
            'gst_percentage', 'quantity', 'minimum_stock', 'rack_number', 'image', 'status',
        ]
        widgets = {
            'name': _text('e.g. Paracetamol 500mg'),
            'code': _text('e.g. MED-0001'),
            'batch_number': _text('e.g. BATCH-2026-01'),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': _text('Manufacturer name'),
            'manufacture_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'gst_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'rack_number': _text('e.g. R-12'),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        manufacture_date = cleaned_data.get('manufacture_date')
        expiry_date = cleaned_data.get('expiry_date')
        purchase_price = cleaned_data.get('purchase_price')
        selling_price = cleaned_data.get('selling_price')

        if manufacture_date and expiry_date and expiry_date <= manufacture_date:
            self.add_error('expiry_date', 'Expiry date must be after the manufacture date.')

        if purchase_price is not None and selling_price is not None and selling_price < purchase_price:
            self.add_error('selling_price', 'Selling price should not be lower than the purchase price.')

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': _text('Category name'),
            'description': _text('Short description (optional)'),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'gst_number', 'is_active']
        widgets = {
            'name': _text('Company / Supplier name'),
            'contact_person': _text('Contact person name'),
            'phone': _text('10-digit phone number'),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'supplier@email.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'gst_number': _text('GSTIN'),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': _text('Customer full name'),
            'phone': _text('10-digit phone number'),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'customer@email.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BillingCustomerForm(forms.Form):
    """Lightweight form used at the top of the billing screen."""
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True), required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_method = forms.ChoiceField(
        choices=[('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_status = forms.ChoiceField(
        choices=[('paid', 'Paid'), ('pending', 'Pending')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    discount_percent = forms.DecimalField(
        required=False, min_value=0, max_value=100, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'})
    )
