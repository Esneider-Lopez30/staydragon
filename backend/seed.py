"""
Carga datos de ejemplo para poder probar y grabar la demo sin partir de cero.
Uso:  python seed.py
"""
from datetime import date
from app import create_app
from extensions import db
from models import User, Listing, Booking, Payment, Review

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(name="Admin StayDragon", email="admin@staydragon.co", role="administrador")
    admin.set_password("admin123")

    maria = User(name="María Gómez", email="maria@staydragon.co", role="anfitrion")
    maria.set_password("anfitrion123")

    juan = User(name="Juan Pérez", email="juan@staydragon.co", role="turista")
    juan.set_password("turista123")

    db.session.add_all([admin, maria, juan])
    db.session.commit()

    finca = Listing(
        host_id=maria.id,
        title="Finca La Esperanza",
        description="Cabaña rodeada de naturaleza, ideal para desconectarse y disfrutar de actividades de ecoturismo.",
        category="alojamiento",
        city="Rionegro",
        country="Colombia",
        latitude=6.1537,
        longitude=-75.3738,
        price_per_night=180000,
    )
    sendero = Listing(
        host_id=maria.id,
        title="Caminata ecológica Cerro Verde",
        description="Recorrido guiado de 3 horas por senderos naturales con avistamiento de aves.",
        category="actividad",
        city="Guatapé",
        country="Colombia",
        latitude=6.2322,
        longitude=-75.1598,
        price_per_night=65000,
    )
    db.session.add_all([finca, sendero])
    db.session.commit()

    booking = Booking(
        listing_id=finca.id,
        tourist_id=juan.id,
        check_in=date(2026, 10, 12),
        check_out=date(2026, 10, 14),
        guests=2,
        total_price=360000,
        status="confirmada",
    )
    db.session.add(booking)
    db.session.flush()

    payment = Payment(
        booking_id=booking.id,
        method="tarjeta",
        amount=360000,
        status="aprobado",
        transaction_id="TXN-SEED0001AB",
    )
    db.session.add(payment)

    review = Review(listing_id=finca.id, tourist_id=juan.id, rating=5, comment="Excelente experiencia, muy recomendado.")
    db.session.add(review)

    db.session.commit()
    print("Base de datos poblada con datos de ejemplo.")
    print("  admin@staydragon.co / admin123  (administrador)")
    print("  maria@staydragon.co / anfitrion123  (anfitrión)")
    print("  juan@staydragon.co / turista123  (turista)")
