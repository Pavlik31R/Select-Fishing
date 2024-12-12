from flask import Blueprint, render_template, request, redirect, url_for, session
from models import get_products, add_order

shop_bp = Blueprint('shop', __name__)

# Маршрут для магазину з підтримкою пагінації та пошуку
@shop_bp.route('/shop', methods=['GET', 'POST'])
def shop():
    # Отримуємо параметр пошуку, якщо він є
    search_query = request.args.get('search', '', type=str)
    
    # Отримуємо продукти з можливим фільтром
    products = get_products(search_query)
    
    # Кількість товарів на сторінку
    PER_PAGE = 8
    page = request.args.get('page', 1, type=int)  # Отримуємо номер сторінки з параметра 'page'
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_products = products[start:end]  # Отримуємо продукти для поточної сторінки

    total_pages = (len(products) + PER_PAGE - 1) // PER_PAGE  # Рахуємо загальну кількість сторінок
    return render_template(
        'shop.html',
        products=paginated_products,
        page=page,
        total_pages=total_pages,
        search_query=search_query  # Повертаємо параметр пошуку для форми
    )

# Додавання товару в корзину
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

# Сторінка корзини
@shop_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

# Оформлення замовлення
@shop_bp.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    email = request.form['email']
    address = request.form['address']
    add_order(email, address, cart)
    session['cart'] = {}  # Очистити корзину після оформлення
    return redirect(url_for('shop.shop'))
