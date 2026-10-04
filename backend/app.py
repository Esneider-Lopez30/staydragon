from flask import Flask, jsonify
from config import Config
from extensions import db, jwt


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    jwt.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.listing_routes import listing_bp
    from routes.booking_routes import booking_bp
    from routes.geo_routes import geo_bp
    from routes.review_routes import review_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(listing_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(geo_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "app": "StayDragon API"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "recurso no encontrado"}), 404

    return app


if __name__ == "__main__":
    flask_app = create_app()
    with flask_app.app_context():
        db.create_all()
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
