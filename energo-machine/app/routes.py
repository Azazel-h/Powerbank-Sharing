"""
Модули:
    - os
    - app
"""
import os
from app import app


@app.route('/')
@app.route('/index')
def index():
    os.system('eject')
    return 'I am machine!'
