// Заглушка: почати віддалений виклик. НЕ чекає — одразу повертає керування.
// Повертає false, якщо попередній виклик іще не завершено.
static bool rpc_call_begin(uint8_t func, int32_t arg) {
    if (g_call.state == CALL_WAITING)
        return false;                  // канал зайнятий попереднім викликом

    g_call.id     = g_next_id++;       // унікальний ID (0..255 по колу)
    g_call.func   = func;
    g_call.arg    = arg;
    g_call.tries  = 1;
    g_call.value  = 0;
    g_call.status = RPC_ERR_BUSY;
    g_call.state  = CALL_WAITING;

    send_req(g_call.id, func, arg);    // шлемо перший запит
    g_call.t_sent = millis();          // заводимо таймер
    return true;
}
