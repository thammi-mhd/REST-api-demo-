from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import Swagger
from datetime import timedelta
from functools import wraps
import re
import os
import logging
from logging.handlers import RotatingFileHandler


# Simple helpers for validating user input
def validate_email(email):
    # Basic email format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    # Keep password rule simple for this project
    return len(password) >= 6


# Flask app setup
app = Flask(__name__)

# Database config (SQLite by default, PostgreSQL if provided)
db_url = os.getenv("DATABASE_URL", "sqlite:///users.db")

# Fix older postgres URL format if present
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT settings
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Swagger is used only for API testing/documentation
swagger = Swagger(app)


# Logging setup (kept simple)
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


# Database models
class User(db.Model):
    # Stores user login and role info
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")


class Task(db.Model):
    # Each task belongs to a user
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# Admin-only route protection
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# Frontend pages (used only to test APIs)
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


# Register API
@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    app.logger.info(
        f"Registration attempt for email: {data.get('email') if data else 'None'}"
    )

    if not data or not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "All fields are required"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if len(name) < 2:
        return jsonify({"message": "Name must be at least 2 characters"}), 400

    if not validate_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    if not validate_password(password):
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Hash password before saving
    hashed_pw = generate_password_hash(password)

    # First user becomes admin (for demo/testing)
    role = "admin" if User.query.count() == 0 else "user"

    user = User(name=name, email=email, password=hashed_pw, role=role)

    try:
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"User registered: {email} ({role})")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(str(e))
        return jsonify({"message": "Registration failed"}), 500


# Login API
@app.route("/api/v1/auth/login", methods=["POST"])
def login_api():
    data = request.get_json()
    app.logger.info(
        f"Login attempt for email: {data.get('email') if data else 'None'}"
    )

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create JWT token with role info
    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "id": user.id
        }
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user.role
    }), 200


# Create task
@app.route("/api/v1/tasks", methods=["POST"])
@jwt_required()
def create_task():
    claims = get_jwt()
    user_id = claims.get("id")

    data = request.get_json()
    app.logger.info(f"Creating task for user {user_id}")

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not title:
        return jsonify({"message": "Task title is required"}), 400

    task = Task(title=title, description=description, user_id=user_id)

    try:
        db.session.add(task)
        db.session.commit()
        return jsonify({"message": "Task created", "id": task.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create task"}), 500


# Get tasks for logged-in user
@app.route("/api/v1/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    claims = get_jwt()
    user_id = claims.get("id")

    tasks = Task.query.filter_by(user_id=user_id).all()

    return jsonify([
        {"id": t.id, "title": t.title, "description": t.description}
        for t in tasks
    ]), 200


# Update task
@app.route("/api/v1/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    claims = get_jwt()
    user_id = claims.get("id")
    data = request.get_json()

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)

    db.session.commit()
    return jsonify({"message": "Task updated"}), 200


# Delete task
@app.route("/api/v1/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    claims = get_jwt()
    user_id = claims.get("id")

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


# Admin: get all users
@app.route("/api/v1/admin/users", methods=["GET"])
@jwt_required()
@admin_required
def get_all_users():
    users = User.query.all()

    return jsonify([
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
        for u in users
    ]), 200


# Admin: delete a user
@app.route("/api/v1/admin/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        Task.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Failed to delete user"}), 500


# Start server
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
