from enum import IntEnum

# ── Константи протоколу ──────────────────────────────────────────────────────
CRSF_SYNC_BYTE   = 0xC8   # байт-старт (він же адреса польотного контролера)
CRSF_LEN_MIN     = 2      # мінімум поля довжини: тип(1) + CRC(1)
CRSF_LEN_MAX     = 62     # максимум: кадр 64 − старт(1) − довжина(1)
CRSF_FRAME_MAX   = 64     # повний кадр разом зі стартом і CRC

# Типи кадрів, які розбираємо
CRSF_TYPE_LINK_STATISTICS    = 0x14
CRSF_TYPE_RC_CHANNELS_PACKED = 0x16

# ── Стани автомата ───────────────────────────────────────────────────────────
class CrsfState(IntEnum):
    ST_SYNC = 0   # шукаємо байт-старт 0xC8
    ST_LEN  = 1   # читаємо й перевіряємо поле довжини
    ST_BODY = 2   # добираємо тип + дані + CRC

class CrsfParser:
    def __init__(self):
        self.buf = bytearray(CRSF_FRAME_MAX)  # сюди складаємо кадр (без байта-старту)
        self.reset()

    def reset(self):
        self.state = CrsfState.ST_SYNC
        self.need = 0   # скільки байтів має бути в тілі (== поле довжини)
        self.got  = 0   # скільки байтів тіла вже назбирали
