// Стан приймача кадрів. Збирає кадр байт за байтом із потоку UART.
typedef struct {
    enum { WAIT_START, COLLECT } state;
    uint8_t buf[sizeof(rpc_req_t)];        // буфер під рівно один кадр
    size_t  have;                          // скільки байтів кадру вже зібрано
} rx_t;

static rx_t g_rx = { WAIT_START, {0}, 0 };

// Згодувати приймачу один байт із UART. Повертає true, коли кадр зібрано
// ЦІЛКОМ (тоді він лежить у *out і CRC уже перевірено).
static bool rx_feed(rx_t *rx, uint8_t byte, rpc_req_t *out) {
    switch (rx->state) {
    case WAIT_START:
        if (byte == RPC_START) {           // дочекалися початку кадру
            rx->have  = 0;
            rx->state = COLLECT;
        }
        return false;                      // байт-початок у буфер не кладемо

    case COLLECT:
        rx->buf[rx->have++] = byte;
        if (rx->have < sizeof(rpc_req_t))
            return false;                  // кадр іще не повний — чекаємо далі

        rx->state = WAIT_START;            // кадр зібрано — готуємось до нового
        memcpy(out, rx->buf, sizeof(*out));
        if (!req_ok(out))                  // CRC не зійшовся → кадр битий
            return false;                  // мовчки викидаємо, ніби не було
        return true;                       // цілий кадр готовий до диспетчеризації
    }
    return false;
}
