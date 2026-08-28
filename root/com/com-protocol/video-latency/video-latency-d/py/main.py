# повний бюджет glass-to-glass для типового цифрового HD-FPV, мс
t_sensor = 18.0  # витримка/2 + зчитування CMOS
t_encode = 22.0  # кодек baseline, без B, zerolatency
t_link   =  8.0  # радіо, бітрейт уміщається в канал
t_buffer = 25.0  # ~1.5 кадру запасу проти джитера
t_decode = 12.0  # апаратний декодер, без переставлення
t_screen = 12.0  # 120 Гц + швидкий піксель

g2g = t_sensor + t_encode + t_link + t_buffer + t_decode + t_screen
# = 18 + 22 + 8 + 25 + 12 + 12 = 97 мс
