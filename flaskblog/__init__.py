import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os 

app = Flask(__name__, static_folder="static")


app.config['SECRET_KEY'] = 'eac4fe84bf54c464bbc87125b50dc143'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager(app)
login_manager.login_view = 'login'   #name of the function 
login_manager.login_message_category = 'info'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')

app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')

mail = Mail(app)


from flaskblog import routes