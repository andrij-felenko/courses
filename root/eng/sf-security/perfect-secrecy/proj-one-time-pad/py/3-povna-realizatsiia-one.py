import os
import secrets
from typing import Tuple

def generate_key(length: int) -> bytes:
    """Генерація криптографічно стійкого одноразового ключа через системний CSPRNG."""
    if length <= 0:
        raise ValueError("Довжина ключа має бути строго додатною")
    # secrets.token_bytes звертається напряму до системного пулу ентропії (/dev/urandom)
    return secrets.token_bytes(length)

def otp_transform(data: bytes, key: bytes) -> bytes:
    """Шифрування та дешифрування One-Time Pad (симетрична операція XOR)."""
    if len(data) != len(key):
        raise ValueError(
            f"Незбіг довжин: дані мають {len(data)} байтів, а ключ — {len(key)} байтів"
        )
    # Побайтове додавання за модулем 2
    return bytes(b_data ^ b_key for b_data, b_key in zip(data, key))

def main():
    message_text = "СЕКРЕТНИЙ_НАКАЗ_АТАКА_О_ПЯТИЙ"
    message_bytes = message_text.encode("utf-8")
    print(f"Відкритий текст ({len(message_bytes)} байтів): {message_text}")

    # 1. Генерація одноразового ключа точно такої ж довжини
    key = generate_key(len(message_bytes))
    print(f"Згенерований ключ (hex): {key.hex()[:32]}...")

    # 2. Шифрування повідомлення
    ciphertext = otp_transform(message_bytes, key)
    print(f"Шифротекст (hex):        {ciphertext.hex()[:32]}...")

    # 3. Дешифрування тим самим ключем
    decrypted_bytes = otp_transform(ciphertext, key)
    decrypted_text = decrypted_bytes.decode("utf-8")
    print(f"Розшифровано:            {decrypted_text}")
    
    assert decrypted_bytes == message_bytes, "Помилка розшифрування!"
    print("Успіх: відкритий текст та розшифровані дані повністю ідентичні.")

if __name__ == "__main__":
    main()
