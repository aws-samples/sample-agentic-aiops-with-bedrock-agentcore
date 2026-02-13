"""Lambda Orchestrator for AgentCore Agents"""
import json
import os
import sys
import boto3
from typing import Dict, Any

sys.path.insert(0, '/opt/python')
try:
    from prompt_injection_detector import detect_prompt_injection
    from log_sanitizer import sanitize_log
    from pii_detector import detect_pii, redact_pii
except ImportError:
    def detect_prompt_injection(text): return False, ""
    def sanitize_log(msg): return msg
    def detect_pii(text): return {}
    def redact_pii(text): return text

# AgentCore ARNs from environment variables
ANALYZE_AGENT_ARN = os.environ.get('ANALYZE_AGENT_ARN')
VALIDATION_AGENT_ARN = os.environ.get('VALIDATION_AGENT_ARN')
SOP_AGENT_ARN = os.environ.get('SOP_AGENT_ARN')
EXECUTION_AGENT_ARN = os.environ.get('EXECUTION_AGENT_ARN')

# Initialize clients
agentcore_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
ec2_client = boto3.client('ec2', region_name='us-east-1')

def get_ec2_instance_id(server_name: str) -> str:
    """Get EC2 instance ID from server name"""
    response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [server_name]}])
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            return instance['InstanceId']
    return None

def invoke_agentcore_agent(agent_arn: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke AgentCore agent via ARN"""
    try:
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            payload=json.dumps(payload).encode('utf-8'),
            contentType='application/json',
            accept='application/json'
        )
        
        # Read streaming response
        result = ""
        if 'completion' in response:
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
        
        print(f"Agent response length: {len(result)} chars")
        return {'result': result, 'success': True}
    except Exception as e:
        print(f"Error invoking agent {agent_arn}: {str(e)}")
        return {'error': str(e), 'success': False}

def lambda_handler(event, context):
    """Main orchestrator for incident processing"""
    try:
        # Parse incoming event - handle both API Gateway and direct invocation
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event
        
        incident_id = body.get('incident_id')
        server_name = body.get('server_name')
        server_ip = body.get('server_ip')
        description = body.get('description', '')
        
        # Detect and redact PII
        pii_findings = detect_pii(description)
        if pii_findings:
            print(f"PII detected: {pii_findings}")
            description = redact_pii(description)
            body['description'] = description
        
        # Detect prompt injection
        is_injection, injection_msg = detect_prompt_injection(description)
        if is_injection:
            print(sanitize_log(f"Security alert: {injection_msg}"))
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid input detected'})}
        
        print(sanitize_log(f"Processing incident {incident_id} for {server_name}"))
        
        # Get instance ID
        instance_id = get_ec2_instance_id(server_name)
        if not instance_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Instance ID not found for {server_name}'})
            }
        
        print(sanitize_log(f"Instance ID: {instance_id}"))
        
        # Step 1: Analyze Agent
        print(sanitize_log("Invoking Analyze Agent..."))
        analyze_payload = {
            'incident_id': incident_id,
            'instance_id': instance_id,
            'server_name': server_name
        }
        analyze_result = invoke_agentcore_agent(ANALYZE_AGENT_ARN, analyze_payload)
        if not analyze_result['success']:
            return {'statusCode': 500, 'body': json.dumps({'error': 'Analyze agent failed', 'details': analyze_result})}
        print(f"Analyze result: {analyze_result}")
        
        # Step 2: Validation Agent
        print("Invoking Validation Agent...")
        validation_payload = {
            'incident_id': incident_id,
            'instance_id': instance_id,
            'server_ip': server_ip,
            'analysis_result': analyze_result.get('result', '')
        }
        validation_result = invoke_agentcore_agent(VALIDATION_AGENT_ARN, validation_payload)
        if not validation_result['success']:
            return {'statusCode': 500, 'body': json.dumps({'error': 'Validation agent failed', 'details': validation_result})}
        print(f"Validation result: {validation_result}")
        
        # Check if issue persists
        validation_text = str(validation_result.get('result', '')).lower()
        print(f"Validation text check: persists={('persists' in validation_text)}, stopped={('stopped' in validation_text)}")
        if 'persists' in validation_text or 'stopped' in validation_text or len(validation_text) == 0:
            # Step 3: SOP Agent
            print("Invoking SOP Agent...")
            sop_payload = {
                'incident_id': incident_id,
                'instance_id': instance_id,
                'analysis_result': analyze_result.get('result', ''),
                'validation_result': validation_result.get('result', '')
            }
            sop_result = invoke_agentcore_agent(SOP_AGENT_ARN, sop_payload)
            if not sop_result['success']:
                return {'statusCode': 500, 'body': json.dumps({'error': 'SOP agent failed', 'details': sop_result})}
            print(f"SOP result: {sop_result}")
            
            # Step 4: Execution Agent
            print("Invoking Execution Agent...")
            execution_payload = {
                'incident_id': incident_id,
                'instance_id': instance_id,
                'server_ip': server_ip,
                'sop_result': sop_result.get('result', '')
            }
            execution_result = invoke_agentcore_agent(EXECUTION_AGENT_ARN, execution_payload)
            if not execution_result['success']:
                return {'statusCode': 500, 'body': json.dumps({'error': 'Execution agent failed', 'details': execution_result})}
            print(f"Execution result: {execution_result}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'incident_id': incident_id,
                    'status': 'remediated',
                    'instance_id': instance_id
                })
            }
        else:
            print("Issue already resolved")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'incident_id': incident_id,
                    'status': 'resolved',
                    'instance_id': instance_id
                })
            }
    
    except Exception as e:
        print(f"Error processing incident: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
