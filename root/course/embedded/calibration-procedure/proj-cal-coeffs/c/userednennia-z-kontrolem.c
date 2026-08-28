#define AVG_N            512u   // відліків на опору; √512 ≈ 22.6 → шум /22.6
#define AVG_TIMEOUT_MS   30000u // якщо за 30 с не набрали — давач мовчить
#define AVG_MAX_SPREAD   2000   // допустимий розмах (max−min) сирих кодів

// Один крок усереднення; повертає true, коли набір завершено (успіх чи ні).
static bool average_step(uint32_t t, int32_t *avg_out)
{
    if (t - cal.t_enter > AVG_TIMEOUT_MS) {     // давач не віддає відліки
        cal_abort(CAL_ERR_NOISY);
        return false;
    }

    int32_t r = sensor_read_raw();
    cal.acc += r;
    if (r < cal.raw_min) cal.raw_min = r;
    if (r > cal.raw_max) cal.raw_max = r;
    cal.n++;
    ui_progress(cal.n, AVG_N);

    if (cal.n < AVG_N) return false;            // ще набираємо

    // Набір завершено: перевіряємо розкид, перш ніж довіряти середньому.
    int32_t spread = cal.raw_max - cal.raw_min;
    if (spread > AVG_MAX_SPREAD) {
        cal_abort(CAL_ERR_NOISY);               // зашумлена точка — не записуємо
        return false;
    }

    // Середнє з округленням (а не зрізанням): +N/2 перед діленням.
    *avg_out = (int32_t)((cal.acc + (int64_t)AVG_N / 2) / AVG_N);
    return true;
}

static void avg_low_step(uint32_t t)
{
    int32_t avg;
    if (average_step(t, &avg)) {
        cal.raw_low = avg;
        cal.state   = CAL_WAIT_HIGH;
        ui_prompt("Поставте ВЕРХНЮ опору (відому гирю) і натисніть «зняти»");
    }
}

static void avg_high_step(uint32_t t)
{
    int32_t avg;
    if (average_step(t, &avg)) {
        cal.raw_high = avg;
        cal.state    = CAL_COMPUTE;     // обидві опори зняті — час рахувати
    }
}
