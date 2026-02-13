"""Gateway-enabled tools for ServiceNow via MCP with Cognito OAuth"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from strands import tool

GATEWAY_URL = "https://<YOUR-GATEWAY-ID>.gateway.bedrock-agentcore.<REGION>.amazonaws.com/mcp"
CLIENT_ID = "<YOUR-CLIENT-ID>"
CLIENT_SECRET = "<YOUR-CLIENT-SECRET>"
TOKEN_ENDPOINT = "https://<YOUR-COGNITO-DOMAIN>.auth.<REGION>.amazoncognito.com/oauth2/token"
SCOPE = "<YOUR-GATEWAY-NAME>/invoke"

class TokenManager:
    def __init__(self):
        self._token = None
        self._expires_at = None
    
    def get_token(self):
        if self._token and self._expires_at and self._expires_at > datetime.now():
            return self._token
        
        response = requests.post(
            TOKEN_ENDPOINT,
            data={
                'grant_type': 'client_credentials',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'scope': SCOPE
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        data = response.json()
        self._token = data['access_token']
        expires_in = data.get('expires_in', 3600) - 300
        self._expires_at = datetime.now() + timedelta(seconds=expires_in)
        return self._token

token_manager = TokenManager()

def call_gateway_tool(tool_name, arguments):
    token = token_manager.get_token()
    
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments
        }
    }
    
    response = requests.post(
        GATEWAY_URL,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json=payload,
        timeout=30
    )
    
    result = response.json()
    if 'error' in result:
        raise Exception(f"Gateway error: {result['error']}")
    
    # Parse MCP response format
    if 'result' in result and 'content' in result['result']:
        import json
        text_content = result['result']['content'][0]['text']
        return json.loads(text_content)
    
    return result.get('result')

@tool
def update_incident_gateway(incident_id: str, notes: str, status: str = None) -> Dict[str, Any]:
    """Update ServiceNow incident via Gateway MCP"""
    try:
        # Get sys_id
        incidents = call_gateway_tool('servicenow-api___getIncidents', {
            'sysparm_query': f'number={incident_id}',
            'sysparm_fields': 'sys_id'
        })
        
        if incidents and 'result' in incidents and incidents['result']:
            sys_id = incidents['result'][0]['sys_id']
            
            # Update incident
            update_data = {'work_notes': notes}
            if status:
                update_data['state'] = status
            
            result = call_gateway_tool('servicenow-api___updateIncident', {
                'sys_id': sys_id,
                **update_data
            })
            
            return {'incident_id': incident_id, 'updated': True, 'notes': notes}
        
        return {'incident_id': incident_id, 'updated': False, 'error': 'Incident not found'}
    except Exception as e:
        return {'incident_id': incident_id, 'updated': False, 'error': str(e)}

@tool
def close_incident_gateway(incident_id: str, resolution_notes: str, resolution_code: str = "Solution provided") -> Dict[str, Any]:
    """Close ServiceNow incident via Gateway MCP"""
    try:
        # Get sys_id
        incidents = call_gateway_tool('servicenow-api___getIncidents', {
            'sysparm_query': f'number={incident_id}',
            'sysparm_fields': 'sys_id'
        })
        
        if incidents and 'result' in incidents and incidents['result']:
            sys_id = incidents['result'][0]['sys_id']
            
            # Close incident
            result = call_gateway_tool('servicenow-api___updateIncident', {
                'sys_id': sys_id,
                'state': '7',
                'close_notes': resolution_notes,
                'close_code': resolution_code
            })
            
            return {'incident_id': incident_id, 'status': 'closed', 'resolution': resolution_notes}
        
        return {'incident_id': incident_id, 'status': 'failed', 'error': 'Incident not found'}
    except Exception as e:
        return {'incident_id': incident_id, 'status': 'error', 'error': str(e)}
