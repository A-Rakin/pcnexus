# store/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
from django.urls import reverse
from django.utils.text import slugify  # Add this import

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='fas fa-microchip')
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

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
    is_active = models.BooleanField(default=True)  # Add this for compatibility
    is_imported = models.BooleanField(default=True)
    import_duty_included = models.BooleanField(default=True)
    
    # Product specifications
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    warranty = models.CharField(max_length=20, choices=WARRANTY_CHOICES, default='1')
    
    # Additional fields for templates
    short_description = models.TextField(blank=True, null=True)
    highlights = models.TextField(blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Ratings and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # Alias
    
    # Featured and promotional flags
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)  # Alias
    is_new_arrival = models.BooleanField(default=False)
    
    # Images
    main_image = models.ImageField(upload_to='products/main/')
    image = models.ImageField(upload_to='products/main/', blank=True, null=True)  # Alias
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
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Set aliases for compatibility
        if not self.old_price and self.discount_percentage > 0:
            self.old_price = self.price_bdt
        
        if not self.rating:
            self.rating = self.average_rating
        
        if not self.is_bestseller:
            self.is_bestseller = self.is_best_seller
        
        if not self.image:
            self.image = self.main_image
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    @property
    def current_price(self):
        if self.discount_percentage > 0:
            discount = (self.price_bdt * self.discount_percentage) / 100
            return self.price_bdt - discount
        return self.price_bdt
    
    @property
    def price(self):
        """Alias for price_bdt for template compatibility"""
        return self.price_bdt
    
    @property
    def stock(self):
        """Alias for stock_quantity for template compatibility"""
        return self.stock_quantity
    
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
    
    # Properties for template compatibility
    @property
    def highlights_as_list(self):
        if self.highlights:
            return [h.strip() for h in self.highlights.split('\n') if h.strip()]
        return []
    
    @property
    def specifications_as_dict(self):
        if self.specifications:
            try:
                return json.loads(self.specifications)
            except:
                return {}
        return {}
    
    def get_quick_specs(self):
        """Return first 5 specifications"""
        specs = self.specifications_as_dict
        return list(specs.items())[:5]
    
    def get_full_specs(self):
        """Return all specifications"""
        specs = self.specifications_as_dict
        return list(specs.items())
    
    @property
    def discount_percentage_calculated(self):
        """Calculate discount percentage if old_price exists"""
        if self.old_price and self.old_price > self.price_bdt:
            return round(((self.old_price - self.price_bdt) / self.old_price) * 100)
        return None
    
    @property
    def save_amount(self):
        """Calculate save amount if old_price exists"""
        if self.old_price and self.old_price > self.price_bdt:
            return self.old_price - self.price_bdt
        return 0
    
    @property
    def emi_amount(self):
        """Calculate EMI amount (12 months)"""
        return round(float(self.current_price) / 12, 2)
    
    @property
    def image_url(self):
        """Get image URL for JSON serialization"""
        if self.main_image:
            return self.main_image.url
        return ''

# REMOVE THE DUPLICATE Product CLASS DEFINITION FROM HERE DOWN
# Everything below this line should be removed

# Add the ProductImage model (properly indented, NOT inside Product class)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'id']
    
    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

class FAQ(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"FAQ: {self.question[:50]}..."

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