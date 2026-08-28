import secrets
import hashlib

def generate_backup_codes(count: int = 8) -> list[str]:
    codes = []
    for _ in range(count):
        raw = secrets.token_hex(5)
        codes.append(f"{raw[:5]}-{raw[5:]}")
    return codes

def hash_backup_code(plain_code: str) -> str:
    clean = plain_code.replace("-", "").replace(" ", "").lower()
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()

def verify_and_consume_code(
    user_input: str,
    stored_hashes: list[dict]
) -> tuple[bool, list[dict]]:
    input_hash = hash_backup_code(user_input)
    
    for item in stored_hashes:
        if not item.get("used", False) and hmac.compare_digest(item["hash"], input_hash):
            item["used"] = True
            return True, stored_hashes
            
    return False, stored_hashes
