# Стан «безпека»: за замовчуванням True — виходи заблоковано.
# Прокидаємося в безпечному стані самі собою, а не сподіваємось,
# що хтось нас заблокує.
safety_on = True

# Найнижча ланка виводу: сигнал на кожен двигун формує IO-чип.
# Хоч би що прислав головний процесор — доки safety_on, виходить нуль.
def io_pwm_output(pwm):
    if safety_on:
        for i in range(NUM_MOTORS):
            pwm_write(i, PWM_DISABLED)    # виходи мертві, крапка
        return
    for i in range(NUM_MOTORS):
        pwm_write(i, pwm[i])              # сюди доходимо ЛИШЕ коли знято
