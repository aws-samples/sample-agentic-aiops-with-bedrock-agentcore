"""AgentCore Handler for Validation Agent"""
from bedrock_agentcore import BedrockAgentCoreApp
from agent import validation_agent
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
        analysis_result = payload.get('analysis_result', '')
        
        # Detect prompt injection
        for field in [analysis_result]:
            is_injection, reason = detect_prompt_injection(field)
            if is_injection:
                app.logger.warning(f"Prompt injection blocked: {reason}")
                return {'error': 'Invalid input detected', 'incident_id': incident_id}
        
        # Sanitize inputs
        analysis_result = sanitize_input(analysis_result)
        
        validation_agent.state = {
            'incident_id': incident_id,
            'instance_id': instance_id,
            'server_ip': server_ip
        }
        
        prompt = f"Validate incident {incident_id}. Instance ID: {instance_id}, IP: {server_ip}. Check status and SSH. Analysis: {analysis_result}"
        result = asyncio.run(validation_agent.invoke_async(prompt))
        
        issue_persists = 'persists' in str(result).lower() or 'stopped' in str(result).lower()
        
        return {
            'agent': 'validation',
            'incident_id': incident_id,
            'result': str(result),
            'issue_persists': issue_persists
        }
    except Exception as e:
        app.logger.error(sanitize_log(f"Agent error: {e}"))
        return {'error': sanitize_log(str(e))}

if __name__ == "__main__":
    app.run()
