from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db
from models import User, ROLES

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role", "turista")

    if not name or not email or not password:
        return jsonify({"error": "name, email y password son obligatorios"}), 400
    if role not in ROLES:
        return jsonify({"error": f"role debe ser uno de {ROLES}"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "ya existe un usuario con ese correo"}), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "name": user.name})
    return jsonify({"user": user.to_dict(), "access_token": token}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "credenciales inválidas"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "name": user.name})
    return jsonify({"user": user.to_dict(), "access_token": token}), 200
