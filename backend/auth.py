from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

client = MongoClient("mongodb+srv://eeshachavan:eesha123@cluster.mongodb.net/")
db = client["souledstore"]
users = db["users"]

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if users.find_one({'email': email}):
        return jsonify({'msg': 'User already exists'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users.insert_one({'email': email, 'password': hashed_password})
    return jsonify({'msg': 'Signup successful'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = users.find_one({'email': email})
    if user and bcrypt.check_password_hash(user['password'], password):
        token = create_access_token(identity=email)
        return jsonify({'token': token, 'msg': 'Login successful'}), 200
    return jsonify({'msg': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
