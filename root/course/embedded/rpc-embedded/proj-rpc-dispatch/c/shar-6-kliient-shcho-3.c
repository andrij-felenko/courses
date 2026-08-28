extern bool uart_read(uint8_t *byte);  // драйвер: дістати байт, false якщо порожньо

// Приймач кадрів ВІДПОВІДІ (дзеркало rx_feed, але під rpc_resp_t).
static rx_t g_crx = { WAIT_START, {0}, 0 };
static bool resp_feed(rx_t *rx, uint8_t byte, rpc_resp_t *out) {
    switch (rx->state) {
    case WAIT_START:
        if (byte == RPC_START) { rx->have = 0; rx->state = COLLECT; }
        return false;
    case COLLECT:
        rx->buf[rx->have++] = byte;
        if (rx->have < sizeof(rpc_resp_t)) return false;
        rx->state = WAIT_START;
        memcpy(out, rx->buf, sizeof(*out));
        return resp_ok(out);           // битий кадр → false (наче не було)
    }
    return false;
}

// Двигун клієнта. Кликати ЧАСТО з головного циклу. Не блокує.
static void rpc_call_poll(void) {
    if (g_call.state != CALL_WAITING)
        return;                        // нема активного виклику — нічого робити

    // 1) Зловити відповідь, якщо прийшла.
    uint8_t byte;
    rpc_resp_t resp;
    while (uart_read(&byte)) {
        if (resp_feed(&g_crx, byte, &resp)) {
            if (resp.id == g_call.id) {        // це відповідь на НАШ виклик
                g_call.value  = resp.value;
                g_call.status = resp.status;
                g_call.state  = CALL_DONE;
                return;
            }
            // чужий ID — відповідь на старий виклик, ігноруємо
        }
    }

    // 2) Перевірити таймаут.
    if (millis() - g_call.t_sent >= RPC_TIMEOUT_MS) {
        if (g_call.tries >= RPC_RETRIES) {
            g_call.state = CALL_FAILED;        // вичерпали повтори — здаємось
            return;
        }
        g_call.tries++;
        send_req(g_call.id, g_call.func, g_call.arg);  // ТОЙ САМИЙ ID!
        g_call.t_sent = millis();              // перезаводимо таймер
    }
}
