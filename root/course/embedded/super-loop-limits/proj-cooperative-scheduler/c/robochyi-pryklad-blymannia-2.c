// Протопотік блимання: увімкни — почекай — вимкни — почекай — знову
static int pt_blink(pt_t *pt) {
    static uint32_t t0;                // ⚠ static: мусить пережити паузу (див. нижче)
    PT_BEGIN(pt);
    for (;;) {
        led_write(1);
        t0 = millis();
        PT_WAIT_UNTIL(pt, timer_expired(t0, 500));   // «горю» 500 мс
        led_write(0);
        t0 = millis();
        PT_WAIT_UNTIL(pt, timer_expired(t0, 500));   // «темно» 500 мс
    }
    PT_END(pt);
}

// Протопотік давача: чекай строку — зніми — опублікуй — знову
static int pt_sensor(pt_t *pt) {
    static uint32_t t0;
    PT_BEGIN(pt);
    for (;;) {
        t0 = millis();
        PT_WAIT_UNTIL(pt, timer_expired(t0, 200));   // раз на 200 мс
        publish(sensor_read());
    }
    PT_END(pt);
}
