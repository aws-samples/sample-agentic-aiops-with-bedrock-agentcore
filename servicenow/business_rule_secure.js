(function executeRule(current, previous) {
    try {
        var shortDesc = current.short_description.toString();
        var serverName = '';
        var serverIP = '';
        
        // Extract server name from description
        var match = shortDesc.match(/SSH Connection Failure:\s*(.+)/);
        if (match && match[1]) serverName = match[1].trim();
        if (current.u_server_ip) serverIP = current.u_server_ip.toString();
        
        // Build payload
        var payload = {
            incident_id: current.number.toString(),
            description: shortDesc,
            priority: current.priority.toString(),
            reported_by: current.sys_created_by.toString(),
            server_name: serverName,
            server_ip: serverIP
        };
        
        // API Gateway endpoint
        var endpoint = 'https://<YOUR-API-GATEWAY-ID>.execute-api.<REGION>.amazonaws.com/prod/incident';
        
        // SECURITY: API Key authentication
        var apiKey = '<API Key of API Gateway>';
        
        var request = new sn_ws.RESTMessageV2();
        request.setEndpoint(endpoint);
        request.setHttpMethod('POST');
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('x-api-key', apiKey); // API key authentication
        request.setRequestBody(JSON.stringify(payload));
        
        var response = request.execute();
        var statusCode = response.getStatusCode();
        
        gs.info('AgentCore Trigger - Incident: ' + current.number + 
                ', Status: ' + statusCode + 
                ', Server: ' + serverName);
        
        if (statusCode == 200 || statusCode == 202) {
            current.work_notes = 'Automated incident processing initiated via AgentCore agents.';
            current.update();
        } else {
            gs.error('AgentCore Trigger Failed - Status: ' + statusCode + 
                    ', Response: ' + response.getBody());
        }
        
    } catch (e) {
        gs.error('AgentCore Trigger Error: ' + e.message + ' | Stack: ' + e.stack);
    }
})(current, previous);
