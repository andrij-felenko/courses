// Викликати ЧАСТО й КОРОТКО — напр. раз на 1–5 мс із головного циклу.
void cal_step(void)
{
    uint32_t t = now_ms();

    // Оператор може скасувати з будь-якого робочого стану.
    if (cal.state > CAL_IDLE && cal.state < CAL_DONE && op_pressed_abort()) {
        cal_abort(CAL_ERR_NONE);
        return;
    }

    switch (cal.state) {

    case CAL_IDLE:
        // Спокій: працює старе калібрування. Старт — через cal_request_start().
        break;

    case CAL_WARMUP:    warmup_step(t);    break;
    case CAL_WAIT_LOW:  wait_low_step(t);  break;
    case CAL_AVG_LOW:   avg_low_step(t);   break;
    case CAL_WAIT_HIGH: wait_high_step(t); break;
    case CAL_AVG_HIGH:  avg_high_step(t);  break;
    case CAL_COMPUTE:   compute_step(t);   break;
    case CAL_SAVE:      save_step(t);      break;

    case CAL_DONE:
    case CAL_ABORT:
        // Термінальні: головний цикл забере нас назад у робоче читання.
        break;
    }
}

// Зовнішня команда «почати калібрування» (кнопка, команда по UART).
void cal_request_start(float x_low, float x_high)
{
    if (cal.state != CAL_IDLE && cal.state != CAL_DONE && cal.state != CAL_ABORT)
        return;                          // вже йде калібрування — не перезапускаємо

    cal = (cal_ctx_t){ .state = CAL_WARMUP, .x_low = x_low, .x_high = x_high };
    cal.t_enter = now_ms();
    ui_prompt("Прогрів... не чіпайте давач");
}
