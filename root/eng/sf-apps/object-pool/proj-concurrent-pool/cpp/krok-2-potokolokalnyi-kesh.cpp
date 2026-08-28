constexpr int BATCH     = 32;              // скільки брати/віддавати гуртом
constexpr int CACHE_CAP = 2 * BATCH;       // місткість магазина

struct Magazine { Conn* slot[CACHE_CAP]; int n = 0; };
thread_local Magazine mag;                 // ← приватний для потоку: 0 синхронізації

Conn* acquire() {
    if (mag.n == 0)                        // локально порожньо?
        refill();                          // ← рідкісний вихід до шарду: візьмемо БАТЧ
    if (mag.n == 0)
        return grow_or_wait();             // геть порожньо: рости / чекати / таймаут
    return mag.slot[--mag.n];              // ← ГАРЯЧИЙ ШЛЯХ: локальний pop, без атоміків
}

void release(Conn* c) {
    c->reset();                            // чистимо ДО того, як об'єкт стане спільним
    if (mag.n == CACHE_CAP)                // локально повно?
        flush();                           // ← рідкісний вихід: віддамо БАТЧ назад
    mag.slot[mag.n++] = c;                 // ← ГАРЯЧИЙ ШЛЯХ: локальний push
}

void refill() {                            // амортизація: один вихід — BATCH об'єктів
    Shard& s = my_shard();
    for (int i = 0; i < BATCH; ++i) {
        Conn* c = s.free.pop();            // звернення до спільної структури
        if (!c) break;
        mag.slot[mag.n++] = c;
    }
}
void flush() {
    Shard& s = my_shard();
    for (int i = 0; i < BATCH; ++i)
        s.free.push(mag.slot[--mag.n]);
}
