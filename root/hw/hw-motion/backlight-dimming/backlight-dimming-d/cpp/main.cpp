// ESP32: ШІМ підсвітки на ніжку EN струмового драйвера.
// Ціль: частота вище 1250 Гц (зона безпеки IEEE 1789) + якнайбільше кроків.
const int CH = 0, BL_EN = 25;
const int FREQ = 2000;     // 2 кГц — вище порога 1250 Гц
const int BITS = 12;       // 12 біт ⇒ 4096 кроків яскравості

void backlight_init() {
    ledcSetup(CH, FREQ, BITS);     // повертає 0, якщо пара (FREQ,BITS) недосяжна
    ledcAttachPin(BL_EN, CH);
}
void backlight_set(uint16_t level) {   // level: 0..4095
    ledcWrite(CH, level);
}
