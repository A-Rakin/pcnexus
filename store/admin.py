from django.contrib import admin
from .models import (
    Category, Product, ProductReview, Cart, CartItem,
    Order, OrderItem, Wishlist, BangladeshLocation
)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_bdt', 'stock_quantity', 'is_available', 'is_featured']
    list_filter = ['category', 'is_available', 'is_featured', 'brand']
    search_fields = ['name', 'brand', 'model']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'total', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'division']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']

class BangladeshLocationAdmin(admin.ModelAdmin):
    list_display = ['division', 'district', 'upazila', 'shipping_cost', 'delivery_time']
    list_filter = ['division']
    search_fields = ['district', 'upazila']

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReview)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Wishlist)
admin.site.register(BangladeshLocation, BangladeshLocationAdmin)