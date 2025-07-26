from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from app.Api.controllers import ApiResource ,UserResource, AuthResource
from dotenv import load_dotenv
# loading all environment variables
load_dotenv()

jwt = JWTManager()

allowed_hosts=["http://localhost:4200/*","http://localhost:4200"]
origin = "http://localhost:4200/*"
ALLOWED_ORIGINS = ["http://localhost:4200"]

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    jwt.init_app(app)

    with app.app_context():

        CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
        ApiResource.register(app)
        AuthResource.register(app)
        UserResource.register(app)

    return app