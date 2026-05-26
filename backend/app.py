from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from extensions import db

# The frontend lives one directory above the backend folder
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
    db_path = os.path.join(app.instance_path, 'dopayments.db')
    os.makedirs(app.instance_path, exist_ok=True)
    app.config['SECRET_KEY'] = 'dopayments-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    from routes.retailer import retailer_bp
    from routes.distributor import distributor_bp
    from routes.money_split import money_split_bp
    from routes.credit import credit_bp
    from routes.forecast import forecast_bp
    from routes.salesperson import salesperson_bp
    from routes.dashboard import dashboard_bp
    from routes.auth import auth_bp
    from routes.communication import communication_bp
    from routes.core_cashflow import core_cashflow_bp
    from routes.state_sync import state_sync_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(retailer_bp, url_prefix='/api')
    app.register_blueprint(distributor_bp, url_prefix='/api')
    app.register_blueprint(money_split_bp, url_prefix='/api')
    app.register_blueprint(credit_bp, url_prefix='/api')
    app.register_blueprint(forecast_bp, url_prefix='/api')
    app.register_blueprint(salesperson_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(communication_bp, url_prefix='/api')
    app.register_blueprint(core_cashflow_bp, url_prefix='/api')
    app.register_blueprint(state_sync_bp, url_prefix='/api')

    # --- Serve frontend HTML pages ---
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/dashboard.html')
    def serve_dashboard():
        return send_from_directory(FRONTEND_DIR, 'dashboard.html')

    with app.app_context():
        db.create_all()
        from seed import ensure_default_admin, ensure_default_cashflow_setup
        ensure_default_admin()
        ensure_default_cashflow_setup()
        if os.getenv('DOPAYMENTS_SEED_SAMPLE_DATA') == '1':
            from seed import seed_database
            seed_database()

    return app

# Gunicorn entry point
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
