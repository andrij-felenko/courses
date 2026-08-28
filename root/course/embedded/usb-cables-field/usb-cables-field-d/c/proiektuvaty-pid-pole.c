// Гістерезис brownout: падаємо низько, а вмикаємось назад із запасом,
// щоб не «дзеленчати» на межі (це саме те дрижання «раз із трьох»).
#define BROWNOUT_TRIP_MV    4000   // нижче цього — переходимо в економний режим
#define BROWNOUT_CLEAR_MV   4300   // назад у повний режим лише вище цього (запас 300 мВ)

static bool low_power_mode = false;

void power_supervise(uint16_t vbus_mv) {
    if (!low_power_mode && vbus_mv < BROWNOUT_TRIP_MV) {
        low_power_mode = true;         // просіли — стишуємо апетит, а не падаємо
        reduce_load();                 // прибрати некритичне: підсвітку, радіо, тактову
    } else if (low_power_mode && vbus_mv > BROWNOUT_CLEAR_MV) {
        low_power_mode = false;        // напруга повернулась із запасом — знову повний режим
        restore_load();
    }
    // проміжок 4000..4300 — «мертва зона» гістерезису: нічого не міняємо,
    // саме вона й не дає системі дрижати на самій межі порога
}
