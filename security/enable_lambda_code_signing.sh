#!/bin/bash
set -e

FUNCTION_NAME="incident-orchestrator"
PROFILE_NAME="incident_lambda_signing_profile"
REGION="us-east-1"

echo "=== Enabling Lambda Code Signing ==="

# Create signing profile
echo "Creating signing profile..."
PROFILE_ARN=$(aws signer put-signing-profile \
  --profile-name $PROFILE_NAME \
  --platform-id AWSLambda-SHA384-ECDSA \
  --region $REGION \
  --query 'arn' --output text)

echo "Signing Profile ARN: $PROFILE_ARN"

# Create code signing config
echo "Creating code signing configuration..."
CONFIG_ARN=$(aws lambda create-code-signing-config \
  --allowed-publishers SigningProfileVersionArns=$PROFILE_ARN \
  --code-signing-policies UntrustedArtifactOnDeployment=Enforce \
  --region $REGION \
  --query 'CodeSigningConfig.CodeSigningConfigArn' --output text 2>/dev/null || \
  aws lambda list-code-signing-configs --region $REGION --query "CodeSigningConfigs[?AllowedPublishers.SigningProfileVersionArns[0]=='$PROFILE_ARN'].CodeSigningConfigArn" --output text)

echo "Code Signing Config ARN: $CONFIG_ARN"

# Update Lambda function with code signing config
echo "Attaching code signing config to Lambda function..."
aws lambda update-function-code-signing-config \
  --function-name $FUNCTION_NAME \
  --code-signing-config-arn $CONFIG_ARN \
  --region $REGION

echo "✓ Lambda code signing enabled successfully"
