from machine import Pin, PWM

VDD_MV = 3300            # живлення в мілівольтах
pwm = PWM(Pin(0))        # апаратний ШІМ на ніжці; duty_u16 бере 0..65535
pwm.freq(62_500)

# Перевести бажану напругу (мВ) на код шпаруватості й виставити її.
# Залізо саме формує ШІМ; процесор лише оновлює число duty.
def dac_set_mv(want_mv):
    want_mv = min(want_mv, VDD_MV)               # не вище живлення
    # duty = want_mv / VDD * 65535 з округленням до найближчого:
    duty = (want_mv * 65535 + VDD_MV // 2) // VDD_MV
    pwm.duty_u16(duty)
