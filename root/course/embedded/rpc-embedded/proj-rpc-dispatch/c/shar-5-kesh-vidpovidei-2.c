extern void uart_write(uint8_t byte);

// Скласти й вислати кадр відповіді (маршалінг відповіді).
static void send_resp(const rpc_resp_t *r) {
    uart_write(RPC_START);
    const uint8_t *p = (const uint8_t *)r;
    for (size_t i = 0; i < sizeof(*r); i++)
        uart_write(p[i]);
}

// Повний обробник одного цілого запиту на боці сервера.
static void server_handle(const rpc_req_t *req) {
    // 1) Уже бачили цей ID? → це ПОВТОР. Шлемо стару відповідь, не виконуючи.
    const rpc_resp_t *cached = cache_find(req->id);
    if (cached != NULL) {
        send_resp(cached);                 // дія НЕ виконується вдруге
        return;
    }

    // 2) Новий запит — виконуємо функцію через диспетчер.
    rpc_resp_t resp;
    resp.id     = req->id;
    resp.status = dispatch(req->func, req->arg, &resp.value);
    resp.crc    = resp_crc(&resp);

    // 3) Запамʼятовуємо відповідь — щоб майбутній повтор не виконав дію знову.
    cache_store(req->id, &resp);

    // 4) Шлемо відповідь.
    send_resp(&resp);
}
