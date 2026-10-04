# StayDragon — Proyecto Integrador (Uniremington)

App móvil de ecoturismo tipo marketplace (alojamientos rurales, actividades y negocios locales). Fase 2: desarrollo, pruebas y presentación.

Stack 100% Python, consistente con la arquitectura definida en la Fase 1:

| Capa | Tecnología |
|---|---|
| App móvil | **Flet 0.28.3** (Python → Android / iOS / web / escritorio) |
| Backend / API REST | **Flask 3.1** |
| Autenticación | **JWT** (Flask-JWT-Extended) |
| Base de datos | **SQLite** en desarrollo (SQLAlchemy); misma base de código soporta **PostgreSQL** en producción solo cambiando `DATABASE_URL` |
| Geolocalización | API externa real: **OpenStreetMap Nominatim** (sin API key) |
| Pagos | Pasarela **simulada** (aprueba y genera un `transaction_id`, igual que haría una integración real con PSE/Wompi) |

## Estructura del proyecto

```
staydragon/
├── backend/                 # API REST Flask
│   ├── app.py                # app factory + registro de blueprints
│   ├── config.py             # configuración (BD, JWT, Nominatim)
│   ├── extensions.py         # instancias de SQLAlchemy y JWTManager
│   ├── models.py              # User, Listing, BlockedDate, Booking, Payment, Review
│   ├── seed.py                # datos de ejemplo (3 usuarios, 2 publicaciones, 1 reserva)
│   ├── routes/                # un blueprint por módulo de negocio
│   │   ├── auth_routes.py        # registro / login
│   │   ├── listing_routes.py     # búsqueda, detalle, publicar, disponibilidad
│   │   ├── booking_routes.py     # reservas + pago simulado
│   │   ├── geo_routes.py         # geolocalización (Nominatim)
│   │   ├── review_routes.py      # calificaciones y reseñas
│   │   └── admin_routes.py       # panel administrativo
│   ├── tests/test_api.py      # 17 pruebas automatizadas (pytest)
│   └── requirements.txt
├── mobile_app/               # App Flet
│   ├── main.py                 # punto de entrada + enrutador de pantallas
│   ├── api_client.py           # cliente HTTP hacia el backend
│   ├── components.py           # barra superior, tarjetas, botones reutilizables
│   ├── views/                  # una pantalla por archivo (login, home, detalle, pago, paneles...)
│   ├── smoke_test.py           # prueba estructural de las 8 pantallas (sin red, sin GUI)
│   └── requirements.txt
├── evidencia_pruebas/          # salidas de pytest, smoke test y curl end-to-end
└── README.md
```

## Cómo ejecutar (en tu máquina, para grabar el video)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # crea staydragon.db con datos de ejemplo
python app.py                   # levanta la API en http://127.0.0.1:5000
```

Usuarios de prueba creados por `seed.py`:

| Rol | Correo | Contraseña |
|---|---|---|
| Turista | juan@staydragon.co | turista123 |
| Anfitrión | maria@staydragon.co | anfitrion123 |
| Administrador | admin@staydragon.co | admin123 |

Pruebas automatizadas del backend:

```bash
pytest -v
```

### 2. App móvil (en otra terminal, con el backend corriendo)

```bash
cd mobile_app
pip install -r requirements.txt
python smoke_test.py            # verifica que las 8 pantallas se construyen sin error
python main.py                  # abre la ventana de la app (Flet)
```

> `main.py` abre una ventana de escritorio nativa (vista `flet_app`, la que corre por defecto). Para verla como app web en el navegador, cambia en `main.py`: `ft.app(target=main, view=ft.AppView.WEB_BROWSER)`.

## Mapeo con la Fase 1

Cada módulo del backend corresponde a un bloque del diagrama de arquitectura entregado en la Fase 1:

- `auth_routes.py` → módulo **Usuarios y Roles**
- `listing_routes.py` → módulo **Publicaciones**
- `booking_routes.py` → módulos **Reservas** y **Pagos**
- `geo_routes.py` → módulo **Geolocalización** (API externa real)
- `review_routes.py` → módulo **Calificaciones**
- `admin_routes.py` → módulo **Administración**

Las pantallas de `mobile_app/views/` corresponden a los wireframes de la Fase 1 (login, búsqueda, detalle, pago, panel del anfitrión), con el panel administrativo agregado en esta fase.

## Alcance de esta fase y trabajo futuro

Implementado: RF-01 a RF-08, RF-09, RF-10 y RF-13 (ver Fase 1). Quedan fuera del alcance de esta entrega — y se documentan como trabajo futuro en el informe final — la mensajería interna (RF-11), las notificaciones push (RF-12) y el directorio de negocios locales (RF-14), por tiempo disponible para esta fase.
