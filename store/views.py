from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem, 
    Wishlist, BangladeshLocation, ProductReview
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
    
    context = {
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'categories': categories,
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
    
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'brands': brands,
        'categories': categories,
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

def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'page_title': 'Product Categories | PC Nexus Bangladesh',
    }
    return render(request, 'store/category_list.html', context)

def category_detail(request, slug):
    """Show products in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'page_title': f'{category.name} in Bangladesh | PC Nexus',
    }
    return render(request, 'store/category_detail.html', context)

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    if product.stock_quantity == 0:
        messages.error(request, 'This product is out of stock.')
        return redirect('store:product_detail', slug=product.slug)
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart, created = Cart.objects.get_or_create(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_items_count': cart.total_items,
            'message': f'{product.name} added to cart.'
        })
    
    return redirect('store:cart')

@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            messages.error(request, 'You do not have permission to modify this cart.')
            return redirect('store:cart')
    else:
        cart_id = request.session.get('cart_id')
        if not cart_id or cart_item.cart.id != int(cart_id):
            messages.error(request, 'You do not have permission to modify this cart.')
            return redirect('store:cart')
    
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'{product_name} removed from cart.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_items_count': cart_item.cart.total_items,
            'message': f'{product_name} removed from cart.'
        })
    
    return redirect('store:cart')

@require_POST
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
    else:
        cart_id = request.session.get('cart_id')
        if not cart_id or cart_item.cart.id != int(cart_id):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > cart_item.product.stock_quantity:
        return JsonResponse({
            'success': False,
            'error': f'Only {cart_item.product.stock_quantity} items available.'
        })
    
    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    cart = cart_item.cart
    
    return JsonResponse({
        'success': True,
        'item_total': cart_item.total_price,
        'subtotal': cart.total_price,
        'cart_items_count': cart.total_items,
        'shipping': 120,
        'vat': (cart.total_price + 120) * 0.15,
        'total': cart.total_price + 120 + ((cart.total_price + 120) * 0.15)
    })

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
    
    # Calculate totals with VAT for Bangladesh
    subtotal = cart.total_price
    shipping_cost = 120  # Default shipping in BDT
    vat = (subtotal + shipping_cost) * 0.15  # 15% VAT
    total = subtotal + shipping_cost + vat
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'vat': vat,
        'total': total,
        'vat_percentage': 15,
        'page_title': 'Shopping Cart | PC Nexus Bangladesh',
    }
    
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
                'customer_phone': '',
            }
            form = CheckoutForm(initial=initial_data)
        else:
            form = CheckoutForm()
        
        shipping_form = BangladeshShippingForm()
    
    # Calculate totals for display
    subtotal = cart.total_price
    shipping_cost = 120
    vat = (subtotal + shipping_cost) * 0.15
    total = subtotal + shipping_cost + vat
    
    context = {
        'form': form,
        'shipping_form': shipping_form,
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'vat': vat,
        'total': total,
        'bd_divisions': BangladeshLocation.DIVISIONS,
        'page_title': 'Checkout | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/checkout.html', context)

def checkout_success(request, order_number):
    """Order success page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
        'page_title': 'Order Confirmed | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/checkout_success.html', context)

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

# Authentication Views
def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                
                # Merge anonymous cart with user cart if exists
                cart_id = request.session.get('cart_id')
                if cart_id:
                    try:
                        anonymous_cart = Cart.objects.get(id=cart_id)
                        user_cart, created = Cart.objects.get_or_create(user=user)
                        
                        for item in anonymous_cart.items.all():
                            user_item, created = CartItem.objects.get_or_create(
                                cart=user_cart,
                                product=item.product,
                                defaults={'quantity': item.quantity}
                            )
                            if not created:
                                user_item.quantity += item.quantity
                                user_item.save()
                        
                        anonymous_cart.delete()
                        del request.session['cart_id']
                    except Cart.DoesNotExist:
                        pass
                
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/login.html', context)

def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to PC Nexus.')
            
            # Create wishlist for new user
            Wishlist.objects.create(user=user)
            
            return redirect('store:home')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/register.html', context)

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store:home')

# Account Views
@login_required
def account(request):
    """User account dashboard"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    context = {
        'user': request.user,
        'orders': orders,
        'wishlist': wishlist,
        'page_title': 'My Account | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/account.html', context)

@login_required
def order_history(request):
    """User order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Order History | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/order_history.html', context)

@login_required
def order_detail(request, order_number):
    """Order detail view"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
        'page_title': f'Order #{order.order_number} | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/order_detail.html', context)

# Wishlist Views
@login_required
def wishlist_view(request):
    """User wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    context = {
        'wishlist': wishlist,
        'page_title': 'My Wishlist | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if wishlist.products.filter(id=product.id).exists():
        messages.info(request, 'This product is already in your wishlist.')
    else:
        wishlist.products.add(product)
        messages.success(request, f'{product.name} added to wishlist.')
    
    return redirect('store:product_detail', slug=product.slug)

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        messages.success(request, f'{product.name} removed from wishlist.')
    
    return redirect('store:wishlist')

# Special Pages for Bangladesh
def pc_builder(request):
    """PC Builder tool page"""
    context = {
        'page_title': 'PC Builder Tool | PC Nexus Bangladesh',
    }
    return render(request, 'store/pc_builder.html', context)

def deals(request):
    """Deals and offers page"""
    discounted_products = Product.objects.filter(
        discount_percentage__gt=0,
        is_available=True
    )
    
    context = {
        'discounted_products': discounted_products,
        'page_title': 'Deals & Offers | PC Nexus Bangladesh',
    }
    return render(request, 'store/deals.html', context)

def laptops(request):
    """Laptops page"""
    laptop_category, created = Category.objects.get_or_create(
        name='Laptops',
        defaults={'slug': 'laptops', 'icon': 'fas fa-laptop', 'description': 'Laptops and notebooks'}
    )
    
    laptops = Product.objects.filter(category=laptop_category, is_available=True)
    
    context = {
        'laptops': laptops,
        'category': laptop_category,
        'page_title': 'Laptops in Bangladesh | PC Nexus',
    }
    return render(request, 'store/laptops.html', context)

def peripherals(request):
    """Peripherals page"""
    peripherals_category, created = Category.objects.get_or_create(
        name='Peripherals',
        defaults={'slug': 'peripherals', 'icon': 'fas fa-keyboard', 'description': 'Keyboards, mice, monitors, and other peripherals'}
    )
    
    peripherals = Product.objects.filter(category=peripherals_category, is_available=True)
    
    context = {
        'peripherals': peripherals,
        'category': peripherals_category,
        'page_title': 'PC Peripherals in Bangladesh | PC Nexus',
    }
    return render(request, 'store/peripherals.html', context)

# Support Pages for Bangladesh
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

def support(request):
    """Support page"""
    context = {
        'page_title': 'Support Center | PC Nexus Bangladesh',
    }
    return render(request, 'store/support.html', context)

def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here you would typically save to database
        # For now, just show success message
        messages.success(request, 'Thank you for subscribing to our newsletter!')
    
    return redirect('store:home')

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                
                # Merge anonymous cart with user cart if exists
                cart_id = request.session.get('cart_id')
                if cart_id:
                    try:
                        anonymous_cart = Cart.objects.get(id=cart_id)
                        user_cart, created = Cart.objects.get_or_create(user=user)
                        
                        for item in anonymous_cart.items.all():
                            user_item, created = CartItem.objects.get_or_create(
                                cart=user_cart,
                                product=item.product,
                                defaults={'quantity': item.quantity}
                            )
                            if not created:
                                user_item.quantity += item.quantity
                                user_item.save()
                        
                        anonymous_cart.delete()
                        del request.session['cart_id']
                    except Cart.DoesNotExist:
                        pass
                
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/login.html', context)

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
    
    # Apply filters from request
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_slug = request.GET.get('category')
    stock_status = request.GET.get('stock')
    sort_by = request.GET.get('sort', '-created_at')
    
    if min_price:
        products = products.filter(price_bdt__gte=min_price)
    if max_price:
        products = products.filter(price_bdt__lte=max_price)
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=0)
    elif stock_status == 'low_stock':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lt=10)
    
    # Sorting
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
    
    # Get categories for filter
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'total_results': products.count(),
        'page_title': f'Search: {query} | PC Nexus Bangladesh',
    }
    
    return render(request, 'store/product_search.html', context)

def laptops(request):
    """Laptops page"""
    # Get or create laptops category
    laptop_category, created = Category.objects.get_or_create(
        name='Laptops',
        defaults={
            'slug': 'laptops', 
            'icon': 'fas fa-laptop', 
            'description': 'Laptops and notebooks for gaming, work, and study'
        }
    )
    
    # Get laptops
    laptops = Product.objects.filter(category=laptop_category, is_available=True)
    
    # Apply filters
    brand = request.GET.get('brand')
    if brand:
        laptops = laptops.filter(brand__iexact=brand)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        laptops = laptops.filter(price_bdt__gte=min_price)
    if max_price:
        laptops = laptops.filter(price_bdt__lte=max_price)
    
    stock_status = request.GET.get('stock')
    if stock_status == 'in_stock':
        laptops = laptops.filter(stock_quantity__gt=0)
    elif stock_status == 'low_stock':
        laptops = laptops.filter(stock_quantity__gt=0, stock_quantity__lt=10)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['price_low', 'price_high', '-average_rating', '-created_at']:
        if sort_by == 'price_low':
            laptops = laptops.order_by('price_bdt')
        elif sort_by == 'price_high':
            laptops = laptops.order_by('-price_bdt')
        else:
            laptops = laptops.order_by(sort_by)
    
    context = {
        'laptops': laptops,
        'category': laptop_category,
        'page_title': 'Laptops in Bangladesh | PC Nexus',
    }
    
    return render(request, 'store/laptops.html', context)


def pc_builder(request):
    context = {
        'title': 'PC Builder Tool',
    }
    return render(request, 'store/pc_builder.html', context)