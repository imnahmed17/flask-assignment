from flask import Flask, request, g, jsonify
from flask_restx import Api, Resource, reqparse
import psycopg2
from elasticsearch import Elasticsearch
import re
import jwt
from datetime import datetime, timedelta
from functools import wraps
import secrets

app = Flask(__name__)
api = Api(app, title='Flask Assignment')

# Configure Swagger UI
api.authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

# Create a namespace
user_namespace = api.namespace('user', description='Operations about user')
room_namespace = api.namespace('room', description='Operations about searching & sorting')

# Database connection
def get_pg_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="testDB",
        user="myuser",
        password="mypassword",
        port="5432"
    )

def get_es_db_connection():
    return Elasticsearch([{
        "host": "localhost", 
        "port": 9201, 
        "scheme": "http"
    }])

# JWT configuration
JWT_SECRET_KEY = secrets.token_hex(16)
JWT_EXPIRATION_DELTA = timedelta(minutes=30)

# Helper function to generate JWT token
def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

logged_in_users = {}
def fetch_user_token():
    return logged_in_users['user_token']

# Define a parser for the authorization header
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('Authorization', type=str, location='headers')

# JWT authentication decorator
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        args = auth_parser.parse_args()
        token = args.get('Authorization', '')

        if not token:
            return {'message': 'Unauthorized access'}, 401

        try:
            decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            g.user = decoded_token
        except jwt.ExpiredSignatureError:
            return {'message': 'Session expired, please login again'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        
        return f(*args, **kwargs)
    
    return decorated

# Create a parser for the login data
login_parser = api.parser()
login_parser.add_argument("username", type=str, location='form', required=True)
login_parser.add_argument("password", type=str, location='form', required=True)

# Create a parser for the signup data
signup_parser = api.parser()
signup_parser.add_argument("email", type=str, required=True)
signup_parser.add_argument("username", type=str, required=True)
signup_parser.add_argument("password", type=str, required=True)

# Create a parser for the search data
search_parser = api.parser()
search_parser.add_argument("title", type=str, required=True)
search_parser.add_argument("amenities", type=str, required=True)
search_parser.add_argument("price", type=float, required=True)
search_parser.add_argument("location", type=str, required=True)

# Controller
@user_namespace.route('/login')
class LoginResource(Resource):
    @api.doc(
        parser=login_parser, 
        description='User Login',
        params={
            'username': 'Enter Your Username',
            'password': 'Enter Password'
        },
        responses={
            200: 'User login successful',
            208: 'User is already logged in',
            404: 'User not found',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Logs user into the system"""
        
        try:
            data = request.form
            username, password = data['username'], data['password']

            conn = get_pg_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name = %s AND user_password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                # Check if the user is already logged in
                if logged_in_users:
                    user_token = fetch_user_token() 
                    return {"message": "User is already logged in", "token": user_token}, 208
            
                token = generate_token(username)
                user_data = {
                    "email": user[1],
                    "username": user[2]
                }

                logged_in_users['user_token'] = token

                return {"message": "User login successful", "user_info": user_data, "token": token}, 200
            else:
                return {"message": "User not found"}, 404
            
        except Exception as e:
            return {'message': 'Internal server error'}, 500

@user_namespace.route('/signup')
class SignupResource(Resource):
    @api.doc(
        parser=signup_parser, 
        description='User Registration',
        params={
            'email': 'Enter Your Email',
            'username': 'Enter Your Username',
            'password': 'Enter Password'
        },
        responses={
            201: 'User created successful',
            400: 'Invalid format',
            409: 'User already exists',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Create a new user"""

        try:
            args = signup_parser.parse_args()
            email = args["email"]
            username = args["username"]
            password = args["password"]

            # Check if the email or username already exists
            conn = get_pg_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_email = %s OR user_name = %s", (email, username))

            existing_user = cursor.fetchone()
            if existing_user:
                if existing_user[1] == email:
                    return {'message': 'User already exists'}, 409
                if existing_user[2] == username:
                    return {'message': 'Username already taken'}, 409
            
            # Validate input fields
            if not email.endswith('@gmail.com'):
                return {'message': 'Invalid email format. Email must end with @gmail.com'}, 400
 
            if not re.match(r'^[a-z]+[0-9]', username):
                return {'message': 'Invalid username format. Username should be start with a small letter, followed by other small letters and a number.'}, 400
            
            if not re.match(r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>])[a-zA-Z0-9!@#$%^&*(),.?":{}|<>]{6}$', password):
                return {'message': 'Invalid password format. Password should be 6 characters long and contain at least 1 number and 1 special character.'}, 400

            # Insert the new user into the database
            cursor.execute("INSERT INTO users (user_email, user_name, user_password) VALUES (%s, %s, %s)", (email, username, password))
            conn.commit()
            return {'message': 'User created successfully'}, 201

        except Exception as e:
            return {'message': 'Internal server error'}, 500
        
@room_namespace.route('/search')
class SearchResource(Resource):
    @api.doc(
        security='apikey',
        parser=search_parser, 
        description='User Login',
        params={
            'title': 'Enter Title',
            'amenities': 'Enter Amenities',
            'price': 'Enter Price',
            'location': 'Enter Location'
        },
        responses={
            200: 'Data found',
            404: 'Data not found',
            500: 'Internal server error'
        }
    )
    # @jwt_required
    def get(self):
        """Searches room by title, amenities, price, and location"""

        try:
            args = search_parser.parse_args()
            title = args["title"]
            amenities = args["amenities"]
            price = args["price"]
            location = args["location"]

            conn = get_es_db_connection()
            body = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"title": title}},
                            {"match": {"amenities": amenities}},
                            {"range": {"price": {"lte": price}}},
                            {"match": {"location": location}}
                        ]
                    }
                }
            }
            result = conn.search(index='room_info', body=body)
            data = result['hits']['hits']
            sources = [entry["_source"] for entry in data]
            
            return {'message': 'User created successfully', 'results': sources}, 200

        except Exception as e:
            return {'message': 'Internal server error'}, 500

# api.add_resource(SignupResource, "/signup")
# api.add_namespace(user_namespace, path='/user')

if __name__=='__main__':
    app.run(debug=True)