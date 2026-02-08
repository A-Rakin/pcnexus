from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, BangladeshLocation
import re

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True, help_text='Format: +8801XXXXXXXXX or 01XXXXXXXXX')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+8801XXXXXXXXX'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Validate Bangladesh phone number
        if not re.match(r'^(?:\+88|88)?(01[3-9]\d{8})$', phone):
            raise forms.ValidationError('Please enter a valid Bangladesh phone number (e.g., +8801XXXXXXXXX)')
        
        # Format to +880 format
        if phone.startswith('88'):
            phone = '+' + phone
        elif phone.startswith('01'):
            phone = '+88' + phone
        elif not phone.startswith('+880'):
            phone = '+880' + phone[2:] if phone.startswith('880') else '+880' + phone
        
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class CheckoutForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'payment_method']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+8801XXXXXXXXX'}),
        }
    
    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Validate Bangladesh phone number
        if not re.match(r'^(?:\+88|88)?(01[3-9]\d{8})$', phone):
            raise forms.ValidationError('Please enter a valid Bangladesh phone number (e.g., +8801XXXXXXXXX)')
        
        # Format to +880 format
        if phone.startswith('88'):
            phone = '+' + phone
        elif phone.startswith('01'):
            phone = '+88' + phone
        elif not phone.startswith('+880'):
            phone = '+880' + phone[2:] if phone.startswith('880') else '+880' + phone
        
        return phone

class BangladeshShippingForm(forms.Form):
    DIVISION_CHOICES = BangladeshLocation.DIVISIONS
    
    division = forms.ChoiceField(
        choices=DIVISION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'division-select'})
    )
    district = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District', 'id': 'district-input'})
    )
    upazila = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Upazila/Thana', 'id': 'upazila-input'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'House, Road, Area details'}),
        max_length=500
    )
    postal_code = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code (Optional)'})
    )

class ProductFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', 'নতুনতম'),
        ('price_low', 'দাম: কম থেকে বেশি'),
        ('price_high', 'দাম: বেশি থেকে কম'),
        ('-average_rating', 'সর্বোচ্চ রেটিং'),
    ]
    
    WARRANTY_CHOICES = [
        ('', 'যেকোনো ওয়ারেন্টি'),
        ('0', 'ওয়ারেন্টি নেই'),
        ('1', '১ বছর'),
        ('2', '২ বছর'),
        ('3', '৩ বছর'),
        ('5', '৫ বছর'),
        ('lifetime', 'লাইফটাইম'),
    ]
    
    STOCK_CHOICES = [
        ('', 'সকল স্টক স্ট্যাটাস'),
        ('in_stock', 'স্টকে আছে'),
        ('low_stock', 'স্টক কম'),
        ('out_of_stock', 'স্টক নেই'),
    ]
    
    min_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'ন্যূনতম দাম (৳)', 'class': 'form-control', 'min': '0'})
    )
    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'সর্বোচ্চ দাম (৳)', 'class': 'form-control', 'min': '0'})
    )
    brand = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'ব্র্যান্ড', 'class': 'form-control'})
    )
    warranty = forms.ChoiceField(
        choices=WARRANTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stock_status = forms.ChoiceField(
        choices=STOCK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )