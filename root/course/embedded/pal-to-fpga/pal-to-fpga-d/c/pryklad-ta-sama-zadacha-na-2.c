// НАЇВНО для CPLD: 256 незалежних усувачів деренчання
static uint8_t cnt[256];           // 256 лічильників
static uint8_t btn[256];           // 256 станів

void debounce_all(const uint8_t *raw) {
    for (int i = 0; i < 256; ++i) { // 256 копій тієї самої логіки
        if (raw[i] == btn[i])      cnt[i] = 0;
        else if (++cnt[i] >= 20) { btn[i] = raw[i]; cnt[i] = 0; }
    }
}
