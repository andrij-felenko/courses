#include "sensor_si.h"

#include "fixedq16.h"

/* 0.061 мг/LSB = 0.000061 g; g0 = 9.80665 м/с²:
   0.000061 * 9.80665 = 0.00059820565 м/с² = 0.59820565 мм/с² на розряд. */
#define W_ACCEL16_MM_S2 Q16_CONST(0.59820565)
/* Після зсуву лівовирівняного кадру на 4 розряди вага розряду ×16. */
#define W_ACCEL12_MM_S2 Q16_CONST(9.5712904)
/* 0.00875 °/с * (pi/180) = 0.0001527163 рад/с = 0.1527163 мрад/с. */
#define W_GYRO_MRAD_S Q16_CONST(0.1527163)
/* 1/6842 Гаус = 100/6842 мкТл = 0.01461561 мкТл = 14.61561 нТл. */
#define W_MAG_NT Q16_CONST(14.61561)

/* Межі, за якими значення вже не фізичне, а наслідок збою кадру:
   ±16 g і ±2000 °/с з добрим запасом покривають ударні перевантаження. */
#define ACCEL_LIMIT_MM_S2 157000
#define GYRO_LIMIT_MRAD_S 40000

int32_t accel_lsb16_to_mm_s2(int16_t raw, int16_t zero) {
    const int32_t v = q16_scale_raw(raw, zero, W_ACCEL16_MM_S2);
    /* Насичення замість загортання знаку: при ударі краще «максимум угору»,
       ніж миттєвий стрибок на «максимум униз». */
    if (v > ACCEL_LIMIT_MM_S2) {
        return ACCEL_LIMIT_MM_S2;
    }
    if (v < -ACCEL_LIMIT_MM_S2) {
        return -ACCEL_LIMIT_MM_S2;
    }
    return v;
}

int32_t accel_lsb12_to_mm_s2(int16_t raw, int16_t zero) {
    const int32_t v = q16_scale_raw(raw, zero, W_ACCEL12_MM_S2);
    if (v > ACCEL_LIMIT_MM_S2) {
        return ACCEL_LIMIT_MM_S2;
    }
    if (v < -ACCEL_LIMIT_MM_S2) {
        return -ACCEL_LIMIT_MM_S2;
    }
    return v;
}

vec3_mm_s2_t accel_frame12_to_si(const int16_t raw[3], const int16_t zero[3]) {
    vec3_mm_s2_t out;
    const int16_t zx = (zero != 0) ? zero[0] : 0;
    const int16_t zy = (zero != 0) ? zero[1] : 0;
    const int16_t zz = (zero != 0) ? zero[2] : 0;

    out.x = accel_lsb12_to_mm_s2(raw[0], zx);
    out.y = accel_lsb12_to_mm_s2(raw[1], zy);
    out.z = accel_lsb12_to_mm_s2(raw[2], zz);
    return out;
}

uint32_t vec3_magnitude_mm_s2(vec3_mm_s2_t v) {
    /* Квадрат 157000 — це 2.5e10, у 32 біти не влазить: сума квадратів
       рахується у 64 бітах, корінь — цілочисельний. */
    const int64_t sx = (int64_t)v.x * (int64_t)v.x;
    const int64_t sy = (int64_t)v.y * (int64_t)v.y;
    const int64_t sz = (int64_t)v.z * (int64_t)v.z;
    return u64_isqrt((uint64_t)(sx + sy + sz));
}

int32_t gyro_lsb_to_mrad_s(int16_t raw, int16_t zero) {
    const int32_t v = q16_scale_raw(raw, zero, W_GYRO_MRAD_S);
    return sat_bits(v, 32u) > GYRO_LIMIT_MRAD_S
               ? GYRO_LIMIT_MRAD_S
               : (v < -GYRO_LIMIT_MRAD_S ? -GYRO_LIMIT_MRAD_S : v);
}

int32_t tmp117_to_mdeg_c(int16_t raw) {
    /* 125/16 — точний дріб, тому множення на 125 і зсув на 4 дають
       результат без похибки заокруглення масштабу. */
    return ((int32_t)raw * 125 + 8) >> 4;
}

int32_t mcp9808_to_mdeg_c(int16_t raw) {
    /* Очікується вже розширений за знаком 13-бітний відлік. */
    return ((int32_t)raw * 125 + 1) >> 1;
}

int32_t mag_lsb_to_nt(int16_t raw) {
    return q16_scale_raw(raw, 0, W_MAG_NT);
}

int32_t adc12_to_mv(uint16_t raw, uint16_t vref_mv) {
    if (raw > 4095u) {
        raw = 4095u; /* поза шкалою АЦП бути не може */
    }
    /* 4095 * 3300 = 13 513 500 — у uint16 лишилось би 13 084.
       Проміжок мусить бути 32-бітним, і лише потім ділення. */
    return (int32_t)(((uint32_t)raw * (uint32_t)vref_mv + 2047u) / 4095u);
}
