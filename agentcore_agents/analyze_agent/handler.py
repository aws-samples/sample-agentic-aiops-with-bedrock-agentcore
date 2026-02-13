"""AgentCore Handler for Analyze Agent"""
from bedrock_agentcore import BedrockAgentCoreApp
from agent import analyze_agent
from log_sanitizer import sanitize_log
from prompt_injection_detector import detect_prompt_injection, sanitize_input
import asyncio

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """Entry point for AgentCore Runtime"""
    try:
        incident_id = payload.get('incident_id')
        instance_id = payload.get('instance_id')
        server_name = payload.get('server_name', '')
        
        # Detect prompt injection
        is_injection, reason = detect_prompt_injection(server_name)
        if is_injection:
            app.logger.warning(f"Prompt injection blocked: {reason}")
            return {'error': 'Invalid input detected', 'incident_id': incident_id}
        
        # Sanitize inputs
        server_name = sanitize_input(server_name)
        
        analyze_agent.state = {
            'incident_id': incident_id,
            'instance_id': instance_id,
            'server_name': server_name
        }
        
        prompt = f"Analyze incident {incident_id}. Instance: {server_name} (ID: {instance_id}). Check status and update incident."
        
        # Run async invoke
        result = asyncio.run(analyze_agent.invoke_async(prompt))
        
        return {
            'agent': 'analyze',
            'incident_id': incident_id,
            'result': str(result)
        }
    except Exception as e:
        app.logger.error(sanitize_log(f"Agent error: {e}"))
        import traceback
        traceback.print_exc()
        return {'error': sanitize_log(str(e))}

if __name__ == "__main__":
    app.run()
