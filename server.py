from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify, Response
from flask_debugtoolbar import DebugToolbarExtension
from model import Show, Show_Color, Brand, Color, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy
import flask_sqlalchemy
import flask_restless
import json

from sqlalchemy.sql import func

from sqlalchemy import create_engine, Column, Integer, String, Date, Float, func


app = Flask(__name__)
# app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///showme'
db = flask_sqlalchemy.SQLAlchemy(app)

manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
show_blueprint = manager.create_api(Show, methods=['GET'])
brand_blueprint = manager.create_api(Brand, methods=['GET'])
color_blueprint = manager.create_api(Color, methods=['GET'])
show_color_blueprint = manager.create_api(Show_Color, methods=['GET'])

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload = True


@app.route('/')
def index():
    """Homepage."""
    shows = Show.query.all()
    show_colors = Show_Color.query.all()
    colors = Color.query.all()
    brands = Brand.query.all()

    return render_template("bleep.html",
                           shows=shows,
                           show_colors=show_colors,
                           colors=colors,
                           brands=brands)


@app.route('/_get_brands')
def get_brands_json():
    brands = {}
    for brand in Brand.query.all():
        brands[brand.brand_id] = {
            'brand_name': brand.brand_name,
        }

    return jsonify(brands)


@app.route('/_get_shows')
def get_shows_json():
    shows = {}
    for show in Show.query.all():
        shows[show.show_id] = {
            'show_id': show.show_id,
            'show_season': show.season,
            'show_year': show.year,
            'brand_name': show.brands.brand_name,
        }

    return jsonify(shows)


@app.route('/_get_colors')
def get_colors_json():
    colors = {}
    for color in Color.query.all():
        colors[color.color_id] = {
            'color_id': color.color_id,
            'color': color.color_name,
            'color_hex': color.color_hex,
        }

    return jsonify(colors)


@app.route('/_get_show_colors')
def get_show_colors_json():
    years = [2017]
    data_d = {'datasets': []}
    sorted_rainbow_hex = {'#808080': 138, '#ADFF2F': 77, '#FFB6C1': 1, '#556B2F': 78, '#FF8C00': 107, '#9932CC': 19, '#8A2BE2': 21, '#BA55D3': 17, '#2F4F4F': 53, '#00008B': 30, '#DB7093': 5, '#0000FF': 28, '#DC143C': 3, '#DDA0DD': 11, '#4169E1': 33, '#DA70D6': 9, '#DCDCDC': 134, '#7B68EE': 23, '#AFEEEE': 49, '#E6E6FA': 26, '#800080': 16, '#FFF5EE': 114, '#6B8E23': 80, '#FF69B4': 6, '#000080': 32, '#228B22': 72, '#008B8B': 54, '#5F9EA0': 46, '#EE82EE': 12, '#D3D3D3': 135, '#FF00FF': 14, '#48D1CC': 56, '#FFFFFF': 132, '#F5DEB3': 97, '#00FA9A': 61, '#F08080': 124, '#808000': 86, '#FAEBD7': 103, '#A9A9A9': 137, '#7FFFD4': 59, '#C0C0C0': 136, '#7FFF00': 75, '#FFEBCD': 101, '#B0C4DE': 35, '#008080': 55, '#FFFACD': 88, '#FFD700': 91, '#000000': 140, '#008000': 73, '#8B4513': 113, '#FFF0F5': 4, '#FFFFF0': 83, '#6A5ACD': 24, '#FFFAFA': 123, '#4682B4': 40, '#FFEFD5': 100, '#EEE8AA': 89, '#00FF00': 71, '#FFDEAD': 102, '#CD853F': 109, '#ADD8E6': 44, '#E0FFFF': 48, '#F8F8FF': 27, '#D8BFD8': 10, '#BC8F8F': 125, '#FF6347': 120, '#FF0000': 127, '#00CED1': 52, '#A0522D': 115, '#FFC0CB': 2, '#9370DB': 22, '#CD5C5C': 126, '#FFF8DC': 92, '#800000': 131, '#B8860B': 94, '#FFA07A': 116, '#40E0D0': 58, '#FAFAD2': 82, '#DEB887': 105, '#F0FFFF': 47, '#2E8B57': 65, '#E9967A': 119, '#87CEEB': 42, '#D2B48C': 104, '#90EE90': 67, '#00FFFF': 51, '#8FBC8F': 69, '#7CFC00': 76, '#FFE4E1': 121, '#BDB76B': 87, '#F4A460': 111, '#F0FFF0': 66, '#9400D3': 18, '#3CB371': 64, '#F5FFFA': 62, '#20B2AA': 57, '#1E90FF': 38, '#708090': 37, '#F5F5DC': 81, '#66CDAA': 60, '#9ACD32': 79, '#C71585': 8, '#F5F5F5': 133, '#32CD32': 70, '#8B0000': 130, '#696969': 139, '#191970': 29, '#0000CD': 31, '#00BFFF': 43, '#483D8B': 25, '#6495ED': 34, '#FFA500': 99, '#00FF7F': 63, '#A52A2A': 128, '#FAF0E6': 108, '#778899': 36, '#FFE4B5': 98, '#B22222': 129, '#DAA520': 93, '#4B0082': 20, '#FFFAF0': 95, '#B0E0E6': 45, '#F0E68C': 90, '#FFFF00': 85, '#006400': 74, '#FFE4C4': 106, '#FDF5E6': 96, '#8B008B': 15, '#FF7F50': 117, '#FFFFE0': 84, '#FA8072': 122, '#FFDAB9': 110, '#D2691E': 112, '#FF1493': 7, '#98FB98': 68, '#F0F8FF': 39, '#87CEFA': 41, '#FF4500': 118}

    color_object = Color.query.all()
    for color in color_object:
        color_id = color.color_id
        color_name = color.color_name
        color_hex = color.color_hex
        rainbow_connection = sorted_rainbow_hex[color_hex.upper()]

        for year in years:
            radius = db.session.query(Show_Color).join(Show).filter_by(year = year).filter(Show_Color.color_id == color_id).count()
            radius = radius*.5

            my_dataset = {
                 'label': color_name,
                 'data': [{'x': rainbow_connection, 'y': year, 'r': radius}],
                 'backgroundColor': color_hex,
                 'hoverBackgroundColor': color_hex,
                 }
             
            data_d['datasets'].append(my_dataset)

    return jsonify(data_d)


@app.route('/_get_color_by_brand')
def get_colors_by_brand_json():
    brands = Brand.query.all()
    brand_by_colors = {brand.brand_name: [] for brand in brands}
    for brand in brands:
        shows = Show.query.filter_by(
            brand_id=brand.brand_id,
        ).all()
        for show in shows:
            show_colors = Show_Color.query.filter_by(
                show_id=show.show_id,
            ).all()
            for color in show_colors:
                color_objects = Color.query.filter_by(
                    color_id=color.color_id,
                ).all()
                for color_object in color_objects:
                    brand_by_colors[brand.brand_name].append(
                        color_object.color_name
                    )

    return jsonify(brand_by_colors)

# <Show_Color show_colors_id=1 show_id=1 color_id=2


@app.route('/bubbles')
def colors_over_time():
    return render_template("bubble.html")


@app.route('/palette')
def palette():
    # shows = Show.query.all()
    # show_colors = Show_Color.query.all()
    # colors = Color.query.all()
    # brands = Brand.query.all()    

    return render_template('palette.html')
                           # shows=shows,
                           # show_colors=show_colors,
                           # colors=colors,
                           # brands=brands)

# @app.route('/bubble_json')
# def more_bubbles():

#     show_colors_json = {}
#     for show_color in Show_Color.query.all():


@app.route('/streams')
def stream_me():

    return render_template("streamgraph.html")

# what i want: {'x=season': epoch time, 'y=count': color_count}
# each colo should have 2 dicts - count for fall,, count for spring
# a list of colors in each season, and their counts
# start off with year = Show.query.filter_by(year).all()
# then with the season = Show.query.filter_by(season).all()
# then with a list of the colors featured in season with hex value & count
# color_name, color_hex = db.engine.execute("SELECT color_name, color_hex FROM colors WHERE color_id='x'"),

    # final series empty list, append indv series to the series list up here
    # examine types of series - make sure they are the type you think


@app.route("/temp")
def temp():
    series = []

    color_data = db.engine.execute("SELECT color_id, shows.year, COUNT(*) FROM show_colors JOIN shows ON show_colors.show_id=shows.show_id GROUP BY color_id, shows.year")

    for l in color_data:
        color_id = l[0],
        # color_id:tuple
        # print color_id, type(color_id)
        # season = l[1],
        # season:tuple
        # print season, type(season)
        year = l[1],
        # year: tuple
        # print year, type(year)
        color_count = l[2]
        # color_count: long - type of int
        # print color_count, type(color_count)
        epoch_time = 1483228800
        if year == 2017:
            # if season[0] == 'spring':
            # print "season at 0 is spring"
            epoch_time = 1483228800
        # elif season[0] == 'fall':
        elif year == 2016:
            # print "season at 0 is fall"
            epoch_time = 1451606400
        else: 
            print year, type(year)

        color_n = db.engine.execute("SELECT color_name FROM colors WHERE color_id=color_id")
        color_n1 = color_n.fetchone()
        color_name = color_n1.values()
        color_h = db.engine.execute("SELECT color_hex FROM colors WHERE color_id=color_id")
        color_h1 = color_h.fetchone()
        color_hex = color_h1.values()

        series.append([
            {'name': color_name,
             'data': [{'x': epoch_time, 'y': color_count}],
             'color': color_hex
             }
             ])


    # print "series", series, type(series)
    return Response(json.dumps(series),  mimetype='application/json')
    # return jsonify(series)


@app.route('/stream')
def make_stream():
    # testing out streamgraph

    # JUST WRITE A SQLALCHEMY QUERY TO RETREIVE:
    """SELECT color_name, color_hex, count(color_name)
    FROM colors 
    JOIN show_colors ON color_id=show_colors.color_id
    WHERE show.year=2017, show.season=fall
    """

    years = [2017]
    seasons = ['fall', 'spring']
    color_counter = []
    import time
    print("AHHHHHHHHHHH!")
    start_time = time.time()
    for year in years:
        print("year", year)
        for season in seasons:
            print("season", season)
            # give me all shows for each season
            shows = Show.query.filter_by(season=season).all()
            for show_id in shows:
                print("show_id", show_id)
                # give me all colors for all shows in season
                show_colors = Show_Color.query.filter_by(show_id=Show.show_id).all()
                for color in show_colors:
                    print("color", color)
                    color_objects = Color.query.filter_by(color_id=color.color_id).all()
                    for color_object in color_objects:
                        color_counter.append(
                            (color_object.color_name, color_object.color_hex)
                        )

            counts = {color: color_counter.count(color) for color in color_counter}
            color_name_hex, color_count = counts.keys(), counts.values()
            color_by_name = []
            color_by_hex = []
            for n, h in color_name_hex:
                color_by_name.append(n)
                color_by_hex.append(h)

            for color in color_by_name:
                for hex_val in color_by_hex:
                    color_name = color
                    color_hex = hex_val

            if year == 2017:
                if season == 'spring':
                    epoch_time = 1501545600
                elif season == 'fall':
                    epoch_time = 1485907200

            series = [
                    {'name': color_name,
                     'data': [{'x': epoch_time, 'y': color_count}],
                     'color': color_hex
                     }
                     ]
    stop_time = time.time()
    print(stop_time-start_time)
    print jsonify(series)
    return jsonify(series)


@app.route('/pie')
def pie():

    brand_id = request.args.get('brand_id')
    season = request.args.get('season')
    year = request.args.get('year')

    if brand_id == 'All':
        brand_id = []
        for brand in Brand.query.all():
            brand_id.append(brand.brand_id)

    color_counter = []

    for brand_id in brand_id:
        if season != 'All':
            if season == 'Fall':
                shows = Show.query.filter_by(season='fall', brand_id=brand_id).all()
            elif season == 'Spring':
                shows = Show.query.filter_by(season='spring', brand_id=brand_id).all()
        else:
            shows = Show.query.filter_by(brand_id=brand_id).all()
    # need a year if else statement here once older years seeded
        for show in shows:
            show_colors = Show_Color.query.filter_by(show_id=show.show_id).all()
            for color in show_colors:
                color_objects = Color.query.filter_by(color_id=color.color_id).all()
                for color_object in color_objects:
                    color_counter.append(
                        (color_object.color_name, color_object.color_hex)
                    )

        counts = {color: color_counter.count(color) for color in color_counter}
        color_name_hex, color_count = counts.keys(), counts.values()
        color_by_name = []
        color_by_hex = []
        for n, h in color_name_hex:
            color_by_name.append(n)
            color_by_hex.append(h)

        x = color_by_name
        data_color = color_count
        backgroundColor = color_by_hex
        hoverBackgroundColor = color_by_hex

        data = {
            'labels': x,
            'datasets': [{
                'data': data_color,
                'backgroundColor': backgroundColor,
                'hoverBackgroundColor': hoverBackgroundColor
            }]
        }

    return jsonify(data)


@app.route('/palette_chart')
def palette_chart():

    sorted_rainbow_hex = {'#808080': 137, '#ADFF2F': 76, '#FFB6C1': 1, '#556B2F': 77, '#FF8C00': 106, '#9932CC': 19, '#8A2BE2': 21, '#BA55D3': 17, '#2F4F4F': 52, '#00008B': 30, '#DB7093': 5, '#0000FF': 28, '#DC143C': 3, '#DDA0DD': 11, '#4169E1': 32, '#DA70D6': 9, '#DCDCDC': 133, '#7B68EE': 23, '#AFEEEE': 48, '#E6E6FA': 26, '#800080': 16, '#FFF5EE': 113, '#6B8E23': 79, '#FF69B4': 6, '#000080': 31, '#228B22': 71, '#008B8B': 53, '#5F9EA0': 45, '#EE82EE': 12, '#D3D3D3': 134, '#FF00FF': 14, '#48D1CC': 55, '#FFFFFF': 131, '#F5DEB3': 96, '#00FA9A': 60, '#F08080': 123, '#808000': 85, '#FAEBD7': 102, '#A9A9A9': 136, '#7FFFD4': 58, '#C0C0C0': 135, '#7FFF00': 74, '#FFEBCD': 100, '#B0C4DE': 34, '#008080': 54, '#FFFACD': 87, '#FFD700': 90, '#000000': 139, '#008000': 72, '#8B4513': 112, '#FFF0F5': 4, '#FFFFF0': 82, '#6A5ACD': 24, '#FFFAFA': 122, '#4682B4': 39, '#FFEFD5': 99, '#EEE8AA': 88, '#00FF00': 70, '#FFDEAD': 101, '#CD853F': 108, '#ADD8E6': 43, '#E0FFFF': 47, '#F8F8FF': 27, '#D8BFD8': 10, '#BC8F8F': 124, '#FF6347': 119, '#FF0000': 126, '#00CED1': 51, '#A0522D': 114, '#FFC0CB': 2, '#9370DB': 22, '#CD5C5C': 125, '#FFF8DC': 91, '#800000': 130, '#B8860B': 93, '#FFA07A': 115, '#40E0D0': 57, '#FAFAD2': 81, '#DEB887': 104, '#F0FFFF': 46, '#2E8B57': 64, '#E9967A': 118, '#87CEEB': 41, '#D2B48C': 103, '#90EE90': 66, '#00FFFF': 50, '#7CFC00': 75, '#FFE4E1': 120, '#BDB76B': 86, '#F4A460': 110, '#F0FFF0': 65, '#9400D3': 18, '#3CB371': 63, '#F5FFFA': 61, '#20B2AA': 56, '#1E90FF': 37, '#708090': 36, '#F5F5DC': 80, '#66CDAA': 59, '#9ACD32': 78, '#C71585': 8, '#F5F5F5': 132, '#32CD32': 69, '#8B0000': 129, '#696969': 138, '#191970': 29, '#8FBC8F': 68, '#00BFFF': 42, '#483D8B': 25, '#6495ED': 33, '#FFA500': 98, '#00FF7F': 62, '#A52A2A': 127, '#FAF0E6': 107, '#778899': 35, '#FFE4B5': 97, '#B22222': 128, '#DAA520': 92, '#4B0082': 20, '#FFFAF0': 94, '#B0E0E6': 44, '#F0E68C': 89, '#FFFF00': 84, '#006400': 73, '#FFE4C4': 105, '#FDF5E6': 95, '#8B008B': 15, '#FF7F50': 116, '#FFFFE0': 83, '#FA8072': 121, '#FFDAB9': 109, '#D2691E': 111, '#FF1493': 7, '#98FB98': 67, '#F0F8FF': 38, '#87CEFA': 40, '#FF4500': 117}

    colors = Color.query.all()

    my_colors = []
    for sorted_rainbow in sorted_rainbow_hex:
        color_by_hex, color_order = sorted_rainbow_hex.keys(), sorted_rainbow_hex.values()
        hex_order = (color_by_hex, color_order)
        my_colors.append(hex_order)
    sorted(my_colors, key=lambda x: x[1])

    import ipdb; ipdb.set_trace()

    x = my_colors[1]
    data_color = my_colors[0]
    backgroundColor = my_colors[0]
    hoverBackgroundColor = my_colors[0]

    data = {
        'labels': x,
        'datasets': [{
            'data': data_color,
            'backgroundColor': backgroundColor,
            'hoverBackgroundColor': hoverBackgroundColor
        }]
    }

    return jsonify(data)

    # show_id route that returns show_id:[color_id[10]]
    # think about the fxn as connectiing many - one color/show/etc

# import ipdb; ipdb.set_trace()

# Query: show all colors, all season/years for 1 brand
# need show_id, color_id, color_hex, season, year, brand_id
# show.show_id
# show.show_colors.color_id
# show.show_colors.color_hex
# show.brands.brand_name

# Query: show all shows/all seasons/all colors
# need all show_id, year, season, brand_name, color_id, color_hex
# show_color.shows.brands.brand_name
# show_color.shows.show_id
# show_color.shows.season
# show_color.shows.year
# show_color.color_id
# show_color.colors.color_hex

# Query: show color over time
# need all color_id/hex & all show_id for all year/season
# color.color_id
# color.color_hex
# color.color_name
# color.show_colors.show_id
# color.show_colors.shows.season
# color.show_colors.shows.year




# @webapp.route('/api/<color_hex>')
# def api_by_season(color_hex):
#     events = Events.query.filter_by(event_type=event_type).all()
#     return jsonify(json_list=[event.serialize for event in events])


# @app.route('/', methods=['GET'])
# def register_form():
#     """Show form for user signup."""

#     return render_template("base.html")


# @app.route('/register', methods=['POST'])
# def register_process():
#     """Process registration."""

#     # Get form variables
#     email = request.form["email"]
#     password = request.form["password"]
#     age = int(request.form["age"])
#     zipcode = request.form["zipcode"]

#     new_user = User(email=email, password=password, age=age, zipcode=zipcode)

#     db.session.add(new_user)
#     db.session.commit()

#     flash("User %s added." % email)
#     return redirect("/")


# @app.route('/login', methods=['GET'])
# def login_form():
#     """Show login form."""

#     return render_template("login_form.html")


# @app.route('/login', methods=['POST'])
# def login_process():
#     """Process login."""

#     # Get form variables
#     email = request.form["email"]
#     password = request.form["password"]

#     user = User.query.filter_by(email=email).first()

#     if not user:
#         flash("No such user")
#         return redirect("/login")

#     if user.password != password:
#         flash("Incorrect password")
#         return redirect("/login")

#     session["user_id"] = user.user_id

#     flash("Logged in")
#     return redirect("/users/%s" % user.user_id)


# @app.route('/logout')
# def logout():
#     """Log out."""

#     del session["user_id"]
#     flash("Logged Out.")
#     return redirect("/")


# @app.route("/users")
# def user_list():
#     """Show list of users."""

#     users = User.query.all()
#     return render_template("user_list.html", users=users)


# @app.route("/users/<int:user_id>")
# def user_detail(user_id):
#     """Show info about user."""

#     user = User.query.get(user_id)
#     return render_template("user.html", user=user)


# @app.route("/movies")
# def movie_list():
#     """Show list of movies."""

#     movies = Movie.query.order_by('title').all()
#     return render_template("movie_list.html", movies=movies)


# @app.route("/movies/<int:movie_id>", methods=['GET'])
# def movie_detail(movie_id):
#     """Show info about movie.

#     If a user is logged in, let them add/edit a rating.
#     """

#     movie = Movie.query.get(movie_id)

#     user_id = session.get("user_id")

#     if user_id:
#         user_rating = Rating.query.filter_by(
#             movie_id=movie_id, user_id=user_id).first()

#     else:
#         user_rating = None

#     # Get average rating of movie

#     rating_scores = [r.score for r in movie.ratings]
#     avg_rating = float(sum(rating_scores)) / len(rating_scores)

#     prediction = None

#     # Prediction code: only predict if the user hasn't rated it.

#     if (not user_rating) and user_id:
#         user = User.query.get(user_id)
#         if user:
#             prediction = user.predict_rating(movie)

#     # Either use the prediction or their real rating

#     if prediction:
#         # User hasn't scored; use our prediction if we made one
#         effective_rating = prediction

#     elif user_rating:
#         # User has already scored for real; use that
#         effective_rating = user_rating.score

#     else:
#         # User hasn't scored, and we couldn't get a prediction
#         effective_rating = None

#     # Get the eye's rating, either by predicting or using real rating

#     the_eye = (User.query.filter_by(email="the-eye@of-judgment.com")
#                          .one())
#     eye_rating = Rating.query.filter_by(
#         user_id=the_eye.user_id, movie_id=movie.movie_id).first()

#     if eye_rating is None:
#         eye_rating = the_eye.predict_rating(movie)

#     else:
#         eye_rating = eye_rating.score

#     if eye_rating and effective_rating:
#         difference = abs(eye_rating - effective_rating)

#     else:
#         # We couldn't get an eye rating, so we'll skip difference
#         difference = None

    # Depending on how different we are from the Eye, choose a
    # message

#     BERATEMENT_MESSAGES = [
#         "I suppose you don't have such bad taste after all.",
#         "I regret every decision that I've ever made that has " +
#             "brought me to listen to your opinion.",
#         "Words fail me, as your taste in movies has clearly " +
#             "failed you.",
#         "That movie is great. For a clown to watch. Idiot.",
#         "Words cannot express the awfulness of your taste."
#     ]

#     if difference is not None:
#         beratement = BERATEMENT_MESSAGES[int(difference)]

#     else:
#         beratement = None

#     return render_template(
#         "movie.html",
#         movie=movie,
#         user_rating=user_rating,
#         average=avg_rating,
#         prediction=prediction,
#         eye_rating=eye_rating,
#         difference=difference,
#         beratement=beratement
#         )


# @app.route("/movies/<int:movie_id>", methods=['POST'])
# def movie_detail_process(movie_id):
#     """Add/edit a rating."""

#     # Get form variables
#     score = int(request.form["score"])

#     user_id = session.get("user_id")
#     if not user_id:
#         raise Exception("No user logged in.")

#     rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

#     if rating:
#         rating.score = score
#         flash("Rating updated.")

#     else:
#         rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
#         flash("Rating added.")
#         db.session.add(rating)

#     db.session.commit()

#     return redirect("/movies/%s" % movie_id)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
