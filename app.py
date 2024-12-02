from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # Change in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# MongoDB Configuration
try:
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    logger.info(f"Attempting to connect to MongoDB with URI: {mongodb_uri.split('@')[0]}...")
    
    client = MongoClient(mongodb_uri)
    # Test the connection
    client.server_info()
    db = client['streakie']
    users = db.users
    todos = db.todos
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    logger.error(f"MongoDB URI being used: {os.getenv('MONGODB_URI', 'mongodb://localhost:27017/').split('@')[0]}")
    raise

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        logger.debug(f"Received registration request for email: {data.get('email')}")
        
        if not all(key in data for key in ['email', 'password', 'name']):
            logger.error("Missing required fields in registration request")
            return jsonify({'error': 'Missing required fields'}), 400
        
        if users.find_one({'email': data['email']}):
            logger.warning(f"Email already exists: {data['email']}")
            return jsonify({'error': 'Email already exists'}), 400
        
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        user = {
            'email': data['email'],
            'password': hashed_password,
            'name': data['name'],
            'highest_streak': 0,
            'current_streak': 0,
            'last_completed_date': None,
            'created_at': datetime.utcnow()
        }
        
        result = users.insert_one(user)
        logger.info(f"Successfully registered user with email: {data['email']}")
        return jsonify({'message': 'User registered successfully'}), 201
        
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users.find_one({'email': data['email']})
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'token': access_token,
            'user': {
                'email': user['email'],
                'name': user['name'],
                'highest_streak': user['highest_streak'],
                'current_streak': user['current_streak']
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()
    user_todos = list(todos.find({'user_id': user_id, 'date': datetime.utcnow().strftime('%Y-%m-%d')}))
    
    for todo in user_todos:
        todo['_id'] = str(todo['_id'])
    
    return jsonify(user_todos)

@app.route('/api/todos', methods=['POST'])
@jwt_required()
def create_todo():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    deadline = None
    if 'deadline' in data and data['deadline']:
        deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
    
    todo = {
        'user_id': user_id,
        'title': data['title'],
        'completed': False,
        'deadline': deadline,
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'created_at': datetime.utcnow()
    }
    
    result = todos.insert_one(todo)
    todo['_id'] = str(result.inserted_id)
    
    return jsonify({
        '_id': todo['_id'],
        'title': todo['title'],
        'completed': todo['completed'],
        'deadline': todo['deadline'].isoformat() + 'Z' if todo['deadline'] else None
    }), 201

@app.route('/api/todos/<todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    todo = todos.find_one_and_update(
        {'_id': ObjectId(todo_id), 'user_id': user_id},
        {'$set': {'completed': data['completed']}},
        return_document=True
    )
    
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Update streak if all todos for today are completed
    if data['completed']:
        today_todos = todos.find({
            'user_id': user_id,
            'date': datetime.utcnow().strftime('%Y-%m-%d')
        })
        
        all_completed = all(t['completed'] for t in today_todos)
        
        if all_completed:
            user = users.find_one({'_id': ObjectId(user_id)})
            last_completed = user.get('last_completed_date')
            today = datetime.utcnow().date()
            
            if last_completed and (today - last_completed).days == 1:
                # Streak continues
                new_streak = user['current_streak'] + 1
                highest_streak = max(new_streak, user['highest_streak'])
                
                users.update_one(
                    {'_id': ObjectId(user_id)},
                    {
                        '$set': {
                            'current_streak': new_streak,
                            'highest_streak': highest_streak,
                            'last_completed_date': today
                        }
                    }
                )
            elif not last_completed or (today - last_completed).days > 1:
                # Streak starts over
                users.update_one(
                    {'_id': ObjectId(user_id)},
                    {
                        '$set': {
                            'current_streak': 1,
                            'last_completed_date': today
                        }
                    }
                )
    
    todo['_id'] = str(todo['_id'])
    return jsonify({
        '_id': todo['_id'],
        'title': todo['title'],
        'completed': todo['completed'],
        'deadline': todo['deadline'].isoformat() + 'Z' if todo['deadline'] else None
    })

@app.route('/api/todos/<todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user_id = get_jwt_identity()
    result = todos.delete_one({'_id': ObjectId(todo_id), 'user_id': user_id})
    
    if result.deleted_count == 0:
        return jsonify({'error': 'Todo not found'}), 404
    
    return jsonify({'message': 'Todo deleted successfully'})

@app.route('/api/user/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    user_id = get_jwt_identity()
    user = users.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'highest_streak': user['highest_streak'],
        'current_streak': user['current_streak']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5005)
