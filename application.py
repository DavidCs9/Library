from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# create app
app = Flask(__name__)
application = app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:kyUvXPpGj3xg0ssBXN02@library-db.cfntbfmybblf.us-west-1.rds.amazonaws.com:3306/librarydb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'asghdhjkgashjdgahjksgd'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


# create form
class Form(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    author = StringField(label='Author', validators=[DataRequired()])
    rating = SelectField(label='Rating', choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                         validators=[DataRequired()])
    submit = SubmitField(label='Add Book')


# create form with rating field
class EditForm(FlaskForm):
    rating = SelectField(label='New Rating', choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                         validators=[DataRequired()])
    submit = SubmitField(label='Confirm')
    cancel = SubmitField(label='Cancel')


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# create a new table
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    user_id = db.Column(db.Integer)
    author = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer)


# Line below only required once, when creating DB.
# db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/usuario')
@login_required
def usuario():
    try:
        all_books = Book.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('usuario.html', books=all_books, user=current_user)
    except:
        return render_template('usuario.html', user=current_user)

@login_required
@app.route('/book')
def book():
    book = Book.query.filter_by(book_id=id)
    return render_template('book.html', book=book, user=current_user)

@login_required
@app.route("/add", methods=["GET", "POST"])
def add():
    form = Form()
    if form.validate_on_submit():
        new_book = Book(title=form.name.data, user_id=current_user.get_id(), author=form.author.data, rating=form.rating.data)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('usuario'))
    return render_template('add.html', form=form)

@login_required
@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    book_id = request.args.get('id')
    book_selected = Book.query.get(book_id)
    if form.validate_on_submit():
        book_to_update = Book.query.get(book_id)
        book_to_update.rating = form.rating.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", book=book_selected, form=form)

@login_required
@app.route('/delete/', methods=['GET', 'POST'])
def delete():
    book_id = request.args.get('id')
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return url_for("usuario")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('usuario'))
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        user = User.query.filter_by(email=email).first()

        # Check stored password hash against entered password hashed.
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Email exists and password correct
        else:
            login_user(user)
            return redirect(url_for('usuario'))
    return render_template("login.html", logged_in=current_user.is_authenticated, user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        psw = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=psw
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("usuario"))
    return render_template("register.html", logged_in=current_user.is_authenticated, user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
