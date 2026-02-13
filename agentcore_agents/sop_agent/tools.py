"""Tools for incident management agents"""
import boto3
import socket
import requests
import time
import json
import os
from typing import Dict, Any
from strands import tool

# Set default AWS region for boto3
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')

# AWS EC2 tools
@tool
def get_ec2_instance_id(instance_name: str) -> str:
    """Get EC2 instance ID from instance name"""
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            return instance['InstanceId']
    return None

@tool
def get_ec2_status(instance_id: str, region: str = 'us-east-1') -> Dict[str, str]:
    """Get EC2 instance status"""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True)
    if response['InstanceStatuses']:
        status = response['InstanceStatuses'][0]
        return {
            "instance_id": instance_id,
            "state": status['InstanceState']['Name'],
            "system_status": status.get('SystemStatus', {}).get('Status', 'N/A'),
            "instance_status": status.get('InstanceStatus', {}).get('Status', 'N/A')
        }
    return {"instance_id": instance_id, "state": "unknown"}

@tool
def start_ec2_instance(instance_id: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """Start EC2 instance"""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.start_instances(InstanceIds=[instance_id])
    return {"instance_id": instance_id, "action": "start", "response": response}

@tool
def stop_ec2_instance(instance_id: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """Stop EC2 instance"""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.stop_instances(InstanceIds=[instance_id])
    return {"instance_id": instance_id, "action": "stop", "response": response}

@tool
def reboot_ec2_instance(instance_id: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """Reboot EC2 instance"""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.reboot_instances(InstanceIds=[instance_id])
    return {"instance_id": instance_id, "action": "reboot", "response": response}

@tool
def wait_for_instance_running(instance_id: str, region: str = 'us-east-1', max_wait_seconds: int = 120) -> Dict[str, Any]:
    """Wait for EC2 instance to reach running state with exponential backoff"""
    max_wait = int(os.environ.get('SOP_RETRY_TIMEOUT_SECONDS', 120))
    backoff_base = int(os.environ.get('EXPONENTIAL_BACKOFF_BASE', 2))
    initial_wait = int(os.environ.get('INITIAL_WAIT_SECONDS', 5))
    
    ec2 = boto3.client('ec2', region_name=region)
    start_time = time.time()
    wait_time = initial_wait
    attempt = 0
    
    while time.time() - start_time < max_wait:
        response = ec2.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True)
        if response['InstanceStatuses']:
            state = response['InstanceStatuses'][0]['InstanceState']['Name']
            if state == 'running':
                return {"instance_id": instance_id, "state": "running", "waited_seconds": int(time.time() - start_time), "attempts": attempt + 1}
        
        time.sleep(wait_time)
        attempt += 1
        wait_time = min(wait_time * backoff_base, 30)
    
    return {"instance_id": instance_id, "state": "timeout", "waited_seconds": max_wait, "attempts": attempt, "escalate": True}

@tool
def check_ssh_connectivity(host: str, port: int = 22, timeout: int = 5) -> Dict[str, Any]:
    """Check SSH connectivity to host using SSM Session Manager"""
    try:
        # Extract instance ID from host if it's an IP, otherwise use as instance ID
        if host.startswith('i-'):
            instance_id = host
        else:
            # Try to find instance by private IP
            ec2 = boto3.client('ec2', region_name='us-east-1')
            response = ec2.describe_instances(
                Filters=[{'Name': 'private-ip-address', 'Values': [host]}]
            )
            instance_id = None
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    break
            if not instance_id:
                return {"host": host, "port": port, "accessible": False, "error": "Instance not found"}
        
        # Check SSM connectivity
        ssm = boto3.client('ssm', region_name='us-east-1')
        response = ssm.describe_instance_information(
            Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}]
        )
        
        if response['InstanceInformationList']:
            info = response['InstanceInformationList'][0]
            ping_status = info.get('PingStatus', 'Unknown')
            accessible = ping_status == 'Online'
            return {
                "host": host,
                "instance_id": instance_id,
                "accessible": accessible,
                "ping_status": ping_status,
                "method": "SSM"
            }
        
        return {"host": host, "instance_id": instance_id, "accessible": False, "error": "SSM agent not connected"}
    except Exception as e:
        return {"host": host, "accessible": False, "error": str(e)}

# Bedrock Knowledge Base tool
@tool
def query_bedrock_knowledgebase(query: str, kb_id: str = None) -> Dict[str, Any]:
    """Query Bedrock Knowledge Base for SOP"""
    try:
        kb_id = 'DFRKHPNEG5'
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': query}
        )
        results = []
        for result in response.get('retrievalResults', []):
            results.append({
                "content": result['content']['text'],
                "score": result.get('score', 0)
            })
        return {"query": query, "results": results, "success": True}
    except Exception as e:
        return {"query": query, "results": [], "success": False, "error": f"{type(e).__name__}: {str(e)}"}
