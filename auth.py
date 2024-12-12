from flask import Blueprint, request, redirect, render_template, url_for, flash, session
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# Маршрут для входу
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Отримання даних із форми
        email = request.form.get('email')
        password = request.form.get('password')

        # Перевірка чи введено всі обов'язкові поля
        if not email or not password:
            flash('Будь ласка, заповніть всі поля.', 'error')
            return redirect(url_for('auth.login'))

        # Перевірка наявності користувача
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Користувача з таким Email не знайдено.', 'error')
            return redirect(url_for('auth.login'))

        # Перевірка пароля
        if not check_password_hash(user.password, password):
            flash('Неправильний пароль. Спробуйте ще раз.', 'error')
            return redirect(url_for('auth.login'))

        # Якщо вхід успішний
        session['user_id'] = user.id  # Збереження ID користувача у сесії
        flash(f'Вітаємо, {user.name}! Ви успішно увійшли.', 'success')
        return redirect(url_for('auth.profile'))  # Перенаправлення на сторінку профілю

    return render_template('login.html')


# Маршрут для реєстрації
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Отримання даних із форми
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # Перевірка чи введено всі обов'язкові поля
        if not email or not name or not password:
            flash('Будь ласка, заповніть всі поля.', 'error')
            return redirect(url_for('auth.signup'))

        # Перевірка наявності користувача
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Цей Email вже зареєстрований.', 'error')
            return redirect(url_for('auth.signup'))

        try:
            # Створення нового користувача
            new_user = User(
                email=email,
                name=name,
                password=generate_password_hash(password, method='pbkdf2:sha256')  # Захешований пароль
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Реєстрація успішна! Ви можете увійти.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()  # Відкат транзакції у разі помилки
            flash(f'Сталася помилка при реєстрації: {str(e)}', 'error')
            return redirect(url_for('auth.signup'))

    return render_template('signup.html')

@auth.route('/logout')
def logout():
    print("Logout route called")
    session.pop('user_id', None)
    flash('Ви успішно вийшли.', 'success')
    return redirect(url_for('auth.login'))


# Маршрут для профілю користувача
@auth.route('/profile')
def profile():
    # Перевірка, чи користувач увійшов у систему
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть у систему для доступу до профілю.', 'error')
        return redirect(url_for('auth.login'))

    # Отримання інформації про користувача
    user = User.query.get(user_id)
    if not user:
        flash('Користувача не знайдено.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=user)
