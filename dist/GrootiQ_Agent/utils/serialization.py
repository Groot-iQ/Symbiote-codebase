import json
import pickle
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from config.settings import settings

class Serializer:
    """Handles serialization and deserialization of agent data."""
    
    def __init__(self):
        """Initialize the serializer with encryption key."""
        self.encryption_key = settings.SECURITY_KEY.encode()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def serialize(self, data: Any, encrypt: bool = True) -> bytes:
        """
        Serialize data to bytes, optionally encrypting it.
        
        Args:
            data: Data to serialize
            encrypt: Whether to encrypt the data
            
        Returns:
            Serialized (and optionally encrypted) data as bytes
        """
        # Convert to JSON first
        json_data = json.dumps(data)
        
        # Encrypt if requested
        if encrypt:
            return self.cipher_suite.encrypt(json_data.encode())
        return json_data.encode()
    
    def deserialize(self, data: bytes, encrypted: bool = True) -> Any:
        """
        Deserialize data from bytes, optionally decrypting it.
        
        Args:
            data: Serialized data
            encrypted: Whether the data is encrypted
            
        Returns:
            Deserialized data
        """
        # Decrypt if necessary
        if encrypted:
            data = self.cipher_suite.decrypt(data)
        
        # Parse JSON
        return json.loads(data.decode())
    
    def save_to_file(self, data: Any, filename: str, encrypt: bool = True) -> bool:
        """
        Save serialized data to a file.
        
        Args:
            data: Data to save
            filename: Target file path
            encrypt: Whether to encrypt the data
            
        Returns:
            Success status
        """
        try:
            serialized = self.serialize(data, encrypt)
            with open(filename, 'wb') as f:
                f.write(serialized)
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def load_from_file(self, filename: str, encrypted: bool = True) -> Optional[Any]:
        """
        Load and deserialize data from a file.
        
        Args:
            filename: Source file path
            encrypted: Whether the data is encrypted
            
        Returns:
            Deserialized data or None if failed
        """
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            return self.deserialize(data, encrypted)
        except Exception as e:
            print(f"Error loading from file: {e}")
            return None 