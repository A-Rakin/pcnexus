from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, BangladeshLocation

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'payment_method']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

class BangladeshShippingForm(forms.Form):
    DIVISION_CHOICES = BangladeshLocation.DIVISIONS
    
    division = forms.ChoiceField(
        choices=DIVISION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'})
    )
    upazila = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Upazila/Thana'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
        max_length=500
    )
    postal_code = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'})
    )

class ProductFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', 'Newest'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('-average_rating', 'Highest Rated'),
    ]
    
    WARRANTY_CHOICES = [
        ('', 'Any Warranty'),
        ('0', 'No warranty'),
        ('1', '1 Year'),
        ('2', '2 Years'),
        ('3', '3 Years'),
        ('5', '5 Years'),
        ('lifetime', 'Lifetime'),
    ]
    
    STOCK_CHOICES = [
        ('', 'Any Stock Status'),
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    min_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price (৳)', 'class': 'form-control'})
    )
    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price (৳)', 'class': 'form-control'})
    )
    brand = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Brand', 'class': 'form-control'})
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