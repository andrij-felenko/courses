const int      PIN      = 5;
const uint32_t PERIOD   = 4000;          // повний вдих-видих, мс
extern uint16_t gammaLUT[256];           // таблиця гамми з попереднього кроку

void loop() {
    unsigned long now = millis();
    float phase = (now % PERIOD) / (float)PERIOD;     // 0..1, циклічно
    // синус робить плавний підйом і спад; зсуваємо в діапазон 0..1:
    float bright = (1.0f - cosf(phase * 2.0f * PI)) * 0.5f;   // 0→1→0
    uint8_t level = (uint8_t)(bright * 255.0f);
    ledcWrite(PIN, gammaLUT[level]);       // гамма + вивід — як ми вже вміємо
    // цикл лишається вільним для всього іншого
}
