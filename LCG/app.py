from flask import Flask
import os.path

app = Flask(__name__)

app.config['SECRET_KEY'] = 'e6bcbfcb-198e-4115-b554-2ebd2f747fc2'

def mkpath (p):
    return os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        p))
