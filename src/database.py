from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4

db = SQLAlchemy()

class Area(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(100), nullable=False)
   assets = db.relationship('Asset', backref='area', lazy=True)
   
   def __init__(self,nama=None):
      super().__init__()
      self.name = nama

   def __ref__(self) -> str:
      return 'Area>>> {self.name}'

class Asset(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(150), nullable=False)
   AreaId = db.Column(db.Integer, db.ForeignKey('area.id'),  nullable=False)
   mps = db.relationship('MeasurePoint', backref='asset', lazy=True)

   def __init__(self,**kwargs):
      super().__init__()

   def __ref__(self) -> str:
      return 'Asset>>> {self.name}'

class MeasurePoint(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(150), nullable=False)
   AssetId = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
   tresholds = db.relationship('Tresholds', backref='measure_points', lazy=True)

   def __init__(self,**kwargs):
      super().__init__()

   def __ref__(self) -> str:
      return 'MP>>> {self.name}'

class Tresholds(db.Model):
   id = db.Column(db.String(36), primary_key=True)
   title = db.Column(db.String(150), nullable=False)
   name = db.Column(db.String(100), nullable=False)
   EmergencyMin = db.Column(db.Float, nullable=True, default=0)
   EmergencyMax = db.Column(db.Float, nullable=True,
   default=0)
   AlertMin = db.Column(db.Float, nullable=True,
   default=0)
   AlertMax = db.Column(db.Float, nullable=True,
   default=0)
   CreateAt = db.Column(db.DateTime(), default=datetime.now())
   LastUpdateAt = db.Column(db.DateTime(), onupdate=datetime.now())
   DeleteAt = db.Column(db.DateTime(), nullable=True)
   MeasurePointId = db.Column(db.String(36), db.ForeignKey('measure_point.id'), nullable=False)

   def __init__(self,**kwargs):
      super().__init__()

      self.id = uuid4()

   def __ref__(self) -> str:
      return 'Treshold>>> {self.id}'
