from flask import Blueprint, render_template, request, redirect, url_for, session
from models import get_products, add_order

shop_bp = Blueprint('shop', name)

@shop_bp.route('/shop')
def shop():
    products = get_products()
    return render_template('shop.html', products=products)

@shop_bp.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {'id': product_id, 'name': product['name'], 'price': product['price'], 'quantity': 1}
        session['cart'] = cart
    return redirect(url_for('shop.shop'))

@shop_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@shop_bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    email = request.form['email']
    address = request.form['address']
    add_order(email, address, cart)
    session['cart'] = {}
    return redirect(url_for('shop.shop'))