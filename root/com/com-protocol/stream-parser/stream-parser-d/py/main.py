SYNC   = 0xAA
MAXLEN = 32

WAIT_SYNC, GET_LEN, GET_DATA, GET_CRC = range(4)


class Parser:
    # весь стан — у полях; він переживає між викликами feed()
    def __init__(self, on_packet):
        self.st = WAIT_SYNC
        self.buf = bytearray()
        self.length = 0
        self.crc = 0
        self.on_packet = on_packet

    def feed(self, b):
        if self.st == WAIT_SYNC:
            if b == SYNC:
                self.st = GET_LEN          # інакше просто ігноруємо
        elif self.st == GET_LEN:
            if b == 0 or b > MAXLEN:       # захист: 0 або завелика довжина
                self.st = WAIT_SYNC
                return
            self.length = b
            self.buf = bytearray()
            self.crc = b                   # CRC накриває й байт довжини
            self.st = GET_DATA
        elif self.st == GET_DATA:
            self.buf.append(b)
            self.crc ^= b                  # CRC рахуємо на льоту
            if len(self.buf) == self.length:
                self.st = GET_CRC
        elif self.st == GET_CRC:
            if b == self.crc:
                self.on_packet(bytes(self.buf))  # цілий пакет — у роботу
            self.st = WAIT_SYNC            # у будь-якому разі — наново
