// ОТРУТА в будь-якому кооперативному світі
static int pt_sensor_BAD(pt_t *pt) {
    PT_BEGIN(pt);
    for (;;) {
        int raw = adc_read_slow();     // блокує 30 мс усередині
        delay(20);                     // ← і ще 20 мс явного блокування
        publish(heavy_filter(raw));    // ← а тут 15 мс лічби без жодної паузи
        PT_WAIT_UNTIL(pt, next_tick());
    }
    PT_END(pt);
}
