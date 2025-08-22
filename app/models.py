from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from . import db






class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    # This relationship will be populated after Sale class is defined
    purchases = db.relationship('Sale', backref='buyer', lazy='dynamic')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    sales = db.relationship('Sale', backref='product', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    
    def is_stock_available(self):
        return self.quantity <= self.product.stock

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id',ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def create_sale(user, product, quantity):
        if quantity > product.stock:
            return False  # Not enough stock
        
        # Calculate total price for the sale
        total_price = product.price * quantity
        
        # Deduct stock
        product.stock -= quantity
        
        # Create sale record
        new_sale = Sale(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price
        )
        
        db.session.add(new_sale)
        try:
            db.session.commit()
            return new_sale
        except Exception as e:
            db.session.rollback()
        return False
    
    
        
        