'''
IP Address Monitor and DNS Updater

Monitors WAN IP address changes and updates:
- Dreamhost DNS records for 'www' and '@' (A records)
- DuckDNS domain 'scprimemn'
'''

import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import common

import requests
import json
import time
import pathlib
import logging
from datetime import datetime
import pytz
import configparser

# Set up dedicated logger for this script
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update_ip_address.log')
script_logger = logging.getLogger('update_ip_address')
script_logger.setLevel(logging.INFO)
# Remove any existing handlers to avoid duplicates
if script_logger.handlers:
    script_logger.handlers.clear()
handler = logging.FileHandler(LOG_FILE)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
script_logger.addHandler(handler)

def log(level, message):
    """Log message to both console and dedicated log file."""
    dt = datetime.now(tz=pytz.utc)
    dt_str = dt.astimezone(pytz.timezone("America/Chicago")).strftime("%Y-%m-%d %I:%M%p")
    formatted_message = f"{dt_str}: {message}"
    print(formatted_message)
    getattr(script_logger, level)(message)

# Configuration
DREAMHOST_API_KEY = ""  # Set this in .ini file or environment variable
DREAMHOST_DOMAIN = ""  # Your domain name (e.g., "example.com")
DUCKDNS_DOMAIN = ""
DUCKDNS_TOKEN = ""

# File to store last known IP
IP_STORAGE_FILE = f"{common.DIR_BASE}last_known_ip.txt"


def get_public_ip():
    """Get current public IP address from multiple services."""
    services = [
        'https://api.ipify.org',
        'https://icanhazip.com',
        'https://ifconfig.me/ip'
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=10)
            if response.status_code == 200:
                ip = response.text.strip()
                # Basic validation - check if it's a valid IP
                parts = ip.split('.')
                if len(parts) == 4 and all(part.isdigit() for part in parts):
                    return ip
        except Exception as e:
            log("warning", f"Failed to get IP from {service}: {e}")
            continue
    
    raise Exception("Unable to retrieve public IP from any service")


def get_last_known_ip():
    """Retrieve the last known IP address from storage file."""
    if os.path.isfile(IP_STORAGE_FILE):
        try:
            with open(IP_STORAGE_FILE, 'r') as f:
                return f.read().strip()
        except Exception as e:
            log("error", f"Error reading last known IP: {e}")
    return None


def save_current_ip(ip):
    """Save the current IP address to storage file."""
    try:
        with open(IP_STORAGE_FILE, 'w') as f:
            f.write(ip)
    except Exception as e:
        log("error", f"Error saving IP address: {e}")
        
        
def list_dreamhost_dns():
   """
   List Dreamhost DNS records for a domain.
   
   Args:
      domain: Domain name (e.g., "example.com")
      api_key: Dreamhost API key
   """
   api_url = "https://api.dreamhost.com/"
   params = {
      'key': DREAMHOST_API_KEY,
      'cmd': 'dns-list_records',
      'format': 'json',
   }
   response = requests.get(api_url, params=params, timeout=30)
   if response.status_code != 200:
      log("error", f"Dreamhost API request failed with status {response.status_code}")
      return None
   data = response.json()
   if data.get('result') != 'success':
      log("error", f"Dreamhost API error: {data.get('data', 'Unknown error')}")
      return None
   return data


def update_dreamhost_dns(domain, api_key, ip):
    """
    Update Dreamhost DNS A records for '@' and 'www'.
    
    Args:
        domain: Domain name (e.g., "example.com")
        api_key: Dreamhost API key
        ip: New IP address
    """
    if not api_key or not domain:
        log("warning", "Dreamhost API key or domain not configured, skipping Dreamhost update")
        return False
    
    api_url = "https://api.dreamhost.com/"
    records_to_update = ['@', 'www']
    
    try:
        # List current DNS records
        data = list_dreamhost_dns(domain, api_key)
        
        if data is None or data.get('result') != 'success':
            if data is None:
                log("error", "Failed to retrieve Dreamhost DNS records")
            else:
                log("error", f"Dreamhost API error: {data.get('data', 'Unknown error')}")
            return False
        
        # Find and update/remove existing A records for '@' and 'www'
        existing_records = data.get('data', [])
        records_updated = []
        
        for record_type in records_to_update:
            # Remove existing A records for this record type
            for record in existing_records:
                if (record.get('type') == 'A' and 
                    record.get('record') == record_type and 
                    record.get('editable') == '1'):
                    
                    # Remove old record
                    remove_params = {
                        'key': api_key,
                        'cmd': 'dns-remove_record',
                        'record': record.get('record'),
                        'type': record.get('type'),
                        'value': record.get('value')
                    }
                    remove_response = requests.get(api_url, params=remove_params, timeout=30)
                    remove_data = remove_response.json()
                    
                    if remove_data.get('result') == 'success':
                        log("info", f"Removed old Dreamhost A record: {record_type}.{domain} -> {record.get('value')}")
                    else:
                        log("warning", f"Failed to remove old record: {remove_data.get('data', 'Unknown error')}")
            
            # Add new A record
            add_params = {
                'key': api_key,
                'cmd': 'dns-add_record',
                'record': record_type,
                'type': 'A',
                'value': ip
            }
            add_response = requests.get(api_url, params=add_params, timeout=30)
            add_data = add_response.json()
            
            if add_data.get('result') == 'success':
                log("info", f"Updated Dreamhost A record: {record_type}.{domain} -> {ip}")
                records_updated.append(record_type)
            else:
                error_msg = add_data.get('data', 'Unknown error')
                # Check if error is because record already exists (which is fine if it's the correct IP)
                if 'already exists' in error_msg.lower() or 'already has that value' in error_msg.lower():
                    log("info", f"Dreamhost A record {record_type}.{domain} already set to {ip}")
                    records_updated.append(record_type)
                else:
                    log("error", f"Failed to add Dreamhost A record for {record_type}: {error_msg}")
        
        return len(records_updated) == len(records_to_update)
        
    except requests.exceptions.RequestException as e:
        log("error", f"Network error updating Dreamhost DNS: {e}")
        return False
    except json.JSONDecodeError as e:
        log("error", f"Invalid JSON response from Dreamhost API: {e}")
        return False
    except Exception as e:
        log("error", f"Unexpected error updating Dreamhost DNS: {e}")
        return False


def update_duckdns(domain, token, ip):
    """
    Update DuckDNS domain with new IP address.
    
    Args:
        domain: DuckDNS domain name
        token: DuckDNS token
        ip: New IP address
    """
    try:
        url = f'https://www.duckdns.org/update?domains={domain}&token={token}&ip={ip}'
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            result = response.text.strip()
            if result == 'OK':
                log("info", f"Updated DuckDNS domain {domain} to {ip}")
                return True
            else:
                log("error", f"DuckDNS update failed: {result}")
                return False
        else:
            log("error", f"DuckDNS API request failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log("error", f"Network error updating DuckDNS: {e}")
        return False
    except Exception as e:
        log("error", f"Unexpected error updating DuckDNS: {e}")
        return False


def check_and_update():
    """Check for IP changes and update DNS records if needed."""
    try:
        current_ip = get_public_ip()
        last_ip = get_last_known_ip()
        
        if current_ip == last_ip:
            log("info", f"No IP change detected. Current IP: {current_ip}")
            return
        
        log("info", f"IP address changed from {last_ip} to {current_ip}")
        
        # Update DNS records
        dreamhost_success = update_dreamhost_dns(DREAMHOST_DOMAIN, DREAMHOST_API_KEY, current_ip)
        duckdns_success = update_duckdns(DUCKDNS_DOMAIN, DUCKDNS_TOKEN, current_ip)
        
        # Only save IP if at least one update succeeded
        if dreamhost_success or duckdns_success:
            save_current_ip(current_ip)
            log("info", "IP address update completed")
        else:
            log("error", "Failed to update DNS records, IP not saved")
            
    except Exception as e:
        log("error", f"Error in check_and_update: {e}")


def load_config():
    """Load configuration from .ini file or environment variables."""
    global DREAMHOST_API_KEY, DREAMHOST_DOMAIN, DUCKDNS_TOKEN, DUCKDNS_DOMAIN
    
    # Try to load from config file
    try:
        # Read config from project directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, '.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'dns' in config:
            DREAMHOST_API_KEY = config['dns'].get('dreamhost_api_key', '')
            DREAMHOST_DOMAIN = config['dns'].get('dreamhost_domain', '')
            DUCKDNS_TOKEN = config['dns'].get('duckdns_token', '')
            DUCKDNS_DOMAIN = config['dns'].get('duckdns_domain', '')
    except Exception as e:
        log("warning", f"Error reading DNS config from .ini: {e}")


def main():    
   load_config()
   log("info", "Script started")
    
    # Do an initial check
   #  check_and_update()
   
   


if __name__ == '__main__':
    main()

