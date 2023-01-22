from flask import Blueprint,jsonify
import os
import requests

isee = Blueprint("isee", __name__, url_prefix="/api-isee")

@isee.get("/")
def getAllData():
   responseLogin = loginAPP()
   token = responseLogin.token
   
   return responseLogin


def loginAPP():
   username = os.environ.get("USER_CREDENTIAL")
   password = os.environ.get("PASS_CREFENTIAL")

   url = requests.post("https://isee.icareweb.com/apiv4/login/",json={"username": username,"password": password})

   return url.json()
