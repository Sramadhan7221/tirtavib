from flask import Blueprint,request,jsonify
from src.database import MeasurePoint,Asset,db
from datetime import datetime
from flask_jwt_extended import jwt_required
from src.constants.http_constants import HTTP_201_CREATED,HTTP_200_OK,HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,HTTP_409_CONFLICT

measure_point = Blueprint("measure_point",__name__,url_prefix="/measures-point")

@measure_point.route("/", methods=['POST','GET'])
@jwt_required(locations='headers')
def handle_assets():
   if request.method == 'POST':
      nama = request.get_json().get('nama','')
      asset_id = request.get_json().get('asset_id')
      accel = request.get_json().get('accel')
      velocity = request.get_json().get('velocity')
      api_id = request.get_json().get('id_api')

      if not asset_id:
         return jsonify({
            'error': "asset_id tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      if not nama :
         return jsonify({
            'error': "Nama Asset tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      if not accel :
         return jsonify({
            'error': "Measure Point Accel tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      if not velocity :
         return jsonify({
            'error': "Measure Point Velocity tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      if not api_id :
         return jsonify({
            'error': "Measure Point Api Asset ID tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST
      
      selectedAsset = Asset.query.filter_by(id=asset_id).first()
      if not selectedAsset:
         return jsonify({
            'error': "asset_id tidak terdaftar "
         }),HTTP_404_NOT_FOUND

      isExist = MeasurePoint.query.filter_by(name=nama,asset_id=asset_id).first()
      if isExist:
         if isExist.delete_at:
            isExist.delete_at = None
            isExist.area_id = asset_id
            db.session.commit()
            return jsonify({
               'id':isExist.id,
               'nama':isExist.name,
               'asset':selectedAsset.name,
               'api_id': isExist.id_api,
               'accel':isExist.accel,
               'velocity':isExist.velocity
            }),HTTP_201_CREATED
         else:
            return jsonify({
               'error': "Measures Point sudah terdaftar "
            }),HTTP_409_CONFLICT

      new_MP = MeasurePoint(name=nama,asset_id=asset_id,accel=accel,velocity=velocity,id_api=api_id)
      db.session.add(new_MP)
      db.session.commit()

      return jsonify({
         'id':new_MP.id,
         'nama':new_MP.name,
         'area':selectedAsset.name,
         'accel':new_MP.accel,
         'velocity':new_MP.velocity,
         'api_id':new_MP.id_api
      }),HTTP_201_CREATED
   else:
      asset_id = request.args.get('asset_id',type=int)

      if not asset_id :
         return jsonify({
            'error': "asset_id tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      data = []

      selectedAsset = Asset.query.filter_by(id=asset_id).first()
      if not selectedAsset:
         return jsonify({
            'error': "asset_id tidak terdaftar "
         }),HTTP_404_NOT_FOUND

      MP_data = MeasurePoint.query.filter_by(delete_at=None,asset_id=asset_id).order_by(MeasurePoint.name).all()
      for item in MP_data:
         data.append({
            'id': item.id,
            'nama': item.name,
            'area': selectedAsset.name,
            'accel': item.accel,
            'velocity': item.velocity,
            'api_id': item.id_api
         })

      return jsonify({'data':data}),HTTP_200_OK

@measure_point.get("/detail/<int:measure_id>")
@jwt_required(locations='headers')
def detail_handler(measure_id):
   detail_MP = MeasurePoint.query.filter_by(id=measure_id).first()

   if not detail_MP:
      return jsonify({'error': 'Measures Point tidak ditemukan'}),HTTP_404_NOT_FOUND

   selectedAsset = Asset.query.filter_by(id=detail_MP.area_id).first()
   return jsonify({
      'id':detail_MP.id,
      'nama':detail_MP.name,
      'area':selectedAsset.name,
      'accel':detail_MP.accel,
      'velocity':detail_MP.velocity,
      'api_id':detail_MP.id_api
   }),HTTP_200_OK

@measure_point.patch("/edit/<int:measure_id>")
@jwt_required(locations='headers')
def edit_handler(measure_id):
   edit_MP = MeasurePoint.query.filter_by(id=measure_id).first()

   if not edit_MP:
      return jsonify({'error': 'Measures Point tidak ditemukan'}),HTTP_404_NOT_FOUND

   nama = request.get_json().get('nama','')
   asset_id = request.get_json().get('asset_id')
   accel = request.get_json().get('accel')
   velocity = request.get_json().get('velocity')

   if not asset_id:
      return jsonify({
         'error': "asset_id tidak boleh kosong "
      }),HTTP_400_BAD_REQUEST

   if not nama:
      return jsonify({
         'error': "Nama Area tidak boleh kosong "
      }),HTTP_400_BAD_REQUEST

   selectedAsset = Asset.query.filter_by(id=asset_id).first()
   if not selectedAsset:
      return jsonify({
         'error': "asset_id tidak terdaftar "
      }),HTTP_404_NOT_FOUND

   edit_MP.name = nama
   edit_MP.asset_id = asset_id
   edit_MP.accel = edit_MP.accel if not accel else accel
   edit_MP.velocity = edit_MP.velocity if not velocity else velocity

   db.session.commit()
   return jsonify({
      'id':edit_MP.id,
      'nama':edit_MP.name,
      'area':selectedAsset.name,
      'accel':edit_MP.accel,
      'velocity':edit_MP.velocity
   }),HTTP_200_OK

@measure_point.delete('/delete/<int:measure_id>')
@jwt_required(locations='headers')
def handle_delete(measure_id):
   deleted_MP = MeasurePoint.query.filter_by(id=measure_id).first()

   if not deleted_MP:
      return jsonify({'error': 'Measures Point tidak ditemukan'}),HTTP_404_NOT_FOUND

   deleted_MP.delete_at = datetime.now()
   db.session.commit()
   # db.session.delete(delete_area)
   # db.session.commit()

   return jsonify({
      'message':'Measures Point berhasil dihapus'
   }),HTTP_200_OK