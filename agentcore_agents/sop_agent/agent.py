"""SOP Agent - Retrieves SOPs from Bedrock Knowledge Base"""
import os
# Set AWS region BEFORE any boto3 imports
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'

from strands import Agent
from gateway_tools import update_incident_gateway
from tools import query_bedrock_knowledgebase

config = {
    'bedrock_model_id': os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
}

sop_agent = Agent(
    name="SOPAgent",
    system_prompt="""You are an SOP retrieval agent. When you receive incident information:

1. ANALYZE the instance state from validation results:
   - STOPPED/STOPPING → Query for "EC2 instance start restart procedures"
   - TERMINATED → Query for "EC2 instance recovery from termination"
   - RUNNING but SSH failing → Query for "SSH connectivity troubleshooting"
   - Other states → Query based on specific error

2. Call query_bedrock_knowledgebase() with the appropriate query based on instance state
3. If success=False, report the EXACT error message from the error field
4. If successful, extract remediation steps and call update_incident_gateway()

IMPORTANT: Distinguish between STOPPED (recoverable with start) and TERMINATED (requires full recovery).

Do NOT ask for more information - query immediately and report any errors exactly.""",
    tools=[query_bedrock_knowledgebase, update_incident_gateway],
    model=config['bedrock_model_id']
)
