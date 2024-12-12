from models import init_db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db'

db = SQLAlchemy()

db.init_app(app)


if __name__ == '__main__':
    init_db()
    print("База даних ініціалізована успішно.")