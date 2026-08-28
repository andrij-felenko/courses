// повний бюджет glass-to-glass для типового цифрового HD-FPV, мс
float t_sensor =  18.0f; // витримка/2 + зчитування CMOS
float t_encode =  22.0f; // кодек baseline, без B, zerolatency
float t_link   =   8.0f; // радіо, бітрейт уміщається в канал
float t_buffer =  25.0f; // ~1.5 кадру запасу проти джитера
float t_decode =  12.0f; // апаратний декодер, без переставлення
float t_screen =  12.0f; // 120 Гц + швидкий піксель

float g2g = t_sensor + t_encode + t_link + t_buffer + t_decode + t_screen;
// = 18 + 22 + 8 + 25 + 12 + 12 = 97 мс
