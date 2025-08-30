from flask import Flask
from routes.responder import responder_bp
from routes.upload_route import upload_bp
from routes.upload_many_route import upload_many_bp
from routes.analyze_files_route import analyze_files_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(responder_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(upload_many_bp)
    app.register_blueprint(analyze_files_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
