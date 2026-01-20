# Task Management REST API - Backend Developer Internship Assignment

A scalable, secure REST API with JWT authentication, role-based access control (RBAC), and a task management CRUD system. Built with Flask, SQLAlchemy, and tested with a modern frontend UI.

## 🎯 Project Overview

This project demonstrates a production-ready backend API that meets enterprise standards for:

- **Security**: JWT-based authentication, password hashing with bcrypt, input validation
- **Scalability**: Database-agnostic design (SQLite/PostgreSQL), logging system, modular architecture
- **RESTful Design**: Proper HTTP status codes, versioned API (`/api/v1/`), comprehensive error handling
- **Documentation**: Swagger/OpenAPI documentation, Postman collection, API logs

### Core Features

✅ User registration & login with JWT tokens  
✅ Role-based access control (Admin/User roles)  
✅ Task CRUD operations (Create, Read, Update, Delete)  
✅ Admin-only endpoints to view all users  
✅ Comprehensive error handling & input validation  
✅ Request/response logging  
✅ Swagger API documentation  
✅ PostgreSQL ready (with environment configuration)

---

## 📋 Requirements

### Tech Stack

- **Backend**: Flask 3.1.2, Flask-SQLAlchemy 3.1.1, Flask-JWT-Extended 4.7.1
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Security**: Werkzeug (password hashing), PyJWT
- **Documentation**: Flasgger (Swagger/OpenAPI)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

### Python Version

- Python 3.8+

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd project
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv env
.\env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables (Optional)

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/taskdb

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production

# Flask
FLASK_ENV=production
FLASK_DEBUG=0
```

### 5. Run Application

```bash
python app.py
```

Server runs on: `http://127.0.0.1:5000`

---

## 📚 API Documentation

### Swagger UI

Access interactive API documentation at:

```
http://127.0.0.1:5000/apidocs
```

### Base URL

```
http://127.0.0.1:5000/api/v1
```

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### Register User

**POST** `/api/v1/auth/register`

Request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

Response (201):

```json
{
  "message": "User registered successfully"
}
```

**Note**: First registered user becomes admin, subsequent users are regular users.

---

### Login User

**POST** `/api/v1/auth/login`

Request:

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

Response (200):

```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin"
}
```

---

## ✅ Task Management Endpoints

### Create Task

**POST** `/api/v1/tasks`

Headers:

```
Authorization: Bearer <token>
Content-Type: application/json
```

Request:

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

Response (201):

```json
{
  "message": "Task created"
}
```

---

### Get All Tasks

**GET** `/api/v1/tasks`

Headers:

```
Authorization: Bearer <token>
```

Response (200):

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  },
  {
    "id": 2,
    "title": "Finish project",
    "description": "Complete backend API"
  }
]
```

---

### Update Task

**PUT** `/api/v1/tasks/<task_id>`

Headers:

```
Authorization: Bearer <token>
Content-Type: application/json
```

Request:

```json
{
  "title": "Buy groceries (updated)",
  "description": "Updated description"
}
```

Response (200):

```json
{
  "message": "Task updated"
}
```

---

### Delete Task

**DELETE** `/api/v1/tasks/<task_id>`

Headers:

```
Authorization: Bearer <token>
```

Response (200):

```json
{
  "message": "Task deleted"
}
```

---

## 👨‍💼 Admin Endpoints

### Get All Users (Admin Only)

**GET** `/api/v1/admin/users`

Headers:

```
Authorization: Bearer <admin_token>
```

Response (200):

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "role": "user"
  }
]
```

**Error Response (403)** - Non-admin trying to access:

```json
{
  "message": "Admin access required"
}
```

---

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);
```

### Tasks Table

```sql
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    user_id INTEGER FOREIGN KEY REFERENCES user(id)
);
```

---

## 🔒 Security Features

### 1. Password Hashing

- Uses bcrypt via Werkzeug's `generate_password_hash()`
- Passwords never stored in plaintext
- Verified with `check_password_hash()`

### 2. JWT Authentication

- Access tokens expire after 1 hour
- Token payload includes: `id`, `email`, `role`
- Invalid/expired tokens rejected

### 3. Input Validation

- Email format validation (regex pattern)
- Password minimum length (6 characters)
- Name minimum length (2 characters)
- Required field checks

### 4. Role-Based Access Control

- Admin decorator (`@admin_required`) protects admin routes
- User can only access/modify own tasks
- First user becomes admin

### 5. Error Handling

- Proper HTTP status codes (400, 401, 403, 404, 500)
- Sanitized error messages (no sensitive data exposed)
- Request/response logging for audit trail

---

## 📝 HTTP Status Codes

| Code | Meaning      | Example                              |
| ---- | ------------ | ------------------------------------ |
| 200  | OK           | Task retrieved successfully          |
| 201  | Created      | User registered or task created      |
| 400  | Bad Request  | Missing required field               |
| 401  | Unauthorized | Invalid credentials or missing token |
| 403  | Forbidden    | Non-admin accessing admin endpoint   |
| 404  | Not Found    | Task doesn't exist                   |
| 500  | Server Error | Database error                       |

---

## 📂 Project Structure

```
project/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (optional)
├── logs/
│   └── app.log                # Application logs
├── instance/
│   └── users.db              # SQLite database (development)
├── static/
│   ├── css/
│   │   └── style.css         # Frontend styling
│   └── js/
│       ├── auth.js           # Authentication handlers
│       └── dashboard.js      # Dashboard functionality
├── templates/
│   ├── base.html             # Base template
│   ├── register.html         # Registration page
│   ├── login.html            # Login page
│   └── dashboard.html        # Dashboard page
├── postman_collection.json    # Postman API collection
├── README.md                  # This file
└── SCALABILITY.md            # Scalability architecture
```

---

## 📤 Logging

All requests, authentication attempts, and database operations are logged to `logs/app.log`:

```
2026-01-20 10:30:15,123 INFO: Backend API server started
2026-01-20 10:30:25,456 INFO: Registration attempt for email: john@example.com
2026-01-20 10:30:26,789 INFO: User registered successfully: john@example.com with role: admin
2026-01-20 10:30:35,012 INFO: Login attempt for email: john@example.com
2026-01-20 10:30:36,345 INFO: User logged in successfully: john@example.com
2026-01-20 10:30:45,678 INFO: Creating task for user 1: Buy groceries
```

---

## 🗄️ Database Configuration

### SQLite (Default - Development)

```python
DATABASE_URL = "sqlite:///users.db"
```

### PostgreSQL (Production)

1. Set environment variable:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/taskdb"
```

2. Or update `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/taskdb
```

The application automatically detects and uses the configured database.

---

## 🧪 Testing with Postman

### 1. Import Collection

- Import `postman_collection.json` into Postman
- All requests are pre-configured with examples

### 2. Testing Workflow

```
1. Register → Get user account
2. Login → Get JWT token
3. Create Task → Add new task
4. Get Tasks → View all tasks
5. Update Task → Modify task
6. Delete Task → Remove task
```

### 3. Admin Testing

- Register second user (becomes regular user)
- Login as first user (admin)
- Access `/api/v1/admin/users` → See all users
- Try same endpoint as second user → Get 403 Forbidden

---

## 🌐 Frontend Integration

### Frontend Features

- ✅ User registration with validation
- ✅ Secure login with JWT storage
- ✅ Protected dashboard (requires token)
- ✅ Task CRUD UI
- ✅ Admin panel (visible only to admins)
- ✅ Error/success message display
- ✅ Responsive design

### Frontend Files

- `templates/register.html` - Registration page
- `templates/login.html` - Login page
- `templates/dashboard.html` - Task dashboard
- `static/js/auth.js` - Authentication logic
- `static/js/dashboard.js` - Dashboard functionality
- `static/css/style.css` - Styling

---

## 🚀 Deployment

### Using Python

```bash
python app.py
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)

```bash
docker build -t taskapi .
docker run -p 5000:5000 taskapi
```

---

## 📖 API Validation Rules

### Email

- Must be valid email format
- Must be unique (not already registered)

### Password

- Minimum 6 characters
- Stored as bcrypt hash

### Task Title

- Required field
- Cannot be empty

### Task Description

- Optional field
- Max 200 characters

---

## 🔄 API Versioning

All endpoints follow versioning scheme: `/api/v1/`

This allows future versions like `/api/v2/` without breaking existing clients.

---

## 📊 Performance Considerations

### Database Indexing

- Email is unique (indexed automatically)
- User_id is indexed via foreign key relationship

### Pagination (Future Enhancement)

```python
tasks = Task.query.filter_by(user_id=identity["id"]).paginate(page=1, per_page=10)
```

### Caching (Future Enhancement)

```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@cache.cached(timeout=300)
def get_all_users():
    ...
```

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution**: Install requirements

```bash
pip install -r requirements.txt
```

### Issue: Port 5000 already in use

**Solution**: Use different port

```bash
python -c "import os; os.environ['FLASK_ENV']='production'; exec(open('app.py').read())" --port 5001
```

### Issue: Database connection error with PostgreSQL

**Solution**: Check `DATABASE_URL` environment variable and PostgreSQL service is running

### Issue: "Invalid token" error

**Solution**: Ensure token is included in Authorization header as `Bearer <token>`

---

## 📞 Support & Documentation

### API Docs

- Swagger UI: `http://127.0.0.1:5000/apidocs`
- ReDoc: `http://127.0.0.1:5000/redoc`

### Logs

- Check `logs/app.log` for detailed request/response logging

### Code Comments

- All functions and endpoints have docstrings with examples

---

## 📝 Assignment Deliverables Checklist

✅ **Backend (Primary Focus)**

- [x] User registration & login APIs with password hashing and JWT
- [x] Role-based access (user vs admin)
- [x] CRUD APIs for tasks
- [x] API versioning (`/api/v1/`)
- [x] Error handling & validation
- [x] Swagger/OpenAPI documentation
- [x] Database schema (SQLite + PostgreSQL ready)

✅ **Basic Frontend**

- [x] Register & log in users
- [x] Protected dashboard (JWT required)
- [x] Perform CRUD actions on tasks
- [x] Show error/success messages

✅ **Security & Scalability**

- [x] Secure JWT token handling
- [x] Input sanitization & validation
- [x] Scalable project structure
- [x] Logging system
- [x] PostgreSQL support
- [x] Role-based access control

✅ **Deliverables**

- [x] GitHub repository with README.md
- [x] Working APIs for authentication & CRUD
- [x] Basic frontend UI
- [x] Swagger API documentation
- [x] Scalability documentation (SCALABILITY.md)
- [x] Postman collection
- [x] Request/response logs

---

## 📄 License

This project is for educational purposes as part of backend developer internship assignment.

---

## 👤 Author

Backend Developer Intern Assignment - 2026

---

**Status**: ✅ Complete and Production-Ready

Last Updated: January 20, 2026
