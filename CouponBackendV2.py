from flask import Flask, request, jsonify, abort, make_response
import jwt
import time
from tinydb import TinyDB, Query
import datetime
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gen this :)'  # Keep this secret!
db_users = TinyDB("users.json")
UserEntryQuery = Query()
db_entries = TinyDB("entries.json")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s (%(filename)s:%(lineno)d)',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


login_logger = logging.getLogger('login')
signup_logger = logging.getLogger('signup')
add_entry_logger = logging.getLogger('add_entry')
remove_entry_logger = logging.getLogger('remove_entry')
view_entries_logger = logging.getLogger('view_entries')


login_file_handler = logging.FileHandler('login.log')
signup_file_handler = logging.FileHandler('signup.log')
add_entry_file_handler = logging.FileHandler('add_entry.log')
remove_entry_file_handler = logging.FileHandler('remove_entry.log')
view_entries_file_handler = logging.FileHandler('view_entries.log')


login_logger.addHandler(login_file_handler)
signup_logger.addHandler(signup_file_handler)
add_entry_logger.addHandler(add_entry_file_handler)
remove_entry_logger.addHandler(remove_entry_file_handler)
view_entries_logger.addHandler(view_entries_file_handler)

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
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            abort(400, "Missing required fields")

        user = db_users.search(UserEntryQuery.username == data['username'])
        if len(user) != 1:
            abort(401, "Invalid username or password")

        user_entry = user[0]
        token = generate_token(data['username'])
        return jsonify({'token': token}), 200
    except Exception as e:
        login_logger.error(f"Exception occurred: {e}")
        abort(500, "Internal server error, Saved to log file.")

    finally:
        login_logger.info("Login request handled")

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            abort(400, "Missing username or password field.")

        existing_user = db_users.search(UserEntryQuery.username == data['username'])
        if len(existing_user) != 0:
            abort(401, "Username already exists, Please use another username.")

        UserEntry(data['username'], None, None, None)
        return jsonify({'message': 'User created successfully'}), 200
    except Exception as e:
        signup_logger.error(f"Exception occurred: {e}")
        abort(500, "Internal server error, Saved to log file.")

    finally:
        signup_logger.info("Signup request handled")

@app.route('/add_entry', methods=['POST'])
def add_entry():
    try:
        data = request.json
        if not data or 'username' not in data or 'coupon_barcode' not in data:
            abort(400, "Missing required fields")

        UserEntry(data['username'], data['coupon_barcode'], None, None)
        return jsonify({'message': 'Entry added successfully'}), 200
    except Exception as e:
        add_entry_logger.error(f"Exception occurred: {e}")
        abort(500, "Internal server error, Saved to log file.")

    finally:
        add_entry_logger.info("Add entry request handled")

@app.route('/remove_entry', methods=['POST'])
def remove_entry():
    try:
        data = request.json
        if not data or 'username' not in data or 'coupon_barcode' not in data:
            abort(400, "Missing required fields")

        db_users.remove(UserEntryQuery.username == data['username'] and UserEntryQuery.Coupon_Barcode == data['coupon_barcode'])
        return jsonify({'message': 'Entry removed successfully'}), 200
    except Exception as e:
        remove_entry_logger.error(f"Exception occurred: {e}")
        abort(500, "Internal server error, Saved to log file.")

    finally:
        remove_entry_logger.info("Remove entry request handled")

@app.route('/view_entries', methods=['GET'])
def view_entries():
    try:
        entries = db_users.all()
        return jsonify(entries), 200
    except Exception as e:
        view_entries_logger.error(f"Exception occurred: {e}")
        abort(500, "Internal server error, Saved to log file.")

    finally:
        view_entries_logger.info("View entries request handled")

if __name__ == '__main__':
    app.run(debug=True)
