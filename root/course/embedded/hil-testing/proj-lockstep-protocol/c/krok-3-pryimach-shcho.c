// Стан приймача кадру давачів. Годуємо його по одному байту.
typedef struct {
    enum { WAIT_S0, WAIT_S1, IN_BODY } st;
    uint8_t  buf[sizeof(hil_sensors_t)];  // сюди складаємо кадр
    size_t   have;                        // скільки байтів тіла вже маємо
} sensor_rx_t;

static sensor_rx_t g_rx = { .st = WAIT_S0 };

// Повертає true РІВНО тоді, коли зібрано повний і CRC-цілий кадр.
// Тоді *out містить готовий кадр; інакше *out не чіпаємо.
bool sensor_rx_byte(sensor_rx_t *rx, uint8_t byte, hil_sensors_t *out) {
    switch (rx->st) {
    case WAIT_S0:
        if (byte == HIL_SYNC0) { rx->buf[0] = byte; rx->st = WAIT_S1; }
        return false;                       // ще не кадр

    case WAIT_S1:
        if (byte == HIL_SYNC1) {            // маркер повний — почалося тіло
            rx->buf[1] = byte;
            rx->have   = 2;
            rx->st     = IN_BODY;
        } else if (byte == HIL_SYNC0) {
            rx->st = WAIT_S1;               // два S0 поспіль — лишаємось напоготові
        } else {
            rx->st = WAIT_S0;               // фальстарт — усе спочатку
        }
        return false;

    case IN_BODY:
        rx->buf[rx->have++] = byte;
        if (rx->have < sizeof(hil_sensors_t))
            return false;                   // тіло ще не повне

        // Кадр набрано цілком. Звіряємо CRC.
        rx->st = WAIT_S0;                   // хай там що — далі шукаємо новий SYNC
        hil_sensors_t f;
        memcpy(&f, rx->buf, sizeof(f));
        if (f.crc == sensors_crc(&f)) {     // CRC збігся — кадр цілий
            *out = f;
            return true;
        }
        return false;                       // CRC не збігся — тихо викинули
    }
    return false;
}
