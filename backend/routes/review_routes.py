from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models import Review, Booking, Listing

review_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@review_bp.post("")
@jwt_required()
def create_review():
    """RF-09: calificar y reseñar un alojamiento/actividad tras la experiencia."""
    claims = get_jwt()
    if claims.get("role") != "turista":
        return jsonify({"error": "solo un turista puede calificar"}), 403

    data = request.get_json(silent=True) or {}
    listing = Listing.query.get_or_404(data.get("listing_id"))
    rating = data.get("rating")
    if rating not in (1, 2, 3, 4, 5):
        return jsonify({"error": "rating debe ser un entero entre 1 y 5"}), 400

    tourist_id = int(get_jwt_identity())
    # Solo puede calificar si tuvo al menos una reserva confirmada de ese listing
    has_booking = Booking.query.filter_by(
        listing_id=listing.id, tourist_id=tourist_id, status="confirmada"
    ).first()
    if not has_booking:
        return jsonify({"error": "solo puedes calificar alojamientos que hayas reservado"}), 403

    review = Review(
        listing_id=listing.id,
        tourist_id=tourist_id,
        rating=rating,
        comment=data.get("comment", ""),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201
