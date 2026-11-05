import os
import binascii

class KeyGenerator:
    """Забезпечує безпечну генерацію та форматування 256-бітних ключів."""
    
    @staticmethod
    def generate_256bit_key() -> bytes:
        """Генерує криптографічно стійкий 256-бітний ключ (32 байти) з ентропії ОС."""
        return os.urandom(32)

    @staticmethod
    def format_key_hex(key: bytes) -> str:
        """Форматує ключ у шістнадцятковий рядок для зручного логування."""
        return binascii.hexlify(key).decode('utf-8')
