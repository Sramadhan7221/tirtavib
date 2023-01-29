from flask import Blueprint,jsonify,request
import os
from src.database import Area,Asset,MeasurePoint,Thresholds,db

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard.get("/")
def home():
   data = []
   id_area = request.args.get('area')
   area_mp = Asset.query.filter_by(area_id=1).all()
   if id_area:
      area_mp = Asset.query.filter_by(area_id=id_area).all()

   for mp in area_mp:
      item = {}
      item['asset_name'] = mp.name
      mp_data = []
      mp_query = db.engine.execute('''
         SELECT a.id, a.name ||' '|| mp.name as nama ,accel ,velocity ,peak_peak ,updated_api ,
         CASE 
            WHEN 
               (SELECT max_warn FROM thresholds t WHERE title = 'acceleration' and measure_point_id_api = mp.id_api) and (SELECT max_alert FROM thresholds t WHERE title = 'acceleration' and measure_point_id_api = mp.id_api) AND  
               (SELECT max_warn FROM thresholds t WHERE title = 'velocity' and measure_point_id_api = mp.id_api) and (SELECT max_alert FROM thresholds t WHERE title = 'velocity' and measure_point_id_api = mp.id_api) AND 
               (SELECT max_warn FROM thresholds t WHERE title = 'peak-peak' and measure_point_id_api = mp.id_api) and (SELECT max_alert FROM thresholds t WHERE title = 'peak-peak' and measure_point_id_api = mp.id_api)
            ISNULL 
            THEN 'normal'
            WHEN 
               mp.accel > (SELECT max_alert FROM thresholds t WHERE title = 'acceleration' and measure_point_id_api = mp.id_api) OR 
               mp.velocity  > (SELECT max_alert FROM thresholds t WHERE title = 'velocity' and measure_point_id_api = mp.id_api) OR 
               mp.peak_peak > (SELECT max_alert FROM thresholds t WHERE title = 'peak-peak' and measure_point_id_api = mp.id_api)
            THEN 'danger'
            WHEN 
               mp.accel = (SELECT max_alert FROM thresholds t WHERE title = 'acceleration' and measure_point_id_api = mp.id_api) OR 
               mp.velocity  = (SELECT max_alert FROM thresholds t WHERE title = 'velocity' and measure_point_id_api = mp.id_api) OR 
               mp.peak_peak = (SELECT max_alert FROM thresholds t WHERE title = 'peak-peak' and measure_point_id_api = mp.id_api) 
            THEN 'danger'
            WHEN 
               mp.accel > (SELECT max_warn FROM thresholds t WHERE title = 'acceleration' and measure_point_id_api = mp.id_api) OR 
               mp.velocity  > (SELECT max_warn FROM thresholds t WHERE title = 'velocity' and measure_point_id_api = mp.id_api) OR 
               mp.peak_peak > (SELECT max_warn FROM thresholds t WHERE title = 'peak-peak' and measure_point_id_api = mp.id_api) 
            THEN 'warning'
            WHEN 
               mp.accel = (SELECT max_warn FROM thresholds t WHERE title = 'acceleration' and measure_point_id_api = mp.id_api) OR 
               mp.velocity  = (SELECT max_warn FROM thresholds t WHERE title = 'velocity' and measure_point_id_api = mp.id_api) OR 
               mp.peak_peak = (SELECT max_warn FROM thresholds t WHERE title = 'peak-peak' and measure_point_id_api = mp.id_api) 
            THEN 'warning'
            ELSE 'normal'
         END
         as status
         from measure_point mp 
         join asset a ON a.id = mp.asset_id 
         WHERE mp.asset_id = '''+mp.id
      ).all()
      for item in mp_query:
         mp_data.append({
            'nama' : item.nama,
            'accel': item.accel,
            'velocity': item.velocity,
            'peak_peak': item.peak_peak,
            'status': item.status
         })
      item['measure_points'] = mp_data
      data.append(item)
   
   return jsonify({'data': data})



