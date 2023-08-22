# Flask Assignment API

The Flask Assignment API is a RESTful web service built using Flask and Flask-RESTx that provides user authentication, user registration, and room search functionalities. The API uses PostgreSQL for user data storage and Elasticsearch for room data storage.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [PostgreSQL Setup](#postgresql-setup)
  - [Elasticsearch and Kibana Setup](#elasticsearch-and-kibana-setip)
- [API Endpoints](#api-endpoints)
  - [User Login](#user-login)
  - [User Registration](#user-registration)
  - [Room Search](#room-search)
- [Authentication](#authentication)
- [Data Storage](#data-storage)
- [Contributing](#contributing)
- [License](#license)

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
Now open your browser and type `http://localhost:8080` into the url to access PostgreSQL. For login give email: admin@user.com and password: adminuser. 

**5. Elasticsearch and Kibana setup:**
```bash
cd ..
cd es
docker-compose up -d
```
Now again open your browser and type `http://localhost:9201` into the url to access Elasticsearch and Kibana.

To find containers name and ports:
```bash
docker ps -a
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