🖥️ PC Nexus Bangladesh - E-commerce Platform
A comprehensive e-commerce platform for PC components and accessories in Bangladesh, built with Django.

📋 Table of Contents
Features

Tech Stack

Installation

Project Structure

Database Models

Key Features

Screenshots

API Endpoints

Running Tests

Deployment

Contributing

License

✨ Features
🛍️ E-commerce Features
Product Catalog with categories, brands, and filters

Shopping Cart with session management

Checkout Process with Bangladesh-specific payment methods

Order Management with status tracking

Wishlist functionality

Product Reviews & Ratings

Stock Management with low stock alerts

🇧🇩 Bangladesh Specific
Bangladeshi Taka (৳) pricing

Localized Payment Methods (bKash, Nagad, Rocket, Cash on Delivery)

Bangladesh Division/District/Upazila based shipping

Import Duty Included pricing

Local Warranty Information

🛠️ Advanced Features
PC Builder Tool with compatibility checking

Product Comparison

Recently Viewed Products

Newsletter Subscription

FAQ System

Store Locator for Bangladesh

Responsive Design for mobile and desktop

🚀 Tech Stack
Backend
Django 5.2.5 - Python web framework

PostgreSQL - Primary database (SQLite for development)

Django ORM - Database abstraction

Django Templates - Server-side rendering

Frontend
HTML5, CSS3, JavaScript - Core web technologies

Bootstrap 5 - Responsive CSS framework

Font Awesome - Icons

Custom CSS with CSS variables

JavaScript ES6+ for interactivity

Additional Tools
Django Humanize - Better number formatting

Django Messages Framework - User notifications

Django Authentication - User management

Session Management - Cart and user sessions

💻 Installation
Prerequisites
Python 3.13.2+

PostgreSQL (optional, SQLite for development)

pip (Python package manager)

Virtual environment (recommended)

Step-by-Step Installation
Clone the repository

``` bash
git clone https://github.com/yourusername/pc-nexus-bangladesh.git
cd pc-nexus-bangladesh
Create virtual environment
```
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies
```
bash
pip install -r requirements.txt
Configure environment variables
Create a .env file in the project root:
```
```bash
env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
Apply migrations
```
```bash
python manage.py makemigrations
python manage.py migrate
Create superuser
```
```bash
python manage.py createsuperuser
Collect static files
```
```bash
python manage.py collectstatic
Run development server
```
```bash
python manage.py runserver
Visit http://127.0.0.1:8000 to see the application.
```
📁 Project Structure
text
pcnexus/
├── store/                          # Main Django app
│   ├── migrations/                 # Database migrations
│   ├── templates/store/           # HTML templates
│   │   ├── base.html             # Base template
│   │   ├── home.html             # Home page
│   │   ├── category.html         # Category page
│   │   ├── product_details.html  # Product detail page
│   │   ├── cart.html             # Shopping cart
│   │   ├── checkout.html         # Checkout page
│   │   └── account.html          # User account
│   ├── models.py                  # Database models
│   ├── views.py                   # View functions
│   ├── urls.py                    # URL routing
│   └── forms.py                   # Django forms
├── pcnexus/                       # Project settings
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL config
│   └── wsgi.py                   # WSGI config
├── static/                        # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── media/                         # User uploaded files
├── requirements.txt              # Python dependencies
└── manage.py                     # Django management script
🗄️ Database Models
Core Models
Product
python
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category)
    price_bdt = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=100)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    # ... more fields
Category
python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50)
    description = models.TextField(blank=True)
Order
python
class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    # ... Bangladesh shipping fields
🔑 Key Features in Detail
1. PC Builder Tool
  Component Compatibility Checking
  Price Calculation in Bangladeshi Taka
  Quick Build Templates (Budget, Mid-range, High-end)
  Save & Share Builds

2. Shopping Experience
  Advanced Product Filtering (price, brand, warranty, stock)
  Multiple Image Support per product
  Product Specifications in JSON format
  Customer Reviews & Ratings

3. User Management
  User Registration & Authentication
  Order History Tracking
  Wishlist Management
  Address Book for Bangladesh addresses

4. Admin Features
  Product Management (CRUD operations)
  Order Processing with status updates
  Stock Management
  Customer Management
