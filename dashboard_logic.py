import requests
import pandas as pd
import logging
import os
import time
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.ERROR)

def fetch_website_status(urls, environment):
    status_data = []
    timestamp = datetime.now()
    
    # Load the JSON data from the file
    try:
        with open("simpleQLDV2.json") as json_file:
            data_to_post = json.load(json_file)
    except FileNotFoundError:
        logging.error("simpleQLDV2.json file not found. Using empty dict instead.")
        data_to_post = {}
    
    for entry in urls:
        url = entry["url"]
        expected_status = entry["pass_method"]
        service_name = entry["service_name"]
        
        try:
            start_time = time.time()
            if "backtest" in url or "flow" in url:
                # Handle POST requests for backtest and flow endpoints
                payload = {
                    "json": data_to_post,
                    "period": "500",
                    "hash": "hashvalue",
                    "end_date": "2024-05-31"
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            else:
                # Handle GET requests for other endpoints
                response = requests.get(url, timeout=10)
            
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
            "Uptime/Downtime": 1 if received_any_response else 0,
            "Pass/Fail": 1 if is_up else 0,
            "Latency (ms)": latency if latency is not None else None,
            "Last Check Time": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "Environment": environment
        })

    return status_data

def save_to_csv(status_data, environment):
    # Create a DataFrame from the status data
    df = pd.DataFrame(status_data)

    # Define the file path based on the environment
    file_path = f'website_status_{environment.lower()}.csv'

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Append to CSV
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)

def update_all_environments(urls):
    all_status_data = []
    for env in ['Dev', 'Staging', 'Prod']:
        status_data = fetch_website_status(urls[env], env)
        all_status_data.extend(status_data)
        save_to_csv(status_data, env)
    return all_status_data
