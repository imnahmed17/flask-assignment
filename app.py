from flask import Flask, request, g
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

# JWT configuration
JWT_SECRET_KEY = secrets.token_hex(32)
JWT_EXPIRATION_DELTA = timedelta(minutes=30)

# Define a parser for the authorization header
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('Authorization', type=str, location='headers')

# Create a parser for the login data
login_parser = api.parser()
login_parser.add_argument("username", type=str, location='form')
login_parser.add_argument("password", type=str, location='form')

# Create a parser for the signup data
signup_parser = api.parser()
signup_parser.add_argument("email", type=str, location='form')
signup_parser.add_argument("username", type=str, location='form')
signup_parser.add_argument("password", type=str, location='form')

# Create a parser for the search data
search_parser = api.parser()
search_parser.add_argument("title", type=str)
search_parser.add_argument("amenities", type=str)
search_parser.add_argument("price", type=str)
search_parser.add_argument("location", type=str)
search_parser.add_argument("sort_by_price", type=str, choices=("asc", "desc"), default="asc")

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

# Helper function to generate JWT token
def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

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
            400: 'Provide username and password',
            404: 'User not found',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Logs user into the system"""
        
        try:
            data = request.form
            username = data.get('username')
            password = data.get('password')

            if username is None:
                return {"message": "Please, provide your username"}, 400
            elif password is None:
                return {"message": "Please, provide your password"}, 400

            conn = get_pg_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name = %s AND user_password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                token = generate_token(username)
                user_data = {
                    "email": user[1],
                    "username": user[2]
                }

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
            400: 'Invalid input format',
            409: 'User already exists',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Create a new user"""

        try:
            data = request.form
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')

            if email is None:
                return {"message": "Please, provide your email"}, 400
            elif username is None:
                return {"message": "Please, provide your username"}, 400
            elif password is None:
                return {"message": "Please, provide your password"}, 400

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
            if not re.match(r'^[a-z][a-z0-9._]*@gmail\.com$', email):
                return {'message': 'Email must be start with a small letter, no space and end with @gmail.com'}, 400
 
            if not re.match(r'^(?=.*\d)[a-z\S]*$', username):
                return {'message': 'Username should be start with a small letter, followed by other small letters and a number.'}, 400
            
            if not re.match(r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>])[a-zA-Z0-9!@#$%^&*(),.?":{}|<>]{6}$', password):
                return {'message': 'Password should be 6 characters long and contain at least 1 number and 1 special character.'}, 400

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
            200: 'Data found successfully',
            400: 'Invalid input format',
            404: 'No data found',
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
            sort_by_price = args["sort_by_price"]

            # Input field validation
            if (title and len(title) < 3) or (amenities and len(amenities) < 3) or (location and len(location) < 3):
                return {'message': 'Input fields must have 3 characters'}, 400

            if price and (not price.isnumeric() or int(price) <= 0):
                return {'message': 'Price must be numeric and positive'}, 400

            if location is None:
                return {'message': 'Location is required'}, 400

            conn = get_es_db_connection()
            body = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "sort": [
                    { "price": { "order": sort_by_price } }
                ]
            }

            if title:
                body["query"]["bool"]["must"].append({ "wildcard": { "title": { "value": "*" + title.strip().lower() + "*" } } })

            if amenities:
                body["query"]["bool"]["must"].append({ "wildcard": { "amenities": { "value": "*" + amenities.strip().lower() + "*" } } })

            if price:
                body["query"]["bool"]["must"].append({ "range": { "price": {"lte": price } } })

            if location:
                body["query"]["bool"]["must"].append({ "wildcard": { "location": { "value": "*" + location.strip().lower() + "*" } } })

            result = conn.search(index='room_info', body=body)
            data = result['hits']['hits']

            if not data:  
                return {'message': 'No data found'}, 404
        
            sources = [entry["_source"] for entry in data]
            
            return {'message': 'Data found successfully', 'results': sources}, 200

        except Exception as e:
            return {'message': 'Internal server error'}, 500

# api.add_resource(SignupResource, "/signup")
# api.add_namespace(user_namespace, path='/user')

if __name__=='__main__':
    app.run(debug=True)