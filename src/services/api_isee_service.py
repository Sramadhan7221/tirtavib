from flask import Blueprint,jsonify
import os
import requests
from src.database import MeasurePoint,Thresholds,db

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
def sync():
   MPS = db.session.execute(db.select(MeasurePoint.id_api, MeasurePoint.asset_id).order_by(MeasurePoint.asset_id)).all()
   token = loginAPP()
   header = {'Authorization': 'Bearer {}'.format(token)}
   mps_results = []
   for item in MPS:
      # threshold = Thresholds.query.filter_by(measure_point_id_api=item.id_api).first()
      # if not threshold:
      #    new_MP = Thresholds(title=)
      #    db.session.add(new_MP)
      #    db.session.commit()
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
