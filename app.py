from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import init_db, get_db
import razorpay
import json
import os

app = Flask(__name__)
app.secret_key = 'winner_sports_secret_key'

RAZORPAY_KEY_ID = 'YOUR_RAZORPAY_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_RAZORPAY_KEY_SECRET'

# Initialize DB
init_db()

@app.route('/')
def home():
    db = get_db()
    featured = db.execute('SELECT * FROM products LIMIT 6').fetchall()
    db.close()
    return render_template('index.html', featured=featured)

@app.route('/products')
def products():
    category = request.args.get('category', 'all')
    db = get_db()
    if category == 'all':
        products = db.execute('SELECT * FROM products').fetchall()
    else:
        products = db.execute('SELECT * FROM products WHERE category = ?', (category,)).fetchall()
    db.close()
    return render_template('products.html', products=products, active_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    db.close()
    return render_template('product_detail.html', product=product)

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    for item in cart:
        item['price'] = float(item['price'])
        item['quantity'] = int(item['quantity'])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == data['id'] and item['size'] == data['size']:
            item['quantity'] += data['quantity']
            session['cart'] = cart
            return jsonify({'success': True, 'cart_count': len(cart)})
    cart.append(data)
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    cart = session.get('cart', [])
    cart = [i for i in cart if not (i['id'] == data['id'] and i['size'] == data['size'])]
    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('cart'))
    for item in cart:
        item['price'] = float(item['price'])
        item['quantity'] = int(item['quantity'])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total=total,
                           razorpay_key=RAZORPAY_KEY_ID)

@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()
    cart = session.get('cart', [])
    total = int(sum(float(item['price']) * int(item['quantity']) for item in cart) * 100)
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    order = client.order.create({'amount': total, 'currency': 'INR', 'payment_capture': 1})
    session['checkout_data'] = data
    return jsonify({'order_id': order['id'], 'amount': total, 'currency': 'INR'})

@app.route('/payment-success', methods=['POST'])
def payment_success():
    data = request.get_json()
    cart = session.get('cart', [])
    checkout_data = session.get('checkout_data', {})
    total = sum(float(item['price']) * int(item['quantity']) for item in cart)
    db = get_db()
    db.execute('''INSERT INTO orders (customer_name, phone, email, address, total, payment_id, status)
                  VALUES (?,?,?,?,?,?,'paid')''',
               (checkout_data.get('name'), checkout_data.get('phone'),
                checkout_data.get('email'), checkout_data.get('address'),
                total, data.get('razorpay_payment_id')))
    order_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    for item in cart:
        db.execute('''INSERT INTO order_items (order_id, product_id, product_name, quantity, size, price)
                      VALUES (?,?,?,?,?,?)''',
                   (order_id, item['id'], item['name'], item['quantity'], item['size'], item['price']))
    db.commit()
    db.close()
    session.pop('cart', None)
    return jsonify({'success': True, 'order_id': order_id})

@app.route('/order-success/<int:order_id>')
def order_success(order_id):
    return render_template('order_success.html', order_id=order_id)

@app.route('/bulk-order')
def bulk_order():
    return render_template('bulk_order.html')

@app.route('/submit-bulk-order', methods=['POST'])
def submit_bulk_order():
    data = request.form
    db = get_db()
    db.execute('''INSERT INTO bulk_orders (team_name, contact_name, phone, email, sport_type,
                  jersey_count, shorts_count, custom_printing, message)
                  VALUES (?,?,?,?,?,?,?,?,?)''',
               (data['team_name'], data['contact_name'], data['phone'], data.get('email'),
                data['sport_type'], data['jersey_count'], data.get('shorts_count'),
                data.get('custom_printing'), data.get('message')))
    db.commit()
    db.close()
    return render_template('bulk_success.html')

@app.route('/admin')
def admin():
    db = get_db()
    orders = db.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    bulk_orders = db.execute('SELECT * FROM bulk_orders ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin.html', orders=orders, bulk_orders=bulk_orders)

if __name__ == '__main__':
    app.run(debug=True)