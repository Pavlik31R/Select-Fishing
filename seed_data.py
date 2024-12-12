from models import get_db_connection, init_db

def seed_products():
    init_db()  # Спочатку ініціалізуємо базу даних
    conn = get_db_connection()
    products = [
        ('Футболка', 299.99, '/api/placeholder/200/200'),
        ('Джинси', 799.99, '/api/placeholder/200/200'),
        ('Кросівки', 1299.99, '/api/placeholder/200/200'),
        ('Куртка', 1599.99, '/api/placeholder/200/200'),
        ('Шапка', 199.99, '/api/placeholder/200/200'),
        ('Шкарпетки', 49.99, '/api/placeholder/200/200'),
        ('Рюкзак', 699.99, '/api/placeholder/200/200'),
        ('Годинник', 2499.99, '/api/placeholder/200/200'),
    ]
    
    conn.executemany('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', products)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed_products()
    print("Тестові продукти додано до бази даних.")