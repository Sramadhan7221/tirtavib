from flask import Blueprint,request,jsonify
from src.database import Area,db
from datetime import datetime
from src.constants.http_constants import HTTP_201_CREATED,HTTP_200_OK,HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,HTTP_409_CONFLICT

area = Blueprint("area",__name__, url_prefix="/areas")

@area.route("/", methods=['POST','GET'])
def handle_areas():
   if request.method == 'POST':
      nama = request.get_json().get('nama','')

      if not nama :
         return jsonify({
            'error': "Nama Area tidak boleh kosong "
         }),HTTP_400_BAD_REQUEST

      isExist = Area.query.filter_by(name=nama).first()

      if isExist:
         if isExist.delete_at:
            isExist.delete_at = None
            db.session.commit()
            return jsonify({
               'id':isExist.id,
               'nama':isExist.name
            }),HTTP_201_CREATED
         else:
            return jsonify({
               'error': "Area sudah terdaftar "
            }),HTTP_409_CONFLICT

      new_area = Area(name=nama)
      db.session.add(new_area)
      db.session.commit()

      return jsonify({
         'id':new_area.id,
         'nama':new_area.name
      }),HTTP_201_CREATED
   else:
      area_id = request.args.get('id',type=int)
      areas = Area.query.filter_by(delete_at=None).order_by(Area.name).all()

      if area_id :
         areas = Area.query.filter_by(id=area_id).first()

      data = []

      for item in areas:
         data.append({
            'id': item.id,
            'nama': item.name
         })

      return jsonify({'data':data}),HTTP_200_OK

@area.patch("/edit/<int:area_id>")
def edit_handler(area_id):
   edit_area = Area.query.filter_by(id=area_id).first()

   if not edit_area:
      return jsonify({'error': 'Area tidak ditemukan'}),HTTP_404_NOT_FOUND

   nama = request.get_json().get('nama','')

   if not nama:
      return jsonify({
         'error': "Nama Area tidak boleh kosong "
      }),HTTP_400_BAD_REQUEST

   edit_area.name = nama

   db.session.commit()
   return jsonify({
      'id':edit_area.id,
      'nama':edit_area.name
   }),HTTP_200_OK

@area.delete('/delete/<int:area_id>')
def handle_delete(area_id):
   delete_area = Area.query.filter_by(id=area_id).first()

   if not delete_area:
      return jsonify({'error': 'Area tidak ditemukan'}),HTTP_404_NOT_FOUND

   delete_area.delete_at = datetime.now()
   db.session.commit()
   # db.session.delete(delete_area)
   # db.session.commit()

   return jsonify({
      'message':'Area berhasil dihapus'
   }),HTTP_200_OK