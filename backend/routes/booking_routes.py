import random
import string
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models import Booking, Listing, Payment, BlockedDate

booking_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


def _dates_overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end


def _generate_transaction_id():
    return "TXN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


@booking_bp.post("")
@jwt_required()
def create_booking():
    """RF-06 + RF-08: crear una reserva y procesar su pago (pasarela simulada)."""
    claims = get_jwt()
    if claims.get("role") != "turista":
        return jsonify({"error": "solo un turista puede reservar"}), 403

    data = request.get_json(silent=True) or {}
    listing = Listing.query.get_or_404(data.get("listing_id"))

    try:
        check_in = date.fromisoformat(data.get("check_in", ""))
        check_out = date.fromisoformat(data.get("check_out", ""))
    except ValueError:
        return jsonify({"error": "check_in/check_out deben tener formato YYYY-MM-DD"}), 400

    if check_out <= check_in:
        return jsonify({"error": "check_out debe ser posterior a check_in"}), 400

    # Validar contra reservas confirmadas existentes
    existing = Booking.query.filter_by(listing_id=listing.id, status="confirmada").all()
    for b in existing:
        if _dates_overlap(check_in, check_out, b.check_in, b.check_out):
            return jsonify({"error": "el alojamiento no está disponible en esas fechas"}), 409

    # Validar contra fechas bloqueadas manualmente por el anfitrión
    blocked = {b.blocked_date for b in listing.blocked_dates}
    d = check_in
    while d < check_out:
        if d in blocked:
            return jsonify({"error": f"la fecha {d.isoformat()} no está disponible"}), 409
        d = date.fromordinal(d.toordinal() + 1)

    nights = (check_out - check_in).days
    total_price = nights * listing.price_per_night

    booking = Booking(
        listing_id=listing.id,
        tourist_id=int(get_jwt_identity()),
        check_in=check_in,
        check_out=check_out,
        guests=data.get("guests", 1),
        total_price=total_price,
        status="pendiente",
    )
    db.session.add(booking)
    db.session.flush()  # para obtener booking.id antes del commit final

    # --- Pasarela de pagos simulada ---
    # En un entorno real, aquí se llamaría a la API de PSE/Wompi/Stripe.
    # Para el entorno académico se simula una aprobación determinística.
    payment_method = data.get("payment_method", "tarjeta")
    payment = Payment(
        booking_id=booking.id,
        method=payment_method,
        amount=total_price,
        status="aprobado",
        transaction_id=_generate_transaction_id(),
    )
    booking.status = "confirmada"
    db.session.add(payment)
    db.session.commit()

    return jsonify(booking.to_dict()), 201


@booking_bp.get("/mine")
@jwt_required()
def my_bookings():
    """Reservas del turista autenticado."""
    bookings = Booking.query.filter_by(tourist_id=int(get_jwt_identity())).order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@booking_bp.get("/host")
@jwt_required()
def host_bookings():
    """Reservas recibidas por un anfitrión, para su panel."""
    claims = get_jwt()
    if claims.get("role") != "anfitrion":
        return jsonify({"error": "solo un anfitrión puede ver reservas recibidas"}), 403

    host_listing_ids = [l.id for l in Listing.query.filter_by(host_id=int(get_jwt_identity())).all()]
    bookings = Booking.query.filter(Booking.listing_id.in_(host_listing_ids)).all()
    return jsonify([b.to_dict() for b in bookings]), 200
