from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

# Roles válidos del sistema (ver Fase 1 - sección "Roles del Sistema")
ROLES = ("turista", "anfitrion", "administrador")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="turista")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    listings = db.relationship("Listing", backref="host", lazy=True)
    bookings = db.relationship("Booking", backref="tourist", lazy=True)
    reviews = db.relationship("Review", backref="author", lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Listing(db.Model):
    """Publicación de un anfitrión: alojamiento o actividad de ecoturismo."""
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    category = db.Column(db.String(40), nullable=False, default="alojamiento")  # alojamiento | actividad
    city = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(80), nullable=False, default="Colombia")
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    price_per_night = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="listing", lazy=True)
    reviews = db.relationship("Review", backref="listing", lazy=True)
    blocked_dates = db.relationship("BlockedDate", backref="listing", lazy=True)

    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    def to_dict(self, include_host=False):
        data = {
            "id": self.id,
            "host_id": self.host_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "city": self.city,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "price_per_night": self.price_per_night,
            "is_active": self.is_active,
            "average_rating": self.average_rating(),
            "review_count": len(self.reviews),
        }
        if include_host and self.host:
            data["host_name"] = self.host.name
        return data


class BlockedDate(db.Model):
    """Fechas que el anfitrión marca manualmente como no disponibles (RF-07)."""
    __tablename__ = "blocked_dates"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)
    blocked_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(160), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "date": self.blocked_date.isoformat(),
            "reason": self.reason,
        }


class Booking(db.Model):
    """Reserva de un turista sobre un listing (RF-06)."""
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pendiente")  # pendiente|confirmada|cancelada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payment = db.relationship("Payment", backref="booking", uselist=False, lazy=True)

    def nights(self):
        return (self.check_out - self.check_in).days

    def to_dict(self):
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "tourist_id": self.tourist_id,
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "nights": self.nights(),
            "guests": self.guests,
            "total_price": self.total_price,
            "status": self.status,
            "payment": self.payment.to_dict() if self.payment else None,
        }


class Payment(db.Model):
    """Pago asociado a una reserva (RF-08). Pasarela simulada para el entorno académico."""
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), unique=True, nullable=False)
    method = db.Column(db.String(30), nullable=False)  # tarjeta | pse | billetera
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="aprobado")
    transaction_id = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "method": self.method,
            "amount": self.amount,
            "status": self.status,
            "transaction_id": self.transaction_id,
        }


class Review(db.Model):
    """Calificación y reseña de un turista sobre un listing (RF-09)."""
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "tourist_id": self.tourist_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
