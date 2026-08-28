// Готовність до нової сесії: викинути недогризки минулого потоку,
// дочекатися ПЕРШОГО цілого кадру давачів — і лише тоді відкрити lockstep.
void hil_await_handshake(void) {
    g_rx.st = WAIT_S0;                   // забути будь-який напівкадр у приймачі
    g_stream_started = false;            // seq/час — з чистого аркуша

    hil_sensors_t first;
    uint8_t byte;
    for (;;) {
        if (!link_read_byte(&byte))      // блокуюче читання одного байта з лінку
            continue;
        if (sensor_rx_byte(&g_rx, byte, &first)) {  // зібрався цілий CRC-кадр?
            hil_on_sensor_frame(&first); // перший такт — і поїхали
            return;                      // далі кадри йдуть звичайним шляхом
        }
    }
}
