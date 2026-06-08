from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from extensions import db

def create_app():
    app = Flask(__name__)
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

    with app.app_context():
        db.create_all()
        from seed import ensure_default_admin, ensure_default_cashflow_setup
        ensure_default_admin()
        ensure_default_cashflow_setup()
        if os.getenv('DOPAYMENTS_SEED_SAMPLE_DATA') == '1':
            from seed import seed_database
            seed_database()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
