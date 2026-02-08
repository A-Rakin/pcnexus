from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='fas fa-microchip')
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    CURRENCY_CHOICES = [
        ('BDT', 'Bangladeshi Taka (৳)'),
        ('USD', 'US Dollar ($)'),
    ]
    
    WARRANTY_CHOICES = [
        ('0', 'No warranty'),
        ('1', '1 Year'),
        ('2', '2 Years'),
        ('3', '3 Years'),
        ('5', '5 Years'),
        ('lifetime', 'Lifetime'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Pricing for Bangladesh market
    price_bdt = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BDT')
    discount_percentage = models.PositiveIntegerField(default=0)
    
    # Stock and availability for Bangladesh
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_imported = models.BooleanField(default=True)
    import_duty_included = models.BooleanField(default=True)
    
    # Product specifications
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    warranty = models.CharField(max_length=20, choices=WARRANTY_CHOICES, default='1')
    
    # Ratings and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    
    # Featured and promotional flags
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    
    # Images
    main_image = models.ImageField(upload_to='products/main/')
    image_1 = models.ImageField(upload_to='products/extra/', blank=True)
    image_2 = models.ImageField(upload_to='products/extra/', blank=True)
    image_3 = models.ImageField(upload_to='products/extra/', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def current_price(self):
        if self.discount_percentage > 0:
            discount = (self.price_bdt * self.discount_percentage) / 100
            return self.price_bdt - discount
        return self.price_bdt
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity < 10:
            return f"Only {self.stock_quantity} left"
        else:
            return "In Stock"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.id} - {self.user.username if self.user else 'Anonymous'}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.product.current_price * self.quantity

class Order(models.Model):
    PAYMENT_METHODS = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Customer information for Bangladesh
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # Shipping address in Bangladesh
    division = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    address = models.TextField()
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment and status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class BangladeshLocation(models.Model):
    DIVISIONS = [
        ('dhaka', 'Dhaka'),
        ('chittagong', 'Chittagong'),
        ('khulna', 'Khulna'),
        ('rajshahi', 'Rajshahi'),
        ('barisal', 'Barisal'),
        ('sylhet', 'Sylhet'),
        ('rangpur', 'Rangpur'),
        ('mymensingh', 'Mymensingh'),
    ]
    
    division = models.CharField(max_length=20, choices=DIVISIONS)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=120)
    delivery_time = models.CharField(max_length=50, default='3-5 business days')
    
    class Meta:
        unique_together = ['division', 'district', 'upazila']
    
    def __str__(self):
        return f"{self.upazila}, {self.district}, {self.division}"