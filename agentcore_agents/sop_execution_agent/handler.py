"""AgentCore Handler for SOP Execution Agent"""
from bedrock_agentcore import BedrockAgentCoreApp
from agent import sop_execution_agent
from log_sanitizer import sanitize_log
from prompt_injection_detector import detect_prompt_injection, sanitize_input
import asyncio

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    try:
        incident_id = payload.get('incident_id')
        instance_id = payload.get('instance_id')
        server_ip = payload.get('server_ip', '')
        sop_result = payload.get('sop_result', '')
        
        # Detect prompt injection
        for field in [sop_result]:
            is_injection, reason = detect_prompt_injection(field)
            if is_injection:
                app.logger.warning(f"Prompt injection blocked: {reason}")
                return {'error': 'Invalid input detected', 'incident_id': incident_id}
        
        # Sanitize inputs
        sop_result = sanitize_input(sop_result)
        
        sop_execution_agent.state = {
            'incident_id': incident_id,
            'instance_id': instance_id,
            'server_ip': server_ip
        }
        
        prompt = f"Execute remediation. Incident: {incident_id}, Instance: {instance_id}, IP: {server_ip}. SOP: {sop_result}. Start instance if stopped."
        result = asyncio.run(sop_execution_agent.invoke_async(prompt))
        
        return {
            'agent': 'sop_execution',
            'incident_id': incident_id,
            'result': str(result)
        }
    except Exception as e:
        app.logger.error(sanitize_log(f"Agent error: {e}"))
        return {'error': sanitize_log(str(e))}

if __name__ == "__main__":
    app.run()
