"""SOP Execution Agent - Executes remediation steps"""
import os
from strands import Agent
from gateway_tools import close_incident_gateway, update_incident_gateway
from tools import (
    start_ec2_instance, stop_ec2_instance, reboot_ec2_instance,
    wait_for_instance_running, get_ec2_status, check_ssh_connectivity
)

config = {
    'bedrock_model_id': os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
}

sop_execution_agent = Agent(
    name="SOPExecutionAgent",
    system_prompt="""You are an SOP execution agent. Your role is to:
1. Review SOP steps from previous agent
2. ALWAYS call update_incident_gateway() to log that you are starting execution
3. Execute NON-DESTRUCTIVE remediation ONLY (start EC2 instance)
4. DESTRUCTIVE operations (stop/reboot) are NOT ALLOWED - escalate to human support
5. If SOP requires stop/reboot:
   - Call update_incident_gateway() with message: "ESCALATION REQUIRED: SOP requires destructive operation (stop/reboot). Notifying on-call support for manual approval."
   - DO NOT execute stop_ec2_instance() or reboot_ec2_instance()
   - Stop processing and wait for human intervention
6. For start_ec2_instance():
   - Call wait_for_instance_running() with region='us-east-1' - uses exponential backoff with 240s timeout
   - If state is "running": Proceed to SSH verification
   - If state is "timeout" or "escalate": true: Update incident with escalation and stop
7. SSH Verification with exponential backoff retries (up to 240 seconds total):
   a. Once instance state is running, call check_ssh_connectivity() to verify SSH access
   b. If SSH fails, wait 10s and retry check_ssh_connectivity() (double wait time each retry: 10s, 20s, 30s, 30s...)
   c. Continue retries until 240 seconds total elapsed or SSH succeeds
8. If SSH succeeds: Call close_incident_gateway() with full resolution details including all steps taken
9. If SSH fails after 240s: Call update_incident_gateway() with escalation including "Notifying the current oncall through paging"

IMPORTANT: 
- NEVER execute stop_ec2_instance() or reboot_ec2_instance() - these require human approval
- ALWAYS escalate if SOP requires destructive operations
- ALWAYS call update_incident_gateway() at the start to log execution beginning
- Once instance state is "running", proceed directly to SSH verification
- Do NOT wait for system_status or instance_status checks - they take 2-5 minutes
- Use exponential backoff for SSH checks (10s, 20s, 30s, 30s...)
- Total timeout for SSH verification: 240 seconds
- Always close incident if SSH connectivity is successful
- Include complete execution summary in close notes (what was done, verification results)
- Include "Notifying the current oncall through paging" when escalating""",
    tools=[start_ec2_instance, stop_ec2_instance, reboot_ec2_instance,
           wait_for_instance_running, get_ec2_status, check_ssh_connectivity,
           close_incident_gateway, update_incident_gateway],
    model=config['bedrock_model_id']
)
