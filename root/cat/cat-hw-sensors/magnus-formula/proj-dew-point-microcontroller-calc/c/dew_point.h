#ifndef DEW_POINT_H
#define DEW_POINT_H

// Формула Магнуса-Тетенса:
// Ts = (b * alpha) / (a - alpha)
// alpha = ln(RH/100) + (a * T) / (b + T)
// де a = 17.625, b = 243.04 (для води від -45 до +60 C)

// Метод 1: Точний розрахунок через math.h
float dew_point_math(float temp_c, float humidity_rh);

// Метод 2: Пошук за таблицею (Look-Up Table)
float dew_point_lut(float temp_c, float humidity_rh);

// Метод 3: Швидка апроксимація логарифма та експоненти
float dew_point_fast(float temp_c, float humidity_rh);

#endif // DEW_POINT_H
