// Неблокуючий автомат розбору UBX: годуємо по одному байту з перервання UART.
// Повертає true, коли зібрано цілий валідний пакет у g_msg.
enum { WAIT_B5, WAIT_62, GET_CLASS, GET_ID, GET_LEN1, GET_LEN2, GET_PAYLOAD, GET_CKA, GET_CKB };
static uint8_t st = WAIT_B5;
static uint16_t len, idx;
static uint8_t g_class, g_id, buf[128], cka, ckb;

bool ubx_feed(uint8_t byte) {
    switch (st) {
    case WAIT_B5: if (byte == 0xB5) st = WAIT_62;  break;   // ловимо сигнатуру
    case WAIT_62: st = (byte == 0x62) ? GET_CLASS : WAIT_B5; break;
    case GET_CLASS: g_class = byte; st = GET_ID;   break;
    case GET_ID:    g_id = byte;    st = GET_LEN1;  break;
    case GET_LEN1:  len = byte;        st = GET_LEN2; break;  // молодший байт довжини
    case GET_LEN2:  len |= byte << 8;  idx = 0;              // старший → повна довжина
                    st = (len <= sizeof buf) ? GET_PAYLOAD : WAIT_B5; break;
    case GET_PAYLOAD:
        buf[idx++] = byte;
        if (idx >= len) st = GET_CKA;                        // набрали всі дані
        break;
    case GET_CKA: cka = byte; st = GET_CKB; break;
    case GET_CKB: {
        ckb = byte;
        uint8_t a, b;
        ubx_checksum_frame(g_class, g_id, len, buf, &a, &b);
        st = WAIT_B5;                                        // хай там як — назад у пошук
        return (a == cka && b == ckb);                       // валідний пакет?
    }
    }
    return false;
}
