from flask import Flask,jsonify,request,redirect,render_template
import os
from src.database import db,MeasurePoint
from src.services.area import area
from src.services.assets import assets
from src.services.auth import auth
from src.services.measure_point import measure_point
from src.services.api_isee_service import isee,sync_mp
from src.services.dashboard import dashboard
from flask_jwt_extended import JWTManager
from src.constants.http_constants import HTTP_200_OK,HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask_jwt_extended import get_jwt_identity
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

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

   def job(app=app):
      with app.app_context():
         mp = MeasurePoint.query.filter_by(delete_at= None).order_by(MeasurePoint.asset_id).all()
         for item in mp:
            sync_mp(mp)

   scheduler = BackgroundScheduler()
   scheduler.add_job(func=job,trigger="interval",seconds=3600)
# scheduler.add_job(func=job_syncMp,trigger="interval", seconds=1800)
# scheduler.add_job(func=job_syncTreshshold,trigger="interval", seconds=1800)
   scheduler.start()

# # Shut down the scheduler when exiting the app
   atexit.register(lambda: scheduler.shutdown())

   @app.route('/')
   def index():
      return jsonify({
         "status": HTTP_200_OK,"message": "Welcome To TirtaVib API",
         "url": request.base_url
      })

   @app.route("/dashboard")
   def home():
      return render_template('dashboard_v1.html')

   @app.errorhandler(HTTP_404_NOT_FOUND)
   def handle_404(e):
      return jsonify({'error': 'Not Found'}), HTTP_404_NOT_FOUND

   @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
   def handle_500(e):
      return jsonify({
         'error': 'Something went wrong, we are working on it'
      }), HTTP_500_INTERNAL_SERVER_ERROR

   return app

