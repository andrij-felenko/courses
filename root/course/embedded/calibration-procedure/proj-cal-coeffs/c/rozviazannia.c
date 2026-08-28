// Тип cal_t і розв'язувач cal_two_point — з теми. Тут — обгортка з перевірками.
#define CAL_MIN_SPAN_X     1.0f     // мінімальна різниця еталонів (у фіз. одиницях)
#define CAL_K_NOMINAL      721.0f   // паспортний нахил (кодів на одиницю)
#define CAL_K_TOL          0.30f    // допуск нахилу: ±30 % від паспорта

static void compute_step(uint32_t t)
{
    (void)t;

    // 1) Опори мусять бути рознесені (і в правильному порядку).
    if (cal.x_high - cal.x_low < CAL_MIN_SPAN_X) {
        cal_abort(CAL_ERR_POINTS_CLOSE);
        return;
    }

    // 2) Та сама формула з теми: нахил і зсув.
    cal.result = cal_two_point(cal.raw_low,  cal.x_low,
                               cal.raw_high, cal.x_high);

    // 3) Перевірка здорового глузду: нахил у паспортному коридорі.
    float k = cal.result.k;
    if (k < CAL_K_NOMINAL * (1.0f - CAL_K_TOL) ||
        k > CAL_K_NOMINAL * (1.0f + CAL_K_TOL)) {
        cal_abort(CAL_ERR_RANGE);          // нахил поза здоровим коридором
        return;
    }
    if (!(k > 0.0f)) {                      // ловить і NaN, і 0, і від'ємний нахил
        cal_abort(CAL_ERR_RANGE);
        return;
    }

    cal.state = CAL_SAVE;                   // коефіцієнти здорові — час зберігати
}
