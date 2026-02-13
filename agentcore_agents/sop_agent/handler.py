"""AgentCore Handler for SOP Agent"""
from bedrock_agentcore import BedrockAgentCoreApp
from agent import sop_agent
from log_sanitizer import sanitize_log
from prompt_injection_detector import detect_prompt_injection, sanitize_input
import asyncio

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    try:
        incident_id = payload.get('incident_id')
        instance_id = payload.get('instance_id')
        analysis_result = payload.get('analysis_result', '')
        validation_result = payload.get('validation_result', '')
        
        # Detect prompt injection
        for field in [analysis_result, validation_result]:
            is_injection, reason = detect_prompt_injection(field)
            if is_injection:
                app.logger.warning(f"Prompt injection blocked: {reason}")
                return {'error': 'Invalid input detected', 'incident_id': incident_id}
        
        # Sanitize inputs
        analysis_result = sanitize_input(analysis_result)
        validation_result = sanitize_input(validation_result)
        
        sop_agent.state = {
            'incident_id': incident_id,
            'instance_id': instance_id
        }
        
        prompt = f"Get SOP for the issue. Incident: {incident_id}, Instance: {instance_id}. Analysis: {analysis_result}. Validation: {validation_result}"
        result = asyncio.run(sop_agent.invoke_async(prompt))
        
        return {
            'agent': 'sop',
            'incident_id': incident_id,
            'result': str(result)
        }
    except Exception as e:
        app.logger.error(sanitize_log(f"Agent error: {e}"))
        return {'error': sanitize_log(str(e))}

if __name__ == "__main__":
    app.run()
