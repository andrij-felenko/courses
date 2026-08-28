static bool g_evq_overflowed = false;   // чи витісняли щось через переповнення
static uint32_t g_evq_dropped = 0;      // скільки саме подій загубили

// Покласти подію в чергу. Ніколи не блокує й ніколи не падає.
static void evq_push(uint8_t type, uint32_t ts,
                     const char *data, uint8_t data_len) {
    event_t *e = &g_evq.buf[g_evq.head];

    // Кільце повне → витісняємо найстарішу (drop-oldest) і фіксуємо втрату.
    if (g_evq.count == EVQ_CAP) {
        g_evq.tail = (g_evq.tail + 1) % EVQ_CAP;   // забули найдавнішу
        g_evq.count--;
        g_evq_overflowed = true;
        g_evq_dropped++;
    }

    // Заповнюємо новий запис.
    e->seq  = ++g_evq.next_seq;      // наскрізний номер, монотонний
    e->ts   = ts;
    e->type = type;
    e->len  = data_len < EVQ_PAYLOAD ? data_len : EVQ_PAYLOAD;
    memcpy(e->payload, data, e->len);

    g_evq.head = (g_evq.head + 1) % EVQ_CAP;
    g_evq.count++;

    evq_persist_one(e);             // дублюємо в NVS — переживе перезавантаження
}
