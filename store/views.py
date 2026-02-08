from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem, 
    Wishlist, BangladeshLocation
)
from .forms import (
    UserRegistrationForm, UserLoginForm, CheckoutForm,
    BangladeshShippingForm
)

def home(request):
    """Home page view with featured products for Bangladesh market"""
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_available=True
    )[:8]
    
    best_sellers = Product.objects.filter(
        is_best_seller=True,
        is_available=True
    )[:4]
    
    new_arrivals = Product.objects.filter(
        is_new_arrival=True,
        is_available=True
    )[:4]
    
    categories = Category.objects.all()[:6]
    
    # Bangladesh specific context
    bd_locations = BangladeshLocation.objects.all()[:10]
    
    context = {
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'bd_locations': bd_locations,
        'page_title': 'PC Components & Laptops in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/home.html', context)

def product_list(request):
    """Product listing with filters for Bangladesh market"""
    products = Product.objects.filter(is_available=True)
    
    # Apply filters
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price_bdt__gte=min_price)
    if max_price:
        products = products.filter(price_bdt__lte=max_price)
    
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__iexact=brand)
    
    warranty = request.GET.get('warranty')
    if warranty:
        products = products.filter(warranty=warranty)
    
    stock_status = request.GET.get('stock')
    if stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=0)
    elif stock_status == 'low_stock':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lt=10)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['price_low', 'price_high', '-average_rating', '-created_at']:
        if sort_by == 'price_low':
            products = products.order_by('price_bdt')
        elif sort_by == 'price_high':
            products = products.order_by('-price_bdt')
        else:
            products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique brands for filter
    brands = Product.objects.filter(is_available=True).values_list(
        'brand', flat=True
    ).distinct()
    
    context = {
        'products': page_obj,
        'brands': brands,
        'page_title': 'PC Components in Bangladesh | PC Nexus',
        'total_products': products.count(),
    }
    
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """Product detail view with Bangladesh pricing"""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    reviews = product.reviews.all()[:10]
    
    # Calculate USD price if not set
    if not product.price_usd:
        # Approximate conversion rate (adjust as needed)
        product.price_usd = round(product.price_bdt / 110, 2)
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'page_title': f'{product.name} in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/product_detail.html', context)

def cart_view(request):
    """Cart view with Bangladesh shipping calculations"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    context = {
        'cart': cart,
        'shipping_cost': 120,  # Default shipping in BDT
        'vat_percentage': 15,  # VAT in Bangladesh
    }
    
    # Calculate totals with VAT
    subtotal = cart.total_price
    shipping = context['shipping_cost']
    vat = (subtotal + shipping) * 0.15
    total = subtotal + shipping + vat
    
    context.update({
        'subtotal': subtotal,
        'vat': vat,
        'total': total,
    })
    
    return render(request, 'store/cart.html', context)

@login_required
def checkout(request):
    """Checkout view with Bangladesh address fields"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
        else:
            messages.error(request, 'Your cart is empty')
            return redirect('store:cart')
    
    if cart.total_items == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('store:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        shipping_form = BangladeshShippingForm(request.POST)
        
        if form.is_valid() and shipping_form.is_valid():
            # Create order
            order = form.save(commit=False)
            
            # Set Bangladesh shipping details
            shipping_data = shipping_form.cleaned_data
            order.division = shipping_data['division']
            order.district = shipping_data['district']
            order.upazila = shipping_data['upazila']
            order.address = shipping_data['address']
            order.postal_code = shipping_data['postal_code']
            
            # Calculate shipping cost based on location
            try:
                location = BangladeshLocation.objects.get(
                    division=order.division,
                    district=order.district,
                    upazila=order.upazila
                )
                order.shipping_cost = location.shipping_cost
            except BangladeshLocation.DoesNotExist:
                order.shipping_cost = 120  # Default shipping
            
            # Calculate totals
            order.subtotal = cart.total_price
            order.total = order.subtotal + order.shipping_cost
            
            # Add VAT for Bangladesh
            vat = order.total * 0.15
            order.total += vat
            
            if request.user.is_authenticated:
                order.user = request.user
            
            # Generate order number
            import uuid
            order.order_number = str(uuid.uuid4())[:8].upper()
            
            order.save()
            
            # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.current_price
                )
            
            # Clear cart
            cart.items.all().delete()
            
            # Clear session cart for anonymous users
            if not request.user.is_authenticated:
                if 'cart_id' in request.session:
                    del request.session['cart_id']
            
            messages.success(request, 'Order placed successfully!')
            return redirect('store:checkout_success', order_number=order.order_number)
    else:
        if request.user.is_authenticated:
            initial_data = {
                'customer_name': request.user.get_full_name() or request.user.username,
                'customer_email': request.user.email,
            }
            form = CheckoutForm(initial=initial_data)
        else:
            form = CheckoutForm()
        
        shipping_form = BangladeshShippingForm()
    
    context = {
        'form': form,
        'shipping_form': shipping_form,
        'cart': cart,
        'bd_divisions': BangladeshLocation.DIVISIONS,
    }
    
    return render(request, 'store/checkout.html', context)

def product_search(request):
    """Search products for Bangladesh market"""
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query),
            is_available=True
        )
    else:
        products = Product.objects.filter(is_available=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'query': query,
        'total_results': products.count(),
        'page_title': f'Search: {query} | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/product_search.html', context)

# Bangladesh specific views
def shipping_info(request):
    """Shipping information for Bangladesh"""
    locations = BangladeshLocation.objects.all()
    
    context = {
        'locations': locations,
        'page_title': 'Delivery Information in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/shipping_info.html', context)

def payment_methods(request):
    """Payment methods available in Bangladesh"""
    context = {
        'page_title': 'Payment Methods in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/payment_methods.html', context)

def warranty_info(request):
    """Warranty information for Bangladesh"""
    context = {
        'page_title': 'Warranty & Returns in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/warranty.html', context)

def contact(request):
    """Contact page for Bangladesh"""
    context = {
        'page_title': 'Contact Us | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/contact.html', context)

def faq(request):
    """FAQ for Bangladesh customers"""
    faqs = [
        {
            'question': 'ডেলিভারি চার্জ কত?',
            'answer': 'ঢাকা শহরে ৳৬০, ঢাকার বাইরে ৳১২০-৳২০০। ৳২০০০+ অর্ডারে ফ্রি শিপিং।'
        },
        {
            'question': 'ডেলিভারি সময় কত?',
            'answer': 'ঢাকায় ১-২ দিন, বিভাগীয় শহরে ২-৪ দিন, অন্যান্য এলাকায় ৩-৭ দিন।'
        },
        {
            'question': 'পেমেন্ট মেথড কি কি?',
            'answer': 'ক্যাশ অন ডেলিভারি, bKash, Nagad, Rocket, ব্যাংক ট্রান্সফার, ক্রেডিট/ডেবিট কার্ড।'
        },
        {
            'question': 'প্রোডাক্টের ওয়ারেন্টি কিভাবে পাবো?',
            'answer': 'সকল প্রোডাক্টের ওয়ারেন্টি কার্ড প্রদান করা হয়। সার্ভিস সেন্টারে সরাসরি ক্লেইম করতে পারবেন।'
        },
        {
            'question': 'রিটার্ন/এক্সচেঞ্জ পলিসি কি?',
            'answer': 'ডেলিভারির ৭ দিনের মধ্যে ত্রুটিপূর্ণ প্রোডাক্ট রিটার্ন/এক্সচেঞ্জ করতে পারবেন।'
        },
    ]
    
    context = {
        'faqs': faqs,
        'page_title': 'Frequently Asked Questions | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/faq.html', context)

def store_locator(request):
    """Store locator for Bangladesh"""
    stores = [
        {
            'name': 'PC Nexus Banani',
            'address': 'Level 5, House 10, Road 12, Block C, Banani, Dhaka',
            'phone': '+880 9611-111111',
            'hours': '10:00 AM - 8:00 PM (Sat-Thu)',
            'services': ['Pickup', 'Service Center', 'Demo Unit']
        },
        {
            'name': 'PC Nexus Dhanmondi',
            'address': 'House 15, Road 8/A, Dhanmondi, Dhaka',
            'phone': '+880 9611-111112',
            'hours': '10:00 AM - 8:00 PM (Sat-Thu)',
            'services': ['Pickup', 'Service Center']
        },
        {
            'name': 'PC Nexus Chittagong',
            'address': 'Shop 5-6, Tower Plaza, GEC Circle, Chittagong',
            'phone': '+880 9611-111113',
            'hours': '10:00 AM - 8:00 PM (Sat-Thu)',
            'services': ['Pickup', 'Service Center']
        },
    ]
    
    context = {
        'stores': stores,
        'page_title': 'Store Locator in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/store_locator.html', context)