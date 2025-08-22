from flask import Blueprint,jsonify, render_template, redirect, url_for, flash,request,current_app
from flask_login import login_user, current_user, logout_user, login_required
from .forms import LoginForm, RegistrationForm
from .models import  User, Product, CartItem, Sale
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import func
import os
import json
from werkzeug.utils import secure_filename
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

import pandas as pd

from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA




main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
customer = Blueprint('customer', __name__)
admin = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('customer.customer_home'))
    
    
    return render_template("first.html")

from flask import render_template
from flask_login import current_user, login_required

@customer.route('/customer/profile')
@login_required
def profile():
    purchases = Sale.query.filter_by(user_id=current_user.id).all()  # Fetch purchases for the logged-in user
    return render_template('customer/profile.html', user=current_user, purchases=purchases)




@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('customer.customer_home'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and check_password_hash(user.password, form.password.data):
                # Log in user
                login_user(user, remember=form.remember.data)
                
                # Get next page from query parameters
                next_page = request.args.get('next')
                
                # Redirect to appropriate dashboard
                if next_page:
                    return redirect(next_page)
                elif user.is_admin:
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('customer.customer_home'))
            else:
                flash('Invalid email or password. Please try again.', 'error')
        
        except Exception as e:
            flash(f'An error occurred during login. Please try again.', 'error')
            current_app.logger.error(f'Login error: {str(e)}')
    
    # If form validation fails, errors will be shown in the template
    return render_template('auth/login.html', form=form)

from .models import db
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('auth/register.html', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                is_admin=False  # Default to regular customer
            )
            
            # Add and commit to database
            db.session.add(user)
            db.session.commit()
            
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            
            current_app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('main.home'))

@customer.route('/home')
@login_required
def customer_home():
    query = request.args.get('query')  # Get search query if any
    if query:
        products = Product.query.filter(
            (Product.name.ilike(f'%{query}%')) | (Product.category.ilike(f'%{query}%'))
        ).all()
    else:
        products = Product.query.order_by(Product.id).all()  # Default to all products
    
    return render_template('customer/home.html', products=products)

@admin.route('/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

@customer.route('/cart')
@login_required
def cart():
    # Get all cart items for the current user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    cart_details = []
    for item in cart_items:
        product = Product.query.get(item.product_id)  # Fetch product by ID
        
        if product:  # Check if product exists
            if item.quantity > product.stock:  # Check if quantity is available
                flash(f"Insufficient stock for {product.name}. Only {product.stock} available.", "danger")
                item.quantity = product.stock  # Optional: Adjust quantity to available stock
                db.session.commit()
            
            cart_details.append({
                'product': {  # Include product details in a nested dictionary
                    'id': product.id,
                    'name': product.name,
                    'price': product.price  # Safe to access price here
                },
                'quantity': item.quantity,
            })
        else:
            # Product does not exist
            flash(f"Product with ID {item.product_id} does not exist and has been removed from your cart.", "warning")
            db.session.delete(item)  # Remove from cart if product not found
            db.session.commit()  # Commit the changes
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('customer/cart.html', cart_items=cart_details, total_price=total_price)


@customer.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    try:
        if request.method == 'POST':
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

            if not cart_items:
                
                return redirect(url_for('customer.cart'))

            total_price = 0

            for item in cart_items:
                product = Product.query.get(item.product_id)

                if product:
                    if item.quantity <= product.stock:
                        sale = Sale.create_sale(current_user, product, item.quantity)
                        if sale:
                            total_price += sale.total_price  # Accumulate total price
                        else:
                            flash(f'Insufficient stock for {product.name}.', 'danger')
                            return redirect(url_for('customer.cart'))
                    else:
                        flash(f'Insufficient stock for {product.name}.', 'danger')
                        return redirect(url_for('customer.cart'))

            # Clear the cart after successful billing
            for item in cart_items:
                db.session.delete(item)
            db.session.commit()
            flash('Your purchase has been confirmed!', 'success')
            
            return redirect(url_for('customer.home'))  # Redirect to the homepage

        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return render_template('customer/billing.html', cart_items=cart_items, total_price=total_price)

    except Exception as e:
        db.session.rollback()
       
        return redirect(url_for('customer.cart'))










@admin.route('/manage-products', methods=['GET', 'POST'])
@login_required
def manage_products():
    if not current_user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('main.home'))
    
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    products = Product.query.all()
    
    # Handle form submission for adding a new product
    if request.method == 'POST':
        product_name = request.form.get('name')
        product_price = float(request.form.get('price', 0))
        
        product_category = request.form.get('category')
        product_stock = int(request.form.get('stock', 0))
        product_description = request.form.get('description')
        image = request.files.get('image')

        new_product = Product(
            name=product_name,
            price=product_price,
            category=product_category,
            stock=product_stock,
            description=product_description
        )
        if image and allowed_file(image.filename):
          filename = secure_filename(image.filename)
          image_path = os.path.join(UPLOAD_FOLDER, filename)
          image.save(image_path)
          
          new_product.image_url = url_for('static', filename='images/' + filename)
        else:
           new_product.image_url = url_for('static', filename='images/default_image.jpeg')
            

        db.session.add(new_product)
        db.session.commit()
        
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/manage_products.html', products=products)

@admin.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('main.home'))
    
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = request.form.get('price')
        product.category = request.form.get('category')
        product.stock = request.form.get('stock')
        product.description = request.form.get('description')

        db.session.commit()
        
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/edit_product.html', product=product)

@admin.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.')
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('admin.manage_products'))


# In routes.py

@admin.route('/manage-customers')
@login_required
def manage_customers():
    if not current_user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('main.home'))
    
    # Fetch customers here. For example, you might use:
    customers = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin/manage_customers.html', customers=customers)



from flask import render_template, redirect, url_for, flash, json
from flask_login import login_required, current_user
from sqlalchemy import func
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.linear_model import LinearRegression
import seaborn as sns


@admin.route('/sales_analysis')
@login_required
def sales_analysis():
    if not current_user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('main.home'))

    # Fetch sales data
    sales_data_query = (
        db.session.query(
            Product.name,
            func.sum(Sale.quantity).label('total_sales'),
            func.sum(Sale.total_price).label('total_revenue')
        )
        .join(Sale, Product.id == Sale.product_id)
        .group_by(Product.id)
        .all()
    )

    sales_data = {
        "labels": [record[0] for record in sales_data_query],
        "values": [record[1] for record in sales_data_query],
        "revenues": [record[2] for record in sales_data_query]
    }

    # Calculate total sales for the day
    today_sales = db.session.query(func.sum(Sale.total_price)).filter(func.date(Sale.date) == func.current_date()).scalar() or 0

    # Identify the most sold product
    most_sold_product = max(sales_data_query, key=lambda x: x.total_sales) if sales_data_query else None

    # Fetch most frequent customer
    most_frequent_customer_query = (
        db.session.query(
            User.username,
            func.count(Sale.id).label('purchase_count')
        )
        .join(Sale, User.id == Sale.user_id)
        .group_by(User.id)
        .order_by(func.count(Sale.id).desc())
        .first()
    )

    # Fetch max product purchased by each customer
    max_product_by_customer = (
        db.session.query(
            User.username,
            Product.name,
            func.sum(Sale.quantity).label('max_quantity')
        )
        .join(Sale, User.id == Sale.user_id)
        .join(Product, Product.id == Sale.product_id)
        .group_by(User.id, Product.id)
        .order_by(func.sum(Sale.quantity).desc())
        .first()
    )

    # Remaining stock
    remaining_stock = db.session.query(
        Product.name,
        Product.stock
    ).all()

    # Predictions (using linear regression)
    sales_df = pd.DataFrame(sales_data_query, columns=['product', 'total_sales', 'total_revenue'])
    sales_df['product_index'] = np.arange(len(sales_df))

    # Fit linear regression for total sales prediction
    model = LinearRegression().fit(sales_df[['product_index']], sales_df['total_sales'])
    predicted_sales = model.predict(sales_df[['product_index']])
    
    # Generate additional graphs
    bar_chart, line_chart, histogram_chart, pie_chart, scatter_chart, box_chart, heatmap_chart = generate_charts(sales_data, predicted_sales)

    return render_template(
        'admin/sales_analysis.html',
        sales_data=json.dumps(sales_data),
        today_sales=today_sales,
        most_sold_product=most_sold_product,
        most_frequent_customer=most_frequent_customer_query,
        max_product_by_customer=max_product_by_customer,
        remaining_stock={name: stock for name, stock in remaining_stock},
        bar_chart=bar_chart,
        line_chart=line_chart,
        histogram_chart=histogram_chart,
        predicted_sales=json.dumps(predicted_sales.tolist()),
        pie_chart=pie_chart,
        scatter_chart=scatter_chart,
        box_chart=box_chart,
        heatmap_chart=heatmap_chart
    )

def generate_charts(sales_data, predicted_sales):
    # Bar chart
    fig, ax = plt.subplots()
    ax.bar(sales_data['labels'], sales_data['values'], color='blue', label='Actual Sales')
    ax.plot(sales_data['labels'], predicted_sales, color='red', label='Predicted Sales', marker='o')
    ax.set_ylabel('Total Sales')
    ax.set_title('Sales by Product with Predictions')
    ax.legend()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    bar_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    # Line chart for revenue
    fig, ax = plt.subplots()
    ax.plot(sales_data['labels'], sales_data['revenues'], marker='o', color='orange')
    ax.set_ylabel('Total Revenue')
    ax.set_title('Revenue by Product')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    line_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    # Histogram for sales distribution
    fig, ax = plt.subplots()
    ax.hist(sales_data['values'], bins=10, color='green', alpha=0.7)
    ax.set_xlabel('Sales Amount')
    ax.set_ylabel('Frequency')
    ax.set_title('Sales Distribution Histogram')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    histogram_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    # Pie chart for sales distribution by product
    fig, ax = plt.subplots()
    ax.pie(sales_data['values'], labels=sales_data['labels'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title('Sales Distribution by Product')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    pie_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    # Scatter Plot for sales
    fig, ax = plt.subplots()
    ax.scatter(sales_data['labels'], sales_data['values'], color='purple')
    ax.set_xlabel('Products')
    ax.set_ylabel('Total Sales')
    ax.set_title('Sales Scatter Plot')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    scatter_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    # Box Plot for sales data
    fig, ax = plt.subplots()
    ax.boxplot(sales_data['values'])
    ax.set_ylabel('Sales Amount')
    ax.set_title('Sales Box Plot')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    box_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    # Heatmap for sales data
    heatmap_data = pd.DataFrame(sales_data['values'], index=sales_data['labels'], columns=['Sales'])
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', cbar=True, ax=ax)
    ax.set_title('Sales Heatmap')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    heatmap_chart = base64.b64encode(buf.getvalue()).decode('utf8')

    return bar_chart, line_chart, histogram_chart, pie_chart, scatter_chart, box_chart, heatmap_chart







@customer.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)  # This will raise a 404 if product doesn't exist
    if product.stock <= 0:
        flash('This product is out of stock!')
        return redirect(url_for('customer.cart'))

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if cart_item:
        if cart_item.quantity < product.stock:  # Check if there's enough stock
            cart_item.quantity += 1
            
        else:
            flash('Not enough stock available!')
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)
       

    db.session.commit()
    return redirect(url_for('customer.cart'))


@admin.route('/delete-customer/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.')
        return redirect(url_for('main.home'))

    customer = User.query.get_or_404(customer_id)

    # Explicitly delete sales associated with the customer
    sales_to_delete = Sale.query.filter_by(user_id=customer.id).all()
    for sale in sales_to_delete:
        db.session.delete(sale)

    db.session.delete(customer)
    db.session.commit()

    
    return redirect(url_for('admin.manage_customers'))









@customer.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        quantity = request.form.get('quantity', type=int)
        
        if quantity is not None and quantity > 0:
            product = Product.query.get(product_id)
            if product and quantity <= product.stock:  # Ensure the requested quantity doesn't exceed stock
                cart_item.quantity = quantity
                db.session.commit()
                
            elif product and quantity > product.stock:
                flash('Not enough stock available for this quantity.')
            else:
                flash('Product does not exist.')
        else:
            flash('Quantity must be greater than zero.')
    else:
        flash('Product not found in cart.')
    
    return redirect(url_for('customer.cart'))



@customer.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    # Fetch the cart item to remove it
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        db.session.delete(cart_item)  # Remove the cart item from the session
        db.session.commit()  # Commit the changes to the database
        flash('Product removed from cart!')  # Flash a success message
    else:
        flash('Product not found in cart.')  # Flash a message if the item is not found
    
    return redirect(url_for('customer.cart'))  # Redirect back to the cart

@customer.route('/search')
def search_products():
    query = request.args.get('query')
    if query:
        products = Product.query.filter(
            (Product.name.ilike(f'%{query}%')) | (Product.category.ilike(f'%{query}%'))
        ).all()
    else:
        products = Product.query.all()  # Fetch all products if no query is provided

    return render_template('customer/home.html', products=products)




