static frame_parser_t parser;

void bridge_framing_init(void) {
    frame_reset(&parser);
    // UART під ту саму швидкість, що й перетворювач/термінал на ПК.
    uart_init(/*tx=*/1, /*rx=*/3, /*baud=*/115200);
    // (увімкнення переривання приймача — за HAL вашого МК; ISR кличе uart_rx_isr())
}

// Викликати в кожному оберті головного циклу.
void bridge_framing_poll(void) {
    while (rx_available()) {                 // забрати ВСЕ, що накопичилось
        uint8_t b = rx_get();
        if (frame_feed(&parser, b)) {        // зібрано цілий перевірений кадр
            on_frame(parser.data, parser.len);
        }
    }
}
