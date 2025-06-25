from models import db


class ServerData(db.Model):
    server_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_address = db.Column(db.String(255), nullable=False)
    cpu_use = db.Column(db.String(55), nullable=True)
    gpu_use = db.Column(db.String(55), nullable=True)
    ram_use = db.Column(db.Integer, nullable=True)
    service_provider = db.Column(db.String(255), nullable=False)
    machine_type = db.Column(db.String(255), nullable=False)


