typedef struct { float throttle; float turn; } guard_gain_t;

// Один такт сторожа. Викликати з тактом IMU (~100 Гц).
//   ax..az   — сирий акселерометр (однакові одиниці, напр. g)
//   gx, gy   — кутові швидкості крену й тангажу з гіроскопа (рад/с)
//   now_ms   — монотонний час, мс (для журналу)
// Повертає множники 0..1 на газ і на поворот.
guard_gain_t tipover_step(tipover_t *g,
                          float ax, float ay, float az,
                          float gx, float gy, uint32_t now_ms)
{
    // 1) Абсолютні кути з акселерометра (шумні, але без дрейфу)
    float acc_roll  = atan2f(ay, sqrtf(ax * ax + az * az));
    float acc_pitch = atan2f(-ax, sqrtf(ay * ay + az * az));

    // Перший виклик: засіваємо фільтр абсолютним кутом, щоб не повзти з нуля
    if (!g->inited) {
        g->roll  = acc_roll;
        g->pitch = acc_pitch;
        g->inited = true;
    }

    // 2) Комплементарний фільтр: гіроскоп веде швидко, акселерометр знімає дрейф
    float a = COMP_TAU / (COMP_TAU + IMU_DT);
    g->roll  = a * (g->roll  + gx * IMU_DT) + (1.0f - a) * acc_roll;
    g->pitch = a * (g->pitch + gy * IMU_DT) + (1.0f - a) * acc_pitch;

    // 3) Сумарний нахил від вертикалі: γ = arccos(cos φ · cos θ)
    float gamma = acosf(cosf(g->roll) * cosf(g->pitch));

    // 4) Запас відносно РОБОЧОЇ межі, обрізаний у [0, 1]
    float margin = gamma / g->phi_work;
    if (margin < 0.0f) margin = 0.0f;
    if (margin > 1.0f) margin = 1.0f;

    // 5) Множник газу: 1 у спокійній зоні, далі лінійно до 0 на межі
    float k;
    if (margin <= DEAD) {
        k = 1.0f;
    } else {
        k = (1.0f - margin) / (1.0f - DEAD);   // 1 → 0 на [DEAD..1]
    }

    // 6) Тривога з гістерезисом + журнал переходів
    bool was = g->alarm;
    if (!g->alarm && margin >= ALARM_ON)  g->alarm = true;
    if ( g->alarm && margin <= ALARM_OFF) g->alarm = false;
    if (g->alarm != was) {
        buzzer_set(g->alarm);                  // писк увімк/вимк
        tipover_log(now_ms, g->alarm, margin,  // рядок у журнал подій
                    g->roll, g->pitch, gamma);
    }

    // 7) Два множники: газ лінійно, поворот — квадрат (душимо сильніше)
    guard_gain_t out;
    out.throttle = k;
    out.turn     = k * k;      // k² : на межі поворот валиться швидше за газ
    return out;
}
