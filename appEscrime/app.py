from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
import os.path
from flask_login import LoginManager

app = Flask(__name__)

app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'e6bcbfcb-198e-4115-b554-2ebd2f747fc2'

def mkpath (p):
    return os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        p))


app.config['SQLALCHEMY_DATABASE_URI'] = (
   'sqlite:///'+ mkpath('../CEB.db'))
db = SQLAlchemy(app)

login_manager = LoginManager(app)
#login_manager.login_view = "login"