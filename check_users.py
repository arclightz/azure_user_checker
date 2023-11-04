import requests
import logging
from datetime import datetime
import configparser
import csv
from tabulate import tabulate


# Initialize logging
logging.basicConfig(filename="user_validation.log", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")

try:
    logging.info("Script started")
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get the URL to monitor
    tenant_id = config['DEFAULT']['tenant_id']

    # Get the User-Agent header
    client_id = config['DEFAULT']['client_id']

    # Get the Discord webhook URL
    client_secret = config['DEFAULT']['client_secret']

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

    # Read the user list from the .csv file
    user_list = []
    with open('user_list.csv', 'r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            last_name = row['Sukunimi']
            first_name = row['Etunimi']
            user_list.append(f"{first_name},{last_name}")

    # Initialize lists to store active users and not found users
    active_users = []
    not_found_users = []

    # Search for users in Azure AD
    for user in user_list:
        first_name, last_name = user.split(',')
        filter_str = f"givenName eq '{first_name}' and surname eq '{last_name}'"
        params = {
            '$filter': filter_str,
        }

        response = requests.get(graph_url + users_endpoint, headers=headers, params=params)

        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('value'):
                # User exists
                user_info = user_data['value'][0]
                user_status = "Active"
                active_users.append([first_name, last_name, user_status])
            else:
                not_found_users.append([first_name, last_name])

    # Create tables
    headers = ["First Name", "Last Name", "Status"]
    active_table = tabulate(active_users, headers, tablefmt="pretty")
    not_found_table = tabulate(not_found_users, ["First Name", "Last Name"], tablefmt="pretty")

    # Print the tables
    print("Active Users:")
    print(active_table)

    print("\nUsers Not Found:")
    print(not_found_table)

    # Log the end of the script
    logging.info("Script completed")
except Exception as e:
    # Log any errors that occur
    logging.error(f"An error occurred: {str(e)}")