from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models import Listing, BlockedDate, User

listing_bp = Blueprint("listings", __name__, url_prefix="/api/listings")


def _require_role(*roles):
    claims = get_jwt()
    if claims.get("role") not in roles:
        return False
    return True


@listing_bp.get("")
def search_listings():
    """RF-04: búsqueda y filtrado por ciudad, categoría y precio máximo."""
    city = request.args.get("city", "").strip()
    category = request.args.get("category", "").strip()
    max_price = request.args.get("max_price", type=float)

    query = Listing.query.filter_by(is_active=True)
    if city:
        query = query.filter(Listing.city.ilike(f"%{city}%"))
    if category:
        query = query.filter_by(category=category)
    if max_price is not None:
        query = query.filter(Listing.price_per_night <= max_price)

    listings = query.order_by(Listing.created_at.desc()).all()
    return jsonify([l.to_dict(include_host=True) for l in listings]), 200


@listing_bp.get("/<int:listing_id>")
def get_listing(listing_id):
    """RF-05: detalle de un alojamiento/actividad."""
    listing = Listing.query.get_or_404(listing_id)
    data = listing.to_dict(include_host=True)
    data["blocked_dates"] = [b.blocked_date.isoformat() for b in listing.blocked_dates]
    data["reviews"] = [
        {"rating": r.rating, "comment": r.comment, "author": r.author.name}
        for r in listing.reviews
    ]
    return jsonify(data), 200


@listing_bp.post("")
@jwt_required()
def create_listing():
    """RF-03: publicación de alojamiento/actividad (solo anfitrión)."""
    if not _require_role("anfitrion"):
        return jsonify({"error": "solo un anfitrión puede publicar"}), 403

    data = request.get_json(silent=True) or {}
    required = ["title", "city", "price_per_night"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"campos obligatorios faltantes: {missing}"}), 400

    listing = Listing(
        host_id=int(get_jwt_identity()),
        title=data["title"],
        description=data.get("description", ""),
        category=data.get("category", "alojamiento"),
        city=data["city"],
        country=data.get("country", "Colombia"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        price_per_night=float(data["price_per_night"]),
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify(listing.to_dict()), 201


@listing_bp.get("/mine")
@jwt_required()
def my_listings():
    """Publicaciones del anfitrión autenticado, para su panel."""
    if not _require_role("anfitrion"):
        return jsonify({"error": "solo un anfitrión tiene publicaciones"}), 403
    listings = Listing.query.filter_by(host_id=int(get_jwt_identity())).all()
    return jsonify([l.to_dict() for l in listings]), 200


@listing_bp.post("/<int:listing_id>/blocked-dates")
@jwt_required()
def block_date(listing_id):
    """RF-07: el anfitrión gestiona la disponibilidad bloqueando fechas puntuales."""
    listing = Listing.query.get_or_404(listing_id)
    if not _require_role("anfitrion") or listing.host_id != int(get_jwt_identity()):
        return jsonify({"error": "no autorizado sobre esta publicación"}), 403

    data = request.get_json(silent=True) or {}
    try:
        blocked = date.fromisoformat(data.get("date", ""))
    except ValueError:
        return jsonify({"error": "date debe tener formato YYYY-MM-DD"}), 400

    entry = BlockedDate(listing_id=listing.id, blocked_date=blocked, reason=data.get("reason"))
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201
