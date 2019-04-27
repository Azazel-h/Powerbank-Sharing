from app import app
import os


@app.route('/')
@app.route('/index')
def index():
    os.system('eject')
    return 'I am machine!'
