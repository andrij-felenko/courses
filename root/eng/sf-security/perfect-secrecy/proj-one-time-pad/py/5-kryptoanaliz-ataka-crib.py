def xor_bytes(a: bytes, b: bytes) -> bytes:
    """Побітове додавання двох байтових рядків."""
    return bytes(x ^ y for x, y in zip(a, b))

def calculate_coincidence_index(data: bytes) -> float:
    """Обчислення індексу збігів (IC) для перевірки наявності мовних патернів."""
    if len(data) < 2:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    numerator = sum(f * (f - 1) for f in freq)
    return numerator / (n * (n - 1))

def is_readable_ascii(byte_seq: bytes) -> bool:
    """Перевірка, чи складається послідовність суто з друкованих символів ASCII."""
    for b in byte_seq:
        # Дозволені друковані символи від пробілу (32) до тільди (126), плюс таб та перенос
        if not (32 <= b <= 126 or b in (9, 10, 13)):
            return False
    return True

def crib_drag(c1_xor_c2: bytes, crib: str):
    """Сковзання слова-здогадки вздовж XOR двох шифротекстів."""
    crib_bytes = crib.encode("ascii")
    crib_len = len(crib_bytes)
    print(f"\n--- Пошук слова-здогадки (Crib): \"{crib}\" ---")

    for offset in range(len(c1_xor_c2) - crib_len + 1):
        target_slice = c1_xor_c2[offset:offset + crib_len]
        candidate = xor_bytes(target_slice, crib_bytes)
        
        # Якщо результат схожий на друкований текст, виводимо знайдену позицію
        if is_readable_ascii(candidate):
            cand_text = candidate.decode("ascii", errors="replace")
            print(f"  Зсув {offset:2d}: m₂[{offset}:{offset+crib_len}] = \"{cand_text}\"")

def demo_attack():
    # Два відкритих повідомлення
    plaintext1 = b"CONFIDENTIAL: THE PRESIDENT WILL ARRIVE AT 0800 HOURS AT NORTH GATE."
    plaintext2 = b"TOP_SECRET_MSG: WE HAVE EVACUATED ALL PERSONNEL ACROSS THE RIVER NOW."
    
    # Фатальна помилка: використання одного ключа для обох повідомлень
    shared_key = secrets.token_bytes(len(plaintext1))
    c1 = xor_bytes(plaintext1, shared_key)
    c2 = xor_bytes(plaintext2, shared_key)

    # Криптоаналітик не знає ключа, але перехоплює c1 та c2
    diff = xor_bytes(c1, c2)
    print(f"Перехоплено шифротексти довжиною {len(diff)} байтів.")
    print(f"Індекс збігів XOR (IC): {calculate_coincidence_index(diff):.5f}")

    # Автоматичне сковзання типових слів
    crib_drag(diff, " PRESIDENT ")
    crib_drag(diff, " PERSONNEL ")
    crib_drag(diff, " EVACUATED ")

if __name__ == "__main__":
    demo_attack()
