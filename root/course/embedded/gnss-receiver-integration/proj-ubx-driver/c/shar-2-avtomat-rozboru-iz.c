// Стани автомата — прямо з каркаса пакета UBX.
enum ubx_state {
    UST_SYNC1, UST_SYNC2, UST_CLASS, UST_ID,
    UST_LEN1,  UST_LEN2,  UST_PAYLOAD, UST_CKA, UST_CKB
};

// Увесь стан парсера — статичний, переживає між викликами gnss_poll.
static struct {
    enum ubx_state state;
    uint8_t  msg_class, msg_id;
    uint16_t len, idx;          // очікувана довжина payload та скільки вже набрано
    uint8_t  buf[UBX_BUF_MAX];  // payload
    uint8_t  ck_a, ck_b;        // сума Флетчера, копиться на льоту
    uint8_t  rx_cka;            // прийнятий CK_A (звіряємо з обчисленим)
    uint32_t last_byte_ms;      // час останнього байта — для таймера простою
} P;

// Підмішати один байт у суму Флетчера (той самий алгоритм, що звіряє UBX).
static inline void ck_step(uint8_t b) {
    P.ck_a += b;                // накопичує суму байтів
    P.ck_b += P.ck_a;          // накопичує суму часткових сум (обидва mod 256 самі)
}

static void ubx_reset(void) {   // єдиний чистий шлях назад у синхронізацію
    P.state = UST_SYNC1;
    P.ck_a = P.ck_b = 0;
    P.idx = 0;
}

// Годуємо по одному байту. Коли зібрано валідний пакет — кличемо ubx_dispatch.
void ubx_feed(uint8_t b, uint32_t now_ms) {
    P.last_byte_ms = now_ms;    // будь-який байт освіжає таймер простою

    switch (P.state) {
    case UST_SYNC1:
        if (b == UBX_SYNC1) P.state = UST_SYNC2;
        break;                   // поки не побачили B5 — крутимося тут

    case UST_SYNC2:
        // Тонкість: якщо після B5 прийшов не 62, а знову B5 — це може бути
        // початок СПРАВЖНЬОЇ сигнатури; лишаємось у SYNC2, не падаємо в SYNC1.
        if (b == UBX_SYNC2)      P.state = UST_CLASS;
        else if (b != UBX_SYNC1) P.state = UST_SYNC1;
        break;

    case UST_CLASS:
        P.msg_class = b;
        P.ck_a = P.ck_b = 0;    // сума рахується від class — обнуляємо саме тут
        ck_step(b);
        P.state = UST_ID;
        break;

    case UST_ID:
        P.msg_id = b; ck_step(b);
        P.state = UST_LEN1;
        break;

    case UST_LEN1:
        P.len = b; ck_step(b);
        P.state = UST_LEN2;
        break;

    case UST_LEN2:
        P.len |= (uint16_t)b << 8;   // little-endian: старший байт довжини
        ck_step(b);
        P.idx = 0;
        // КРИТИЧНА перевірка стелі: брехлива довжина від шуму не сміє
        // переповнити buf. Не влазить — це не наш пакет, назад у пошук.
        if (P.len == 0)               P.state = UST_CKA;         // порожній payload
        else if (P.len <= UBX_BUF_MAX) P.state = UST_PAYLOAD;
        else                          ubx_reset();               // задовга — відкидаємо
        break;

    case UST_PAYLOAD:
        P.buf[P.idx++] = b; ck_step(b);
        if (P.idx >= P.len) P.state = UST_CKA;   // набрали рівно len байтів
        break;                                    // тут сигнатуру НЕ шукаємо — лічимо байти

    case UST_CKA:
        P.rx_cka = b;           // прийнятий CK_A запам'ятали, чекаємо CK_B
        P.state = UST_CKB;
        break;

    case UST_CKB:
        // Обчислені ck_a/ck_b уже готові (копилися на льоту). Звіряємо.
        if (P.rx_cka == P.ck_a && b == P.ck_b) {
            ubx_dispatch(P.msg_class, P.msg_id, P.buf, P.len);  // валідний пакет!
        }
        ubx_reset();            // хай там як — назад у чистий стан
        break;
    }
}
