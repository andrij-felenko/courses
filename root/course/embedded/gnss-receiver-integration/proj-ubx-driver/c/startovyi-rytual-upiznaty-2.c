// Стан очікувача ACK — заповнюється dispatch'ем, читається ритуалом.
static struct {
    bool    waiting;         // чи ми зараз чекаємо ACK
    uint8_t want_cls, want_id;  // на яку саме команду
    bool    got, ok;         // прийшла квитанція? і яка — ACK(true)/NAK(false)
} A;

// dispatch кличе це, отримавши ACK-ACK або ACK-NAK. payload квитанції несе
// class+id команди, яку вона підтверджує (2 байти) — звіряємо, що це «наша».
static void cfg_on_ack(bool is_ack, const uint8_t *buf, uint16_t len) {
    if (!A.waiting || len < 2) return;
    if (buf[0] == A.want_cls && buf[1] == A.want_id) {
        A.got = true;
        A.ok  = is_ack;
    }
}

// Зовнішні функції платформи: час і згодовування вхідних байтів під час чекання.
extern uint32_t millis(void);

// Надіслати команду й ДОЧЕКАТИСЯ її ACK. Повертає true, якщо ACK-ACK.
// Не блокує апарат надовго: у циклі чекання крутить gnss_poll, тож автомат
// живе, а таймаут обмежує чекання зверху.
static bool ubx_send_await(uint8_t cls, uint8_t id,
                           const uint8_t *payload, uint16_t len,
                           uint32_t timeout_ms, int retries) {
    for (int attempt = 0; attempt <= retries; attempt++) {
        A.waiting = true; A.got = false; A.ok = false;
        A.want_cls = cls; A.want_id = id;

        ubx_send(cls, id, payload, len);      // послали команду

        uint32_t t0 = millis();
        while ((uint32_t)(millis() - t0) < timeout_ms) {
            gnss_poll(millis());              // крутимо приймання — ACK прийде сюди
            if (A.got) {
                A.waiting = false;
                if (A.ok) return true;        // ACK-ACK — крок удався
                break;                        // ACK-NAK — ретраїти нема сенсу, вийти
            }
        }
        A.waiting = false;
        if (A.got && !A.ok) return false;     // явний NAK — не ретраїмо
        // інакше таймаут — пробуємо ще раз (наступна ітерація attempt)
    }
    return false;   // спроби вичерпано — крок провалено
}
