// кожна активна відмова дає кандидат-режим; беремо той, що з НАЙГЛИБШОЮ
// деградацією. Ранг зашитий у значення mode_t (більше = безпечніше/тяжче).
mode_t fsm_step_ranked(mode_t current, const health_t *h, float dt) {
    mode_t target = current;   // за замовчуванням — лишитись, де є

    // від найлегшої відмови до найтяжчої; кожна лише ПОГЛИБЛЮЄ ціль
    if (!h->gnss_ok)                         target = worse_of(target, MODE_LOITER);
    if (!debounce_link(h->rc_link, dt))      target = worse_of(target, MODE_RTL);
    if (batt_classify(h->batt_volt) == BATT_LOW)      target = worse_of(target, MODE_RTL);
    if (batt_classify(h->batt_volt) == BATT_CRITICAL) target = worse_of(target, MODE_LAND);
    if (!debounce_imu(h->imu_ok, dt))        target = worse_of(target, MODE_LAND);

    return target;
}
