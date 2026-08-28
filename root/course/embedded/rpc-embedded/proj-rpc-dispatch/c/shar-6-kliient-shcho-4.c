// Десь у головному циклі програми:
void main_loop(void) {
    static bool asked = false;

    rpc_call_poll();                       // двигун RPC — крутиться завжди

    if (!asked) {
        if (rpc_call_begin(1, 3))          // func 1 = read_sensor, arg = 3
            asked = true;
    }

    if (g_call.state == CALL_DONE) {
        int32_t temp = g_call.value;       // відповідь прийшла
        use_temperature(temp);
        g_call.state = CALL_IDLE;
        asked = false;
    } else if (g_call.state == CALL_FAILED) {
        handle_link_loss();                // віддалена сторона мовчить
        g_call.state = CALL_IDLE;
        asked = false;
    }

    run_control_loop();                    // ← це крутиться ВЕСЬ час,
    feed_watchdog();                       //    навіть поки чекаємо відповідь
}
