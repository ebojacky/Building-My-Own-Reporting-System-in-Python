import logging
import random
import string
import threading
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd

import config
import database
import forms
import plot


import directories
directories.create()

# Setting up logging
log_format = config.lf
log_file_name = f'{config.LOG_PATH}/ireport_main.log'
log_handler = TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=10)
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[log_handler])
logging.info("Starting")

# Loading Initial dataframe to memory
logging.info("Loading Initial DataFrame")
df = database.dataframe_getter_manager()
last_data_reload_date = datetime.now().strftime('%Y%m%d')
logging.info("Finished Loading Initial DataFrame")

# WEB SERVER CODE
logging.info("Starting Web")

app = Flask(__name__)
app.config['SECRET_KEY'] = "ireport is the real deal !@#$%"

# Setting Up User DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()

logging.info("DB Objects Created")

# Setting Up Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login"))


# Setting Up URLS and Route Methods
@app.route('/', methods=["GET", "POST"])
@login_required
def home():
    temp_html = ""
    plot_ready = False
    new_form = forms.QueryForm()
    if new_form.validate_on_submit():
        event = new_form.event.data.split("-")[0]
        start = new_form.start.data
        end = new_form.end.data
        data_source = new_form.data_source.data
        aggregation = new_form.aggregation.data

        figs = plot.graphs_plotter(df, event, start, end, data_source, aggregation)
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        temp_html = f"user_temp_html/{now}.{''.join(random.sample(string.ascii_lowercase, 12))}.html"

        if not figs:
            flash("No results for this query, please try again.")
            return redirect(url_for('home'))

        with open(f"templates/{temp_html}", 'a') as f:
            for fig in figs:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

        plot_ready = True

    return render_template("index.html", form=new_form, temp_html=temp_html, plot_ready=plot_ready)


@app.route('/temp', methods=["GET", "POST"])
def temp():
    temp_html = request.args.get('temp_html')
    return render_template(temp_html)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = forms.LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("That username does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Function to create a new GUI user
def user_creator(user, passwd):
    hash_and_salted_password = generate_password_hash(passwd, method='pbkdf2:sha256', salt_length=8)
    new_user = User(
        username=user,
        password=hash_and_salted_password)
    db.session.add(new_user)
    db.session.commit()


# Function to update a GUI user passwd
def password_changer(user, passwd):
    user = User.query.filter_by(username=user).first()
    hash_and_salted_password = generate_password_hash(passwd, method='pbkdf2:sha256', salt_length=8)
    user.password = hash_and_salted_password
    db.session.commit()


# One-time code to setup default users
"""
with app.app_context():

    user_creator("admin", "@dmin")
    user_creator("ireport", "!report")
        
    password_changer("ireport", "!report")
    password_changer("admin", "@dmin")
"""


# Background jobs
def dataframe_in_memory_updater():
    global df, last_data_reload_date

    while True:
        try:
            df_new_updates = database.database_update_manager()
            df = pd.concat([df, df_new_updates])

            # Reload Data from disk once a day
            if datetime.now().strftime('%Y%m%d') not in last_data_reload_date:
                df = database.dataframe_getter_manager()
                last_data_reload_date = datetime.now().strftime('%Y%m%d')

        except Exception as e:
            logging.info(f"{str(e)}")

        time.sleep(config.DATABASE_SLEEP_IN_SECONDS)


logging.info("Starting Background Task for Data Frame Reload")

df_thr = threading.Thread(name='df_thread', target=dataframe_in_memory_updater)
df_thr.start()

logging.info("Starting Flask Web App")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5050)
    # app.run(host="0.0.0.0", port=5050, debug=False)
