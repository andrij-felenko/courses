enum Level : uint8_t { ERR, WARN, INFO, DEBUG, VERBOSE };
static const char* NAME[] = { "ERR", "WRN", "INF", "DBG", "VRB" };

#define LOG_LEVEL  DEBUG        // поріг: усе, що нижче, компілятор викине

// ── Кільцевий буфер останніх рядків ──────────────────────────────────────
static const int N = 32;       // скільки «останніх слів» тримаємо
static char ring[N][80];       // фіксовані рядки — без купи, без фрагментації
static int  head = 0;

void ring_push(const char* s) {
    strncpy(ring[head], s, sizeof(ring[0]) - 1);
    ring[head][sizeof(ring[0]) - 1] = '\0';
    head = (head + 1) % N;      // по колу: новий затирає найстаріший
}

// ── Один лог-рядок: час · рівень · мітка · повідомлення ──────────────────
void log_line(Level lv, const char* tag, const char* msg) {
    char buf[80];
    snprintf(buf, sizeof(buf), "%lu [%s] %s: %s",
             millis(), NAME[lv], tag, msg);
    ring_push(buf);            // завжди — у кільце
    Serial.println(buf);       // і на екран (поки дивимось наживо)
}

// Макрос ховає поріг: при level > LOG_LEVEL весь виклик зникне з прошивки
#define LOG(level, tag, msg)  do { if ((level) <= LOG_LEVEL) log_line((level), (tag), (msg)); } while (0)

// ── При аварії — висипати кільце від найстарішого ────────────────────────
void dump_ring() {
    Serial.println(">>> останні слова:");
    for (int i = 0; i < N; i++)
        Serial.println(ring[(head + i) % N]);   // від найстарішого до свіжого
}
