from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import logging
from datetime import datetime
import configparser
import csv
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)  # This enables CORS for your entire Flask app

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize logging
logging.basicConfig(filename="user_validation.log", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")

class UserAnalysisResource(Resource):
    def get(self):
        logging.info("GET request received for UserAnalysisResource")
        return {"message": "The API is working and can be reached."}
    
    def post(self):
        logging.info("POST request received for UserAnalysisResource")
        if 'file' not in request.files:
            return {"message": "No file provided."}, 400

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return {"message": "No selected file."}, 400

        if uploaded_file:
            try:
                # Save the uploaded file to a temporary location
                temp_file_path = "/home/mrdj/hacking/AI/python/azure_uservalidation/uploaded_file.csv"  # Adjust this path
                uploaded_file.save(temp_file_path)

                # Process the uploaded file
                logging.info("Processing the uploaded file...")
                results = analyze_users(temp_file_path)
                return jsonify(results)
            except Exception as e:
                logging.error("Error processing the uploaded file: %s", str(e))
                return {"message": "Error processing the uploaded file.", "error": str(e)}, 500
        else:
            return {"message": "No file provided."}, 400

api.add_resource(UserAnalysisResource, '/api/user_analysis')

def detect_delimiter(first_line):
    if ";" in first_line:
        return ";"
    elif "," in first_line:
        return ","
    return None  # If the delimiter is not detected

def analyze_users(csv_file_path):
    logging.info("Script started")
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get the URL to monitor
    tenant_id = config['AzureAD']['tenant_id']

    # Get the User-Agent header
    client_id = config['AzureAD']['client_id']

    # Get the Discord webhook URL
    client_secret = config['AzureAD']['client_secret']

    # Log Azure AD authentication step
    logging.info("Authenticating with Azure AD...")

    # Microsoft Graph API endpoints
    graph_url = 'https://graph.microsoft.com/v1.0'
    users_endpoint = '/users'

    # Acquire an access token
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://graph.microsoft.com',
    }

    # Log token acquisition step
    logging.info("Acquiring access token...")
    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json()['access_token']

    # Initialize a session with the access token
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
    }

    # Log successful authentication
    logging.info("Azure AD authentication successful")

 # Read the uploaded CSV file
    with open(csv_file_path, 'r', encoding='ISO-8859-1') as csv_file:
        # Read the first line to detect the delimiter
        first_line = csv_file.readline()

        delimiter = detect_delimiter(first_line)
        if delimiter is None:
            return "Unable to detect the delimiter (, or ;)."
        csv_file.seek(0)

        logging.info("Delimiter checked...")
        next(csv_file)
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        user_list = [f"{row[2]},{row[1]}" for row in csv_reader]  # Assuming first, last name order in CSV

    logging.info("Initialize lists to store active users and not found users")
    active_users = []
    not_found_users = []

    logging.info("Search for users in Azure AD")
    for user in user_list:
        logging.debug("Cheking User List... " + user)
        # first_name, last_name = user.split(',')
        # filter_str = f"givenName eq '{first_name}' and surname eq '{last_name}'"
        # params = {
        #    '$filter': filter_str,
        # }
        parts = user.split(',')
        if len(parts) == 2:
            first_name, last_name = parts
            filter_str = f"givenName eq '{first_name}' and surname eq '{last_name}'"
            params = {
                '$filter': filter_str,
            }
        else:
            # Handle or log improperly formatted lines
            logging.error("Invalid format in CSV: %s", user)
            continue  # Skip to the next line

        response = requests.get(graph_url + users_endpoint, headers=headers, params=params)
        logging.debug("Response sent...")
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('value'):
                # User exists
                user_info = user_data['value'][0]
                user_status = "Active"
                active_users.append([first_name, last_name, user_status])
                logging.debug("User appended to active users list")
            else:
                not_found_users.append([first_name, last_name])
                logging.debug("User appended to not found users list")

    response = {
        "active_users": [{"first_name": first_name, "last_name": last_name, "status": status} for first_name, last_name, status in active_users],
        "not_found_users": [{"first_name": first_name, "last_name": last_name} for first_name, last_name in not_found_users]
    }
    logging.debug("Returning response")
    return response

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # Load configuration settings
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Access configuration settings
    app.config['UPLOAD_FOLDER'] = config.get('Flask', 'upload_folder')
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the uploaded CSV file
            with open(file_path, 'r', encoding='ISO-8859-1') as csv_file:
                # Read the first line to detect the delimiter
                first_line = csv_file.readline()

                delimiter = detect_delimiter(first_line)
                if delimiter is None:
                    return "Unable to detect the delimiter (, or ;)."
                file.seek(0)

                #csv_reader = csv.reader(csv_file, delimiter=delimiter)
                #user_list = [f"{row[2]},{row[1]}" for row in csv_reader]  # Assuming first, last name order in CSV

            # Analyze users and get the results
            active_users, not_found_users = analyze_users(file_path)

            # Return the report page with the analysis results
            return render_template('report.html', active_users=active_users, not_found_users=not_found_users)

        else:
            return "No file provided."

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)