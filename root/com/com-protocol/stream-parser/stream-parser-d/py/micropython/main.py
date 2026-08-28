SYNC   = const(0xAA)
MAXLEN = const(32)

WAIT_SYNC, GET_LEN, GET_DATA, GET_CRC = 0, 1, 2, 3

# стан живе в модульних змінних — переживає між викликами feed()
_st  = WAIT_SYNC
_buf = bytearray(MAXLEN)
_len = 0
_idx = 0
_crc = 0

def feed(b):
    global _st, _len, _idx, _crc
    if _st == WAIT_SYNC:
        if b == SYNC:
            _st = GET_LEN                  # інакше просто ігноруємо
    elif _st == GET_LEN:
        if b == 0 or b > MAXLEN:           # захист: 0 або завелика довжина
            _st = WAIT_SYNC
            return
        _len = b; _idx = 0; _crc = b       # CRC накриває й байт довжини
        _st = GET_DATA
    elif _st == GET_DATA:
        _buf[_idx] = b; _idx += 1
        _crc ^= b                          # CRC рахуємо на льоту
        if _idx == _len:
            _st = GET_CRC
    elif _st == GET_CRC:
        if b == _crc:
            handle_packet(_buf, _len)      # цілий пакет — у роботу
        _st = WAIT_SYNC                    # у будь-якому разі — наново
