static cal_t  active_cal;          // чинні коефіцієнти в роботі
static bool   calibrated = false;  // чи можна вірити active_cal

// Викликати ОДИН раз на старті, ДО першого читання й ДО cal_step().
void measurement_init(void)
{
    calibrated = cal_store_read(&active_cal);   // підняти найновіше ціле з NVS
    if (!calibrated) {
        // Чесний стан: коефіцієнтів нема або побиті. НЕ вигадуємо їх.
        ui_prompt("Давач НЕ калібрований — запустіть калібрування");
        // тут típово: автозапуск cal_request_start(...) або блокування вимірів
    }
}

// Робоче читання: сирий код → фізична величина. Нечесні дані не повертаємо.
bool measurement_read(float *value_out)
{
    if (!calibrated) return false;              // нема чому вірити — і не вдаємо

    int32_t raw = sensor_read_raw();
    *value_out = cal_apply(&active_cal, raw);   // (raw − b)/k — формула з теми
    return true;
}

// Коли калібрувальний автомат дійшов до DONE — підхопити свіжі коефіцієнти.
void measurement_on_cal_done(void)
{
    if (cal.state == CAL_DONE) {
        active_cal = cal.result;                // нові коефіцієнти — одразу в роботу
        calibrated = true;
        cal.state  = CAL_IDLE;                  // автомат назад у спокій
    }
}
