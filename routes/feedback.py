from flask import Blueprint, render_template, request, jsonify 
from models import get_db_connection 
from datetime import datetime 
 
feedback_bp = Blueprint('feedback', __name__) 
 
@feedback_bp.route('/feedback', methods=['GET', 'POST']) 
def feedback(): 
    if request.method == 'POST': 
        # Отримання даних з форми 
        name = request.form['name'] 
        email = request.form['email'] 
        message = request.form['message'] 
         
        # Перевірка, чи всі поля заповнені 
        if not name or not email or not message: 
            return jsonify({"status": "error", "message": "All fields are required!"}), 400 
 
        # Поточна дата та час 
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
 
        # Підключення до бази даних 
        conn = get_db_connection() 
        # Вставка відгуку разом з датою 
        conn.execute('INSERT INTO feedback (name, email, message, date) VALUES (?, ?, ?, ?)', 
                     (name, email, message, now))  # Вставляємо поточну дату та час 
        conn.commit() 
        conn.close() 
         
        return jsonify({"status": "success", "message": "Feedback submitted successfully!"}), 200 
 
    # GET-запит для відображення всіх відгуків (якщо потрібно) 
    conn = get_db_connection() 
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall() 
    conn.close() 
     
    return render_template('feedback.html', feedbacks=feedbacks)