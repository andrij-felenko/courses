// Викликається бібліотекою, коли прийшов PUBACK на наше QoS-1 повідомлення.
static void on_puback(uint16_t acked_msg_id) {
    // (Зіставлення acked_msg_id ↔ seq бібліотека веде сама; тут ми знаємо,
    //  що підтверджено найстарішу відіслану — ту, що на tail.)
    if (g_evq.count == 0) return;

    event_t *e = &g_evq.buf[g_evq.tail];
    evq_forget_persisted(e->seq);              // прибрати з NVS-журналу
    g_evq.tail = (g_evq.tail + 1) % EVQ_CAP;   // ось тепер зсуваємо tail
    g_evq.count--;

    // Штовхаємо наступну, якщо ще є що слати.
    if (g_evq.count > 0) evq_flush();
}
