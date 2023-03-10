from flask import Blueprint,request,jsonify
from werkzeug.security import check_password_hash,generate_password_hash
from src.constants.http_constants import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK
import validators
from src.database import Users,db
from flask_jwt_extended import jwt_required, create_access_token,create_refresh_token,get_jwt_identity
# from flasgger import swag_from

auth = Blueprint("auth",__name__, url_prefix="/auth")

@auth.post('/register')
# @jwt_required('header')
def register():
   # user_id = get_jwt_identity()
   # user = Users.query.filter_by(id=user_id).first()
   
   # if (user.role != "superadmin" or user.role != "Superadmin"):
   #    return jsonify({'error': "Role tidak memiliki akses terhadap menu ini"}),HTTP_401_UNAUTHORIZED

   nama = request.json['nama']
   email = request.json['email']
   password = request.json['password']
   role = request.json['role']

   if len(password)<6:
      return jsonify({'error': "Password Terlalu pendek"}), HTTP_400_BAD_REQUEST

   if len(nama)<3:
      return jsonify({'error': "Nama Terlalu pendek"}), HTTP_400_BAD_REQUEST

   if not nama.isalpha() :
      return jsonify({'error': "Nama tidak valid , nama tidak boleh terdapat karakter selain huruf"}), HTTP_400_BAD_REQUEST

   if not validators.email(email):
      return jsonify({'error': "Email Tidak valid"}), HTTP_400_BAD_REQUEST

   if Users.query.filter_by(email=email).first() is not None:
      return jsonify({'error': "Email sudah terdaftar"}), HTTP_409_CONFLICT

   pwd_hash = generate_password_hash(password)
   user = Users(nama=nama,password=pwd_hash,email=email,role=role)
   
   db.session.add(user)
   db.session.commit()

   return jsonify({
      'message': "User created",
      'user':{
         'nama': nama, 'email': email
      }
   }), HTTP_201_CREATED

@auth.post('/login')
# @swag_from('./docs/auth/login.yaml')
def login():
   email = request.json.get('email','')
   password = request.json.get('password','')

   user = Users.query.filter_by(email=email).first()

   if user:
      is_pass_correct = check_password_hash(user.password,password)

      if is_pass_correct:
         refresh = create_refresh_token(identity=user.id)
         access = create_access_token(identity=user.id)

         return jsonify({
            'user':{
               'refresh': refresh,
               'access': access,
               'email':user.email,
               'base_url': request.base_url
            }
         })

   return jsonify({'error': "Wrong credentials"}), HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required('header')
def me():
   user_id = get_jwt_identity()

   user = Users.query.filter_by(id=user_id).first()

   return jsonify({
      'username': user.username,
      'email': user.email
   }), HTTP_200_OK

@auth.post("/token/refresh")
@jwt_required('header',refresh=True)
def refresh_user_token():
   identity = get_jwt_identity()
   access = create_access_token(identity=identity)

   return jsonify({
      'access': access
   }), HTTP_200_OK