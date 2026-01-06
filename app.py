from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, Product, CartItem, User, Order, OrderItem
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database creation moved to main block

def seed_data():
    products = [
        Product(title="MacBook Pro 14-inch", category="laptops", price=1999.99, rating=4.8, image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca4?auto=format&fit=crop&w=500&q=60", description="Apple M1 Pro chip, 16GB RAM, 512GB SSD. The most powerful MacBook Pro ever is here."),
        Product(title="Sony WH-1000XM4", category="headphones", price=348.00, rating=4.7, image_url="https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=500&q=60", description="Industry-leading noise canceling with Dual Noise Sensor technology."),
        Product(title="iPhone 13 Pro", category="phones", price=999.00, rating=4.9, image_url="https://images.unsplash.com/photo-1632661674596-df8be070a5c5?auto=format&fit=crop&w=500&q=60", description="Super Retina XDR display with ProMotion. A dramatic leap in battery life."),
        Product(title="Dell XPS 13", category="laptops", price=1250.00, rating=4.5, image_url="https://images.unsplash.com/photo-1593642632823-8f78536788c6?auto=format&fit=crop&w=500&q=60", description="13.4-inch FHD+ Touch Laptop, Intel Core i7-1185G7, 16GB RAM, 512GB SSD."),
        Product(title="Samsung Galaxy S21", category="phones", price=799.99, rating=4.6, image_url="https://images.unsplash.com/photo-1610945265078-3858a0828671?auto=format&fit=crop&w=500&q=60", description="Pro-grade camera, 8K video, 64MP high res camera."),
        Product(title="Apple Watch Series 7", category="electronics", price=399.00, rating=4.8, image_url="https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?auto=format&fit=crop&w=500&q=60", description="Always-on Retina display. The most durable Apple Watch ever built."),
        Product(title="Bose QuietComfort 45", category="headphones", price=329.00, rating=4.6, image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=500&q=60", description="Iconic quiet, comfort, and sound. The perfect balance of quiet, comfort, and sound."),
        Product(title="iPad Air", category="electronics", price=599.00, rating=4.8, image_url="https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=500&q=60", description="Stunning 10.9-inch Liquid Retina display with True Tone and P3 wide color."),
        Product(title="Logitech MX Master 3", category="electronics", price=99.99, rating=4.9, image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=500&q=60", description="Ultrafast magspeed scrolling, ergonomic design, 4000 DPI sensor."),
        Product(title="Kindle Paperwhite", category="electronics", price=139.99, rating=4.7, image_url="https://images.unsplash.com/photo-1592434134753-a70baf7979d5?auto=format&fit=crop&w=500&q=60", description="Now with a 6.8” display and thinner borders, adjustable warm light, up to 10 weeks of battery life."),
        Product(title="Asus ROG Zephyrus", category="laptops", price=1499.99, rating=4.7, image_url="https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=500&q=60", description="World's most powerful 14-inch gaming laptop. AMD Ryzen 9, RTX 3060."),
        Product(title="Google Pixel 6", category="phones", price=599.00, rating=4.5, image_url="https://images.unsplash.com/photo-1598327105666-5b89351aff23?auto=format&fit=crop&w=500&q=60", description="Powered by Google Tensor, Google's first custom-built processor.")
    ]
    db.session.bulk_save_objects(products)
    db.session.bulk_save_objects(products)
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('signup'))
            
        new_user = User(
            username=username, 
            email=email, 
            password_hash=generate_password_hash(password),
            is_admin=False # Default to regular user
        )
        
        # Make the first user an admin for convenience
        if User.query.count() == 0:
            new_user.is_admin = True
            
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    category = request.args.get('category')
    search = request.args.get('search')
    sort = request.args.get('sort', 'featured')
    
    query = Product.query

    if category and category != 'all':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.title.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))

    if sort == 'low-high':
        query = query.order_by(Product.price.asc())
    elif sort == 'high-low':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
        
    products = query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product.html', product=product)

@app.route('/cart')
def cart():
    cart_items = CartItem.query.all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add-to-cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    item = CartItem.query.filter_by(product_id=id).first()
    if item:
        item.quantity += 1
    else:
        new_item = CartItem(product_id=id, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/update-cart/<int:id>', methods=['POST'])
def update_cart(id):
    data = request.get_json()
    change = data.get('change', 0)
    item = CartItem.query.get_or_404(id)
    item.quantity += change
    if item.quantity <= 0:
        db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/remove-from-cart/<int:id>', methods=['POST'])
def remove_from_cart(id):
    item = CartItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/clear-cart', methods=['POST'])
def clear_cart():
    CartItem.query.delete()
    db.session.commit()
    return jsonify({'success': True})

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.all() # Note: In a real app, filter by user
    if not cart_items:
        return redirect(url_for('cart'))
        
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        address = request.form.get('address')
        city = request.form.get('city')
        zip_code = request.form.get('zip')
        country = request.form.get('country')
        shipping_details = f"{address}, {city}, {zip_code}, {country}"
        
        new_order = Order(
            user_id=current_user.id,
            total_amount=total,
            shipping_details=shipping_details,
            status='Pending'
        )
        db.session.add(new_order)
        db.session.commit()
        
        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            db.session.add(order_item)
            
        # Clear cart
        CartItem.query.delete() # Note: In a real app, filter by user
        db.session.commit()
        
        flash('Order placed successfully!')
        return redirect(url_for('user_orders'))
        
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/orders')
@login_required
def user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/order/update/<int:id>', methods=['POST'])
@login_required
def update_order_status(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    order = Order.query.get_or_404(id)
    order.status = request.form.get('status')
    db.session.commit()
    return redirect(url_for('admin_orders'))

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin only.')
        return redirect(url_for('index'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    title = request.form.get('title')
    price = float(request.form.get('price'))
    description = request.form.get('description')
    category = request.form.get('category')
    rating = float(request.form.get('rating', 0))
    
    # Handle Image Upload
    image_url = request.form.get('image_url') # Fallback to URL
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('static', filename='uploads/' + filename)
    
    new_product = Product(
        title=title,
        price=price,
        description=description,
        image_url=image_url,
        category=category,
        rating=rating
    )
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit/<int:id>', methods=['POST'])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    product = Product.query.get_or_404(id)
    product.title = request.form.get('title')
    product.price = float(request.form.get('price'))
    product.description = request.form.get('description')
    product.category = request.form.get('category')
    product.rating = float(request.form.get('rating'))
    
    # Handle Image Upload
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image_url = url_for('static', filename='uploads/' + filename)
    elif request.form.get('image_url'):
        product.image_url = request.form.get('image_url')
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    product = Product.query.get_or_404(id)
    # Also delete associated cart items to avoid foreign key constraint issues if any
    CartItem.query.filter_by(product_id=id).delete()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            seed_data()
    app.run(debug=True, port=5001)
