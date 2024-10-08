from flask import Flask, request, jsonify, abort, make_response
import jwt
import time
from tinydb import TinyDB, Query
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tpLFjfJ3c5ynUPHZ9Jvjt2wAsM5jWEyn'  # Keep this secret!
db_users = TinyDB("users.json")
UserEntryQuery = Query()
db_entries = TinyDB("entries.json")

def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        abort(401, "Token has expired")
    except jwt.InvalidTokenError:
        abort(401, "Invalid token")

def UserEntry(username, UCB, UVO, UOI):
    UE = {
        'username': username,
        'Coupon_Barcode': UCB,
        'Valid_On': UVO,
        'Other_Info': UOI
    }
    db_users.insert(UE)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        abort(400, "Missing required fields")

    user = db_users.search(UserEntryQuery.username == data['username'])
    if len(user) != 1:
        abort(401, "Invalid username or password")

    user_entry = user[0]
    token = generate_token(data['username'])
    return jsonify({'token': token}), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        abort(400, "Missing required fields")

    existing_user = db_users.search(UserEntryQuery.username == data['username'])
    if len(existing_user) != 0:
        abort(401, "Username already exists")

    UserEntry(data['username'], None, None, None)
    return jsonify({'message': 'User created successfully'}), 200

@app.route('/add_entry', methods=['POST'])
def add_entry():
    token = request.headers.get('Authorization').split("Bearer ")[1]
    if not token:
        abort(403, "Token is missing")

    payload = verify_token(token)
    user_id = payload['sub']
    data = request.json
    if not data or 'Coupon_Barcode' not in data or 'Valid_On' not in data or 'Other_Info' not in data:
        abort(400, "Missing required fields")

    UserEntryQuery.username == user_id
    entries = db_entries.search(UserEntryQuery.Coupon_Barcode == data['Coupon_Barcode'])
    if len(entries) != 0:
        abort(403, "Permission denied")

    db_entries.insert({
        'username': user_id,
        'Coupon_Barcode': data['Coupon_Barcode'],
        'Valid_On': data['Valid_On'],
        'Other_Info': data['Other_Info']
    })
    return jsonify({'message': 'Entry added successfully'}), 201

@app.route('/remove_entry', methods=['DELETE'])
def remove_entry():
    token = request.headers.get('Authorization').split("Bearer ")[1]
    if not token:
        abort(403, "Token is missing")

    payload = verify_token(token)
    user_id = payload['sub']
    data = request.json
    if not data or 'Coupon_Barcode' not in data:
        abort(400, "Missing required fields")

    UserEntryQuery.username == user_id
    entries = db_entries.search(UserEntryQuery.Coupon_Barcode == data['Coupon_Barcode'])
    if len(entries) != 1 or entries[0]['username'] != user_id:
        abort(403, "Permission denied")

    db_entries.remove(UserEntryQuery.Coupon_Barcode == data['Coupon_Barcode'])
    return jsonify({'message': 'Entry removed successfully'}), 200

@app.route('/view_entries', methods=['GET'])
def view_entries():
    token = request.headers.get('Authorization').split("Bearer ")[1]
    if not token:
        abort(403, "Token is missing")

    payload = verify_token(token)
    user_id = payload['sub']
    UserEntryQuery.username == user_id
    entries = db_entries.search(UserEntryQuery.Coupon_Barcode.isnull())
    return jsonify({'entries': entries}), 200

def generate_csrf():
    return str(uuid.uuid4())

@app.after_request
def add_csrf(response):
    response.set_cookie('csrf_token', generate_csrf(), httponly=True, secure=False)
    return response

def verify_csrf(token, user_id):
    stored_token = db_users.search(UserEntryQuery.username == user_id)[0]['csrf_token']
    if token != stored_token:
        abort(403, "Invalid CSRF token")

@app.route('/check_csrf', methods=['POST'])
def check_csrf():
    data = request.json
    verify_csrf(data['token'], data['username'])
    return jsonify({'message': 'CSRF token verified'}), 200

if __name__ == '__main__':
    app.run(debug=True)
