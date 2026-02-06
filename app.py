from flask import Flask, request, jsonify
from models import db, EscalationApproval
from config import SQLALCHEMY_DATABASE_URL
# Import service functions and the custom error
from services import (
    create_escalation, 
    get_all_escalations, 
    get_escalation_by_id, 
    update_escalation, 
    delete_escalation,
    EscalationServiceError
)

# Hardcoded PostgreSQL connection string
# NOTE: Replace 'abcd' with the actual user and add the password if required in a real-world scenario.
# Example with password: "postgresql+psycopg2://user:password@host:port/database"

# Remove this connection string if config.py is working fine.


app = Flask(__name__)
# Flask-SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended to set to False

# Initialize the database object with the app
db.init_app(app)

# --- Database Initialization (Run once) ---
# ... (Keep the db initialization block if needed)
# ----------------------------------------


# --- CRUD Operations as API Endpoints ---

# 1. CREATE: Add a new escalation approval record (POST)
@app.route('/escalations', methods=['POST'])
def create_escalation_endpoint():
    data = request.json
    if not data:
        return jsonify({'message': 'Missing request data'}), 400

    try:
        # Pass the data to the service function
        new_record = create_escalation(data) 
        return jsonify(new_record.to_dict()), 201
    except ValueError as e:
        # Handle specific validation errors (e.g., missing 'escid')
        return jsonify({'message': f'Validation Error: {str(e)}'}), 400
    except EscalationServiceError as e:
        # Handle database/service errors
        return jsonify({'message': f'Error creating record: {str(e)}'}), 500
    except Exception as e:
        # Catch any unexpected errors
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500


# 2. READ ALL: Get all escalation approval records (GET)
@app.route('/escalations', methods=['GET'])
def get_all_escalations_endpoint():
    try:
        records = get_all_escalations()
        return jsonify([record.to_dict() for record in records])
    except EscalationServiceError as e:
        return jsonify({'message': f'Error retrieving records: {str(e)}'}), 500


# 3. READ ONE: Get a single record by escid (GET)
@app.route('/escalations/<string:escid>', methods=['GET'])
def get_escalation_endpoint(escid):
    try:
        record = get_escalation_by_id(escid)
        if record:
            return jsonify(record.to_dict())
        return jsonify({'message': 'Record not found'}), 404
    except EscalationServiceError as e:
        return jsonify({'message': f'Error retrieving record: {str(e)}'}), 500


# 4. UPDATE: Update a record by escid (PUT)
@app.route('/escalations/<string:escid>', methods=['PUT'])
def update_escalation_endpoint(escid):
    data = request.json
    if not data:
        return jsonify({'message': 'Missing update data'}), 400

    try:
        # Pass the escid and data to the service function
        updated_record = update_escalation(escid, data)
        if updated_record:
            return jsonify(updated_record.to_dict())
        return jsonify({'message': 'Record not found'}), 404
    except EscalationServiceError as e:
        # Handle database/service errors
        return jsonify({'message': f'Error updating record: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500


# 5. DELETE: Delete a record by escid (DELETE)
@app.route('/escalations/<string:escid>', methods=['DELETE'])
def delete_escalation_endpoint(escid):
    try:
        # Pass the escid to the service function
        was_deleted = delete_escalation(escid)
        if was_deleted:
            return jsonify({'message': 'Record deleted successfully'}), 200
        return jsonify({'message': 'Record not found'}), 404
    except EscalationServiceError as e:
        # Handle database/service errors
        return jsonify({'message': f'Error deleting record: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500

# This line has been added in order to push to github

if __name__ == '__main__':
    app.run(debug=True)

# to run the app use python app.py