// Доповнення до poll: скидати недозібраний кадр, якщо байти давно не йдуть.
// FRAME_IDLE_MS підбирають із запасом над часом передачі кількох байтів на цій швидкості.
#define FRAME_IDLE_MS 50

void bridge_framing_poll_timed(uint32_t now_ms) {
    static uint32_t last_byte_ms;
    bool got = false;

    while (rx_available()) {
        uint8_t b = rx_get();
        got = true;
        if (frame_feed(&parser, b))
            on_frame(parser.data, parser.len);
    }
    if (got) {
        last_byte_ms = now_ms;                       // оновили мітку останнього байта
    } else if (parser.state != WAIT_SYNC &&
               (uint32_t)(now_ms - last_byte_ms) > FRAME_IDLE_MS) {
        frame_reset(&parser);                        // кадр завис — скинути й чекати SYNC
    }
}
