#!/bin/bash
set -e

echo "=== Building Lambda Security Layer ==="

cd "$(dirname "$0")/.."

# Create layer directory
mkdir -p lambda/layer/python
rm -rf lambda/layer/python/*

# Copy security modules
echo "Copying security modules..."
cp security/prompt_injection_detector.py lambda/layer/python/
cp security/log_sanitizer.py lambda/layer/python/
cp security/pii_detector.py lambda/layer/python/

# Create layer package
echo "Creating layer package..."
cd lambda/layer
zip -r ../security-layer.zip python/
cd ../..

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Publish layer
echo "Publishing Lambda layer..."
LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name incident-security-modules \
  --description "Security modules: prompt injection detection, log sanitization, PII detection" \
  --zip-file fileb://lambda/security-layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region us-east-1 \
  --query 'LayerVersionArn' --output text)

echo "Layer ARN: $LAYER_ARN"

# Update Lambda function
echo "Attaching layer to Lambda function..."
aws lambda update-function-configuration \
  --function-name incident-orchestrator \
  --layers $LAYER_ARN \
  --region us-east-1

echo "✓ Lambda security layer deployed successfully"
echo ""
echo "Security modules included:"
echo "  - Prompt injection detection"
echo "  - Log sanitization"
echo "  - PII detection and redaction"
