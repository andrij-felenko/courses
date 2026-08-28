/* Один крок PID. Викликати кожні dt секунд (dt — реальний, виміряний).
   sp — уставка (ціль), y — вимір датчика. Повертає керівний сигнал у [out_min, out_max]. */
float pid_step(pid_t *c, float sp, float y, float dt)
{
    /* --- Перший виклик: лише зарядити стан, без стрибка --- */
    if (!c->initialized) {
        c->y_prev = y;
        c->initialized = true;
    }

    float e = sp - y;                     /* похибка (для P та I) */

    /* --- P: пропорційна складова --- */
    float P = c->Kp * e;

    /* --- D: похідна ПО ВИМІРУ (не по похибці!) з фільтром 1-го порядку ---
       Знак «−»: диференціюємо −y, тож стрибок уставки не дає удару.
       dt стоїть у коефіцієнтах → стійко до плаваючого кроку. */
    if (c->Td > 0.0f) {
        float tau = c->Td / c->N;                 /* τ_f = Td/N */
        float a   = tau / (tau + dt);             /* пам'ять фільтра (→1 при малому dt) */
        c->D_term = a * c->D_term
                  - (c->Kp * c->Td / (tau + dt)) * (y - c->y_prev);
    } else {
        c->D_term = 0.0f;                          /* D вимкнено */
    }

    /* --- Попередній (необмежений) вихід --- */
    float u = P + (float)c->I_term + c->D_term;

    /* --- Обмеження виходу в межі виконавчого органу --- */
    float u_sat = u;
    if (u_sat > c->out_max) u_sat = c->out_max;
    if (u_sat < c->out_min) u_sat = c->out_min;

    /* --- Куди «відстежувати» інтеграл ---
       В автоматі — до обмеженого виходу (anti-windup, back-calculation).
       У ручному — до заданого оператором виходу (bumpless-перехід). */
    float track = c->manual ? c->man_out : u_sat;

    /* --- Оновлення інтеграла: власне I + зворотний перерахунок ---
       I_term += (Kp·dt/Ti)·e            ← накопичення похибки, У ОДИНИЦЯХ ВИХОДУ
               + (dt/Tt)·(track − u)     ← злив надлишку (windup / tracking)
       Множення на dt ДО додавання; накопичувач double не губить малих доданків. */
    if (c->Ti > 0.0f) {
        c->I_term += ((double)c->Kp * dt / c->Ti) * e;
    }
    if (c->Tt > 0.0f) {
        c->I_term += ((double)dt / c->Tt) * ((double)track - (double)u);
    }

    /* --- Запам'ятати вимір для наступної похідної --- */
    c->y_prev = y;

    /* --- Вихід --- */
    return c->manual ? c->man_out : u_sat;
}
