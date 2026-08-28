// Стан «безпека»: за замовчуванням TRUE — виходи заблоковано.
// Прокидаємося в безпечному стані самі собою, а не сподіваємось,
// що хтось нас заблокує.
static volatile bool safety_on = true;

// Найнижча ланка виводу: сигнал на кожен двигун формує IO-чип.
// Хоч би що прислав головний процесор — доки safety_on, виходить нуль.
void io_pwm_output(const uint16_t pwm[NUM_MOTORS]) {
    if (safety_on) {
        for (int i = 0; i < NUM_MOTORS; i++)
            pwm_write(i, PWM_DISABLED);   // виходи мертві, крапка
        return;
    }
    for (int i = 0; i < NUM_MOTORS; i++)
        pwm_write(i, pwm[i]);             // сюди доходимо ЛИШЕ коли знято
}
