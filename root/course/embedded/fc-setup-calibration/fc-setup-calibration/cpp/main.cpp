// збережене з калібрування RC (у мкс), лежить у RC1_MIN/TRIM/MAX
const uint16_t rc_min  = 1095;   // стік у лівий упор
const uint16_t rc_trim = 1502;   // стік відпущено (центр)
const uint16_t rc_max  = 1918;   // стік у правий упор

// нормувати сирий імпульс у частку відхилення від центру: [-1 .. +1]
float rc_normalize(uint16_t pwm)
{
    if (pwm >= rc_trim)
        return (float)(pwm - rc_trim) / (rc_max - rc_trim);   // права половина
    else
        return (float)(pwm - rc_trim) / (rc_trim - rc_min);   // ліва половина
}

// приклад: приймач віддав 1710 мкс
// pwm >= trim → (1710 − 1502) / (1918 − 1502) = 208 / 416 = 0.50
// керування бачить +0.50 — рівно півкрена вправо, хоч який передавач
