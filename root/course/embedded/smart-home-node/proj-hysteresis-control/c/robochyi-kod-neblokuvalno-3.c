#define MIN_ON_MS    30000U     // раз увімкнувши — тримати ≥ 30 с
#define MIN_OFF_MS   30000U     // раз вимкнувши — тримати ≥ 30 с

static uint32_t t_last_switch = 0;   // коли востаннє клацнули реле

// Спроба перемкнути реле в бажаний стан want, але не раніше мінімального часу.
// Повертає true, якщо перемикання відбулося.
static bool try_switch(bool want, uint32_t now) {
    if (want == heater_on) return false;             // вже в потрібному стані
    uint32_t min_hold = heater_on ? MIN_ON_MS : MIN_OFF_MS;
    if (now - t_last_switch < min_hold) return false; // ще рано — тримаємо стан
    heater_on = want;
    relay_set(want);
    t_last_switch = now;
    return true;
}
