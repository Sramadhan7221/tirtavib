from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4

db = SQLAlchemy()

class Users(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   email = db.Column(db.String(250), nullable=False)
   password = db.Column(db.String(128), nullable=False)
   nama = db.Column(db.String(250), nullable=False)
   no_telp = db.Column(db.String(14), nullable=True)
   
   def __init__(self,**kwargs):
      super().__init__(**kwargs)

   def __ref__(self) -> str:
      return 'Area>>> {self.name}'

class Area(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(100), nullable=False)
   create_at = db.Column(db.DateTime(), default=datetime.now())
   last_update_at = db.Column(db.DateTime(), onupdate=datetime.now())
   delete_at = db.Column(db.DateTime(), nullable=True)
   assets = db.relationship('Asset', backref='area', lazy=True)
   
   def __init__(self,**kwargs):
      super().__init__(**kwargs)

   def __ref__(self) -> str:
      return 'Area>>> {self.name}'

class Asset(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(150), nullable=False)
   create_at = db.Column(db.DateTime(), default=datetime.now())
   last_update_at = db.Column(db.DateTime(), onupdate=datetime.now())
   delete_at = db.Column(db.DateTime(), nullable=True)
   area_id = db.Column(db.Integer, db.ForeignKey('area.id'),  nullable=False)
   mps = db.relationship('MeasurePoint', backref='asset', lazy=True)

   def __init__(self,**kwargs):
      super().__init__(**kwargs)

   def __ref__(self) -> str:
      return 'Asset>>> {self.name}'

class MeasurePoint(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   id_api = db.Column(db.String(30), nullable=False, unique=True)
   name = db.Column(db.String(150), nullable=False)
   accel = db.Column(db.Float, nullable=False)
   velocity = db.Column(db.Float, nullable=False)
   create_at = db.Column(db.DateTime(), default=datetime.now())
   last_update_at = db.Column(db.DateTime(), onupdate=datetime.now())
   delete_at = db.Column(db.DateTime(), nullable=True)
   asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
   tresholds = db.relationship('Tresholds', backref='measure_points', lazy=True)

   def __init__(self,**kwargs):
      super().__init__(**kwargs)

   def __ref__(self) -> str:
      return 'MP>>> {self.name}'

class Tresholds(db.Model):
   id = db.Column(db.String(36), primary_key=True)
   title = db.Column(db.String(150), nullable=False)
   name = db.Column(db.String(100), nullable=False)
   emergency_min = db.Column(db.Float, nullable=True, default=0)
   emergency_max = db.Column(db.Float, nullable=True,
   default=0)
   alert_min = db.Column(db.Float, nullable=True,
   default=0)
   alert_max = db.Column(db.Float, nullable=True,
   default=0)
   create_at = db.Column(db.DateTime(), default=datetime.now())
   last_update_at = db.Column(db.DateTime(), onupdate=datetime.now())
   delete_at = db.Column(db.DateTime(), nullable=True)
   measure_point_id = db.Column(db.String(36), db.ForeignKey('measure_point.id'), nullable=False)

   def __init__(self,**kwargs):
      super().__init__(**kwargs)

      self.id = uuid4()

   def __ref__(self) -> str:
      return 'Treshold>>> {self.id}'
