from flask import Flask,jsonify
import os
from src.database import db
from src.services.area import area
from src.services.assets import assets
from src.services.auth import auth
from src.services.measure_point import measure_point
from flask_jwt_extended import JWTManager
from src.constants.http_constants import HTTP_200_OK,HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

def create_app(test_conifg=None):
   app = Flask(__name__, instance_relative_config=True,template_folder='templates')

   if test_conifg is None:
      app.config.from_mapping(
         SECRET_KEY = os.environ.get("SECRET_KEY"),
         SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DB_URI"),SQLALCHEMY_TRACK_MODIFICATIONS = False,
      )
   else:
      app.config.from_mapping(test_conifg)

   db.app=app
   db.init_app(app)
   JWTManager(app)

   app.register_blueprint(auth)
   app.register_blueprint(area)
   app.register_blueprint(assets)
   app.register_blueprint(measure_point)

   @app.route('/')
   def index():
      return jsonify({"status": HTTP_200_OK,"message": "Welcome To TirtaVib API"})

   @app.errorhandler(HTTP_404_NOT_FOUND)
   def handle_404(e):
      return jsonify({'error': 'Not Found'}), HTTP_404_NOT_FOUND

   @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
   def handle_500(e):
      return jsonify({
         'error': 'Something went wrong, we are working on it'
      }), HTTP_500_INTERNAL_SERVER_ERROR

   return app