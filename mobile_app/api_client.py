"""
Cliente HTTP que conecta la app Flet con el backend Flask de StayDragon.
Centraliza la URL base, el token JWT de la sesión y el manejo de errores.
"""
import requests

BASE_URL = "http://127.0.0.1:5000/api"


class ApiError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self):
        self.token = None
        self.user = None  # {"id", "name", "email", "role"}

    # ---------- helpers internos ----------
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _handle(self, resp):
        if resp.status_code >= 400:
            try:
                msg = resp.json().get("error", "Ocurrió un error")
            except Exception:
                msg = f"Error HTTP {resp.status_code}"
            raise ApiError(msg, resp.status_code)
        return resp.json() if resp.content else None

    # ---------- autenticación ----------
    def register(self, name, email, password, role):
        resp = requests.post(f"{BASE_URL}/auth/register",
                              json={"name": name, "email": email, "password": password, "role": role})
        data = self._handle(resp)
        self.token = data["access_token"]
        self.user = data["user"]
        return data

    def login(self, email, password):
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        data = self._handle(resp)
        self.token = data["access_token"]
        self.user = data["user"]
        return data

    def logout(self):
        self.token = None
        self.user = None

    # ---------- publicaciones ----------
    def search_listings(self, city="", category="", max_price=None):
        params = {}
        if city:
            params["city"] = city
        if category:
            params["category"] = category
        if max_price:
            params["max_price"] = max_price
        resp = requests.get(f"{BASE_URL}/listings", params=params)
        return self._handle(resp)

    def get_listing(self, listing_id):
        resp = requests.get(f"{BASE_URL}/listings/{listing_id}")
        return self._handle(resp)

    def create_listing(self, payload):
        resp = requests.post(f"{BASE_URL}/listings", json=payload, headers=self._headers())
        return self._handle(resp)

    def my_listings(self):
        resp = requests.get(f"{BASE_URL}/listings/mine", headers=self._headers())
        return self._handle(resp)

    def block_date(self, listing_id, date_str, reason=""):
        resp = requests.post(f"{BASE_URL}/listings/{listing_id}/blocked-dates",
                              json={"date": date_str, "reason": reason}, headers=self._headers())
        return self._handle(resp)

    # ---------- reservas y pagos ----------
    def create_booking(self, listing_id, check_in, check_out, guests, payment_method):
        resp = requests.post(f"{BASE_URL}/bookings", json={
            "listing_id": listing_id, "check_in": check_in, "check_out": check_out,
            "guests": guests, "payment_method": payment_method,
        }, headers=self._headers())
        return self._handle(resp)

    def my_bookings(self):
        resp = requests.get(f"{BASE_URL}/bookings/mine", headers=self._headers())
        return self._handle(resp)

    def host_bookings(self):
        resp = requests.get(f"{BASE_URL}/bookings/host", headers=self._headers())
        return self._handle(resp)

    # ---------- reseñas ----------
    def create_review(self, listing_id, rating, comment):
        resp = requests.post(f"{BASE_URL}/reviews", json={
            "listing_id": listing_id, "rating": rating, "comment": comment,
        }, headers=self._headers())
        return self._handle(resp)

    # ---------- geolocalización (API externa real) ----------
    def geocode(self, query):
        resp = requests.get(f"{BASE_URL}/geo/search", params={"q": query})
        return self._handle(resp)

    # ---------- administración ----------
    def admin_stats(self):
        resp = requests.get(f"{BASE_URL}/admin/stats", headers=self._headers())
        return self._handle(resp)

    def admin_users(self):
        resp = requests.get(f"{BASE_URL}/admin/users", headers=self._headers())
        return self._handle(resp)
