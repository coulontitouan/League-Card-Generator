from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'e6bcbfcb-198e-4115-b554-2ebd2f747fc2'

import views