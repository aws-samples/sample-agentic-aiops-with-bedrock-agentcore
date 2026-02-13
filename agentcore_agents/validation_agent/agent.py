"""Validation Agent - Validates if issues persist"""
import os
from strands import Agent
from gateway_tools import close_incident_gateway, update_incident_gateway
from tools import check_ssh_connectivity, get_ec2_status

config = {
    'bedrock_model_id': os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
}

validation_agent = Agent(
    name="ValidationAgent",
    system_prompt="""You are a validation agent. Your role is to:
1. Check current EC2 instance status using get_ec2_status tool
2. If instance is running, test SSH connectivity using check_ssh_connectivity tool
3. Determine if the issue still persists:
   - If instance is STOPPED or STOPPING: Issue PERSISTS
   - If instance is RUNNING but SSH fails: Issue PERSISTS
   - If instance is RUNNING and SSH succeeds: Issue RESOLVED
4. Update ServiceNow incident with validation results using update_incident_gateway tool
5. If issue is RESOLVED, close the incident using close_incident_gateway tool
6. If issue PERSISTS, clearly state "Issue persists" in your response""",
    tools=[check_ssh_connectivity, get_ec2_status, close_incident_gateway, update_incident_gateway],
    model=config['bedrock_model_id']
)
