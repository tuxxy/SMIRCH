from app import app
from flask import request

@app.route('/', methods=['POST'])
def main():
    print(request.form.get('source'), request.form.get('message'))
    return 'Hello!'
