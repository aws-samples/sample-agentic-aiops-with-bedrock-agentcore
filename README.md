# Incident Management Multi-Agent System using Bedrock AgentCore

An autonomous incident management system that analyzes, validates, and resolves infrastructure incidents using Agentic AI. Built with Strands multi-agent framework deployed on AWS Bedrock AgentCore, featuring ServiceNow integration, EC2 monitoring, and secure credential management via AgentCore Gateway.

---

## ⚠️ IMPORTANT: Educational and Reference Implementation

**This project is designed to help you understand multi-agent architecture patterns for automating incident management systems.** It demonstrates how to orchestrate multiple AI agents using AWS Bedrock AgentCore to handle real-world infrastructure incidents.

**Before deploying to production:**
- This is a reference implementation for learning and proof-of-concept purposes
- Production deployments require careful planning and customization for your specific environment
- **Work with your AWS Solutions Architect or Account Team** to:
  - Review security requirements and compliance needs
  - Design appropriate guardrails and approval workflows
  - Plan scalability, monitoring, and incident response procedures
  - Validate integration points with your existing systems
  - Establish testing and rollback strategies
- **Work with your APPSEC team for security clearance before deploying to PROD**

**Use this project to:**
- Understand multi-agent coordination patterns
- Learn AgentCore Gateway integration with external systems
- Explore autonomous remediation workflows
- Build your own customized incident management solution

---

## Table of Contents

### Overview
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Agents](#agents)

### Deployment
- [Incident Management Multi-Agent System using Bedrock AgentCore](#incident-management-multi-agent-system-using-bedrock-agentcore)
  - [⚠️ IMPORTANT: Educational and Reference Implementation](#️-important-educational-and-reference-implementation)
  - [Table of Contents](#table-of-contents)
    - [Overview](#overview)
    - [Deployment](#deployment)
    - [Testing \& Validation](#testing--validation)
    - [Resources \& Configuration](#resources--configuration)
    - [Troubleshooting \& Maintenance](#troubleshooting--maintenance)
    - [Additional Information](#additional-information)
  - [Architecture](#architecture)
    - [System Flow](#system-flow)
    - [Technical Architecture](#technical-architecture)
    - [Component Details](#component-details)
  - [Project Structure](#project-structure)
  - [Agents](#agents)
- [Deployment Guide](#deployment-guide)
  - [Prerequisites](#prerequisites)
  - [Step 1: Install Dependencies](#step-1-install-dependencies)
  - [Step 2: Setup ServiceNow Service Account](#step-2-setup-servicenow-service-account)
    - [2.1 Create Dedicated Service Account](#21-create-dedicated-service-account)
    - [2.2 Add Custom Fields](#22-add-custom-fields)
    - [2.3 Store Credentials in Secrets Manager](#23-store-credentials-in-secrets-manager)
  - [Step 3: Setup SSH Monitoring Service](#step-3-setup-ssh-monitoring-service)
    - [3.1 Configure Servers](#31-configure-servers)
    - [3.2 Update ServiceNow URL](#32-update-servicenow-url)
    - [3.3 Migrate SSH Keys to Secrets Manager](#33-migrate-ssh-keys-to-secrets-manager)
    - [3.4 Start Monitoring Service](#34-start-monitoring-service)
  - [Step 4: Setup AgentCore Gateway](#step-4-setup-agentcore-gateway)
    - [4.1 Create ServiceNow OpenAPI Specification](#41-create-servicenow-openapi-specification)
    - [4.2 Create MCP Gateway](#42-create-mcp-gateway)
    - [4.3 Add Gateway Target with Basic Auth](#43-add-gateway-target-with-basic-auth)
  - [Step 5: Deploy AgentCore Agents](#step-5-deploy-agentcore-agents)
    - [5.1 Configure Environment Variables](#51-configure-environment-variables)
    - [5.2 Deploy Agents](#52-deploy-agents)
  - [Step 6: Deploy Lambda Orchestrator](#step-6-deploy-lambda-orchestrator)
    - [6.1 Create Lambda Package](#61-create-lambda-package)
    - [6.2 Create IAM Role](#62-create-iam-role)
    - [6.3 Create Lambda Function](#63-create-lambda-function)
    - [6.4 Deploy Security Modules](#64-deploy-security-modules)
    - [6.5 Enable Lambda Code Signing](#65-enable-lambda-code-signing)
  - [Step 7: Create API Gateway](#step-7-create-api-gateway)
  - [Step 8: Create ServiceNow Business Rule](#step-8-create-servicenow-business-rule)
    - [8.1 Create Business Rule with API Key Authentication](#81-create-business-rule-with-api-key-authentication)
- [Testing](#testing)
  - [Test End-to-End](#test-end-to-end)
    - [Without API Key (Should Fail)](#without-api-key-should-fail)
    - [With API Key (Should Succeed)](#with-api-key-should-succeed)
    - [Test PII Detection](#test-pii-detection)
  - [Monitor Logs](#monitor-logs)
- [IAM Roles and Permissions](#iam-roles-and-permissions)
  - [EC2 Monitoring Instance Role](#ec2-monitoring-instance-role)
  - [Lambda Orchestrator Role](#lambda-orchestrator-role)
  - [AgentCore Gateway Role](#agentcore-gateway-role)
  - [AgentCore Agent Execution Roles](#agentcore-agent-execution-roles)
    - [Analyze Agent Permissions](#analyze-agent-permissions)
    - [Validation Agent Permissions](#validation-agent-permissions)
    - [SOP Agent Permissions](#sop-agent-permissions)
    - [SOP Execution Agent Permissions](#sop-execution-agent-permissions)
  - [API Gateway Execution Role](#api-gateway-execution-role)
  - [Security Best Practices Applied](#security-best-practices-applied)
  - [IAM Policy Validation](#iam-policy-validation)
- [Troubleshooting](#troubleshooting)
  - [Gateway Issues](#gateway-issues)
  - [Agent Issues](#agent-issues)
  - [Lambda Issues](#lambda-issues)
- [Maintenance](#maintenance)
  - [Update Agent Code](#update-agent-code)
  - [Rotate ServiceNow Credentials](#rotate-servicenow-credentials)
- [Security Features](#security-features)
  - [Authentication \& Authorization](#authentication--authorization)
  - [Secrets Management](#secrets-management)
  - [Input Validation \& Logging](#input-validation--logging)
  - [Supply Chain \& Code Integrity](#supply-chain--code-integrity)
  - [Monitoring \& Compliance](#monitoring--compliance)
- [Cost Estimate](#cost-estimate)

### Testing & Validation
- [Testing](#testing)
  - [Test End-to-End](#test-end-to-end)
  - [Monitor Logs](#monitor-logs)

### Resources & Configuration
- [IAM Roles and Permissions](#iam-roles-and-permissions)
  - [EC2 Monitoring Instance Role](#ec2-monitoring-instance-role)
  - [Lambda Orchestrator Role](#lambda-orchestrator-role)
  - [AgentCore Gateway Role](#agentcore-gateway-role)
  - [AgentCore Agent Execution Roles](#agentcore-agent-execution-roles)
  - [API Gateway Execution Role](#api-gateway-execution-role)

### Troubleshooting & Maintenance
- [Troubleshooting](#troubleshooting)
  - [Gateway Issues](#gateway-issues)
  - [Agent Issues](#agent-issues)
  - [Lambda Issues](#lambda-issues)
- [Maintenance](#maintenance)
  - [Update Agent Code](#update-agent-code)
  - [Rotate ServiceNow Credentials](#rotate-servicenow-credentials)

### Additional Information
- [Security Features](#security-features)
  - [Authentication & Authorization](#authentication--authorization)
  - [Secrets Management](#secrets-management)
  - [Input Validation & Logging](#input-validation--logging)
  - [Supply Chain & Code Integrity](#supply-chain--code-integrity)
  - [Monitoring & Compliance](#monitoring--compliance)
- [Cost Estimate](#cost-estimate)

---

## Architecture

### System Flow
![System Flow](images/System%20Flow.png)

### Technical Architecture
![Technical Architecture](images/Technical%20Architecture.png)

### Component Details

**Monitoring Layer:**
- **SSH Monitor Service**: Checks server connectivity every 30 seconds
- **ServiceNow**: Incident management system

**Orchestration Layer:**
- **API Gateway**: Receives incident webhooks from ServiceNow
- **Lambda Orchestrator**: Coordinates multi-agent workflow (180s timeout)

**Agent Layer:**
1. **Analyze Agent**: Investigates EC2 instance status
2. **Validation Agent**: Validates SSH connectivity issues
3. **SOP Agent**: Retrieves remediation procedures from Bedrock KB
4. **SOP Execution Agent**: Executes remediation and verifies resolution

**Integration Layer:**
- **AgentCore Gateway**: Secure MCP gateway with OAuth + credential management
- **AWS Services**: EC2, SSM, Bedrock Knowledge Base

## Project Structure

```
Incident-Management-Multi-Agent-System-using-Bedrock-Agentcore/
├── agentcore_agents/              # AgentCore deployed agents
│   ├── analyze_agent/
│   ├── validation_agent/
│   ├── sop_agent/
│   ├── sop_execution_agent/
│   └── .env.template
├── lambda/                        # Lambda orchestrator
│   ├── lambda_orchestrator.py     # With prompt injection detection & log sanitization
│   └── requirements.txt
├── servicenow/                    # ServiceNow integration
│   └── business_rule_secure.js    # With API key authentication
├── server_monitoring/             # SSH monitoring service
│   ├── server-monitoring-agentcore-demo.py    # Main monitoring script
│   ├── server-monitoring-agentcore-demo.sh    # Service management
│   ├── server-monitoring-agentcore-demo.service # Systemd service
│   ├── servers.json               # Server list configuration
│   └── requirements.txt           # Pinned dependencies with SHA256 hashes
├── security/                      # Security hardening modules
│   ├── build_lambda_security_layer.sh         # Lambda layer deployment script
│   ├── enable_lambda_code_signing.sh          # Code signing setup script
│   ├── iam-monitoring-policy.json             # IAM policy for monitoring service
│   ├── log_sanitizer.py                       # Log sanitization module
│   ├── pii_detector.py                        # PII detection and redaction module
│   ├── prompt_injection_detector.py           # Prompt injection detection
│   ├── ssh_key_manager.py                     # SSH key from Secrets Manager
│   └── tool_authorization.py                  # EC2 operation authorization
├── images/
│   ├── System Flow.png
│   └── Technical Architecture.png
├── README.md                      # Main deployment guide
└── THREAT_MODEL.md                # Complete threat analysis
```

## Agents

| Agent | Tools | Role |
|-------|-------|------|
| **Analyze Agent** | update_incident_gateway, get_ec2_status | Investigates incidents and EC2 status |
| **Validation Agent** | check_ssh_connectivity, get_ec2_status, update_incident_gateway, close_incident_gateway | Validates if issues persist |
| **SOP Agent** | query_bedrock_knowledgebase, update_incident_gateway | Retrieves SOPs from Bedrock KB and MUST update incident with full SOP |
| **SOP Execution Agent** | start/stop/reboot_ec2_instance, wait_for_instance_running, check_ssh_connectivity, update_incident_gateway, close_incident_gateway | Executes NON-DESTRUCTIVE remediation (start only). DESTRUCTIVE operations (stop/reboot) escalate to human support. Verifies SSH connectivity with exponential backoff (10s, 20s, 30s...). Skips system_status checks (take 2-5 min). MUST log execution start and include complete summary in close notes |

---

# Deployment Guide

## Prerequisites

- AWS CLI configured with credentials
- Python 3.11+
- Strands Agents SDK: `pip install strands-agents`
- AgentCore CLI: `pip install bedrock-agentcore-starter-toolkit`
- ServiceNow instance with admin access
- IAM permissions for: EC2, Lambda, API Gateway, Bedrock, AgentCore, Secrets Manager, SSM
- EC2 instance with IAM role for SSH monitoring service

---

## Step 1: Install Dependencies

```bash
cd server_monitoring
pip install -r requirements.txt
```

---

## Step 2: Setup ServiceNow Service Account

**⚠️ CRITICAL**: Complete this step FIRST before proceeding. ServiceNow credentials are required for Steps 3, 4, and 8.

### 2.1 Create Dedicated Service Account

**⚠️ IMPORTANT**: Do NOT use admin account for API access. Create a dedicated service account with minimal permissions.

1. Navigate to: **User Administration > Users > New**
2. Create user:
   - **User ID**: `agentcore_service`
   - **First name**: `AgentCore`
   - **Last name**: `Service`
   - **Email**: `agentcore@yourdomain.com`
   - **Active**: ✓
   - **Web service access only**: ✓
   - **Password**: Set strong password

3. Create custom role:
   - Navigate to: **User Administration > Roles > New**
   - **Name**: `x_incident_api_user`
   - **Description**: `API access for incident read/write/update only`
   - Add role: `itil` (for incident table access)

4. Assign role to service account:
   - Open user `agentcore_service`
   - Add role: `x_incident_api_user`

### 2.2 Add Custom Fields

1. Navigate to: **System Definition > Tables > Incident**
2. Add fields:
   - **u_server_name** (String, 100)
   - **u_server_ip** (String, 50)

### 2.3 Store Credentials in Secrets Manager

```bash
aws secretsmanager create-secret \
  --name incident-management/servicenow-credentials \
  --description "ServiceNow service account (non-admin)" \
  --secret-string '{"username":"agentcore_service","password":"YOUR_PASSWORD","instance":"YOUR_INSTANCE.service-now.com"}' \
  --region us-east-1
```

**Note**: Replace `YOUR_PASSWORD` with the password you set, and `YOUR_INSTANCE` with your ServiceNow instance name.

---

## Step 3: Setup SSH Monitoring Service

### 3.1 Configure Servers

> **🖥️ Server Configuration Required:** Update `server_monitoring/servers.json` with your actual server names and IP addresses. The file currently contains placeholder values.

Edit `server_monitoring/servers.json`:

```json
[
  {
    "name": "server-1",
    "ip": "<SERVER_1_IP_OR_HOSTNAME>"
  },
  {
    "name": "server-2",
    "ip": "<SERVER_2_IP_OR_HOSTNAME>"
  }
]
```

### 3.2 Update ServiceNow URL

Edit `server_monitoring/server-monitoring-agentcore-demo.py`:

```python
SERVICENOW_URL = "https://<YOUR_INSTANCE>.service-now.com/api/now/table/incident"
SERVICENOW_CREDENTIALS_SECRET = "incident-management/servicenow-credentials"
```

**Note**: ServiceNow credentials are automatically retrieved from Secrets Manager (configured in Step 2.3).

### 3.3 Migrate SSH Keys to Secrets Manager

```bash
# Store SSH private key in Secrets Manager
aws secretsmanager create-secret \
  --name incident-management/ssh-key \
  --description "SSH private key for server monitoring" \
  --secret-string file://~/.ssh/id_rsa \
  --region us-east-1

# Attach IAM policy to EC2 instance role
INSTANCE_ROLE=$(aws ec2 describe-instances \
  --instance-ids $(ec2-metadata --instance-id | cut -d' ' -f2) \
  --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' \
  --output text | cut -d'/' -f2)

aws iam put-role-policy \
  --role-name $INSTANCE_ROLE \
  --policy-name SecretsManagerAccess \
  --policy-document file://security/iam-monitoring-policy.json
```

### 3.4 Start Monitoring Service

```bash
cd server_monitoring
bash server-monitoring-agentcore-demo.sh start
bash server-monitoring-agentcore-demo.sh status
```

**Service Commands:**
- `start` - Install and start the service
- `stop` - Stop the service
- `restart` - Restart the service
- `status` - Check service status
- `logs` - View real-time logs

**How It Works:**
1. Retrieves SSH keys and ServiceNow credentials from Secrets Manager
2. Monitors SSH connectivity every 30 seconds
3. On SSH failure → Queries ServiceNow for existing open incidents (states 1,2,3) by server name
4. If no open incident exists → Creates ServiceNow incident with Basic Auth:
   - Short description: "SSH Connection Failure: <Server_name>"
   - u_server_name: Server name
   - u_server_ip: Server IP
5. ServiceNow business rule triggers AgentCore workflow via API Gateway
6. On recovery → Logs that existing incident will be auto-closed
7. Duplicate prevention persists across service restarts (queries ServiceNow, not in-memory)

---

## Step 4: Setup AgentCore Gateway

### 4.1 Create ServiceNow OpenAPI Specification

```bash
cat > servicenow-openapi.json << 'EOF'
{
  "openapi": "3.0.0",
  "info": {"title": "ServiceNow Incident API", "version": "1.0.0"},
  "servers": [{"url": "https://<YOUR_INSTANCE>.service-now.com/api/now"}],
  "paths": {
    "/table/incident": {
      "get": {
        "operationId": "getIncidents",
        "parameters": [
          {"name": "sysparm_query", "in": "query", "schema": {"type": "string"}},
          {"name": "sysparm_fields", "in": "query", "schema": {"type": "string"}}
        ],
        "responses": {"200": {"description": "Success"}}
      }
    },
    "/table/incident/{sys_id}": {
      "patch": {
        "operationId": "updateIncident",
        "parameters": [{"name": "sys_id", "in": "path", "required": true, "schema": {"type": "string"}}],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "work_notes": {"type": "string"},
                  "state": {"type": "string"},
                  "close_notes": {"type": "string"},
                  "close_code": {"type": "string"}
                }
              }
            }
          }
        },
        "responses": {"200": {"description": "Success"}}
      }
    }
  }
}
EOF

# Upload to S3
aws s3 mb s3://agentcore-incident-management-<YOUR_ACCOUNT_ID> --region us-east-1
aws s3 cp servicenow-openapi.json s3://agentcore-incident-management-<YOUR_ACCOUNT_ID>/
```

### 4.2 Create MCP Gateway

> **🔧 Configuration Required:** After creating the gateway, you must update the Gateway URL and Cognito OAuth endpoints in all `agentcore_agents/*/gateway_tools.py` files. Replace the placeholder values:
> - `<YOUR-GATEWAY-ID>` with your actual Gateway ID
> - `<YOUR-COGNITO-DOMAIN>` with your Cognito domain
> - `<YOUR-CLIENT-ID>` and `<YOUR-CLIENT-SECRET>` with OAuth credentials
> - `<YOUR-GATEWAY-NAME>` with your gateway name (e.g., `servicenow-gateway`)

```bash
agentcore gateway create-mcp-gateway \
  --name servicenow-gateway \
  --region us-east-1 \
  --enable_semantic_search

# Note the Gateway ARN, URL, and Role ARN from output
# Gateway URL format: https://<gateway-id>.gateway.bedrock-agentcore.<region>.amazonaws.com/mcp
```

### 4.3 Add Gateway Target with Basic Auth

```bash
# Generate Basic Auth token from Secrets Manager
python3 << 'EOF'
import base64, json, boto3
client = boto3.client('secretsmanager', region_name='us-east-1')
response = client.get_secret_value(SecretId='incident-management/servicenow-credentials')
creds = json.loads(response['SecretString'])
basic_auth = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
print(f"Basic {basic_auth}")
EOF

# Create gateway target with Basic Authentication
agentcore gateway create-mcp-gateway-target \
  --gateway-arn <GATEWAY_ARN> \
  --gateway-url <GATEWAY_URL> \
  --role-arn <ROLE_ARN> \
  --name servicenow-api \
  --target-type openApiSchema \
  --region us-east-1 \
  --target-payload '{"s3": {"uri": "s3://agentcore-incident-management-<YOUR_ACCOUNT_ID>/servicenow-openapi.json"}}' \
  --credentials '{"api_key": "Basic <BASE64_TOKEN>", "credential_location": "HEADER", "credential_parameter_name": "Authorization"}'
```

---

## Step 5: Deploy AgentCore Agents

### 5.1 Configure Environment Variables

> **📝 Configuration Required:** This is an external distribution version. Create `.env` files from the provided `.env.template` in each agent directory. Update with your AWS resources (Bedrock model ID, Knowledge Base ID, region).

Create `.env` file in each agent directory:

```bash
# agentcore_agents/analyze_agent/.env
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_KB_ID=<YOUR-KNOWLEDGE-BASE-ID>
SOP_RETRY_TIMEOUT_SECONDS=120
EXPONENTIAL_BACKOFF_BASE=2
INITIAL_WAIT_SECONDS=5
AWS_REGION=us-east-1
```

Copy to all agents:
```bash
for agent in validation_agent sop_agent sop_execution_agent; do
  cp agentcore_agents/analyze_agent/.env agentcore_agents/$agent/.env
done
```

### 5.2 Deploy Agents

```bash
cd agentcore_agents/analyze_agent && agentcore deploy
cd ../validation_agent && agentcore deploy
cd ../sop_agent && agentcore deploy
cd ../sop_execution_agent && agentcore deploy
```

**Note the ARNs** from deployment output.

**Security Features Enabled:**
- ✅ **Log Sanitization**: Automatically redacts IP addresses, passwords, API keys, AWS credentials, Base64 credentials
- ✅ **Prompt Injection Protection**: 20+ detection patterns, destructive keyword blocking, input sanitization (2000 char limit)

---

## Step 6: Deploy Lambda Orchestrator

**⚠️ IMPORTANT**: Agent ARNs must NOT include `/DEFAULT` suffix. Use format:
`arn:aws:bedrock-agentcore:REGION:ACCOUNT:runtime/AGENT_NAME-ID`

### 6.1 Create Lambda Package

> **🔨 Build Required:** Build the Lambda deployment package from source using the commands below.

```bash
cd lambda
mkdir -p package
pip install boto3 -t package/
cp lambda_orchestrator.py package/lambda_function.py
cd package && zip -r ../lambda_deployment.zip . && cd ..
```

### 6.2 Create IAM Role

```bash
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:SourceAccount": "<YOUR_ACCOUNT_ID>"
      }
    }
  }]
}
EOF

aws iam create-role \
  --role-name incident-orchestrator-role \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy \
  --role-name incident-orchestrator-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > agentcore-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock-agentcore:InvokeAgentRuntime", "bedrock-agentcore:GetAgentRuntime"],
    "Resource": "arn:aws:bedrock-agentcore:us-east-1:<YOUR_ACCOUNT_ID>:runtime/*"
  }]
}
EOF

aws iam create-policy --policy-name AgentCoreInvokePolicy --policy-document file://agentcore-policy.json
aws iam attach-role-policy --role-name incident-orchestrator-role --policy-arn arn:aws:iam::<YOUR_ACCOUNT_ID>:policy/AgentCoreInvokePolicy
```

### 6.3 Create Lambda Function

```bash
# Get agent ARNs from deployment configs
ANALYZE_ARN=$(grep 'agent_arn:' agentcore_agents/analyze_agent/.bedrock_agentcore.yaml | awk '{print $2}')
VALIDATION_ARN=$(grep 'agent_arn:' agentcore_agents/validation_agent/.bedrock_agentcore.yaml | awk '{print $2}')
SOP_ARN=$(grep 'agent_arn:' agentcore_agents/sop_agent/.bedrock_agentcore.yaml | awk '{print $2}')
EXECUTION_ARN=$(grep 'agent_arn:' agentcore_agents/sop_execution_agent/.bedrock_agentcore.yaml | awk '{print $2}')

aws lambda create-function \
  --function-name incident-orchestrator \
  --runtime python3.11 \
  --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/incident-orchestrator-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 180 \
  --environment Variables="{ANALYZE_AGENT_ARN=$ANALYZE_ARN,VALIDATION_AGENT_ARN=$VALIDATION_ARN,SOP_AGENT_ARN=$SOP_ARN,EXECUTION_AGENT_ARN=$EXECUTION_ARN}"
```

**Note:** Lambda code uses `EXECUTION_AGENT_ARN` environment variable name.

### 6.4 Deploy Security Modules

**Deploy Lambda security layer with PII detection, prompt injection detection, and log sanitization:**

```bash
cd security
./build_lambda_security_layer.sh
```

**Security modules include:**
- **Prompt injection detection** - Blocks malicious inputs (20+ patterns)
- **Log sanitization** - Redacts credentials, IPs, API keys, passwords from logs
- **PII detection and redaction** - Auto-redacts emails, SSN, phone numbers, credit cards, IP addresses, AWS keys, names

### 6.5 Enable Lambda Code Signing

**Enforce code integrity and prevent unsigned code deployment:**

```bash
cd security
./enable_lambda_code_signing.sh
```

**Benefits:**
- Prevents deployment of unsigned/tampered code
- Ensures code integrity
- Compliance requirement for SOC 2, HIPAA

**Verification:**
```bash
# Check code signing enabled
aws lambda get-function-code-signing-config \
  --function-name incident-orchestrator \
  --region us-east-1
```

---

## Step 7: Create API Gateway

```bash
API_ID=$(aws apigateway create-rest-api --name incident-api --query 'id' --output text)
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text)
RESOURCE_ID=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part incident --query 'id' --output text)

aws apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --authorization-type NONE

LAMBDA_ARN=$(aws lambda get-function --function-name incident-orchestrator --query 'Configuration.FunctionArn' --output text)

aws apigateway put-integration \
  --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --type AWS --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
  --request-parameters '{"integration.request.header.X-Amz-Invocation-Type":"'\''Event'\''"}' 

aws apigateway put-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code 200
aws apigateway put-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code 200 --selection-pattern ""
aws apigateway create-deployment --rest-api-id $API_ID --stage-name prod

aws lambda add-permission --function-name incident-orchestrator --statement-id apigateway-invoke \
  --action lambda:InvokeFunction --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:<YOUR_ACCOUNT_ID>:$API_ID/*/*"

# Configure API Key and Rate Limiting
API_KEY_ID=$(aws apigateway create-api-key --name incident-api-key --enabled --query 'id' --output text)
API_KEY=$(aws apigateway get-api-key --api-key $API_KEY_ID --include-value --query 'value' --output text)

USAGE_PLAN_ID=$(aws apigateway create-usage-plan \
  --name incident-usage-plan \
  --throttle rateLimit=100,burstLimit=200 \
  --quota limit=10000,period=DAY \
  --api-stages apiId=$API_ID,stage=prod \
  --query 'id' --output text)

aws apigateway create-usage-plan-key \
  --usage-plan-id $USAGE_PLAN_ID \
  --key-id $API_KEY_ID \
  --key-type API_KEY

echo "API Gateway URL: https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/incident"
echo "API Key: $API_KEY"
echo ""
echo "⚠️  IMPORTANT: Save this API key - you'll need it for ServiceNow business rule (Step 8.1)"
```

---

## Step 8: Create ServiceNow Business Rule

### 8.1 Create Business Rule with API Key Authentication

1. Navigate to: **System Definition > Business Rules > New**
2. Configure:
   - **Name**: Trigger AgentCore for SSH Incidents
   - **Table**: Incident
   - **Active**: ✓
   - **Advanced**: ✓
   - **When**: after, Insert: ✓
   - **Filter**: Short description CONTAINS "SSH Connection Failure"
3. Script (from `servicenow/business_rule_secure.js`):

```javascript
(function executeRule(current, previous) {
    try {
        var shortDesc = current.short_description.toString();
        var serverName = '';
        var serverIP = '';
        
        var match = shortDesc.match(/SSH Connection Failure:\s*(.+)/);
        if (match && match[1]) serverName = match[1].trim();
        if (current.u_server_ip) serverIP = current.u_server_ip.toString();
        
        var payload = {
            incident_id: current.number.toString(),
            description: shortDesc,
            priority: current.priority.toString(),
            reported_by: current.sys_created_by.toString(),
            server_name: serverName,
            server_ip: serverIP
        };
        
        var endpoint = 'https://<YOUR_API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/incident';
        
        // SECURITY: API Key authentication
        var apiKey = '<YOUR_API_KEY>';  // From Step 6 output
        
        var request = new sn_ws.RESTMessageV2();
        request.setEndpoint(endpoint);
        request.setHttpMethod('POST');
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('x-api-key', apiKey);  // API key authentication
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
```

---

# Testing

## Test End-to-End

### Without API Key (Should Fail)
```bash
curl -X POST https://<YOUR-API-GATEWAY-ID>.execute-api.<REGION>.amazonaws.com/prod/incident \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "TEST001"}'
# Expected: {"message":"Forbidden"}
```

### With API Key (Should Succeed)
```bash
curl -X POST https://<YOUR-API-GATEWAY-ID>.execute-api.<REGION>.amazonaws.com/prod/incident \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "incident_id": "<INCIDENT-ID>",
    "description": "SSH Connection Failure: <SERVER-NAME>",
    "priority": "High",
    "reported_by": "test_user",
    "server_name": "<SERVER-NAME>",
    "server_ip": "<SERVER-IP>"
  }'
# Expected: 200 OK
```

### Test PII Detection
```bash
curl -X POST https://YOUR_API_GATEWAY.execute-api.us-east-1.amazonaws.com/prod/incident \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "incident_id": "<INCIDENT-ID>",
    "description": "Contact john.doe@example.com at <IP-ADDRESS>",
    "server_name": "test-server",
    "server_ip": "<SERVER-IP>"
  }'

# Check CloudWatch Logs for:
# PII detected: {'email': 1, 'ip_address': 1}
# Description redacted to: "Contact [EMAIL] at [IP_ADDRESS]"
```

## Monitor Logs

```bash
# Lambda
aws logs tail /aws/lambda/incident-orchestrator --follow

# Agents
aws logs tail /aws/bedrock-agentcore/runtimes/<ANALYZE-AGENT-ID>-DEFAULT --follow
aws logs tail /aws/bedrock-agentcore/runtimes/<VALIDATION-AGENT-ID>-DEFAULT --follow
aws logs tail /aws/bedrock-agentcore/runtimes/<SOP-AGENT-ID>-DEFAULT --follow
aws logs tail /aws/bedrock-agentcore/runtimes/<SOP-EXECUTION-AGENT-ID>-DEFAULT --follow

# Gateway
aws logs tail /aws/vendedlogs/bedrock-agentcore/gateway/APPLICATION_LOGS/<YOUR-GATEWAY-NAME> --follow
```

---

# IAM Roles and Permissions

This section documents all IAM roles, policies, and permissions required for each service in the incident management solution.

## EC2 Monitoring Instance Role

**Role Name**: `<INSTANCE_ROLE>` (auto-detected from EC2 instance profile)

**Purpose**: Allows SSH monitoring service to retrieve secrets from AWS Secrets Manager

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:SourceAccount": "<ACCOUNT_ID>"
      }
    }
  }]
}
```

**Inline Policy** (`SecretsManagerAccess`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:incident-management/ssh-key-*",
        "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:incident-management/servicenow-credentials-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:ListSecrets",
      "Resource": "*"
    }
  ]
}
```

---

## Lambda Orchestrator Role

**Role Name**: `incident-orchestrator-role`

**Purpose**: Allows Lambda function to invoke AgentCore agents and write CloudWatch logs

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:SourceAccount": "<ACCOUNT_ID>"
      }
    }
  }]
}
```

**Managed Policies**:
- `arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`

**Custom Policy** (`AgentCoreInvokePolicy`):
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock-agentcore:InvokeAgentRuntime",
      "bedrock-agentcore:GetAgentRuntime"
    ],
    "Resource": "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:runtime/*"
  }]
}
```

---

## AgentCore Gateway Role

**Role Name**: Auto-generated by AgentCore (format: `AgentCoreGateway-<GATEWAY_ID>-Role`)

**Purpose**: Allows AgentCore Gateway to access ServiceNow OpenAPI spec from S3 and authenticate agents via Cognito

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:SourceAccount": "<ACCOUNT_ID>"
      }
    }
  }]
}
```

**S3 Read Access Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::agentcore-incident-management-<ACCOUNT_ID>",
      "arn:aws:s3:::agentcore-incident-management-<ACCOUNT_ID>/*"
    ]
  }]
}
```

**Cognito OAuth Access Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "cognito-idp:InitiateAuth",
      "cognito-idp:GetUser"
    ],
    "Resource": "arn:aws:cognito-idp:us-east-1:<ACCOUNT_ID>:userpool/<POOL_ID>"
  }]
}
```

---

## AgentCore Agent Execution Roles

**Role Names**: Auto-generated per agent (format: `AgentCoreRuntime-<AGENT_NAME>-<ID>-Role`)

**Purpose**: Allows agents to perform EC2 operations, query Bedrock Knowledge Base, and access Gateway

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:SourceAccount": "<ACCOUNT_ID>"
      }
    }
  }]
}
```

### Analyze Agent Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeGateway",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:gateway/servicenow-gateway-*"
    }
  ]
}
```

---

### Validation Agent Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus",
        "ssm:SendCommand",
        "ssm:GetCommandInvocation"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ssm:resourceTag/Environment": ["production", "staging"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeGateway",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:gateway/servicenow-gateway-*"
    }
  ]
}
```

---

### SOP Agent Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:us-east-1:<ACCOUNT_ID>:knowledge-base/<KB_ID>"
    },
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeGateway",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:gateway/servicenow-gateway-*"
    }
  ]
}
```

---

### SOP Execution Agent Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/AutoRemediation": "enabled"
        }
      }
    },
    {
      "Effect": "Deny",
      "Action": [
        "ec2:StopInstances",
        "ec2:RebootInstances",
        "ec2:TerminateInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:SendCommand",
        "ssm:GetCommandInvocation"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ssm:resourceTag/Environment": ["production", "staging"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeGateway",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:gateway/servicenow-gateway-*"
    }
  ]
}
```

---

## API Gateway Execution Role

**Role Name**: Auto-generated by API Gateway (format: `APIGateway-<API_ID>-Role`)

**Purpose**: Allows API Gateway to invoke Lambda orchestrator asynchronously

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "apigateway.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:SourceAccount": "<ACCOUNT_ID>"
      }
    }
  }]
}
```

**Lambda Invocation Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "lambda:InvokeFunction",
    "Resource": "arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:incident-orchestrator"
  }]
}
```

---

## Security Best Practices Applied

✅ **Least Privilege**: Each role has minimum permissions required  
✅ **Resource-Level Restrictions**: Policies scoped to specific resources (no wildcards except where required)  
✅ **Tag-Based Authorization**: EC2 operations require specific tags  
✅ **Explicit Denies**: Destructive operations explicitly denied  
✅ **Condition Keys**: SSM and EC2 actions restricted by tags  
✅ **No Hardcoded Credentials**: All authentication via IAM roles  
✅ **Secrets Manager Integration**: Credentials encrypted at rest and in transit  
✅ **CloudWatch Logging**: All actions logged for audit trail  
✅ **Service-Specific Trust Policies**: Roles can only be assumed by intended services  
✅ **Regional Restrictions**: Policies scoped to us-east-1  
✅ **Confused Deputy Protection**: All trust policies include aws:SourceAccount condition to prevent cross-account role assumption attacks  

---

## IAM Policy Validation

Validate IAM policies before deployment:

```bash
# Validate Lambda role policy
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::<ACCOUNT_ID>:role/incident-orchestrator-role \
  --action-names bedrock-agentcore:InvokeAgentRuntime \
  --resource-arns arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:runtime/analyzeagent-*

# Check for overly permissive policies
aws iam get-role-policy \
  --role-name incident-orchestrator-role \
  --policy-name AgentCoreInvokePolicy

# Audit EC2 instance role
aws iam get-role-policy \
  --role-name <INSTANCE_ROLE> \
  --policy-name SecretsManagerAccess
```

---

# Troubleshooting

## Gateway Issues

```bash
# List gateways
agentcore gateway list-mcp-gateways --region us-east-1

# Get gateway details
agentcore gateway get-mcp-gateway --name servicenow-gateway --region us-east-1

# View gateway logs
aws logs tail /aws/vendedlogs/bedrock-agentcore/gateway/APPLICATION_LOGS/<YOUR-GATEWAY-NAME>-<ID> --follow
```

## Agent Issues

```bash
# Check agent status
agentcore status

# View agent logs
aws logs tail /aws/bedrock-agentcore/runtimes/AGENT_NAME-XXXXX-DEFAULT --follow

# Redeploy agent
cd agentcore_agents/AGENT_NAME
agentcore deploy
```

## Lambda Issues

```bash
# View logs
aws logs tail /aws/lambda/incident-orchestrator --follow

# Update code
cd lambda/package
zip -r ../lambda_deployment.zip .
aws lambda update-function-code --function-name incident-orchestrator --zip-file fileb://lambda_deployment.zip
```

---

# Maintenance

## Update Agent Code

```bash
cd agentcore_agents/AGENT_NAME
# Modify agent.py or gateway_tools.py
agentcore deploy
```

## Rotate ServiceNow Credentials

```bash
# Delete old target
agentcore gateway delete-mcp-gateway-target --name servicenow-gateway --target-name servicenow-api --region us-east-1

# Generate new Basic Auth token
python3 << 'EOF'
import base64
basic_auth = base64.b64encode(b"<SERVICE_ACCOUNT_USERNAME>:<NEW_PASSWORD>").decode()
print(f"Basic {basic_auth}")
EOF

# Recreate target with new credentials
agentcore gateway create-mcp-gateway-target \
  --gateway-arn <GATEWAY_ARN> \
  --gateway-url <GATEWAY_URL> \
  --role-arn <ROLE_ARN> \
  --name servicenow-api \
  --target-type openApiSchema \
  --region us-east-1 \
  --target-payload '{"s3": {"uri": "s3://agentcore-incident-management-<YOUR_ACCOUNT_ID>/servicenow-openapi.json"}}' \
  --credentials '{"api_key": "Basic <NEW_BASE64_TOKEN>", "credential_location": "HEADER", "credential_parameter_name": "Authorization"}'
```

---
## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
