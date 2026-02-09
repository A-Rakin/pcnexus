from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/search/', views.product_search, name='product_search'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<str:order_number>/', views.checkout_success, name='checkout_success'),
    
    # User Account
    path('account/', views.account, name='account'),
    path('account/orders/', views.order_history, name='order_history'),
    path('account/orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Special Pages for Bangladesh
    path('pc-builder/', views.pc_builder, name='pc_builder'),
    path('deals/', views.deals, name='deals'),
    path('laptops/', views.laptops, name='laptops'),
    path('peripherals/', views.peripherals, name='peripherals'),
    
    # Support Pages
    path('shipping-info/', views.shipping_info, name='shipping_info'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('warranty/', views.warranty_info, name='warranty'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('store-locator/', views.store_locator, name='store_locator'),
    path('support/', views.support, name='support'),

    # Legal Pages - ADD THESE MISSING URLS
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    
    # Other missing pages
    path('about/', views.about, name='about'),
]