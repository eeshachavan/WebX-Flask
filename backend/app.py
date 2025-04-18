from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import json

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# MongoDB URI - Replace with your actual MongoDB connection string
MONGO_URI = "mongodb+srv://eeshachavan:eesha123@cluster0.h3dgvur.mongodb.net/"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database('souled_store')
products_collection = db.products

# Check if products collection is empty, if yes, seed with initial data
def seed_database():
    if products_collection.count_documents({}) == 0:
        print("Seeding database with initial products...")
        # Load products from products.json
        try:
            with open('products.json', 'r') as f:
                products = json.load(f)
                products_collection.insert_many(products)
            print("Database seeded successfully!")
        except Exception as e:
            print(f"Error seeding database: {str(e)}")

# Call seed_database function
seed_database()

# In-memory cart
cart = []

# Route to get all products (for debugging)
@app.route('/api/products', methods=['GET'])
def get_all_products():
    try:
        products = list(products_collection.find())
        # Convert ObjectId to string for JSON response
        for product in products:
            product['_id'] = str(product['_id'])
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get products based on category
@app.route('/api/products/<category>', methods=['GET'])
def get_products(category):
    try:
        # Print for debugging
        print(f"Looking for products in category: {category}")
        
        # Find products by category
        products = list(products_collection.find({"category": category}))
        
        # Print for debugging
        print(f"Found {len(products)} products")
        
        # Convert ObjectId to string for JSON response
        for product in products:
            product['_id'] = str(product['_id'])
        
        return jsonify(products), 200
    except Exception as e:
        print(f"Error getting products: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Route to get a single product by ID
@app.route('/api/product/<id>', methods=['GET'])
def get_product(id):
    try:
        # Print for debugging
        print(f"Looking for product with ID: {id}")
        
        product = products_collection.find_one({"_id": ObjectId(id)})
        
        if product:
            product['_id'] = str(product['_id'])
            return jsonify(product), 200
        
        # If product not found by ObjectId, try finding by string ID (for testing)
        product = products_collection.find_one({"id": id})
        if product:
            product['_id'] = str(product['_id'])
            return jsonify(product), 200
            
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        print(f"Error getting product: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Cart routes
@app.route('/api/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_cart():
    global cart
    if request.method == 'GET':
        return jsonify(cart), 200

    elif request.method == 'POST':
        item = request.get_json()
        cart.append(item)
        return jsonify({"message": "Item added", "cart": cart}), 201

    elif request.method == 'PUT':
        item = request.get_json()
        for i in range(len(cart)):
            if cart[i].get('id') == item.get('id'):
                cart[i] = item
                return jsonify({"message": "Item updated", "cart": cart}), 200
        return jsonify({"error": "Item not found"}), 404

    elif request.method == 'DELETE':
        item_id = request.get_json().get('id')
        cart = [item for item in cart if item.get('id') != item_id]
        return jsonify({"message": "Item removed", "cart": cart}), 200

# Main route for testing
@app.route('/')
def index():
    return "API is working!"

# Users collection
users_collection = db.users

#Signup route
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'msg': 'User already exists'}), 400

    users_collection.insert_one({'email': email, 'password': password})
    return jsonify({'msg': 'Signup successful'}), 201

# Users collection
users_collection = db.users

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email, 'password': password})
    if user:
        return jsonify({'msg': 'Login successful', 'token': 'dummy-jwt-token'}), 200
    else:
        return jsonify({'msg': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(debug=True)