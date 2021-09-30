from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
import requests

URL = "https://api.themoviedb.org/3/search/movie"
Find = "https://api.themoviedb.org/3/movie/"
KEY = "6351ebd9c07ac7f1a9c006bef24ab51a"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
db = SQLAlchemy(app)
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Movie{self.title}>'


class Edit(FlaskForm):
    rating = StringField('Your Rating out of 10 e.g 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])

    submit = SubmitField('Submit')


class Add(FlaskForm):
    movie_title = StringField('Movie Title')
    submit = SubmitField('Submit')


db.create_all()





@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)-i

    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = Edit()
    id = request.args.get("id")
    movie = Movie.query.get(id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["POST", "GET"])
def add_movie():
    form = Add()
    if form.validate_on_submit():
        response = requests.get(url=URL, params={"api_key": KEY, "query": form.movie_title.data})
        response = response.json()
        return render_template("select.html", data=response)

    return render_template("add.html", form=form)

@app.route('/select', methods=["POST", "GET"])
def select():
    id = request.args.get('id')
    print(id)
    new_url = Find+id
    response = requests.get(url=new_url, params={"api_key": KEY})
    film = response.json()
    print(film)
    title = film['title']
    description = film['overview']
    img_url = "https://image.tmdb.org/t/p/w500/" + film['poster_path']
    year = film['release_date'].split('-')[0]
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        rating=0,
        ranking=10,
        review='',
        img_url=img_url
    )
    db.session.add(new_movie)
    db.session.commit()
    movie = Movie.query.filter_by(title=title).first()
    id = movie.id

    return redirect(url_for('edit', id=id))


if __name__ == '__main__':
    app.run(debug=True)
