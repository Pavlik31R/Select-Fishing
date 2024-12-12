from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Ініціалізація SQLAlchemy
db = SQLAlchemy()

# Модель User для SQLAlchemy
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Таблиця називається users
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

# SQLite-з'єднання для роботи зі специфічними таблицями без SQLAlchemy
def get_db_connection():
    conn = sqlite3.connect('data/db.sqlite')
    conn.row_factory = sqlite3.Row  # Повертає результати у форматі словника
    return conn

# Ініціалізація бази даних для SQLite
def init_db():
    conn = get_db_connection()
    # Створення таблиці users, якщо вона не використовується через SQLAlchemy
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    # Створення інших таблиць
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    conn.commit()
    conn.close()

# Операції з користувачами
# Додавання користувача
def add_user(email, password, name):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
            (email, hashed_password, name)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Помилка додавання користувача: {e}")
    finally:
        conn.close()

# Отримання користувача за email
def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

# Перевірка існування користувача
def user_exists(email):
    return get_user_by_email(email) is not None

# Перевірка користувача за паролем
def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        return True  # Пароль вірний
    return False  # Пароль або email невірні

# Отримання всіх користувачів
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

# Робота з товарами
def get_products(search_query=""):
    conn = get_db_connection()
    if search_query:
        products = conn.execute(
            'SELECT * FROM products WHERE name LIKE ?',
            ('%' + search_query + '%',)
        ).fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return products

# Додавання замовлення
def add_order(email, address, cart):
    conn = get_db_connection()
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO orders (email, address, total_price, status, date) VALUES (?, ?, ?, ?, ?)',
        (email, address, total_price, 'New', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    order_id = cur.lastrowid
    for item in cart.values():
        cur.execute(
            'INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)',
            (order_id, item['id'], item['quantity'])
        )
    conn.commit()
    conn.close()

# Отримання замовлень
def get_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return orders

# Отримання деталей замовлення
def get_order_details(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = conn.execute('''
        SELECT oi.quantity, p.name, p.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    conn.close()
    return order, items

# Оновлення статусу замовлення
def update_order_status(order_id, status):
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()

# Видалення замовлення
def delete_order(order_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

# Додавання відгуку
def add_feedback(name, email, message):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO feedback (name, email, message, date) VALUES (?, ?, ?, ?)',
        (name, email, message, now)
    )
    conn.commit()
    conn.close()

# Отримання всіх відгуків
def get_feedback():
    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback ORDER BY date DESC').fetchall()
    conn.close()
    return feedback

# Запуск функції ініціалізації бази даних, якщо модуль запускається як основний
if __name__ == "__main__":
    init_db()
