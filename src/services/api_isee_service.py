from flask import Blueprint,jsonify,request
import os
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from src.database import Asset,MeasurePoint,Thresholds,db
from src.constants.http_constants import HTTP_404_NOT_FOUND

isee = Blueprint("isee", __name__, url_prefix="/api-isee")

@isee.get("/")
def getAllData():
   responseLogin = loginAPP()
   return responseLogin


def loginAPP():
   username = os.environ.get("USER_CREDENTIAL")
   password = os.environ.get("PASS_CREFENTIAL")
   db = os.environ.get("DB_ASSET")

   url = requests.post("https://isee.icareweb.com/apiv4/login/",json={"username": username,"password": password})
   loginResponse = url.json()
   token_auth = loginResponse["token"]

   header = {'Authorization': 'Bearer {}'.format(token_auth)}
   db_access = requests.get(f"https://isee.icareweb.com/apiv4/login/{db}", headers=header)
   db_token = db_access.json()

   return db_token["token"]

@isee.get("/syncronize-threshold")
def sync(param1=None):
   area_id = request.args.get('area_id',type=int)
   if param1:
      area_id = param1
   MPS = db.session.execute(db.select(MeasurePoint.id_api, MeasurePoint.asset_id).order_by(MeasurePoint.asset_id)).all()
   if area_id:
      MPS = db.engine.execute('''
         SELECT mp.id_api , mp.asset_id  FROM measure_point mp 
         INNER JOIN asset a ON a.id = mp.asset_id 
         INNER JOIN area a2 ON a2.id = a.area_id 
         WHERE a2.id = %d
         ORDER BY mp.asset_id;
         '''%area_id).all()
   token = loginAPP()
   header = {'Authorization': 'Bearer {}'.format(token)}
   mps_results = []
   for item in MPS:
      threshold_api = requests.get(f"https://isee.icareweb.com/apiv4/assets/{item.id_api}/thresholds",headers=header)
      result_api = threshold_api.json()
      results = []
      for item_res in result_api["vibration"]:
         is_exist = Thresholds.query.filter_by(measure_point_id_api=item.id_api,title=item_res["threshold_type"]).first()
         levels = item_res["levels"]
         if is_exist:
            if levels:
               is_exist.max_alert = levels["maxalert"]
               is_exist.max_warn = levels["maxwarn"]
               db.session.commit()

            continue

         new_threshold = Thresholds(title=item_res["threshold_type"],measure_point_id_api=item.id_api)

         if levels:
            new_threshold.max_alert = levels["maxalert"]
            new_threshold.max_warn = levels["maxwarn"]

         db.session.add(new_threshold)
         db.session.commit()
         results.append(item_res)
      
      mps_results.append({
         'id': item.id_api,
         'thresholds': results
      })

   return jsonify({'data':mps_results})

@isee.get("/syncronize-mp")
def sync_mp(param1=None,param2=None):
   asset_id = request.args.get('asset_id','')
   area = request.args.get('is_area')
   if param1 and param2:
      asset_id = param1,
      area = param2
   MPS = db.session.execute(db.select(MeasurePoint.id_api, MeasurePoint.asset_id, MeasurePoint.accel, MeasurePoint.velocity,MeasurePoint.peak_peak, MeasurePoint.dna12, MeasurePoint.dna500, MeasurePoint.updated_api).order_by(MeasurePoint.asset_id)).all()
   
   if asset_id:
      MPS = MeasurePoint.query.filter_by(asset_id=asset_id, delete_at=None).order_by(MeasurePoint.asset_id).all()
   if asset_id and area:
      MPS = get_MP_byArea(asset_id)

   token = loginAPP()
   header = {'Authorization': 'Bearer {}'.format(token)}
   mps_results = []

   for item in MPS:
      mpItem = MeasurePoint.query.filter_by(id_api=item.id_api).first()
      mp_api = requests.get(f"https://isee.icareweb.com/apiv4/assets/{item.id_api}/results",headers=header)
      result_api = mp_api.json()
      if not result_api["_embedded"]:
         continue
      mp_api_update = result_api["_embedded"]
      mpItem.updated_api = result_api["_updated"]
      for result in mp_api_update:
         itemval = result["statistics"]
         res = {}
         for stat in itemval:
            if stat["global_type"] == "acceleration":
               res['accel'] = stat["value"]
            if stat["global_type"] == "velocity":
               res['velocity'] = stat["value"]
            if stat["global_type"] == "peak-peak":
               res['peak_peak'] = stat["value"]
            if stat["global_type"] == "dna12":
               res['dna12'] = stat["value"]
            if stat["global_type"] == "dna500":
               res['dna500'] = stat["value"]
         if 'dna12' in res or 'dna500' in res:
            mpItem.dna12 = res["dna12"]
            mpItem.dna500 = res["dna500"]
         else:
            mpItem.accel = res["accel"]
            mpItem.velocity = res["velocity"]
            mpItem.peak_peak = res["peak_peak"]
         db.session.commit()
         break
      mps_results.append({
         'id':item.id,
         'velocity':item.velocity,
         'accel':item.accel,
         'peak_peak':item.peak_peak
      })
   return jsonify({'data':mps_results})

def get_MP_byArea(area_id):
   assets = Asset.query.filter_by(area_id=area_id).all()
   MPS = []

   for item in assets:
      mps = MeasurePoint.query.filter_by(asset_id=item.id,delete_at= None).all()
      for mp in mps:
         MPS.append(mp)

   return MPS

def job_syncMp():
   area = db.session.execute(db.select(Asset.area_id).group_by(Asset.area_id).order_by(Asset.area_id)).all()
   for item in area:
      sync_mp(item.area_id,True)

def job_syncTreshshold():
   area = db.session.execute(db.select(Asset.area_id).group_by(Asset.area_id).order_by(Asset.area_id)).all()
   for item in area:
      sync(item.area_id)

# def job():
#    print("I'm working...")

scheduler = BackgroundScheduler()
scheduler.add_job(func=job_syncMp,trigger="interval", seconds=7200)
scheduler.add_job(func=job_syncTreshshold,trigger="interval", seconds=19800)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
