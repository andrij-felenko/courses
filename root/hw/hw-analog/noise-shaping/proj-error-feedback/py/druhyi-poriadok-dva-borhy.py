PWM_TOP =   500
IN_MAX  = 65535

# Формувач шуму 2-го порядку. NTF = (1 - z^-1)^2.
def shape2(sample):
    # поправка входу: 2*e1 - e2  (розкриті дужки (1 - z^-1)^2)
    u = sample + 2 * shape2.e1 - shape2.e2

    level = (u * PWM_TOP + IN_MAX // 2) // IN_MAX
    level = max(0, min(level, PWM_TOP))

    y = (level * IN_MAX + PWM_TOP // 2) // PWM_TOP
    e = u - y                            # нова похибка

    shape2.e2 = shape2.e1                # ЗСУВ станів: спершу старе
    shape2.e1 = e                        # тоді нове

    return level

shape2.e1 = shape2.e2 = 0                # дві останні похибки (масштаб входу)
