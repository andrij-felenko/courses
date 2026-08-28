import struct

# Кільце з N секторів; у кожному — один запис {seq, value, crc}.
# «Жива» комірка та, у якої найбільший seq; писати треба в наступну за нею.
N_SECT    = 64          # скільки секторів ділять знос
SECT_SIZE = 4096        # розмір сектора Flash, байтів
MAGIC     = 0xC0FFEE

# один слот = одна фізична комірка: magic, seq, value, crc — чотири uint32 LE
_REC = struct.Struct("<4I")     # magic, seq, value, crc

# апаратура застабована ззовні: flash_read/flash_write/flash_erase_sector, crc32

class Counter:
    def __init__(self, base_addr):
        self.base = base_addr
        self.seq  = 0           # seq останнього запису
        self.slot = 0           # індекс сектора з останнім записом

    # Знайти найсвіжіший запис серед усіх секторів (виклик раз, на старті).
    def mount(self):
        best_seq = 0
        value = 0
        found = False
        for i in range(N_SECT):
            raw = flash_read(self.base + i * SECT_SIZE, _REC.size)
            magic, seq, val, crc = _REC.unpack(raw)
            if magic != MAGIC:                        # порожній/стертий сектор
                continue
            if crc32(raw[:-4]) != crc:                # битий запис — пропустити
                continue
            if not found or seq > best_seq:           # запам'ятати найсвіжіший
                best_seq, self.slot, value, found = seq, i, val, True
        self.seq = best_seq if found else 0
        return (found, value)

    # Записати нове значення — у НАСТУПНИЙ сектор по колу (ось і все вирівнювання).
    def save(self, value):
        nxt  = (self.slot + 1) % N_SECT               # ротація: наступний сектор
        addr = self.base + nxt * SECT_SIZE
        flash_erase_sector(addr)                      # одне стирання раз на оберт
        body = struct.pack("<3I", MAGIC, self.seq + 1, value)  # новий seq — на одиницю більший
        rec  = body + struct.pack("<I", crc32(body))
        flash_write(addr, rec)                        # дописуємо у вільну комірку
        self.slot, self.seq = nxt, self.seq + 1       # тепер «жива» комірка — ця
