// Приклад інтеграції: у циклі прошивки чи в перерві по прийому UART.
// uart_read(dst, maxn) повертає, скільки байтів реально прочитано (0…maxn).
static CrsfParser g_parser;

void crsf_service(void) {
    uint8_t chunk[64];
    int n = uart_read(chunk, sizeof(chunk));   // порція довільного розміру
    for (int i = 0; i < n; ++i)
        crsf_parser_push(&g_parser, chunk[i]); // згодовуємо по байту
}

void crsf_init(void) {
    crsf_crc8_init();
    crsf_parser_reset(&g_parser);
}
