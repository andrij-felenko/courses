// Пошук першого відлуння вище СПАДНОГО порогу (після бланкування дзвону)
// adc_read() — миттєва амплітуда з приймача; повертає час польоту в мкс, 0 — нема цілі
uint32_t pick_echo(uint32_t blank_us, uint32_t timeout_us) {
    uint32_t t0 = micros();
    while (micros() - t0 < blank_us) { /* глуха зона: пластина ще дзвенить */ }
    while (micros() - t0 < timeout_us) {
        uint32_t t = micros() - t0;
        // поріг високий одразу після імпульсу, спадає з часом:
        uint16_t thr = THR_MIN + (THR_MAX - THR_MIN) * (timeout_us - t) / timeout_us;
        if (adc_read() > thr)          // перший сплеск вище живого порогу
            return t;                  // це і є час польоту до цілі
    }
    return 0;                          // тиша — цілі в діапазоні нема
}
