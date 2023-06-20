from flask import Flask, render_template, redirect, request, session
from .forms import RegisterForm, LoginForm, LogoutForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user


app = Flask(__name__)
app.config["SECRET_KEY"] = '1234'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
app.app_context().push()

login.login_view = "login_page"


@login.user_loader
def user_loader(id):
    return UserTable.query.get(int(id))


class UserTable(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


@app.route('/', methods=["GET", "POST"])
def main_page():
    return render_template('main.html')


@app.route('/home', methods=["GET", "POST"])
@login_required
def home_page():
    logout_form = LogoutForm()
    message = f'Welcome, {current_user.username}'
    if logout_form.validate_on_submit():
        logout_user()
        return redirect('/')
    return render_template('home.html', message=message, logout_form=logout_form)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = UserTable.query.filter_by(username=username).first()
        if user is None or user.password != password:
            return redirect('/registration')
        login_user(user, remember=login_form.remember_me.data)
        return redirect('/home')
    return render_template('login.html', form=login_form)


@app.route('/registration', methods=['GET', 'POST'])
def registration_page():
    registration_form = RegisterForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        email = registration_form.email.data
        password = registration_form.password.data
        user = UserTable(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('registration.html', form=registration_form)