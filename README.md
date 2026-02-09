🖥️ PC Nexus Bangladesh - E-commerce Platform
A comprehensive e-commerce platform for PC components and accessories in Bangladesh, built with Django.

📋 Table of Contents

✨ Main Features
• ✅ User authentication and authorization
• 🛒 Shopping cart with session management
• 📱 Responsive mobile-first design

## ✨ **Core Features**

### 🛍️ **E-commerce Essentials**
• **Product Catalog** - Browse by categories, brands, and filters
• **Shopping Cart** - Session-based cart management
• **Checkout Process** - Multiple payment methods
• **Order Management** - Real-time status tracking
• **Wishlist** - Save products for later

### 🇧🇩 **Bangladesh Specific**
• **Local Currency** - Pricing in Bangladeshi Taka (৳)
• **Payment Gateways** - bKash, Nagad, Rocket, Cash on Delivery
• **Shipping** - Division/District/Upazila based delivery
• **Import Duty** - Included in pricing calculations
• **Local Warranty** - Bangladesh-specific warranty information

### 🛠️ **Advanced Tools**
• **PC Builder Tool** - Component compatibility checking
• **Product Comparison** - Side-by-side product comparison
• **Recently Viewed** - Track browsing history
• **Newsletter System** - Email subscriptions
• **Store Locator** - Find physical stores in Bangladesh

## 🚀 **Technology Stack**

### **Backend** (Python/Django)
• Django 5.2.5 - Web framework
• PostgreSQL - Production database
• SQLite - Development database
• Django ORM - Database abstraction

### **Frontend**
• HTML5, CSS3, JavaScript - Core web technologies
• Bootstrap 5 - Responsive framework
• Font Awesome - Icons
• Custom CSS - Theme customization

### **Additional Tools**
• Django Humanize - Number formatting
• Session Management - Cart persistence
• Django Messages - User notifications

## 💻 **Installation Guide**

### **Prerequisites**
• Python 3.13.2 or higher
• pip (Python package manager)
• Virtual environment (recommended)
• PostgreSQL (optional for development)

### **Step-by-Step Setup**
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pc-nexus-bangladesh.git
   cd pc-nexus-bangladesh
  
```bash
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




Screenshots:

<img width="1342" height="674" alt="image" src="https://github.com/user-attachments/assets/9b7ce787-ddec-49cb-bd4b-403f68f92317" />

<img width="1346" height="592" alt="image" src="https://github.com/user-attachments/assets/6f8a92fe-8a9c-4481-98d7-56b16f19a77c" />

<img width="1350" height="598" alt="image" src="https://github.com/user-attachments/assets/7b9cf717-f2f1-4768-a37b-e612cf092b25" />

<img width="1346" height="604" alt="image" src="https://github.com/user-attachments/assets/efd9912f-1f84-4e0f-9941-f37d81557760" />

<img width="1318" height="539" alt="image" src="https://github.com/user-attachments/assets/e7e3bb0a-d5f5-45b4-84d8-5807f9ca3210" />

<img width="1337" height="517" alt="image" src="https://github.com/user-attachments/assets/ed011a16-0a5a-4dae-978d-752bd2c55958" />

<img width="1343" height="668" alt="image" src="https://github.com/user-attachments/assets/437110a1-45f0-4feb-abfe-e735dc605639" />

<img width="1352" height="545" alt="image" src="https://github.com/user-attachments/assets/6389b651-93f3-4119-8d91-e00c55ac7e59" />

<img width="1325" height="585" alt="image" src="https://github.com/user-attachments/assets/15c71d35-92be-4768-b443-d216c7473b51" />

<img width="1341" height="583" alt="image" src="https://github.com/user-attachments/assets/6a0cdf0d-8a11-48b6-a1d4-5eb5d37bcd99" />

<img width="1351" height="606" alt="image" src="https://github.com/user-attachments/assets/357e3fed-441d-4fef-a63d-ff064048c82e" />

<img width="1334" height="585" alt="image" src="https://github.com/user-attachments/assets/5675c83a-c2d9-4d64-b027-d46ba876a28a" />

