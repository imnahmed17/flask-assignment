# Flask Assignment API

The Flask Assignment API is a RESTful web service built using Flask and Flask-RESTx that provides user authentication, user registration, and room search functionalities. The API uses PostgreSQL for user data storage and Elasticsearch for room data storage.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
  - [User Login](#user-login)
  - [User Registration](#user-registration)
  - [Room Search](#room-search)

## Prerequisites

- Python 
- Flask
- Flask-RESTx
- PyJWT
- Docker
- PostgreSQL / PGAdmin
- Elasticsearch / Kibana

## Installation

**1. Clone this repository:**
```bash
git clone https://github.com/imnahmed17/flask-assignment.git
cd flask-assignment
```

**2. Create and activate virtual environment:**

Firstly, type `Ctrl+Shift+P`. Then select the **Python: Create Environment** command to create a virtual environment in your workspace. Select `venv` and then the Python environment you want to use to create it. After this, type `` Ctrl+Shift+` ``, which creates a terminal and automatically activates the virtual environment by running its activation script.

**3. Install the required dependencies:**

```bash
pip install -r requirement.txt
```

**4. PostgreSQL setup:**
```bash
cd pg
docker-compose up -d
```
Now open your browser and type `http://localhost:8080` into the url to access PostgreSQL. For login give Email: admin@user.com and Password: adminuser. After that, right click on `Server > Register > Server` in left sidemenu. In general tab give type any name you want as Server name. In connection tab give Host name: postgres, Username: myuser, Password: mypassword and save it. Then nevigate your server name and create a database right clicking on your server name. For writing database queries open `Query Tool`. To open `Query Tool` right click on your database name. Now write the below query to create a table using `Query Tool`:
```bash
CREATE TABLE users (
  user_id serial PRIMARY KEY,
  user_email varchar(30) UNIQUE,
  user_name varchar(30) UNIQUE,
  user_password varchar(20)
);
```

**5. Elasticsearch and Kibana setup:**
```bash
cd ..
cd es
docker-compose up -d
```
Now again open your browser and type `http://localhost:5601` into the url to access Elasticsearch and Kibana. After that click on the menu icon and select Dev Tools under Management for writing queries. Write the bellow queries to perform further operations.
```bash
POST /room_info/_bulk
{ "index": { "_id": "1" } }
{ "title": "Spacious Loft", "amenities": ["Gym", "Pool", "Balcony"], "price": 150, "location": "Dhaka, Bangladesh" }
{ "index": { "_id": "2" } }
{ "title": "Lakeside Bungalow", "amenities": ["Fishing Dock", "BBQ"], "price": 130, "location": "Chittagong, Bangladesh" }
{ "index": { "_id": "3" } }
{ "title": "Family Playground", "amenities": ["Playground", "Kid's Room", "WiFi"], "price": 140, "location": "Khulna, Bangladesh" }
{ "index": { "_id": "4" } }
{ "title": "Family Farmhouse", "amenities": ["Canoe", "Fire Pit", "WiFi", "Gym"], "price": 175, "location": "Rajshahi, Bangladesh" }
{ "index": { "_id": "5" } }
{ "title": "Family Townhouse", "amenities": ["Loft Bed", "Artistic Space", "Gym"], "price": 90, "location": "Sylhet, Bangladesh" }
{ "index": { "_id": "6" } }
{ "title": "Family Resthouse", "amenities": ["Hot Tub", "Wildlife Viewing", "WiFi"], "price": 220, "location": "Cox's Bazar, Bangladesh" }
```

To find containers name and ports:
```bash
docker ps -a
```

To stop docker containers:
```bash
docker-compose down
```

**6. Run this application:**
```bash
python app.py
```

## API Endpoints

### User Login

**Endpoint:** `/user/login`

- **Method:** `POST`
- **Description:** Logs a user into the system using their username and password.
- **Request Body:**
  - `username`: User's username
  - `password`: User's password
- **Response:**
  - Success: Appropriate login message with authentication token, user information and http response code.
  - Error: Appropriate error message with http response code.

### User Registration

**Endpoint:** `/user/signup`

- **Method:** `POST`
- **Description:** Creates a new user account.
- **Request Body:**
  - `email`: User's email
  - `username`: User's desired username
  - `password`: User's desired password
- **Response:**
  - Success: Appropriate registration message with http response code.
  - Error: Appropriate error message with http response code.

### Room Search

**Endpoint:** `/room/search`

- **Method:** `GET`
- **Description:** Searches for rooms based on specified criteria.
- **Request Body:**
  - `title`: Room title keyword
  - `amenities`: Room amenities keyword
  - `price`: Maximum room price
  - `location`: Room location keyword
  - `sort_by_price`: Sorting order for search results
- **Response:**
  - Success: List of rooms search result including sorting with http response code.
  - Error: Appropriate error message with http response code.