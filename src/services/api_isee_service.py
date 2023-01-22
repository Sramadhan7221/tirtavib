from flask import Blueprint,jsonify
import os
import requests

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
