# papillon-flask server for Papillon API
# ---------------------------------------------
# Code original de papillon-python réecrit en Flask et optimisé
# ---------------------------------------------
# Note pour déployer
# Gestion des requêtes (multithreading) : https://stackoverflow.com/questions/14672753/handling-multiple-requests-in-flask

from flask import Flask, request, jsonify
from functools import wraps
import secrets
import pronotepy
import time

from pronotepy.ent import *

# Initialize Flask app
app = Flask(__name__)

# Dictionary to store active clients
saved_clients = {}
# Timeout threshold for clients
client_timeout_threshold = 300

# Decorator to require a token for certain routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from request arguments
        token = request.args.get('token')
        # If no token provided or token is expired, return error
        if not token or (token not in saved_clients or time.time() - saved_clients[token]['last_interaction'] > client_timeout_threshold):
            return jsonify({"error": "expired"}), 403
        # Otherwise, proceed with the function
        return f(*args, **kwargs)
    return decorated

# Route to generate a token
@app.route("/generatetoken", methods=['POST'])
def generate_token():
    # Get url, username, and password from form data
    url = request.form.get('url')
    username = request.form.get('username')
    password = request.form.get('password')

    # If any of the required data is missing, return error
    if not all([url, username, password]):
        return jsonify({"token": False, "error": "missing"}), 400

    # Try to create a new client with the provided data
    try:
        client = pronotepy.Client(url, username=username, password=password)
    except Exception as e:
        return jsonify({"token": False, "error": f"[PRONOTEPY] : {str(e)}"}), 498 

    # Generate a new token and save the client
    token = secrets.token_urlsafe(16)
    saved_clients[token] = {'client': client, 'last_interaction': time.time()}

    # Return the token if the client is logged in, otherwise return error
    return jsonify({"token": token, "error": False}) if client.logged_in else jsonify({token: False, "error": "Login failed"}), 200 if client.logged_in else 498

import routes.user
