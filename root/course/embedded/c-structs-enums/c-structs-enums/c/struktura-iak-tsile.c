// зробити один вимір, повернувши цілу структуру:
Measurement read_sensor(void) {
    Measurement m;
    m.ts    = millis();
    m.value = adc_to_celsius(read_adc());
    m.ok    = 1;
    return m;               // повертаємо всю структуру
}

void use(void) {
    Measurement now = read_sensor();   // now — копія повернутого
    printf("%.1f°C\n", now.value);
}
