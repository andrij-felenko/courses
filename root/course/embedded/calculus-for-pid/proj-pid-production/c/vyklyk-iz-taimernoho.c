/* Приклад для Cortex-M: PID у перериванні таймера на ~1 кГц.
   dt міряємо за апаратним лічильником — тож плаваючий інтервал урахований чесно. */

#define TICKS_PER_SEC  1000000UL      /* лічильник тикає на 1 МГц (1 тик = 1 мкс) */

static pid_t heater;
static volatile float control_output = 0.0f;
static uint32_t last_ticks = 0;

/* Обробник переривання таймера — викликається апаратно кожні ~1 мс */
void TIM_IRQHandler(void)
{
    TIM_ClearITPending();                      /* скинути прапорець переривання */

    /* --- виміряти реальний dt від попереднього виклику --- */
    uint32_t now = timer_read_counter();       /* поточне значення лічильника */
    uint32_t d   = now - last_ticks;           /* різниця (беззнакова: коректна й при переповненні) */
    last_ticks   = now;
    float dt = (float)d / (float)TICKS_PER_SEC; /* у секундах */

    /* захист від патологій: пропущене переривання чи перший запуск */
    if (dt <= 0.0f || dt > 0.05f) dt = 0.001f;  /* підстрахувати номінальним 1 мс */

    /* --- прочитати датчик, порахувати крок, виставити вихід --- */
    float y  = adc_read_temperature();          /* вимір */
    float sp = setpoint_get();                  /* поточна уставка */

    control_output = pid_step(&heater, sp, y, dt);

    pwm_set_duty(control_output);               /* на виконавчий орган (нагрівач) */
}
