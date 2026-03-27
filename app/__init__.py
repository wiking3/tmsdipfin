import os
import click

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_pagedown import PageDown

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
pagedown = PageDown()

def create_app():
    app = Flask(__name__)
    SECRET_KEY= os.environ.get("SECRET_KEY")
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", f"{SECRET_KEY}")
    DB_USER= os.environ.get("DB_USER")
    DB_PASS= os.environ.get("DB_PASS")
    DB_NAME= os.environ.get("DB_NAME")
    host= os.environ.get("host")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", f"mysql://{DB_USER}:{DB_PASS}@{host}:3306/{DB_NAME}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING']=True

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .models import User
    from .routes import bp
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(bp)
    

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    def create_admin(username, password):
        if User.query.filter_by(username=username).first():
            click.echo("Пользователь с таким именем уже существует.")
            return
        user = User(username=username, role='admin')
        user.set_password(password)  # метод должен быть в вашей модели User
        db.session.add(user)
        db.session.commit()
        click.echo(f"Администратор {username} успешно создан!")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("password")
    @click.argument("role")  # 'teacher' или 'student' или 'admin'
    def create_user(username, password, role):
        if role not in ['admin', 'teacher', 'student']:
            click.echo("Роль должна быть одной из ['admin', 'teacher', 'student']")
            return
        if User.query.filter_by(username=username).first():
            click.echo("Пользователь с таким именем уже существует.")
            return
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Пользователь {username} с ролью {role} успешно создан!")


    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
