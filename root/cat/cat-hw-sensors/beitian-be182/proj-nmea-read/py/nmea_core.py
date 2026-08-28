# nmea_core.py — контрольна сума й переведення поля координати.
# Ті самі дві дії, що й у C, лише коротше.

def checksum_ok(line: str) -> bool:
    """XOR усіх байтів між '$' і '*'; True, якщо збіглося з полем після '*'."""
    line = line.strip()
    if "*" not in line:
        return False                       # немає зірки — рядок обрізаний
    body, given = line[1:].split("*", 1)   # [1:] прибирає '$'; body — до зірки
    calc = 0
    for ch in body:
        calc ^= ord(ch)                    # побайтний XOR
    return calc == int(given[:2], 16)      # дві шістнадцяткові цифри

def to_degrees(field: str, direction: str, deg_digits: int) -> float:
    """Поле 'ddmm.mmmm' + літера напрямку → десяткові градуси."""
    if not field:
        return 0.0                         # порожнє поле — нема fix
    raw = float(field)                     # напр. 4807.038
    deg = int(raw // 100)                  # 48  (відкидаємо хвилини)
    minutes = raw - deg * 100              # 7.038
    dec = deg + minutes / 60.0             # 48.1173
    if direction in ("S", "W"):
        dec = -dec                         # південь/захід — мінус
    return dec
