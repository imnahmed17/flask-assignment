from flask import Flask
from flask_restx import Api, Resource
import psycopg2
import jwt
import re

app = Flask(__name__)
api = Api(app, title='Flask Assignment')

# Create a namespace
user_namespace = api.namespace('user', description='Operations about user')
my_namespace = api.namespace('my', description='Operations about my')

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="testDB",
        user="myuser",
        password="mypassword",
        port="5432"
    )

# Create a parser for the login data
login_parser = api.parser()
login_parser.add_argument("username", type=str, required=True)
login_parser.add_argument("password", type=str, required=True)

# Create a parser for the signup data
signup_parser = api.parser()
signup_parser.add_argument("email", type=str, required=True)
signup_parser.add_argument("username", type=str, required=True)
signup_parser.add_argument("password", type=str, required=True)

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
            404: 'User not found',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Logs user into the system"""
        
        try:
            args = login_parser.parse_args()
            username = args["username"]
            password = args["password"]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name = %s AND user_password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                user_data = {
                    "email": user[1],
                    "username": user[2]
                }
                return {"message": "User login successful", "user_info": user_data}, 200
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
            conn = get_db_connection()
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

# api.add_resource(SignupResource, "/signup")
# api.add_namespace(user_namespace, path='/user')

if __name__=='__main__':
    app.run(debug=True)