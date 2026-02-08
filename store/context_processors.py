from .models import Category, Cart, Wishlist

def store_context(request):
    """Context processor for global store data"""
    context = {
        'bd_currency_symbol': '৳',
        'bd_vat_percentage': 15,
        'default_shipping_cost': 120,
    }
    
    # Get all categories for navigation
    categories = Category.objects.all()[:8]  # Limit to 8 for navigation
    context['categories'] = categories
    
    # Cart item count
    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.total_items
        except Cart.DoesNotExist:
            cart_items_count = 0
    else:
        # For anonymous users, use session
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart_items_count = cart.total_items
            except Cart.DoesNotExist:
                cart_items_count = 0
        else:
            cart_items_count = 0
    
    context['cart_items_count'] = cart_items_count
    
    # Wishlist count
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_count = wishlist.products.count()
        except Wishlist.DoesNotExist:
            wishlist_count = 0
    
    context['wishlist_count'] = wishlist_count
    
    return context