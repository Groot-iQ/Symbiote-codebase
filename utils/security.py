import hashlib
import hmac
import time
import os
import base64
from typing import Dict, Optional
from cryptography.fernet import Fernet
from config.settings import settings

class SecurityManager:
    """
    Manages security and encryption for the agent.
    This class provides:
    1. Data encryption and decryption using Fernet (symmetric encryption)
    2. Token generation and verification using HMAC
    3. Password hashing and verification
    4. Secure key management
    
    The manager uses industry-standard cryptographic libraries and practices.
    """
    
    def __init__(self):
        """
        Initialize the security manager.
        This method:
        1. Sets up the encryption key
        2. Creates the Fernet cipher suite
        3. Handles key generation if needed
        
        The encryption key is either loaded from settings or generated securely.
        """
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
        
        # Create Fernet cipher suite for encryption/decryption
        self.cipher_suite = Fernet(self.encryption_key)
    
    def generate_token(self, data: Dict) -> str:
        """
        Generate a secure token for data verification.
        This method:
        1. Creates a timestamp-based message
        2. Generates an HMAC using SHA-256
        3. Returns the token as a hex string
        
        Args:
            data: Data to generate token for, containing:
                 - id: Unique identifier for the data
                 
        Returns:
            str: HMAC token for data verification
        """
        # Create a timestamp-based message
        message = f"{data.get('id', '')}:{time.time()}"
        
        # Generate HMAC using SHA-256
        h = hmac.new(self.encryption_key, message.encode(), hashlib.sha256)
        return h.hexdigest()
    
    def verify_token(self, token: str, data: Dict) -> bool:
        """
        Verify a token against data.
        This method:
        1. Generates the expected token
        2. Compares it with the provided token
        3. Uses constant-time comparison for security
        
        Args:
            token: Token to verify
            data: Data to verify against
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        expected_token = self.generate_token(data)
        return hmac.compare_digest(token, expected_token)
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using Fernet symmetric encryption.
        This method:
        1. Takes raw bytes as input
        2. Encrypts using the Fernet cipher suite
        3. Returns encrypted bytes
        
        Args:
            data: Raw data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        return self.cipher_suite.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using Fernet symmetric encryption.
        This method:
        1. Takes encrypted bytes as input
        2. Decrypts using the Fernet cipher suite
        3. Returns decrypted bytes
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            bytes: Decrypted data
        """
        return self.cipher_suite.decrypt(encrypted_data)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        This method:
        1. Takes a plain text password
        2. Hashes it using SHA-256
        3. Returns the hash as a hex string
        
        Args:
            password: Plain text password to hash
            
        Returns:
            str: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        This method:
        1. Hashes the provided password
        2. Compares it with the stored hash
        3. Uses constant-time comparison for security
        
        Args:
            password: Plain text password to verify
            hashed: Stored hash to verify against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return hmac.compare_digest(
            self.hash_password(password),
            hashed
        ) 