import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Configuración del backend StayDragon.

    Por defecto usa SQLite (cero configuración, ideal para desarrollo y para
    la sustentación en video). Para producción se define DATABASE_URL con una
    cadena de conexión de PostgreSQL, tal como se documentó en la Fase 1
    (arquitectura 100% Python: Flask + PostgreSQL). El resto del código no
    cambia: SQLAlchemy abstrae el motor de base de datos.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-staydragon")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'staydragon.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-staydragon")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # API externa de geolocalización (OpenStreetMap Nominatim) - sin API key.
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    NOMINATIM_USER_AGENT = "StayDragonApp/1.0 (proyecto academico Uniremington)"
