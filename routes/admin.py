from datetime import datetime 
from flask import Blueprint, render_template, redirect, url_for, request 
from models import get_db_connection, get_orders, get_order_details, update_order_status, delete_order 
from flask import flash
 
admin_bp = Blueprint('admin', __name__) 
 
# Функція додавання відгуку 
def add_feedback(name, email, message): 
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Поточна дата та час 
    conn = get_db_connection() 
    conn.execute('INSERT INTO feedback (name, email, message, date) VALUES (?, ?, ?, ?)', 
                 (name, email, message, now))  # Вставка дати і часу 
    conn.commit() 
    conn.close() 
 
@admin_bp.route('/admin')
def admin():
    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback').fetchall()
    products = conn.execute('SELECT * FROM products').fetchall()  # Завантаження товарів
    conn.close()
    orders = get_orders()
    return render_template('admin.html', feedback=feedback, orders=orders, products=products)
 
@admin_bp.route('/admin/delete_feedback/<int:id>', methods=['POST']) 
def delete_feedback(id): 
    conn = get_db_connection() 
    conn.execute('DELETE FROM feedback WHERE id = ?', (id,)) 
    conn.commit() 
    conn.close() 
    return redirect(url_for('admin.admin')) 
 
@admin_bp.route('/admin/order/<int:order_id>') 
def order_details(order_id): 
    order, items = get_order_details(order_id) 
    return render_template('order_details.html', order=order, items=items) 
 
@admin_bp.route('/admin/update_order_status/<int:order_id>', methods=['POST']) 
def update_order(order_id): 
    status = request.form['status'] 
    update_order_status(order_id, status) 
    return redirect(url_for('admin.admin')) 
 
@admin_bp.route('/admin/delete_order/<int:order_id>', methods=['POST']) 
def delete_order_route(order_id): 
    delete_order(order_id) 
    return redirect(url_for('admin.admin')) 
 
# Маршрут для обробки форми відгуку 
@admin_bp.route('/feedback', methods=['POST']) 
def feedback(): 
    name = request.form['name'] 
    email = request.form['email'] 
    message = request.form['message'] 
    add_feedback(name, email, message)  # Додаємо відгук з поточним часом 
    return redirect(url_for('admin.admin'))  # Перенаправляємо на адмін 

# Функція для додавання товару в базу даних
@admin_bp.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = request.form.get('price')
    image = request.form.get('image')
    if not name or not price:
        flash('Name and price are required fields!', 'error')
        return redirect(url_for('admin.admin'))
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', (name, float(price), image))
    conn.commit()
    conn.close()
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin.admin'))

# Функція для видалення товару з бази даних за ID
@admin_bp.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.admin'))

# Функція для редагування товару
@admin_bp.route('/admin/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    name = request.form.get('name')
    price = request.form.get('price')
    image = request.form.get('image')
    conn = get_db_connection()
    conn.execute('UPDATE products SET name = ?, price = ?, image = ? WHERE id = ?', (name, float(price), image, product_id))
    conn.commit()
    conn.close()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('admin.admin'))

