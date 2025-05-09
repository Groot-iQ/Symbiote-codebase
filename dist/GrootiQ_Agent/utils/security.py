import hashlib
import hmac
import time
import os
import base64
from typing import Dict, Optional
from cryptography.fernet import Fernet
from config.settings import settings

class SecurityManager:
    """Manages security and encryption for the agent."""
    
    def __init__(self):
        """Initialize the security manager."""
        # Ensure the encryption key is properly formatted
        if not settings.ENCRYPTION_KEY:
            # Generate a new key if none exists
            self.encryption_key = base64.urlsafe_b64encode(os.urandom(32))
        else:
            try:
                # Try to decode the existing key
                self.encryption_key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY)
                # Re-encode to ensure proper padding
                self.encryption_key = base64.urlsafe_b64encode(self.encryption_key)
            except:
                # If decoding fails, generate a new key
                self.encryption_key = base64.urlsafe_b64encode(os.urandom(32))
        
        self.cipher_suite = Fernet(self.encryption_key)
    
    def generate_token(self, data: Dict) -> str:
        """
        Generate a secure token for data verification.
        
        Args:
            data: Data to generate token for
            
        Returns:
            HMAC token
        """
        # Create a timestamp-based message
        message = f"{data.get('id', '')}:{time.time()}"
        
        # Generate HMAC
        h = hmac.new(self.encryption_key, message.encode(), hashlib.sha256)
        return h.hexdigest()
    
    def verify_token(self, token: str, data: Dict) -> bool:
        """
        Verify a token against data.
        
        Args:
            token: Token to verify
            data: Data to verify against
            
        Returns:
            Whether the token is valid
        """
        expected_token = self.generate_token(data)
        return hmac.compare_digest(token, expected_token)
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        return self.cipher_suite.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Data to decrypt
            
        Returns:
            Decrypted data
        """
        return self.cipher_suite.decrypt(encrypted_data)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed: Hashed password to verify against
            
        Returns:
            Whether the password matches
        """
        return hmac.compare_digest(
            self.hash_password(password),
            hashed
        ) 