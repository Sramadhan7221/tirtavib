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

# @isee.get("/syncronize-threshold")
def sync(MPS):
   print("Fetch Teshold data begins...")
   # area_id = request.args.get('area_id', type=int)
   # MPS = db.session.execute(db.select(MeasurePoint.id_api, MeasurePoint.asset_id).order_by(MeasurePoint.asset_id)).all()
   # if area_id:
   #    MPS = db.engine.execute('''
   #       SELECT mp.id_api , mp.asset_id  FROM measure_point mp 
   #       INNER JOIN asset a ON a.id = mp.asset_id 
   #       INNER JOIN area a2 ON a2.id = a.area_id 
   #       WHERE a2.id = %d
   #       ORDER BY mp.asset_id;
   #       '''%area_id).all()
   token = loginAPP()
   header = {'Authorization': 'Bearer {}'.format(token)}
   for item in MPS:
      threshold_api = requests.get(f"https://isee.icareweb.com/apiv4/assets/{item.id_api}/thresholds",headers=header)
      result_api = threshold_api.json()
      result_fromAPI = result_api["dna"] if 'dna' in result_api else result_api["vibration"]
      results = []
      if 'temperature' in result_api:
         for item_res in result_api["temperature"]:
            for item_res in result_fromAPI:
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
         
      for item_res in result_fromAPI:
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
   print("Success Fetch tresholds data")
   return jsonify({'Success':True})

# @isee.get("/syncronize-mp")
def sync_mp(MPS):
   # asset_id = request.args.get('asset_id','')
   # area = request.args.get('is_area')
   # MPS = db.session.execute(db.select(MeasurePoint.id_api, MeasurePoint.asset_id, MeasurePoint.accel, MeasurePoint.velocity,MeasurePoint.peak_peak, MeasurePoint.dna12, MeasurePoint.dna500, MeasurePoint.temp, MeasurePoint.updated_api).order_by(MeasurePoint.asset_id)).all()
   
   # if asset_id:
   #    MPS = MeasurePoint.query.filter_by(asset_id=asset_id, delete_at=None).order_by(MeasurePoint.asset_id).all()
   # if asset_id and area:
   #    MPS = get_MP_byArea(asset_id)
   print("Fetch MP data begins...")

   token = loginAPP()
   header = {'Authorization': 'Bearer {}'.format(token)}

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
            if stat["global_type"] == "temperature":
               res['temp'] = stat["value"]
         if 'dna12' in res or 'dna500' in res:
            mpItem.dna12 = res["dna12"]
            mpItem.dna500 = res["dna500"]
         else:
            if 'temp' in res:
               mpItem.temp = res["temp"]
            mpItem.accel = res["accel"]
            mpItem.velocity = res["velocity"]
            mpItem.peak_peak = res["peak_peak"]
         db.session.commit()
         break
   print("Success Fetch MP data")
   return jsonify({'success':True})

def get_MP_byArea(area_id):
   assets = Asset.query.filter_by(area_id=area_id).all()
   MPS = []

   for item in assets:
      mps = MeasurePoint.query.filter_by(asset_id=item.id,delete_at= None).all()
      for mp in mps:
         MPS.append(mp)
   print("success")
   return MPS

async def job_syncMp():
   area = db.session.execute(db.select(Asset.area_id).group_by(Asset.area_id).order_by(Asset.area_id)).all()
   for item in area:
      await sync_mp(item.area_id,True)

async def job_syncTreshshold():
   area = db.session.execute(db.select(Asset.area_id).group_by(Asset.area_id).order_by(Asset.area_id)).all()
   for item in area:
      await sync(item.area_id)

# def job():
#    print("I'm working...")

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=job_syncMp,trigger="interval", seconds=1800)
# scheduler.add_job(func=job_syncTreshshold,trigger="interval", seconds=1800)
# scheduler.start()

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
