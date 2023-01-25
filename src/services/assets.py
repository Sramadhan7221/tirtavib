from flask import Blueprint,request,jsonify
from src.database import Asset,Area,MeasurePoint,db
from datetime import datetime
from flask_jwt_extended import jwt_required
from src.constants.http_constants import HTTP_201_CREATED,HTTP_200_OK,HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,HTTP_409_CONFLICT

assets = Blueprint("assets",__name__,url_prefix="/assets")

@assets.route("/", methods=['POST','GET'])
@jwt_required(locations='headers')
def handle_assets():
   if request.method == 'POST':
      nama = request.get_json().get('nama','')
      area_id = request.get_json().get('area_id')

      if not area_id:
         return jsonify({
            'error': "area_id tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      if not nama :
         return jsonify({
            'error': "Nama Asset tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      selectedArea = Area.query.filter_by(id=area_id).first()
      if not selectedArea:
         return jsonify({
            'error': "area_id tidak terdaftar "
         }),HTTP_404_NOT_FOUND

      isExist = Asset.query.filter_by(name=nama,area_id=area_id).first()
      if isExist:
         if isExist.delete_at:
            isExist.delete_at = None
            isExist.area_id = area_id
            db.session.commit()
            return jsonify({
               'id':isExist.id,
               'nama':isExist.name,
               'area':selectedArea.name
            }),HTTP_201_CREATED
         else:
            return jsonify({
               'error': "Asset sudah terdaftar "
            }),HTTP_409_CONFLICT

      new_asset = Asset(name=nama,area_id=area_id)
      db.session.add(new_asset)
      db.session.commit()

      return jsonify({
         'id':new_asset.id,
         'nama':new_asset.name,
         'area':selectedArea.name
      }),HTTP_201_CREATED
   else:
      area_id = request.args.get('area_id',type=int)

      if not area_id :
         return jsonify({
            'error': "area_id tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      data = []

      selectedArea = Area.query.filter_by(id=area_id).first()
      if not selectedArea:
         return jsonify({
            'error': "area_id tidak terdaftar "
         }),HTTP_404_NOT_FOUND

      assets = Asset.query.filter_by(delete_at=None,area_id=area_id).order_by(Asset.name).all()
      for item in assets:
         data.append({
            'id': item.id,
            'nama': item.name,
            'area':selectedArea.name
         })

      return jsonify({'data':data}),HTTP_200_OK

@assets.get("/assets-mp")
def getListAsset():
   assets = db.session.execute(db.select(Asset.id, Asset.name, Asset.mps).order_by(Asset.area_id)).all()
   data = []
   for item in assets:
      Mps = MeasurePoint.query.filter_by(asset_id=item.id).order_by(MeasurePoint.id).all()
      list_mps = []
      for mp in Mps:
         list_mps.append(mp.id_api)

      data.append({
         'nama' : item["name"],
         'list_mps': list_mps
      })

   return jsonify({'data': data})

@assets.get("/detail/<int:asset_id>")
@jwt_required(locations='headers')
def detail_handler(asset_id):
   detail_asset = Asset.query.filter_by(id=asset_id).first()

   if not detail_asset:
      return jsonify({'error': 'Asset tidak ditemukan'}),HTTP_404_NOT_FOUND

   selectedArea = Area.query.filter_by(id=detail_asset.area_id).first()
   return jsonify({
      'id':detail_asset.id,
      'nama':detail_asset.name,
      'area':selectedArea.name
   }),HTTP_200_OK

@assets.patch("/edit/<int:asset_id>")
@jwt_required(locations='headers')
def edit_handler(asset_id):
   edit_asset = Asset.query.filter_by(id=asset_id).first()

   if not edit_asset:
      return jsonify({'error': 'Asset tidak ditemukan'}),HTTP_404_NOT_FOUND

   nama = request.get_json().get('nama','')
   area_id = request.get_json().get('area_id')

   if not area_id:
      return jsonify({
         'error': "area_id tidak boleh kosong "
      }),HTTP_400_BAD_REQUEST

   if not nama:
      return jsonify({
         'error': "Nama Area tidak boleh kosong "
      }),HTTP_400_BAD_REQUEST

   selectedArea = Area.query.filter_by(id=area_id).first()
   if not selectedArea:
      return jsonify({
         'error': "area_id tidak terdaftar "
      }),HTTP_404_NOT_FOUND

   edit_asset.name = nama
   edit_asset.area_id = area_id

   db.session.commit()
   return jsonify({
      'id':edit_asset.id,
      'nama':edit_asset.name,
      'area':selectedArea.name
   }),HTTP_200_OK

@assets.delete('/delete/<int:asset_id>')
@jwt_required(locations='headers')
def handle_delete(asset_id):
   deleted_asset = Asset.query.filter_by(id=asset_id).first()

   if not deleted_asset:
      return jsonify({'error': 'Asset tidak ditemukan'}),HTTP_404_NOT_FOUND

   deleted_asset.delete_at = datetime.now()
   db.session.commit()
   # db.session.delete(delete_area)
   # db.session.commit()

   return jsonify({
      'message':'Asset berhasil dihapus'
   }),HTTP_200_OK