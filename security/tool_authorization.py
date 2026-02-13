"""Tool authorization checks for agent operations"""

ALLOWED_EC2_OPERATIONS = ['start', 'stop', 'reboot', 'describe']
PROTECTED_INSTANCES = []  # Add critical instance IDs here

class AuthorizationError(Exception):
    pass

def authorize_ec2_operation(operation: str, instance_id: str) -> None:
    """Verify EC2 operation is authorized"""
    if operation not in ALLOWED_EC2_OPERATIONS:
        raise AuthorizationError(f"Operation '{operation}' not allowed")
    
    if instance_id in PROTECTED_INSTANCES:
        raise AuthorizationError(f"Instance {instance_id} is protected from {operation}")
