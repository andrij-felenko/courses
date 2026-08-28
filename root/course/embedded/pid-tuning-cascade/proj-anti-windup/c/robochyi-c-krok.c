// Один крок ПІД. setpoint — завдання, meas — вимір, dt — ВИМІРЯНИЙ крок часу.
// Повертає обмежений вихід u, готовий іти прямо на привід.
float pid_update(pid_t *p, float setpoint, float meas, float dt)
{
    // ── 0. Захист від хворого dt (пропущений тик, перший виклик) ──────────
    if (dt <= 0.0f) return 0.0f;          // безглуздий крок — нічого не робимо

    // ── 1. Перший виклик: підхопити вимір, не рахувати фальшиву похідну ───
    if (!p->initialized) {
        p->meas_prev  = meas;             // "попередній" = поточний → похідна 0
        p->deriv_filt = 0.0f;
        p->initialized = true;
    }

    // ── 2. Помилка (з вагою завдання для P) ──────────────────────────────
    float e     = setpoint - meas;        // звичайна помилка (для I)
    float e_p   = p->b * setpoint - meas; // зважена помилка для пропорційної

    // ── 3. Похідна ВІД ВИМІРУ, крізь одно-полюсний фільтр ─────────────────
    //     (беремо старий вимір і старий стан фільтра — ДО оновлення)
    float d_raw = -(meas - p->meas_prev) / dt;    // мінус: похідна помилки = −d(вимір)
    float tau_d = (p->Kp != 0.0f) ? (p->Kd / p->Kp) / p->N : 0.0f;
    float alpha = dt / (dt + tau_d);              // прив'язка фільтра до часу
    p->deriv_filt += alpha * (d_raw - p->deriv_filt);
    float d_term = p->Kd * p->deriv_filt;

    // ── 4. Пробний інтеграл і НЕОБМЕЖЕНИЙ вихід ───────────────────────────
    float integral_try = p->integral + p->Ki * e * dt;   // Ki всередині суми
    float u_unsat = p->Kp * e_p + integral_try + d_term;

    // ── 5. Обрізання до фізичних меж ──────────────────────────────────────
    float u = u_unsat;
    if (u > p->u_max) u = p->u_max;
    if (u < p->u_min) u = p->u_min;

    // ── 6. Анти-віндап — АЖ ТЕПЕР, коли відомо, чи обрізали ───────────────
    if (p->aw == AW_CLAMP) {
        // затиск: приймаємо пробний інтеграл, ЯКЩО не заганяємо глибше в стелю
        bool push_high = (u_unsat > p->u_max) && (e > 0.0f);
        bool push_low  = (u_unsat < p->u_min) && (e < 0.0f);
        if (!push_high && !push_low)
            p->integral = integral_try;   // інакше — лишаємо старий інтеграл
    } else { // AW_BACKCALC
        // зворотний перерахунок: різниця (дав − хотів) підтягує інтеграл назад
        p->integral += (p->Ki * e + p->Kaw * (u - u_unsat)) * dt;
    }

    // ── 7. Зберегти стан для наступного кроку ─────────────────────────────
    p->meas_prev = meas;
    return u;
}
