import streamlit as st
import requests
import pandas as pd
import logging
import os
import time
import hashlib
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Load environment variables


# Initialize global variables
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
TOKEN_GENERATION_DATE = os.getenv('TOKEN_GENERATION_DATE')

def generate_oauth_token(secret_key):
    today = datetime.now().strftime('%Y-%m-%d')
    salted_string = f"{secret_key}{today}"
    token = hashlib.sha256(salted_string.encode()).hexdigest()
    return token

def update_oauth_token(secret_key, env_file='.env'):
    global OAUTH_TOKEN, TOKEN_GENERATION_DATE
    
    # Initialize OAUTH_TOKEN if it's not already defined
    if 'OAUTH_TOKEN' not in globals():
        OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get the current date from environment or Streamlit secrets
    current_date = os.getenv('TOKEN_GENERATION_DATE')
    
    if current_date != today or OAUTH_TOKEN is None:
        new_token = generate_oauth_token(secret_key)
        OAUTH_TOKEN = new_token
        TOKEN_GENERATION_DATE = today

        # Update Streamlit session state
        if 'session_state' in st.__dict__:
            st.session_state['OAUTH_TOKEN'] = new_token
            st.session_state['TOKEN_GENERATION_DATE'] = today

        # Update .env file if it exists
        if os.path.exists(env_file):
            set_key(env_file, 'OAUTH_TOKEN', new_token)
            set_key(env_file, 'TOKEN_GENERATION_DATE', today)

        # Update environment variables
        os.environ['OAUTH_TOKEN'] = new_token
        os.environ['TOKEN_GENERATION_DATE'] = today

        return new_token
    else:
        return OAUTH_TOKEN

def fetch_website_status(urls_dict, oauth_token):
    all_status_data = {}
    timestamp = datetime.now()
    
    # Load the JSON data from the file
    with open("simpleQLDV2.json") as json_file:
        data_to_post = json.load(json_file)
    
    for environment, urls in urls_dict.items():
        status_data = []
        for entry in urls:
            url = entry["url"]
            expected_status = entry["pass_method"]
            service_name = entry["service_name"]
            
            try:
                start_time = time.time()
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {oauth_token}"
                }
                if "backtest" in url or "flow" in url:
                    # Handle POST requests for backtest and flow endpoints
                    payload = {
                        "json": data_to_post,
                        "period": "500",
                        "hash": "hashvalue",
                        "end_date": "2024-05-31"
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                else:
                    # Handle GET requests for other endpoints
                    response = requests.get(url, headers=headers, timeout=10)
                
                latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                actual_status = f"{response.status_code} {response.reason}"
                is_up = actual_status == expected_status
                received_any_response = response.status_code is not None
            except requests.exceptions.RequestException as e:
                logging.error(f"Error checking {url}: {str(e)}")
                is_up = False
                received_any_response = False
                latency = None
            
            status_data.append({
                "Service Name": service_name,
                "Uptime/Downtime": "normal" if received_any_response else "error",
                "Pass/Fail": "normal" if is_up else "error",
                "Latency (ms)": latency if latency is not None else "error",
                "Last Check Time": timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        all_status_data[environment] = status_data

    return all_status_data


def save_to_csv(status_data, file_path):
    # Create a DataFrame from the status data
    df = pd.DataFrame(status_data)

    # Convert "normal" to 1 and "error" to 0 for CSV saving
    df["Uptime/Downtime"] = df["Uptime/Downtime"].apply(lambda x: 1 if x == "normal" else 0)
    df["Pass/Fail"] = df["Pass/Fail"].apply(lambda x: 1 if x == "normal" else 0)
    df["Latency (ms)"] = df["Latency (ms)"].apply(lambda x: int(x) if x != "error" else None)

    # Append to CSV
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
