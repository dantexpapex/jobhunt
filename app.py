import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "jobs.db")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from routes import api, web

    app.register_blueprint(api.bp)
    app.register_blueprint(web.bp)

    return app


if __name__ == "__main__":
    app = create_app()

    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    with app.app_context():
        db.create_all()

    print("\n" + "=" * 50)
    print("JobHunt AI starting...")
    print("=" * 50)
    print("Open: http://localhost:5000")
    print("\nAvailable pages:")
    print("  /             - Dashboard")
    print("  /jobs         - Job listings")
    print("  /applications - Application queue")
    print("  /interview    - Interview prep")
    print("  /settings    - Settings")
    print("\nAPI endpoints:")
    print("  /api/health    - Health check")
    print("  /api/jobs     - Get jobs")
    print("  /api/search   - Search jobs")
    print("  /api/apply/*  - Application endpoints")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
