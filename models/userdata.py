from models import db

class UserData(db.Model):
    __tablename__ = 'userdata'
    ip_address = db.Column(db.String(255), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    asn = db.Column(db.String(100), nullable=True)
    asn_description = db.Column(db.String(255), nullable=True)
    subnet_mask = db.Column(db.String(100), nullable=True)
    subnet = db.Column(db.String(100), nullable=True)
