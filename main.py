from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = api_key = os.getenv('API_KEY')
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'movies.db')}"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
db = SQLAlchemy(app)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


class RateForm(FlaskForm):
    rating = StringField("Your Rating Out of 10")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


def movie_exists(title):
    # Check if the movie exists in the database
    return Movies.query.filter_by(title=title).first() is not None


@app.route("/")
def home():
    result = db.session.execute(db.select(Movies))
    all_movies = result.scalars().all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = AddForm()
    if form.validate_on_submit():
        MOVIE_NAME = form.movie_title.data
        url = f"https://api.themoviedb.org/3/search/movie?query={MOVIE_NAME}&language=en-US"

        # Set the headers with the Bearer token
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            all_movies = response.json()
            formatted_movies_data = all_movies['results']
            return render_template('select.html', movies=formatted_movies_data)


    return render_template('add.html', form=form)

@app.route('/find')
def find_movie():
    movie_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(url, headers=headers)
    data =response.json()


    new_movie = Movies(
                title=data['original_title'],
                year=data['release_date'].split('-')[0],
                img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
                description=data['overview'],
            )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('update',id=new_movie.id))

@app.route("/update", methods=["GET", "POST"])
def update():
    form = RateForm()
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movies, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
    if movie_to_delete is not None:
        db.session.delete(movie_to_delete)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
