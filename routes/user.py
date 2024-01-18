import sys
sys.path.append('../')
from server import app, saved_clients, token_required
from flask import request, jsonify
import time
import pronotepy

# Route to get user data
@app.route('/user', methods=['GET'])
@token_required
def user():
    # Get token and client from request arguments and saved clients
    token = request.args.get('token')
    client = saved_clients[token]['client']

    # Define keys to get from client info
    client_info_keys = [
        "name",
        "class_name",
        "establishment",
        "phone",
        "email",
        "address",
        "ine_number",
        "profile_picture",
        "delegue"
    ]
    
    # Get client info
    client_info = {
        key: getattr(client.info, key, "") for key in client_info_keys
    }

    # Convert profile picture to url if it exists
    client_info["profile_picture"] = client_info["profile_picture"].url if client_info["profile_picture"] else None

    # Get user type and children if user is a parent
    usertype = type(client).__name__
    children = client.children.to_dict() if usertype == "ParentClient" else []

    # Combine all user data
    userData = {
        **client_info,
        "client": {"type": usertype, "children": children}
    }

    # Return user data if client is logged in, otherwise return error
    return userData if client.logged_in else jsonify({"error": "expired"}), 498
