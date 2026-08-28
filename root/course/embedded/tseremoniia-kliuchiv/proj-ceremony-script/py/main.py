#!/usr/bin/env python3
import hashlib
import binascii
import sys

def sha256_hex(data: bytes) -> str:
    """Обчислення стандартизованого SHA-256 хешу."""
    return hashlib.sha256(data).hexdigest()

def verify_transcript_entry(role: str, name: str, share_index: int, share_hex: str, expected_bag_id: str):
    """
    Звірка параметрів частки крипто-офіцера свідком церемонії.
    """
    share_bytes = binascii.unhexlify(share_hex)
    fingerprint = sha256_hex(share_bytes)
    
    print(f"=== ЗВІРКА ЧАСТКИ #{share_index} ===")
    print(f"Володар частки  : {role} ({name})")
    print(f"Сейф-пакет ID   : {expected_bag_id}")
    print(f"Довжина частки  : {len(share_bytes)} байтів")
    print(f"SHA-256 відбиток: {fingerprint}")
    print(f"Підпис аудитора : [ ______________________ ]\n")

if __name__ == "__main__":
    print("--- ПРОТОКОЛ ЦЕРЕМОНІЇ ГЕНЕРАЦІЇ КОРЕНЕВИХ КЛЮЧІВ ---")
    print("Дата й час: 2026-08-28 10:00 UTC")
    print("Конфігурація: Поріг 3 з 5 (Shamir Secret Sharing GF(256))\n")
    
    # Приклад перевірки відбитків трьох часток кворуму
    verify_transcript_entry("CTO", "Олександр К.", 1, "4a8f9c112233445566778899aabbccddeeff00112233445566778899aabbccdd", "BAG-UA-2026-001")
    verify_transcript_entry("CISO", "Марія В.", 2, "9b2c3d4e5f60718293a4b5c6d7e8f90112233445566778899aabbccddeeff001", "BAG-UA-2026-002")
    verify_transcript_entry("Bank Vault", "Сейф №402", 3, "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00", "BAG-UA-2026-003")
