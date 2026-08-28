// Викликається з bridge_framing_poll() на КОЖЕН цілий перевірений кадр.
void on_frame(const uint8_t *data, uint8_t len) {
    if (len == 0) return;                   // порожній кадр — нічого робити
    uint8_t cmd = data[0];

    switch (cmd) {
    case 0x01: {                            // PING → луна тих самих байтів
        frame_send(data, len);
        break;
    }
    case 0x02: {                            // READ_OVERRUNS → 4 байти лічильника
        uint8_t resp[5];
        resp[0] = 0x02;                     // відлуння коду команди
        uint32_t v = rx_overruns;
        resp[1] = (uint8_t)(v      );       // молодший байт уперед
        resp[2] = (uint8_t)(v >>  8);
        resp[3] = (uint8_t)(v >> 16);
        resp[4] = (uint8_t)(v >> 24);
        frame_send(resp, 5);
        break;
    }
    default: {                              // невідома команда → кадр-помилка
        uint8_t resp[2] = { 0xFF, cmd };    // 0xFF = «не зрозумів», далі — що саме
        frame_send(resp, 2);
        break;
    }
    }
}
