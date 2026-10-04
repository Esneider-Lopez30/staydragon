from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import User, Listing, Booking

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _require_admin():
    return get_jwt().get("role") == "administrador"


@admin_bp.get("/users")
@jwt_required()
def list_users():
    """RF-13: panel administrativo - gestión de usuarios."""
    if not _require_admin():
        return jsonify({"error": "solo un administrador puede ver esta información"}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.get("/stats")
@jwt_required()
def stats():
    """RF-13: reportes básicos para el panel administrativo."""
    if not _require_admin():
        return jsonify({"error": "solo un administrador puede ver esta información"}), 403
    return jsonify({
        "total_usuarios": User.query.count(),
        "total_turistas": User.query.filter_by(role="turista").count(),
        "total_anfitriones": User.query.filter_by(role="anfitrion").count(),
        "total_publicaciones": Listing.query.count(),
        "total_reservas": Booking.query.count(),
        "reservas_confirmadas": Booking.query.filter_by(status="confirmada").count(),
    }), 200


@admin_bp.patch("/users/<int:user_id>/deactivate")
@jwt_required()
def deactivate_user_listings(user_id):
    """RF-13: moderación básica - desactivar todas las publicaciones de un anfitrión."""
    if not _require_admin():
        return jsonify({"error": "solo un administrador puede moderar contenido"}), 403
    listings = Listing.query.filter_by(host_id=user_id).all()
    for l in listings:
        l.is_active = False
    from extensions import db
    db.session.commit()
    return jsonify({"desactivadas": len(listings)}), 200
