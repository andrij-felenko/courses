import struct

SECTOR    = 4096            # розмір сектора Flash (типово 4 КБ)
N_SECTORS = 16              # скільки секторів під лог
EMPTY_SEQ = 0xFFFFFFFF      # стерте слово = вільний сектор
PAYLOAD   = SECTOR - 8      # тіло запису; 8 байтів — на seq + crc

# --- апаратні примітиви Flash (надає драйвер платформи) ---
# flash_read(sector) -> bytes    (повертає SECTOR байтів)
# flash_erase(sector)            -> усі біти в 0xFF
# flash_write(sector, data)      (data — рівно SECTOR байтів)
# crc32(data) -> int

head = 0                    # індекс сектора-голови
next_seq = 1                # номер для наступного запису

# Дописати подію. O(1): майже завжди це лише запис у голову.
def log_append(event: bytes) -> None:
    global head, next_seq
    if len(event) > PAYLOAD:                     # не влазить
        return

    ahead = (head + 1) % N_SECTORS               # сектор попереду голови
    flash_erase(ahead)                           # стираємо наперед — губимо найдавніше

    payload = event + b"\xFF" * (PAYLOAD - len(event))  # лишок — як стертий
    seq = next_seq
    next_seq += 1
    crc = crc32(payload)                         # мітка ставиться ОСТАННЬОЮ
    rec = struct.pack("<II", seq, crc) + payload

    flash_write(head, rec)                       # запис у голову
    head = ahead                                 # голова посунулась по колу

# Відновлення при старті: знайти голову й продовжити нумерацію. O(n).
def log_init() -> None:
    global head, next_seq
    best_seq = 0
    best_idx = 0
    found = False

    for i in range(N_SECTORS):
        rec = flash_read(i)
        seq, crc = struct.unpack_from("<II", rec)
        payload = rec[8:SECTOR]
        if seq == EMPTY_SEQ:                      # вільний — пропустити
            continue
        if crc != crc32(payload):                 # обірваний запис —
            continue                              # мітка не сходиться
        if not found or seq > best_seq:           # шукаємо найбільший №
            best_seq, best_idx, found = seq, i, True

    if not found:                    # чистий Flash: лог іще порожній
        head, next_seq = 0, 1
    else:                            # голова — одразу за найновішим записом
        head = (best_idx + 1) % N_SECTORS
        next_seq = best_seq + 1
