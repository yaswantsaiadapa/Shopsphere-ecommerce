# ShopSphere ✨ - Your Ultimate Shopping Destination

A full-featured e-commerce web application built with Flask, featuring an intuitive shopping interface, secure authentication, and comprehensive admin management tools.

## 📋 Project Overview

ShopSphere is a Python-based web application that provides a complete shopping platform with dual user roles (Admin and Customer). It uses Flask as the web framework, SQLAlchemy for database management, and offers features like product management, shopping carts, billing, and sales analytics.

## 🏗️ Project Structure

```
ShopSphere-main/
├── config.py                 # Configuration settings for the app
├── run.py                    # Application entry point
├── requirments.txt          # Python dependencies
└── app/
    ├── __init__.py          # Flask app factory and extensions initialization
    ├── models.py            # Database models (User, Product, CartItem, Sale)
    ├── routes.py            # All route handlers and blueprints
    ├── forms.py             # WTForms for login and registration
    ├── create_admin.py      # Script to create admin user
    ├── static/
    │   ├── css/
    │   │   └── style.css    # Custom styling
    │   ├── images/          # Uploaded product images
    │   └── js/
    │       └── cart.js      # Cart functionality scripts
    └── templates/
        ├── base.html        # Base template with navigation
        ├── first.html       # Landing page
        ├── auth/
        │   ├── login.html   # Login page
        │   └── register.html # Registration page
        ├── customer/
        │   ├── home.html    # Customer product listing
        │   ├── cart.html    # Shopping cart page
        │   ├── billing.html # Checkout/billing page
        │   └── profile.html # User profile with purchase history
        └── admin/
            ├── dashboard.html       # Admin dashboard
            ├── manage_products.html # Product management
            ├── edit_product.html    # Edit product details
            ├── manage_customers.html # Customer management
            └── sales_analysis.html  # Sales analytics
```

## 🗄️ Database Models

### User Model
- `id` (Primary Key): Unique user identifier
- `username` (String, Unique): User's login name
- `email` (String, Unique): User's email address
- `password` (String): Hashed password
- `is_admin` (Boolean): Admin privilege flag
- **Relationships**: 
  - `cart_items`: Items in user's cart
  - `purchases`: User's purchase history

### Product Model
- `id` (Primary Key): Unique product identifier
- `name` (String): Product name
- `price` (Float): Product price
- `category` (String): Product category
- `stock` (Integer): Available quantity
- `description` (Text): Detailed product description
- `image_url` (String): Path to product image
- **Relationships**:
  - `cart_items`: Product items in carts
  - `sales`: Sales records for the product

### CartItem Model
- `id` (Primary Key): Unique cart item identifier
- `user_id` (Foreign Key): Reference to User
- `product_id` (Foreign Key): Reference to Product
- `quantity` (Integer): Quantity in cart
- **Methods**:
  - `is_stock_available()`: Check if quantity is available in stock

### Sale Model
- `id` (Primary Key): Unique sale identifier
- `product_id` (Foreign Key): Reference to Product
- `user_id` (Foreign Key): Reference to User (buyer)
- `quantity` (Integer): Quantity purchased
- `total_price` (Float): Total sale amount
- `date` (DateTime): Sale timestamp
- **Methods**:
  - `create_sale()`: Static method to create a sale and update inventory

## 🔐 Authentication & Authorization

### Login System (`/auth/login`)
- Email and password-based authentication
- "Remember Me" functionality
- Password validation using Werkzeug's secure hashing
- Auto-redirects admins to dashboard and customers to home page
- Next-page redirect support for protected routes

### Registration System (`/auth/register`)
- Create new customer accounts
- Email validation and uniqueness checking
- Password confirmation
- Secure password hashing

### Admin Access
- Admin-only routes are protected with `@login_required` decorator
- Authorization check: `is_admin` flag
- Unauthorized users are redirected with flash messages

## 🎯 Key Features

### Customer Features
1. **Product Browsing**
   - View all products with details
   - Search functionality by product name or category
   - Browse by category

2. **Shopping Cart**
   - Add/remove items from cart
   - Adjust quantities
   - Stock availability validation
   - Real-time price calculations

3. **Checkout & Billing**
   - Secure checkout process
   - Order summary with total price
   - Automatic stock deduction upon purchase
   - Order confirmation

4. **Profile Management**
   - View purchase history
   - Track previous orders
   - User profile information

### Admin Features
1. **Product Management**
   - Add new products with images
   - Edit product details (name, price, stock, description)
   - Upload product images (PNG, JPG, JPEG, GIF)
   - Delete products
   - Stock management

2. **Analytics & Reporting**
   - Sales analysis dashboard
   - Statistical visualizations (using Matplotlib and NumPy)
   - Customer management interface

3. **Dashboard**
   - Overview of store operations
   - Quick access to management features

## 🔧 Configuration

### config.py Settings
```python
SECRET_KEY          # Flask secret key (from environment or default)
SQLALCHEMY_DATABASE_URI  # Database URL (SQLite by default)
UPLOAD_FOLDER       # Path for uploaded images: app/static/images
MAX_CONTENT_LENGTH  # Maximum file upload size: 16 MB
```

### Environment Variables (Recommended)
- `SECRET_KEY`: Your Flask secret key for session management
- `DATABASE_URL`: Database connection URL (e.g., sqlite:///store.db)

## 📦 Dependencies

```
Flask             # Web framework
Flask-SQLAlchemy  # ORM for database management
Flask-WTF         # Form handling and CSRF protection
Flask-Login       # User session management
Werkzeug          # WSGI utilities and security
Jinja2            # Template engine
matplotlib        # Data visualization
numpy             # Numerical computing
```

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ShopSphere-main
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirments.txt
```

### 5. Create Admin User
```bash
python app/create_admin.py
```

Default admin credentials:
- Email: `admin@example.com`
- Password: `yourpassword123` (⚠️ Change this!)

### 6. Run the Application
```bash
python run.py
```

The application will start at `http://localhost:5000/`

## 📝 Routes Overview

### Main Routes
- `/` - Landing/home page
- `/auth/login` - User login
- `/auth/register` - User registration
- `/auth/logout` - User logout

### Customer Routes (Protected)
- `/customer/home` - Product listing and browsing
- `/customer/cart` - Shopping cart
- `/customer/billing` - Checkout page
- `/customer/profile` - User profile with purchase history

### Admin Routes (Protected, Admin Only)
- `/admin/dashboard` - Admin dashboard
- `/admin/manage-products` - Add/view/edit products
- `/admin/edit-product/<id>` - Edit specific product
- `/admin/manage-customers` - View and manage customers
- `/admin/sales-analysis` - Sales statistics and analytics

## 🔒 Security Features

1. **Password Security**: Uses Werkzeug's `generate_password_hash` and `check_password_hash`
2. **Form Protection**: Flask-WTF CSRF protection on all forms
3. **Session Management**: Flask-Login for secure user sessions
4. **File Upload Validation**: Only allows specific image formats (PNG, JPG, JPEG, GIF)
5. **File Size Limits**: 16 MB maximum upload size
6. **Secure Filenames**: Uses `secure_filename()` for uploaded files

## 🗂️ File Upload Handling

- **Upload Location**: `app/static/images/`
- **Allowed Formats**: PNG, JPG, JPEG, GIF
- **Max File Size**: 16 MB
- **Default Image**: `default_image.jpeg` for products without custom images

## 💾 Database

- **Default**: SQLite (`store.db`)
- **ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate support (migrations folder present)

### Database Initialization
- Automatic table creation on app startup
- Error handling with rollback on failures

## 🎨 Frontend

- **Responsive Design**: Mobile-friendly HTML/CSS templates
- **Theme Colors**:
  - Primary Blue: `#1e3799`
  - Secondary Blue: `#4a69bd`
  - Primary Yellow: `#ffd32a`
  
- **Features**:
  - Fixed navigation header
  - Hero section on landing page
  - Bootstrap-like responsive layout
  - Font Awesome icons
  - Interactive cart management with JavaScript

## ⚠️ Important Notes

1. **Default Credentials**: Change the default admin password after first setup
2. **Secret Key**: Set a strong `SECRET_KEY` environment variable in production
3. **Database**: Use a production database (PostgreSQL, MySQL) instead of SQLite for production
4. **Debug Mode**: Set `debug=False` in production (`run.py`)

## 🔄 Workflow

### Customer Workflow
1. Register or login to account
2. Browse products on home page
3. Add items to cart
4. Review cart and adjust quantities
5. Proceed to billing/checkout
6. Complete purchase
7. View purchase history in profile

### Admin Workflow
1. Login with admin account
2. Access admin dashboard
3. Manage products (add/edit/delete)
4. View customer information
5. Analyze sales data and statistics
6. Monitor inventory levels

## 📊 Analytics Features

The application includes data visualization capabilities:
- Matplotlib for generating charts
- NumPy for statistical calculations
- Sales trend analysis
- Product performance metrics
- Customer purchase patterns

## 🐛 Error Handling

- Comprehensive try-catch blocks for database operations
- User-friendly flash messages for errors
- Logging for debugging
- Validation on all form inputs
- Stock availability checks before purchase

## 🤝 Contributing

When contributing to this project:
1. Test all authentication flows
2. Verify admin authorization checks
3. Validate file uploads
4. Test cart and billing functionality
5. Check database integrity

## 📄 License

This project is part of the ShopSphere e-commerce platform.

---

**Last Updated**: March 2, 2026  
**Project Name**: ShopSphere ✨  
**Status**: Active Development
