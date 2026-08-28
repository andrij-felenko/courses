/* Тестовий двійковий вектор пакета QUIC Initial v1 (C99) */
const uint8_t raw_packet[] = {
    /* 1. Long Header Байт прапорців: Initial, Form=1 */
    0xC0,
    /* 2. Version (4B): 0x00000001 (QUIC v1) */
    0x00, 0x00, 0x00, 0x01,
    /* 3. DCIL (1B): 4 байти + DCID (0xAA, 0xBB, 0xCC, 0xDD) */
    0x04, 0xAA, 0xBB, 0xCC, 0xDD,
    /* 4. SCIL (1B): 4 байти + SCID (0x11, 0x22, 0x33, 0x44) */
    0x04, 0x11, 0x22, 0x33, 0x44,
    /* 5. Token Length: 0 (Varint: 0x00) */
    0x00,
    /* 6. Payload Length (Varint: 12 байтів -> 0x0C) */
    0x0C,
    /* 7. Корисне навантаження: кадр STREAM (0x0E -> OFF=1, LEN=1, FIN=0) */
    0x0E,
    /* Stream ID: 0 (Varint 0x00) */
    0x00,
    /* Offset: 256 (Varint 2 байти: 0x4100 -> 0x0100 = 256) */
    0x41, 0x00,
    /* Length: 4 байти (Varint 0x04) */
    0x04,
    /* Прикладні байти корисного навантаження */
    'T', 'E', 'S', 'T'
};
