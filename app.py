from flask import Flask
from flask import request
from flask import Response
import json
from flask_cors import CORS
from flask import render_template
from flask import send_from_directory
from flask.helpers import make_response
import os
app = Flask(__name__)

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
def home():
    return make_response(render_template('signup.html'), 200)

@app.route('/signup', methods=['POST'])
def signup():
    post_data = request.form.to_dict()

    if "email" not in post_data:
        return Response(status=404)
    
    with open('data/emails.json', 'r') as f:
        data = json.loads(f.read())
    
    data["emails"].append(post_data["email"])

    with open('data/emails.json', 'w') as f:
        json.dump(data, f)
    
    return make_response(render_template('success.html'), 200)

@app.route('/get-da-data-por-favor', methods=['GET'])
def data():
    with open('data/emails.json', 'r') as f:
        data = json.loads(f.read())
    
    return data

app.run(debug=True)
