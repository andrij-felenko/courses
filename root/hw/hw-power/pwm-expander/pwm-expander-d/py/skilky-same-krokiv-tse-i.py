# MicroPython: той самий запис по I2C через machine.I2C.
# Регістри каналу йдуть четвірками: ON_L, ON_H, OFF_L, OFF_H.
def pwm_set_duty(ch, off_count):
    reg = 0x06 + 4 * ch                      # база регістрів каналу ch
    buf = bytes((
        0x00, 0x00,                          # ON = 0  (вмикаємось на початку)
        off_count & 0xFF,                    # OFF молодший байт
        off_count >> 8,                      # OFF старший байт (лише 4 біти значущі)
    ))
    i2c.writeto_mem(EXPANDER_ADDR, reg, buf)

# 40 % на каналі 5:
pwm_set_duty(5, int(0.40 * 4096))            # → 1638
