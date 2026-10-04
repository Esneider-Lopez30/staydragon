import requests
from flask import Blueprint, request, jsonify, current_app

geo_bp = Blueprint("geo", __name__, url_prefix="/api/geo")


@geo_bp.get("/search")
def geocode_search():
    """
    RF-10: Geolocalización.

    Integración real con la API pública de OpenStreetMap Nominatim para
    convertir un nombre de lugar (ej. "Rionegro, Antioquia") en coordenadas
    (lat/lon), sin necesidad de API key. Es la integración con API externa
    que exige el entregable 3 de la Fase 2.
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "parámetro 'q' es obligatorio"}), 400

    try:
        resp = requests.get(
            current_app.config["NOMINATIM_URL"],
            params={"q": q, "format": "json", "limit": 5, "addressdetails": 1},
            headers={"User-Agent": current_app.config["NOMINATIM_USER_AGENT"]},
            timeout=6,
        )
        resp.raise_for_status()
        raw_results = resp.json()
    except requests.RequestException as exc:
        return jsonify({"error": f"no se pudo consultar el servicio de mapas: {exc}"}), 502

    results = [
        {
            "display_name": r.get("display_name"),
            "latitude": float(r["lat"]),
            "longitude": float(r["lon"]),
        }
        for r in raw_results
    ]
    return jsonify(results), 200
