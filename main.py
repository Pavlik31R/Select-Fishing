from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
from models import init_db
from routes.feedback import feedback_bp
from routes.admin import admin_bp
from routes.shop import shop_bp
from routes.api import api_bp
from auth import auth
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User
from flask_login import LoginManager
from models import db

app = Flask(__name__)
app.secret_key = '9b1f743b85c8c4268a9e3f0af45d4b6e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ініціалізація бази даних
init_db()
db.init_app(app)

with app.app_context():
    db.create_all()  # Створення таблиць через SQLAlchemy
    init_db()        # Створення таблиць для SQLite

login_manager = LoginManager(app)  # Ініціалізація flask_login
login_manager.login_view = 'auth.login'  # Перенаправлення на сторінку логіну

@login_manager.user_loader

def load_user(user_id):

    return User.query.get(int(user_id))

# Реєстрація блюпрінтів
app.register_blueprint(feedback_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(api_bp)
app.register_blueprint(auth)

# Головна сторінка
@app.route('/')
def home():
    return render_template('home.html')

# Сторінка команди
@app.route('/team')
def team():
    return render_template('team.html')

# Сторінка "Про нас"
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

# Сторінка корзини
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    discounted_price = session.get('discounted_price', total)  # Знижена ціна або загальна, якщо знижки немає
    return render_template('cart.html', cart=cart, total=total, discounted_price=discounted_price)

# Маршрут для застосування промокоду
@app.route('/apply_discount', methods=['POST'])
def apply_discount():
    data = request.get_json()
    promo_code = data.get('promo_code')

    # Якщо промокод коректний
    if promo_code == "2024":
        cart = session.get('cart', {})
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        discounted_price = total * 0.8  # Знижка 20%
        
        session['discounted_price'] = discounted_price  # Зберігаємо знижену ціну в сесії
        return jsonify({"success": True, "discounted_price": discounted_price})
    else:
        return jsonify({"success": False, "message": "Невірний промокод"})

# Маршрут для очищення корзини
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('Корзина успішно очищена.', 'success')
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)