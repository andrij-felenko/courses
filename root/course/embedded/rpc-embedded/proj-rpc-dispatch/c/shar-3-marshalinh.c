extern void uart_write(uint8_t byte);     // драйвер UART: вислати один байт

// Маршалінг + відправка кадру запиту.
static void send_req(uint8_t id, uint8_t func, int32_t arg) {
    rpc_req_t r;
    r.id   = id;
    r.func = func;
    r.arg  = arg;                          // 32-бітне число лягає 4 байтами
    r.crc  = req_crc(&r);                  // сума над {id, func, arg}

    uart_write(RPC_START);                 // байт-початок (під CRC не йде)
    const uint8_t *p = (const uint8_t *)&r;
    for (size_t i = 0; i < sizeof(r); i++) // байти структури як є
        uart_write(p[i]);
}
