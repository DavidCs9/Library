from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


# create app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'asghdhjkgashjdgahjksgd'
Bootstrap(app)

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


# create a new table
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'


db.create_all()


@app.route('/')
def home():
    all_books = db.session.query(Book).all()
    return render_template('index.html', books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = Form()
    if form.validate_on_submit():
        new_book = Book(title=form.name.data, author=form.author.data, rating=form.rating.data)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


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


@app.route('/delete/', methods=['GET', 'POST'])
def delete():
    book_id = request.args.get('id')
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
