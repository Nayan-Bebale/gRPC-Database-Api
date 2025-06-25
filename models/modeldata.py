from models import db


class ModelData(db.Model):
    __tablename__ = 'model_data'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(255), db.ForeignKey('userdata.ip_address'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    model_name = db.Column(db.String(255), nullable=True)  # New column for the model name
    server_id = db.Column(db.Integer, nullable=False)
    latency_time = db.Column(db.Float, nullable=False)
    cpu_usage = db.Column(db.Float, nullable=True)  # Optionally track CPU usage
    accuracy = db.Column(db.Float, nullable=True)
    memory_usage = db.Column(db.Float, nullable=True)  # Optionally track memory usage
    response_time = db.Column(db.Float, nullable=True)  # New column for response time
    throughput = db.Column(db.Float, nullable=True)  # New column for throughput
    energy_required = db.Column(db.Float, nullable=True)  # New column for energy required
    power_watts = db.Column(db.Float, nullable=True)  # New column for power in watts
    message = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, nullable=False) 
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
