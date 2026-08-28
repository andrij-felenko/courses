static pt_t blink_pt, sensor_pt;

void setup(void) {
    PT_INIT(&blink_pt);
    PT_INIT(&sensor_pt);
}

void loop(void) {
    pt_blink(&blink_pt);      // кожен викликається щооберту;
    pt_sensor(&sensor_pt);    // сам вирішить — робити чи вийти
}
