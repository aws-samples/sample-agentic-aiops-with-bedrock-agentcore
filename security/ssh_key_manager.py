"""SSH key management via AWS Secrets Manager"""
import boto3
import tempfile
import os
from botocore.config import Config

class SSHKeyManager:
    _shared_client = None
    
    def __init__(self, secret_name: str, region: str = 'us-east-1'):
        self.secret_name = secret_name
        if SSHKeyManager._shared_client is None:
            config = Config(retries={'max_attempts': 3, 'mode': 'standard'})
            SSHKeyManager._shared_client = boto3.client('secretsmanager', region_name=region, config=config)
        self.client = SSHKeyManager._shared_client
    
    def get_key_file(self) -> str:
        """Retrieve SSH key from Secrets Manager and write to temp file"""
        response = self.client.get_secret_value(SecretId=self.secret_name)
        key_content = response['SecretString']
        
        # Create temp file with secure permissions
        fd, path = tempfile.mkstemp(suffix='.pem')
        os.chmod(path, 0o400)
        
        with os.fdopen(fd, 'w') as f:
            f.write(key_content)
        
        return path
    
    def cleanup_key_file(self, path: str) -> None:
        """Securely delete temp key file"""
        if os.path.exists(path):
            os.remove(path)
