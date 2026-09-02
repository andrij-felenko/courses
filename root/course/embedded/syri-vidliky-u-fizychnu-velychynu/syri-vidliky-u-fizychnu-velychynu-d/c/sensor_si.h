#ifndef SENSOR_SI_H
#define SENSOR_SI_H

#include <stdint.h>

/* Переведення сирих відліків у стандартні одиниці SI.
   Драйвер віддає мілі-одиниці цілим числом: мм/с², мрад/с, м°C, нТл, мВ.
   Так у формулах верхнього рівня немає ні float, ні магічних коефіцієнтів
   конкретної моделі давача. */

typedef struct {
    int32_t x; /* мм/с² */
    int32_t y;
    int32_t z;
} vec3_mm_s2_t;

/* Акселерометр ±2 g. Вага 16-бітного слова — 0.061 мг/LSB; якщо кадр був
   із лівим вирівнюванням і його вже зсунули на 4 розряди, вага виросла
   вшістнадцятеро — для цього окрема функція. */
int32_t accel_lsb16_to_mm_s2(int16_t raw, int16_t zero);
int32_t accel_lsb12_to_mm_s2(int16_t raw, int16_t zero);
/* zero може бути NULL — тоді зміщення нуля не віднімається. */
vec3_mm_s2_t accel_frame12_to_si(const int16_t raw[3], const int16_t zero[3]);
uint32_t vec3_magnitude_mm_s2(vec3_mm_s2_t v);

/* Гіроскоп ±250 °/с, 8.75 мград/с на розряд → мрад/с. */
int32_t gyro_lsb_to_mrad_s(int16_t raw, int16_t zero);

/* Термометри: вага — точний ступінь двійки, множення й зсув без Q16.16. */
int32_t tmp117_to_mdeg_c(int16_t raw);  /* 0.0078125 °C = 125/16 м°C */
int32_t mcp9808_to_mdeg_c(int16_t raw); /* 0.0625 °C = 125/2 м°C */

/* Магнітометр ±4 Гаус, 6842 LSB/Гаус → нТл. */
int32_t mag_lsb_to_nt(int16_t raw);

/* АЦП 12 біт → мілівольти. Приклад із розділу 6: множення робиться
   у 32 бітах, бо 4095 * 3300 переповнює 16-бітний тип. */
int32_t adc12_to_mv(uint16_t raw, uint16_t vref_mv);

#endif /* SENSOR_SI_H */
