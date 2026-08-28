// Ключі конфігурації M9/M10 (32-бітні; біти 28-30 = код розміру значення).
#define KEY_UART1_BAUD     0x40520001u   // U4: швидкість UART1
#define KEY_MSGOUT_PVT     0x20910007u   // U1: темп NAV-PVT на UART1 (1 = щоцикл)
#define KEY_RATE_MEAS      0x30210001u   // U2: період вимірювання, мс
#define KEY_RATE_NAV       0x30210002u   // U2: скільки вимірів на навігаційний розв'язок

#define VALSET_LAYER_RAM    0x01
#define VALSET_LAYER_FLASH  0x04         // RAM|FLASH = діє зараз І переживе перезапуск

// Дописати ключ (4 байти LE) і значення потрібної ширини у буфер VALSET.
// val — 64-бітне, бо ключ може вимагати аж 8 байтів (розмір 0x5).
static uint16_t put_key(uint8_t *p, uint32_t key, uint64_t val) {
    p[0]=key; p[1]=key>>8; p[2]=key>>16; p[3]=key>>24;   // ключ, LE
    // Ширину значення кодує поле бітів 28-30 ключа, і кодує НЕ числом байтів:
    // 0x1→1 біт (1 байт), 0x2→1 байт, 0x3→2 байти, 0x4→4 байти, 0x5→8 байтів.
    int sz = (key >> 28) & 0x7;
    int n  = (sz <= 2) ? 1 : (sz == 3) ? 2 : (sz == 4) ? 4 : 8;
    for (int i = 0; i < n; i++) p[4 + i] = (uint8_t)(val >> (8 * i));  // значення, LE
    return (uint16_t)(4 + n);
}

static bool configure_m9_m10(void) {
    uint8_t pl[64];
    uint16_t n = 0;
    pl[n++] = 0x00;                          // версія
    pl[n++] = VALSET_LAYER_RAM | VALSET_LAYER_FLASH;  // куди писати
    pl[n++] = 0x00; pl[n++] = 0x00;          // резерв

    n += put_key(pl + n, KEY_MSGOUT_PVT, 1);      // увімкнути NAV-PVT щоцикл
    n += put_key(pl + n, KEY_RATE_MEAS,  100);    // 100 мс → 10 Гц
    n += put_key(pl + n, KEY_RATE_NAV,   1);      // 1 вимір на розв'язок
    // Швидкість UART міняємо ОСТАННЬОЮ й окремо — див. пастку порядку нижче.

    if (!ubx_send_await(UBX_CLS_CFG, UBX_CFG_VALSET, pl, n, 300, 2))
        return false;

    // Тепер окремий VALSET лише на швидкість — і одразу перемикаємо свій UART.
    uint8_t bp[16]; uint16_t bn = 0;
    bp[bn++] = 0x00; bp[bn++] = VALSET_LAYER_RAM | VALSET_LAYER_FLASH;
    bp[bn++] = 0x00; bp[bn++] = 0x00;
    bn += put_key(bp + bn, KEY_UART1_BAUD, 115200);
    ubx_send(UBX_CLS_CFG, UBX_CFG_VALSET, bp, bn);   // без await: модуль зараз змінить швидкість
    uart_flush();                                    // дочекатися, поки байти пішли
    uart_set_baud(115200);                           // МИ теж переходимо на 115200
    return true;
}
