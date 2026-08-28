// БОРГ: те саме число живе трьома копіями. Хто знає, що їх рівно три?
void charge_indicator(float v) {
    if (v >= 4.20f) led_full();          // копія 1
}
void battery_protection(float v) {
    if (v >= 4.20f) cut_off_load();      // копія 2
}
void battery_log(float v) {
    if (v >= 4.20f) log_event(EVT_FULL); // копія 3
}
