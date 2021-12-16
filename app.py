from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random
from random import sample
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Urls(db.Model):
    id_ = db.Column("id_",db.Integer, primary_key=True)
    long = db.Column("long",db.String())
    short = db.Column("short",db.String())

    def __init__(self, long, short):
        self.long = long
        self.short = short

@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=3)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters

def longen_url():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    WORDS = response.content.splitlines()
    word_list = sample(WORDS,15)
    joined_word_list = b'-'.join(word_list)
    joined_word_list = joined_word_list.decode()
    long_url = Urls.query.filter_by(short=joined_word_list).first()
    if not long_url:
        return joined_word_list



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_recieved = request.form['nm']
        # recieving long url
        found_url = Urls.query.filter_by(long=url_recieved).first()
        # check if exists already
        if found_url:
            # return short url
            return redirect(url_for("display_short_url", url=found_url.short))

        else:
            short_url = longen_url()
            new_url = Urls(url_recieved, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('home.html')

@app.route("/display/<url>")
def display_short_url(url):
    return render_template('short_url.html', short_url_display=url)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f"<h1>URL doesn't exist</h1>"

@app.route('/all_urls')
def display_all():
    return render_template('all_urls.html', vals=Urls.query.all())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)