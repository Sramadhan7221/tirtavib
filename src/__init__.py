from flask import Flask,jsonify,request,redirect,render_template
import os
from src.database import db
from src.services.area import area
from src.services.assets import assets
from src.services.auth import auth
from src.services.measure_point import measure_point
from src.services.api_isee_service import isee
from src.services.dashboard import dashboard
from flask_jwt_extended import JWTManager
from src.constants.http_constants import HTTP_200_OK,HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask_jwt_extended import get_jwt_identity

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
   app.register_blueprint(isee)
   app.register_blueprint(dashboard)

   @app.route('/')
   def index():
      user_id = get_jwt_identity()
      if not user_id:
         return redirect(f"{request.base_url}/login")

      return jsonify({
         "status": HTTP_200_OK,"message": "Welcome To TirtaVib API",
         "url": request.base_url
      })

   @app.route("/login")
   def home():
      return render_template('index.html')
      
   @app.errorhandler(HTTP_404_NOT_FOUND)
   def handle_404(e):
      return jsonify({'error': 'Not Found'}), HTTP_404_NOT_FOUND

   @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
   def handle_500(e):
      return jsonify({
         'error': 'Something went wrong, we are working on it'
      }), HTTP_500_INTERNAL_SERVER_ERROR

   return app