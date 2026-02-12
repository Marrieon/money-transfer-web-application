from flask import Flask, jsonify
from flasgger import Swagger

# --- App Config & Extensions ---
from .config import config_by_name
from .extensions import db, migrate, jwt, cors, cache, limiter
from .utils.exceptions import APIException

# --- Blueprint Imports (All Phases) ---
from .api.auth.routes import auth_bp
from .api.users.routes import users_bp
from .api.wallets.routes import wallets_bp
from .api.transactions.routes import transactions_bp
from .api.admin.routes import admin_bp
from .api.savings.routes import savings_bp
from .api.analytics.routes import analytics_bp
from .api.beneficiaries.routes import beneficiaries_bp
from .api.notifications.routes import notifications_bp
from .api.circles.routes import circles_bp
from .api.loans.routes import loans_bp
from .api.insurance.routes import insurance_bp
from .api.merchants.routes import merchants_bp


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)
    limiter.init_app(app)

    # --- Swagger / API Docs Config (MODIFIED) ---
    app.config['SWAGGER'] = {
        'title': 'Money Transfer App API',
        'uiversion': 3,
        "specs_route": "/api/docs/",
        # NEW: This template defines the "Authorize" button for JWT
        "template": {
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"bearerAuth": []}]
        }
    }
    Swagger(app)

    # --- Apply Rate Limits ---
    limiter.limit("10 per minute")(auth_bp)

    # --- Register Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(wallets_bp, url_prefix='/api/wallets')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(savings_bp, url_prefix='/api/savings')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(beneficiaries_bp, url_prefix='/api/beneficiaries')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(circles_bp, url_prefix='/api/circles')
    app.register_blueprint(loans_bp, url_prefix='/api/loans')
    app.register_blueprint(insurance_bp, url_prefix='/api/insurance')
    app.register_blueprint(merchants_bp, url_prefix='/api/merchants')

    # --- Global APIException Handler ---
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # --- Basic Index Health Check ---
    @app.route('/')
    def index():
        return "Backend is running!"

    return app