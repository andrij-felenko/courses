struct Sensor { float scale; };

Sensor* find_sensor(uint8_t id) {
    if (id < count) return &table[id];
    return nullptr;                 // не знайшли — повертаємо порожній
}

void loop() {
    Sensor* s = find_sensor(99);    // такого id нема → s == nullptr
    float v = raw * s->scale;       // ← звернення за порожнім покажчиком
}
