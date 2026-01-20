Task Management REST API

Backend Developer Internship Assignment

This project is a Task Management REST API built as part of a Backend Developer Internship assignment.
The main focus of this project is backend development, including authentication, role-based access control, and CRUD operations, along with a small frontend to test the APIs.

The backend is built using Flask and SQLAlchemy, with JWT-based authentication for securing routes.

Project Overview

The API allows users to:

Register and log in

Receive a JWT token after login

Create, view, update, and delete tasks

Access protected routes using JWT

Restrict certain routes to admin users only

A basic frontend is included to test authentication and task operations.

Tech Stack

Backend

Flask

Flask-SQLAlchemy

Flask-JWT-Extended

Werkzeug (password hashing)

Flasgger (Swagger documentation)

Database

SQLite (development)

PostgreSQL (production-ready)

Frontend

HTML

CSS

Vanilla JavaScript

Tools

Postman

Git and GitHub

Getting Started
1. Clone the Repository
git clone <repository-url>
cd project

2. Create Virtual Environment
python -m venv env


Activate the environment:

# Windows
.\env\Scripts\activate

# macOS / Linux
source env/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Environment Variables (Optional)

Create a .env file in the project root:

DATABASE_URL=postgresql://user:password@localhost/taskdb
JWT_SECRET_KEY=your-secret-key


If no database URL is provided, SQLite will be used by default.

5. Run the Application
python app.py


The server will run at:

http://127.0.0.1:5000

API Documentation
Swagger

Swagger UI is available at:

http://127.0.0.1:5000/apidocs

Base API URL
/api/v1

Authentication

Users register using /api/v1/auth/register

Users log in using /api/v1/auth/login

A JWT token is returned after login

The token must be sent in the Authorization header for protected routes:

Authorization: Bearer <token>


The first registered user is assigned the admin role. All other users are regular users.

API Endpoints
Authentication

POST /api/v1/auth/register

POST /api/v1/auth/login

Tasks (JWT Required)

POST /api/v1/tasks

GET /api/v1/tasks

PUT /api/v1/tasks/<task_id>

DELETE /api/v1/tasks/<task_id>

Admin (Admin Only)

GET /api/v1/admin/users

Database Schema
Users

id

name

email (unique)

password (hashed)

role

Tasks

id

title

description

user_id (foreign key)

Security

Passwords are hashed using Werkzeug

JWT tokens are required for protected routes

Tokens expire automatically

Role-based access control is enforced for admin routes

Users can only access their own tasks

Logging

Application logs are stored in:

logs/app.log


Logs include authentication attempts and task-related actions.

Testing

A Postman collection is included in the repository

All endpoints were tested using Postman

Protected routes return appropriate error codes when accessed without a token

Deployment

Run locally using:

python app.py


For production, the app can be deployed using Gunicorn and PostgreSQL.

Project Structure
project/
├── app.py
├── requirements.txt
├── templates/
├── static/
├── logs/
├── postman_collection.json
├── README.md
└── SCALABILITY.md

Notes

This project was built to demonstrate backend fundamentals such as API design, authentication, security, and basic scalability considerations as part of an internship assignment.

Author

Backend Developer Internship Assignment
2026
