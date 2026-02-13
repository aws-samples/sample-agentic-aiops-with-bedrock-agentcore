#!/usr/bin/env python3
import json
import time
import subprocess
import requests
import logging
from datetime import datetime
import os
import sys
import boto3
import base64
import re
import shlex

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'security'))
from ssh_key_manager import SSHKeyManager
from log_sanitizer import sanitize_log

# Configuration
SERVERS_FILE = "servers.json"
SSH_KEY_SECRET = "incident-management/ssh-key"
SSH_USER = "ec2-user"
SSH_TIMEOUT = 10
SERVICENOW_URL = "https://dev192162.service-now.com/api/now/table/incident"
SERVICENOW_CREDENTIALS_SECRET = "incident-management/servicenow-credentials"
CHECK_INTERVAL = 30
ssh_key_manager = SSHKeyManager(SSH_KEY_SECRET)

def get_servicenow_auth():
    """Get ServiceNow Basic Auth from Secrets Manager"""
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId=SERVICENOW_CREDENTIALS_SECRET)
        creds = json.loads(response['SecretString'])
        auth_string = f"{creds['username']}:{creds['password']}"
        return base64.b64encode(auth_string.encode()).decode()
    except Exception as e:
        logging.error(f"Failed to get ServiceNow credentials: {e}")
        return None

# Setup logging
def setup_logging():
    """Setup logging with date-formatted file in log folder"""
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')
    log_file = os.path.join(log_dir, f'monitoring_{log_date}.log')
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

setup_logging()

def validate_server_input(server_name, server_ip):
    """Validate server name and IP to prevent command injection"""
    # Allow alphanumeric, dots, hyphens, underscores only
    if not re.match(r'^[\w\.\-]+$', server_name):
        raise ValueError(f"Invalid server name format: {server_name}")
    if not re.match(r'^[\w\.\-]+$', server_ip):
        raise ValueError(f"Invalid server IP format: {server_ip}")
    return True

def load_servers():
    """Load server list from JSON file"""
    try:
        with open(SERVERS_FILE, 'r') as f:
            servers = json.load(f)
            # Validate all servers on load
            for server in servers:
                validate_server_input(server['name'], server['ip'])
            return servers
    except ValueError as e:
        logging.error(f"Server validation failed: {e}")
        return []
    except Exception as e:
        logging.error(f"Failed to load servers file: {e}")
        return []

def test_ssh_connection(server_name, server_ip):
    """Test SSH connection to server"""
    ssh_key_path = None
    try:
        # Validate inputs to prevent command injection
        validate_server_input(server_name, server_ip)
        
        ssh_key_path = ssh_key_manager.get_key_file()
        # Use shlex.escape() for additional safety
        cmd = [
            "ssh",
            "-i",
            shlex.escape(ssh_key_path),
            "-o",
            "ConnectTimeout=10",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "BatchMode=yes",
            shlex.escape(SSH_USER + "@" + server_ip),
            "echo",
            "SSH test successful"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=SSH_TIMEOUT)  # nosemgrep: dangerous-subprocess-use-audit
        
        if result.returncode == 0:
            logging.info(sanitize_log(f"SSH connection to {server_name} successful"))
            return True, "Connection successful"
        else:
            error_msg = result.stderr.strip() or "SSH connection failed"
            logging.warning(sanitize_log(f"SSH connection to {server_name} failed: {error_msg}"))
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "SSH connection timeout"
        logging.warning(sanitize_log(f"SSH connection to {server_name} timed out"))
        return False, error_msg
    except Exception as e:
        error_msg = f"SSH test error: {str(e)}"
        logging.error(sanitize_log(f"SSH test to {server_name} error: {e}"))
        return False, error_msg
    finally:
        if ssh_key_path:
            ssh_key_manager.cleanup_key_file(ssh_key_path)



def check_existing_incident(server_name):
    """Check if open incident exists for server in ServiceNow"""
    try:
        auth_token = get_servicenow_auth()
        if not auth_token:
            return None
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_token}"
        }
        
        query = f"u_server_name={server_name}^stateIN1,2,3^ORDERBYDESCsys_created_on"
        response = requests.get(
            f"{SERVICENOW_URL}?sysparm_query={query}&sysparm_fields=number,state,sys_id",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json().get("result", [])
            if results:
                return results[0]["number"]
        return None
    except Exception as e:
        logging.error(sanitize_log(f"Error checking existing incident: {e}"))
        return None

def create_servicenow_incident(server_name, server_ip):
    """Create ServiceNow incident (triggers AgentCore via business rule)"""
    try:
        incident_data = {
            "short_description": f"SSH Connection Failure: {server_name}",
            "description": f"Automated SSH connectivity failure detected for {server_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "u_server_name": server_name,
            "u_server_ip": server_ip
        }
        
        auth_token = get_servicenow_auth()
        if not auth_token:
            logging.error("Cannot create incident: ServiceNow credentials unavailable")
            return False, None
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_token}"
        }
        
        response = requests.post(
            SERVICENOW_URL,
            headers=headers,
            json=incident_data,
            timeout=30
        )
        
        if response.status_code == 201:
            incident_number = response.json()["result"]["number"]
            logging.info(sanitize_log(f"✓ Incident {incident_number} created for {server_name} - AgentCore workflow triggered"))
            return True, incident_number
        else:
            logging.error(sanitize_log(f"Failed to create incident: {response.status_code}"))
            return False, None
            
    except Exception as e:
        logging.error(sanitize_log(f"Error creating incident: {e}"))
        return False, None

def monitor_servers():
    """Main monitoring function"""
    servers = load_servers()
    if not servers:
        logging.error("No servers to monitor")
        return
    
    logging.info(f"Monitoring {len(servers)} servers")
    
    for server in servers:
        server_name = server['name']
        server_ip = server['ip']
        
        ssh_success, _ = test_ssh_connection(server_name, server_ip)
        
        if not ssh_success:
            existing_incident = check_existing_incident(server_name)
            if existing_incident:
                logging.info(f"Open incident {existing_incident} already exists for {server_name}")
            else:
                logging.warning(f"⚠ SSH FAILED: {server_name} ({server_ip})")
                create_servicenow_incident(server_name, server_ip)
        else:
            existing_incident = check_existing_incident(server_name)
            if existing_incident:
                logging.info(f"✓ {server_name} recovered - Incident {existing_incident} will be auto-closed")
    
    for handler in logging.getLogger().handlers:
        if hasattr(handler, 'flush'):
            handler.flush()

def main():
    """Main function with continuous monitoring loop"""
    # Initial logging setup
    setup_logging()
    logging.info("Server monitoring script started")
    
    try:
        while True:
            # Setup logging for current date
            setup_logging()
            monitor_servers()
            logging.info(f"Waiting {CHECK_INTERVAL} seconds before next check...")
            time.sleep(CHECK_INTERVAL)  # nosemgrep: arbitrary-sleep
            
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Monitoring error: {e}")

if __name__ == "__main__":
    main()