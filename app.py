from flask import Flask, render_template,redirect,url_for, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from geopy.geocoders import Nominatim
from sqlalchemy.orm import class_mapper
from dotenv import load_dotenv

import os

load_dotenv()

import csv

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = '/tmp'  # Temporary folder to store uploaded images


db = SQLAlchemy(app)

migrate = Migrate(app, db)

geolocator = Nominatim(user_agent=os.getenv("Nominatim_USER"))


# Define Userdata table
class Userdata(db.Model):
    __tablename__ = 'userdata'
    ip_address = db.Column(db.String(255), primary_key=True)  # Primary key
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    asn = db.Column(db.String(100), nullable=True)
    asn_description = db.Column(db.String(255), nullable=True)
    subnet_mask = db.Column(db.String(100), nullable=True)
    subnet = db.Column(db.String(100), nullable=True)
    

# Update ModelResult table
class ModelResult(db.Model):
    __tablename__ = 'model_results'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(255), db.ForeignKey('userdata.ip_address'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    model_name = db.Column(db.String(255), nullable=True)  # New column for the model name
    model_id = db.Column(db.Integer, nullable=True)
    latency_time = db.Column(db.Float, nullable=False)
    cpu_usage = db.Column(db.Float, nullable=True)  # Optionally track CPU usage
    accuracy = db.Column(db.Float, nullable=True)
    memory_usage = db.Column(db.Float, nullable=True)  # Optionally track memory usage
    response_time = db.Column(db.Float, nullable=True)  # New column for response time
    throughput = db.Column(db.Float, nullable=True)  # New column for throughput
    energy_required = db.Column(db.Float, nullable=True)  # New column for energy required
    power_watts = db.Column(db.Float, nullable=True)  # New column for power in watts

    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)



# NEW SERVICE
# class ServerData(db.Model):
#     __tablename__ = 'server_data'
#     public_ip = db.Column(db.String(255), primary_key=True)  # Primary key set as public IP
#     local_ip = db.Column(db.String(255), nullable=False)
#     latitude = db.Column(db.Float, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)
#     service_provider = db.Column(db.String(255), nullable=False)
#     city = db.Column(db.String(255), nullable=False)
#     region = db.Column(db.String(255), nullable=False)
#     country = db.Column(db.String(255), nullable=False)
#     geo_location_coordinates = db.Column(db.String(255), nullable=False)
#     asn = db.Column(db.String(255), nullable=False)
#     asn_description = db.Column(db.String(255), nullable=False)
#     subnet = db.Column(db.String(255), nullable=False)
#     subnet_mask = db.Column(db.String(255), nullable=False)
#     timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)


class ServerData(db.Model):
    server_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_address = db.Column(db.String(255), nullable=False)
    cpu_use = db.Column(db.String(55), nullable=True)
    gpu_use = db.Column(db.String(55), nullable=True)
    ram_use = db.Column(db.Integer, nullable=True)
    service_provider = db.Column(db.String(255), nullable=False)
    machine_type = db.Column(db.String(255), nullable=False)



# Initialize the database
with app.app_context():
    db.create_all()


def export_userdata_to_csv():
    try:
        # Query all records from the Userdata table
        results = Userdata.query.all()

        # Define the column headers for the CSV
        column_headers = [
            'IP Address', 'Latitude (°)', 'Longitude (°)', 
            'City', 'Region', 'Country', 'Subnet Mask', 
            'Subnet', 'ASN', 'ASN Description'
        ]

        # Create an in-memory CSV file (using Flask Response for sending as a file)
        def generate():
            # Create a CSV writer using StringIO to properly handle commas within data
            import io
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

            # Write the header row
            writer.writerow(column_headers)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

            # Iterate through the query results and write each row
            for result in results:
                row = [
                    result.ip_address or '',
                    str(result.latitude) or '',
                    str(result.longitude) or '',
                    result.city or '',
                    result.region or '',
                    result.country or '',
                    result.subnet_mask or '',
                    result.subnet or '',
                    result.asn or '',
                    result.asn_description or ''
                ]
                writer.writerow(row)
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

        # Return the CSV file as a downloadable response
        return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=userdata.csv"})
    except Exception as e:
        print(f"Error exporting data from Userdata table: {e}")
        return "Error exporting data"
    

def export_model_results_to_csv():
    # Query all records from the ModelResult table
    results = ModelResult.query.all()

    # Define the column headers for the CSV
    column_headers = [
        'id', 'ip_address', 'model_name', 
        'latency_time (sec)', 'cpu_usage (%)', 
        'memory_usage (%)', 'throughput (kbps)', 
        'energy_required (Joules)', 'power_watts (Watts)', 'response_time (sec)', 'timestamp'
    ]
    
    # Create an in-memory CSV file (using Flask Response for sending as a file)
    def generate():
        # Write the header row
        yield ','.join(column_headers) + '\n'

        # Iterate through the query results and write each row
        for result in results:
            yield ','.join([
                str(result.id),
                result.ip_address,
                result.model_name or '',  # Handle nullable fields
                str(result.latency_time),
                str(result.cpu_usage) if result.cpu_usage is not None else '',
                str(result.memory_usage) if result.memory_usage is not None else '',
                str(result.response_time) if result.response_time is not None else '',
                str(result.throughput) if result.throughput is not None else '',
                str(result.energy_required) if result.energy_required is not None else '',
                str(result.power_watts) if result.power_watts is not None else '',
                str(result.timestamp)
            ]) + '\n'

    # Return the CSV file as a downloadable response
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=model_results.csv"})


def model_to_dict(model):
    if not model:
        return None
    mapper = class_mapper(model.__class__)
    return {col.key: getattr(model, col.key) for col in mapper.columns}



@app.route('/')
def show_data():
    # Query the database
    data = Userdata.query.all()
    models = ModelResult.query.all()
    return render_template('show_data.html', data=data, models=models)


@app.route('/show_server')
def show_server():
    # Query the database
    data = ServerData.query.all()

    return render_template('show_server.html', data=data)


@app.route('/download_csv')
def download_csv():
    return export_model_results_to_csv()

@app.route('/download_userdata_csv')
def download_userdata_csv():
    return export_userdata_to_csv()


@app.route('/add_userdata', methods=['POST'])
def add_userdata():
    data = request.json
    ip_address = data.get('ip_address')

    # Skip if the IP is localhost or 127.0.0.1
    if ip_address in ['127.0.0.1', 'localhost']:
        return jsonify({'message': 'Skipping localhost IP'}), 200
    
    # Check if user data already exists
    ip_exists = Userdata.query.filter_by(ip_address=ip_address).first()
    if ip_exists:
        return jsonify({'message': 'Userdata already exists'}), 200

    # Add new user data only if latitude and longitude are not None
    if data.get('latitude') is not None and data.get('longitude') is not None:
        new_entry = Userdata(**data)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({'message': 'Userdata added successfully'}), 201
    else:
        return jsonify({'error': 'Latitude and Longitude cannot be NULL'}), 400



@app.route('/userdata', methods=['GET'])
def get_userdata():
    return jsonify([u.__dict__ for u in Userdata.query.all() if '_sa_instance_state' not in u.__dict__])


@app.route('/userdata/<ip_address>', methods=['PUT'])
def update_userdata(ip_address):
    data = request.json
    entry = Userdata.query.get(ip_address)
    if entry:
        for key, value in data.items():
            setattr(entry, key, value)
        db.session.commit()
        return jsonify({'message': 'Userdata updated'})
    return jsonify({'error': 'Userdata not found'}), 404


@app.route('/userdata/<ip_address>', methods=['DELETE'])
def delete_userdata(ip_address):
    entry = Userdata.query.get(ip_address)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Userdata deleted'})
    return jsonify({'error': 'Userdata not found'}), 404


# CRUD Routes for ModelResult
@app.route('/modelresult', methods=['POST'])
def add_modelresult():
    data = request.json
    new_entry = ModelResult(**data)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'ModelResult added successfully'}), 201



@app.route('/modelresult', methods=['GET'])
def get_modelresult():
    return jsonify([m.__dict__ for m in ModelResult.query.all() if '_sa_instance_state' not in m.__dict__])


@app.route('/modelresult/<int:id>', methods=['DELETE'])
def delete_modelresult(id):
    entry = ModelResult.query.get(id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'ModelResult deleted'})
    return jsonify({'error': 'ModelResult not found'}), 404


# Route to handle form submission
@app.route('/add-server-data', methods=['GET','POST'])
def add_server_data():
    if request.method == 'POST':
        new_data = ServerData(
            ip_address=request.form['ip_address'],
            cpu_use=request.form.get('cpu_use'),
            gpu_use=request.form.get('gpu_use'),
            ram_use=request.form.get('ram_use') or None,
            service_provider=request.form['service_provider'],
            machine_type=request.form['machine_type']
        )
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('show_server'))
    
    return render_template('add_server_data.html')


@app.route('/serverdata/<int:server_id>', methods=['DELETE'])
def delete_serverdata(server_id):
    entry = ServerData.query.get(server_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'ServerData deleted'})
    return jsonify({'error': 'ServerData not found'}), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT"), debug=True)