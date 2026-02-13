"""Analyze Agent - Investigates incidents and checks EC2 status"""
import json
import os
from strands import Agent
from gateway_tools import update_incident_gateway
from tools import get_ec2_status

config = {
    'bedrock_model_id': os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
}

analyze_agent = Agent(
    name="AnalyzeAgent",
    system_prompt="""You are an incident analysis agent. Your role is to:
1. Call get_ec2_status(instance_id) to check instance status
2. Analyze the findings
3. Call update_incident_gateway() with findings in this EXACT format:

**Instance Status Check Results:**
[Status details from get_ec2_status]

**Analysis:**
[Your analysis of the situation]

**Root Cause:**
[Identified root cause]

Do NOT include any other sections like Recommended Actions or Impact.""",
    tools=[update_incident_gateway, get_ec2_status],
    model=config['bedrock_model_id']
)
