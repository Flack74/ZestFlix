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











#
# import sqlite3
#
# db = sqlite3.connect("movies.db")
#
# cursor = db.cursor()
#
# cursor.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE,"
#                "year INTEGER NOT NULL, description varchar(500)  NULL, rating REAL  NULL, "
#                "ranking INTEGER  NULL, review varchar(250) NOT NULL, img_url varchar(250) NOT NULL)")
#
# db.commit()

# import sqlite3
#
# db = sqlite3.connect("movies.db")
# cursor = db.cursor()
#
# # Create a table that allows NULL values for rating, ranking, and review
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS movies (
#         id INTEGER PRIMARY KEY,
#         title VARCHAR(250) NOT NULL UNIQUE,
#         year INTEGER NOT NULL,
#         description VARCHAR(500) NULL,
#         rating REAL NULL,          -- Allow NULL for rating
#         ranking INTEGER NULL,      -- Allow NULL for ranking
#         review VARCHAR(250) NULL,  -- Allow NULL for review
#         img_url VARCHAR(250) NOT NULL
#     )
# """)
#
# db.commit()
# db.close()






# with app.app_context():
#     if not movie_exists("Inception"):
#         new_movie = Movies(
#             title="Inception",
#             year=2010,
#             description="A skilled thief, "
#                         "who specializes in stealing secrets from within the subconscious during the dream state, "
#                         "is given a chance to have his criminal history erased as payment for the implantation of"
#                         " another person's idea "
#                         "into a target's subconscious.",
#             rating=8.8,
#             ranking=8,
#             review="The concept of dreams within dreams blew my mind.",
#             img_url="data:image/jpeg;base64,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"
#         )
#         db.session.add(new_movie)
#         db.session.commit()


# movie_id = 1
# with app.app_context():
#     movie_to_delete = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
#     # or book_to_delete = db.get_or_404(Book, book_id)
#     if movie_to_delete is not None:
#         db.session.delete(movie_to_delete)
#         db.session.commit()