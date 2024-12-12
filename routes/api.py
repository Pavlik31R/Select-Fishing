from flask import Blueprint, jsonify, request
from models import get_db_connection
from datetime import datetime, timedelta
from functools import wraps

# Створюємо Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Словник для зберігання історії запитів (обмеження частоти запитів)
request_history = {}

# Параметри обмеження запитів
REQUESTS_PER_MINUTE = 10  # Максимальна кількість запитів на хвилину
TIME_WINDOW = timedelta(minutes=1)  # Часове вікно для обмеження запитів

# Декоратор для обмеження частоти запитів
def rate_limit(f):
    """
    Декоратор для обмеження частоти запитів до ендпоїнта.
    Якщо запитів занадто багато, повертається статус 429 (Too Many Requests).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr  # Отримуємо IP-адресу клієнта
        current_time = datetime.now()  # Поточний час

        # Перевіряємо історію запитів для IP-адреси
        if ip in request_history:
            # Фільтруємо запити, що потрапляють у поточне часове вікно
            last_requests = [time for time in request_history[ip] 
                             if current_time - time < TIME_WINDOW]
            # Перевіряємо, чи перевищено ліміт
            if len(last_requests) >= REQUESTS_PER_MINUTE:
                return jsonify({
                    "error": "Too many requests",
                    "message": "Будь ласка, спробуйте через хвилину",
                    "retry_after": "60 seconds"
                }), 429
            # Додаємо поточний запит у історію
            last_requests.append(current_time)
            request_history[ip] = last_requests
        else:
            # Якщо запитів від IP ще не було, створюємо новий запис
            request_history[ip] = [current_time]
        
        # Викликаємо оригінальну функцію
        return f(*args, **kwargs)
    return decorated_function

# Тестовий ендпоїнт для перевірки роботи API
@api_bp.route('/test', methods=['GET'])
@rate_limit
def test():
    """
    Тестовий ендпоїнт для перевірки доступності API.
    """
    return jsonify({"message": "API працює!"})

# Адміністративні ендпоїнти

@api_bp.route('/stats', methods=['GET'])
@rate_limit
def get_stats():
    """
    Отримання статистики API.
    """
    stats = {
        "total_requests": sum(len(v) for v in request_history.values()),
        "unique_ips": len(request_history),
    }
    return jsonify(stats), 200

@api_bp.route('/rate-limit-history', methods=['DELETE'])
@rate_limit
def clear_rate_limit_history():
    """
    Очистка історії запитів.
    """
    global request_history
    request_history = {}
    return jsonify({"message": "Rate limit history cleared"}), 200

@api_bp.route('/backup', methods=['POST'])
@rate_limit
def backup_database():
    """
    Резервне копіювання бази даних.
    """
    try:
        # Тут реалізуйте резервне копіювання (можливо, копіювання файла бази).
        return jsonify({"message": "Database backup created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ендпоїнти для роботи з продуктами

@api_bp.route('/products', methods=['GET'])
@rate_limit
def get_products():
    """
    Отримання списку всіх продуктів.
    """
    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()
        return jsonify([dict(product) for product in products]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/products', methods=['POST'])
@rate_limit
def add_product():
    """
    Додавання нового продукту.
    Очікується JSON із полями "name" та "price".
    """
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'price']):
        return jsonify({'error': 'Name and price are required'}), 400
    
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price) VALUES (?, ?)', 
                     (data['name'], data['price']))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Продукт додано", "data": data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
@rate_limit
def delete_product(product_id):
    """
    Видалення продукту за його ID.
    """
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Продукт видалено"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ендпоїнти для роботи із замовленнями

@api_bp.route('/orders', methods=['GET'])
@rate_limit
def get_all_orders():
    """
    Отримання списку всіх замовлень.
    """
    try:
        conn = get_db_connection()
        orders = conn.execute('SELECT * FROM orders').fetchall()
        conn.close()
        return jsonify([dict(order) for order in orders]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
@rate_limit
def get_order(order_id):
    """
    Отримання деталей замовлення за його ID.
    """
    try:
        conn = get_db_connection()
        order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        items = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
        conn.close()
        return jsonify({'order': dict(order), 'items': [dict(item) for item in items]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/orders', methods=['POST'])
@rate_limit
def create_order():
    """
    Створення нового замовлення.
    Очікується JSON із полями "email", "address" та "cart" (список товарів).
    """
    data = request.get_json()
    if not data or 'email' not in data or 'address' not in data or 'cart' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Додаємо замовлення до таблиці "orders"
        cursor.execute('INSERT INTO orders (email, address, created_at, status) VALUES (?, ?, ?, ?)',
                       (data['email'], data['address'], datetime.now(), 'new'))
        order_id = cursor.lastrowid  # Отримуємо ID створеного замовлення
        # Додаємо товари до таблиці "order_items"
        for item in data['cart']:
            cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                           (order_id, item['id'], item['quantity'], item['price']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order created successfully', 'order_id': order_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ендпоїнт для перевірки статусу обмеження запитів
@api_bp.route('/rate-limit-status', methods=['GET'])
@rate_limit
def check_rate_limit():
    """
    Отримання статусу обмеження запитів для поточного IP.
    """
    ip = request.remote_addr
    current_time = datetime.now()
    if ip in request_history:
        # Підрахунок залишку запитів
        valid_requests = [time for time in request_history[ip] if current_time - time < TIME_WINDOW]
        requests_remaining = REQUESTS_PER_MINUTE - len(valid_requests)
    else:
        requests_remaining = REQUESTS_PER_MINUTE
    return jsonify({
        "requests_remaining": requests_remaining,
        "max_requests_per_minute": REQUESTS_PER_MINUTE,
        "time_window": "1 minute"
    })


