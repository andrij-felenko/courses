// Повільна база (зсунута ліворуч на 6 — це ділення на 64 у цілих числах)
uint32_t baseline = 0;        // зберігаємо базу в 64× збільшеному масштабі
const uint16_t TOUCH_DELTA = 12;   // поріг стрибка над базою, у одиницях n

void setup() {
    Serial.begin(115200);
    baseline = (uint32_t)measure_pad() << 6;  // початкова база з першого заміру
}

void loop() {
    uint16_t raw = measure_pad();
    uint16_t base = baseline >> 6;            // поточна база у звичайних одиницях

    bool touched = (raw > base + TOUCH_DELTA); // дотик = стрибок над базою

    // База доганяє сире значення ПОВІЛЬНО — і лише коли пальця немає,
    // щоб дотик не "розчинився" у підтягнутій базі.
    if (!touched)
        baseline += ((int32_t)((uint32_t)raw << 6) - (int32_t)baseline) >> 6;

    Serial.println(touched ? "TOUCH" : "----");
    delay(20);                                // ~50 замірів за секунду
}
