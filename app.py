from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import Swagger
from datetime import timedelta
from functools import wraps
import re
import os
import logging
from logging.handlers import RotatingFileHandler

# ===============================
# VALIDATION HELPERS
# ===============================
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength (min 6 chars)"""
    return len(password) >= 6

# ===============================
# APP CONFIG
# ===============================
app = Flask(__name__)

# Database Configuration - Support both SQLite and PostgreSQL
db_url = os.getenv("DATABASE_URL", "sqlite:///users.db")
# Fix PostgreSQL URL format if needed
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Initialize Swagger for API documentation
swagger = Swagger(app)

# ===============================
# LOGGING CONFIGURATION
# ===============================
if not os.path.exists("logs"):
    os.mkdir("logs")

file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info("Backend API server started")

# ===============================
# DATABASE MODELS
# ===============================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ===============================
# ROLE-BASED DECORATOR
# ===============================
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# ===============================
# FRONTEND ROUTES
# ===============================
@app.route("/")
def home():
    return render_template("register.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ===============================
# AUTH APIs
# ===============================
@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User registered successfully"
      400:
        description: Invalid input or email already exists
      500:
        description: Registration failed
    """
    data = request.get_json()
    app.logger.info(f"Registration attempt for email: {data.get('email') if data else 'None'}")

    # Validate all required fields
    if not data or not data.get("name") or not data.get("email") or not data.get("password"):
        app.logger.warning("Registration failed: Missing required fields")
        return jsonify({"message": "All fields are required"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Validate name
    if len(name) < 2:
        return jsonify({"message": "Name must be at least 2 characters"}), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    # Validate password strength
    if not validate_password(password):
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        app.logger.warning(f"Registration failed: Email {email} already exists")
        return jsonify({"message": "Email already exists"}), 400

    # Hash password
    hashed_pw = generate_password_hash(password)

    # First user becomes admin (demo purpose)
    role = "admin" if User.query.count() == 0 else "user"

    # Create user
    user = User(
        name=name,
        email=email,
        password=hashed_pw,
        role=role
    )

    try:
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"User registered successfully: {email} with role: {role}")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration failed: {str(e)}")
        return jsonify({"message": "Registration failed. Please try again."}), 500


@app.route("/api/v1/auth/login", methods=["POST"])
def login_api():
    """
    Login user and receive JWT token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
            token:
              type: string
            role:
              type: string
      401:
        description: Invalid credentials
      400:
        description: Missing email or password
    """
    data = request.get_json()
    app.logger.info(f"Login attempt for email: {data.get('email') if data else 'None'}")

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        app.logger.warning(f"Login failed: Invalid credentials for {data.get('email')}")
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "id": user.id
        }
    )

    app.logger.info(f"User logged in successfully: {user.email}")
    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user.role
    }), 200


# ===============================
# TASK CRUD APIs
# ===============================
@app.route("/api/v1/tasks", methods=["POST"])
@jwt_required()
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: "Buy groceries"
            description:
              type: string
              example: "Buy milk and eggs"
    responses:
      201:
        description: Task created successfully
      400:
        description: Task title is required
      401:
        description: Unauthorized - missing token
    """
    claims = get_jwt()
    user_id = claims.get("id")
    
    try:
        data = request.get_json()
    except Exception as e:
        app.logger.error(f"Invalid JSON received: {str(e)}")
        return jsonify({"message": "Invalid request format"}), 400
    
    app.logger.info(f"Creating task for user {user_id}: {data.get('title') if data else 'None'}")

    if not data:
        return jsonify({"message": "Request body is required"}), 400
    
    title = data.get("title", "").strip() if isinstance(data.get("title"), str) else ""
    description = data.get("description", "").strip() if isinstance(data.get("description"), str) else ""
    
    if not title:
        return jsonify({"message": "Task title is required"}), 400

    task = Task(
        title=title,
        description=description,
        user_id=user_id
    )

    try:
        db.session.add(task)
        db.session.commit()
        app.logger.info(f"Task created successfully: {task.id}")
        return jsonify({"message": "Task created", "id": task.id}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Task creation failed: {str(e)}")
        return jsonify({"message": "Failed to create task"}), 500


@app.route("/api/v1/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    """
    Get all tasks for the current user
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    responses:
      200:
        description: List of user's tasks
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              description:
                type: string
      401:
        description: Unauthorized
    """
    claims = get_jwt()
    user_id = claims.get("id")
    app.logger.info(f"Fetching tasks for user {user_id}")

    tasks = Task.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description
        } for t in tasks
    ]), 200


@app.route("/api/v1/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    """
    Update a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      200:
        description: Task updated successfully
      404:
        description: Task not found
      401:
        description: Unauthorized
    """
    claims = get_jwt()
    user_id = claims.get("id")
    data = request.get_json()
    app.logger.info(f"Updating task {task_id} for user {user_id}")

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id
    ).first()

    if not task:
        app.logger.warning(f"Task {task_id} not found for user {identity['id']}")
        return jsonify({"message": "Task not found"}), 404

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)

    db.session.commit()
    app.logger.info(f"Task {task_id} updated successfully")
    return jsonify({"message": "Task updated"}), 200


@app.route("/api/v1/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    """
    Delete a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Task deleted successfully
      404:
        description: Task not found
      401:
        description: Unauthorized
    """
    claims = get_jwt()
    user_id = claims.get("id")
    app.logger.info(f"Deleting task {task_id} for user {user_id}")

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id
    ).first()

    if not task:
        app.logger.warning(f"Task {task_id} not found for user {user_id}")
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    app.logger.info(f"Task {task_id} deleted successfully")

    return jsonify({"message": "Task deleted"}), 200


# ===============================
# ADMIN-ONLY API
# ===============================
@app.route("/api/v1/admin/users", methods=["GET"])
@jwt_required()
@admin_required
def get_all_users():
    """
    Get all users (admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              email:
                type: string
              role:
                type: string
      403:
        description: Admin access required
      401:
        description: Unauthorized
    """
    app.logger.info("Admin fetching all users")
    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role
        } for u in users
    ]), 200


@app.route("/api/v1/admin/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Delete a specific user (admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
      403:
        description: Admin access required
      401:
        description: Unauthorized
    """
    user = User.query.filter_by(id=user_id).first()

    if not user:
        app.logger.warning(f"Delete user attempt: User {user_id} not found")
        return jsonify({"message": "User not found"}), 404

    try:
        # Delete all tasks for this user first
        Task.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        app.logger.info(f"Admin deleted user: {user_id}")
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify({"message": "Failed to delete user"}), 500


@app.route("/api/v1/admin/users/delete-all", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_all_users():
    """
    Delete all users except the current admin (DANGEROUS - admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: All users deleted successfully
      403:
        description: Admin access required
      401:
        description: Unauthorized
    """
    claims = get_jwt()
    current_admin_id = claims.get("id")
    
    try:
        # Delete all tasks
        Task.query.delete()
        # Delete all users except current admin
        User.query.filter(User.id != current_admin_id).delete()
        db.session.commit()
        app.logger.warning(f"Admin {current_admin_id} deleted all users")
        return jsonify({"message": "All users deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting all users: {str(e)}")
        return jsonify({"message": "Failed to delete users"}), 500


# ===============================
# START SERVER
# ===============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

