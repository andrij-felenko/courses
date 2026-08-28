// ── Словник подій: ID замість рядків ──────────────────────────────────────
enum LogId : uint8_t {
    LOG_BOOT    = 0,   // "boot"
    LOG_TEMP    = 1,   // "temp=%d mV"
    LOG_VBAT_LOW = 2,  // "VBAT low %d"
};

// ── Кадр: [0x7E маркер][id][n байтів аргументів][XOR контроль] ────────────
void blog(uint8_t id, const void* args, uint8_t n) {
    uint8_t xor_sum = 0x7E ^ id ^ n;
    Serial.write(0x7E);          // маркер-початок (ресинхронізація)
    Serial.write(id);
    Serial.write(n);
    const uint8_t* p = (const uint8_t*)args;
    for (uint8_t i = 0; i < n; i++) {
        Serial.write(p[i]);
        xor_sum ^= p[i];
    }
    Serial.write(xor_sum);       // контрольний байт (XOR усього кадру)
}

// ── Макрос: одна змінна, sizeof автоматично ────────────────────────────────
#define BLOG(id, val)  do { auto _v = (val); blog((id), &_v, sizeof(_v)); } while(0)

// ── Використання ──────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    blog(LOG_BOOT, nullptr, 0);        // подія без аргументів (n=0)
}

void loop() {
    int16_t temp_mv = (int16_t)analogReadMilliVolts(34);
    BLOG(LOG_TEMP, temp_mv);           // int16_t → 2 байти сирих у кадр
    // якщо напруга критична — сигналізуємо
    int16_t vbat_mv = (int16_t)analogReadMilliVolts(35);
    if (vbat_mv < 3300) {
        BLOG(LOG_VBAT_LOW, vbat_mv);
    }
    delay(100);
}
