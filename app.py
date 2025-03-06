from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kissan_e_market_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kissan_market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'farmer' or 'consumer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For farmers
    farm_name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200))
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<Cart Item {self.id}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

# OAuth Setup for Google Login
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID',  # Replace with your Google Client ID
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',  # Replace with your Google Client Secret
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    token_url='https://accounts.google.com/o/oauth2/token',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

# Routes
@app.route('/')
def home():
    products = Product.query.limit(8).all()
    return render_template('index.html', products=products)

@app.route('/products.html')
def redirect_products_html():
    return redirect(url_for('products'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type=user_type
        )
        
        if user_type == 'farmer':
            new_user.farm_name = request.form.get('farm_name')
            new_user.location = request.form.get('location')
            new_user.phone = request.form.get('phone')
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please login.')
        return redirect(url_for('home'))
    
    user_type = request.args.get('type', 'consumer')
    return render_template('register.html', user_type=user_type)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        flash('Login successful')
        return redirect(url_for('home'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('home'))

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)
    
    # Check if user exists, if not create a new one
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            username=user_info['name'],
            email=user_info['email'],
            password=generate_password_hash(user_info['sub']),  # Use Google ID as password
            user_type='consumer'  # Default to consumer for Google login
        )
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    session['user_type'] = user.user_type
    flash('Login successful')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/farmer/dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        flash('Please login as a farmer to access this page')
        return redirect(url_for('home'))
    
    farmer_id = session['user_id']
    products = Product.query.filter_by(farmer_id=farmer_id).all()
    return render_template('farmer_dashboard.html', products=products)

@app.route('/farmer/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        flash('Please login as a farmer to access this page')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        category = request.form.get('category')
        image_url = request.form.get('image_url')
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category=category,
            image_url=image_url,
            farmer_id=session['user_id']
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        flash('Product added successfully')
        return redirect(url_for('farmer_dashboard'))
    
    return render_template('add_product.html')

@app.route('/products')
def products():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    farmer = User.query.get(product.farmer_id)
    return render_template('product_detail.html', product=product, farmer=farmer)

@app.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to add items to cart'}), 401
    
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        new_cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=1
        )
        db.session.add(new_cart_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'})

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login to view your cart')
        return redirect(url_for('home'))
    
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    total = 0
    cart_products = []
    
    for item in cart_items:
        product = Product.query.get(item.product_id)
        total += product.price * item.quantity
        cart_products.append({
            'cart_id': item.id,
            'product': product,
            'quantity': item.quantity
        })
    
    return render_template('cart.html', cart_products=cart_products, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
        
        if not cart_items:
            flash('Your cart is empty')
            return redirect(url_for('cart'))
        
        total = 0
        for item in cart_items:
            product = Product.query.get(item.product_id)
            total += product.price * item.quantity
        
        new_order = Order(
            user_id=session['user_id'],
            total_amount=total,
            status='pending'
        )
        db.session.add(new_order)
        db.session.flush()
        
        for item in cart_items:
            product = Product.query.get(item.product_id)
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price
            )
            db.session.add(order_item)
            product.quantity -= item.quantity
            db.session.delete(item)
        
        db.session.commit()
        flash('Order placed successfully')
        return redirect(url_for('orders'))
    
    return render_template('checkout.html')

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        flash('Please login to view your orders')
        return redirect(url_for('home'))
    
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>')
def order_detail(order_id):
    if 'user_id' not in session:
        flash('Please login to view order details')
        return redirect(url_for('home'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id'] and session['user_type'] != 'farmer':
        flash('You do not have permission to view this order')
        return redirect(url_for('orders'))
    
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    items = []
    
    for item in order_items:
        product = Product.query.get(item.product_id)
        items.append({
            'product': product,
            'quantity': item.quantity,
            'price': item.price
        })
    
    return render_template('order_detail.html', order=order, items=items)

@app.route('/cart_count')
def cart_count():
    if 'user_id' in session:
        count = Cart.query.filter_by(user_id=session['user_id']).count()
        return jsonify({'count': count})
    return jsonify({'count': 0})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)