#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#pragma pack(push, 1)
/* Сирий бінарний пакет Subframe 4 Page 18 (упакований) */
typedef struct {
    int8_t  alpha0_raw; /* LSB = 2^-30 s */
    int8_t  alpha1_raw; /* LSB = 2^-27 s/semi-circle */
    int8_t  alpha2_raw; /* LSB = 2^-24 s/semi-circle^2 */
    int8_t  alpha3_raw; /* LSB = 2^-24 s/semi-circle^3 */
    int8_t  beta0_raw;  /* LSB = 2^11 s */
    int8_t  beta1_raw;  /* LSB = 2^14 s/semi-circle */
    int8_t  beta2_raw;  /* LSB = 2^16 s/semi-circle^2 */
    int8_t  beta3_raw;  /* LSB = 2^16 s/semi-circle^3 */
} gps_klobuchar_raw_t;
#pragma pack(pop)

/* Декодовані фізичні параметри у міжнародних одиницях */
typedef struct {
    double alpha[4];    /* Альфа-коефіцієнти амплітуди (с, с/напівколо, ...) */
    double beta[4];     /* Бета-коефіцієнти періоду (с, с/напівколо, ...) */
    uint32_t tow_sec;   /* Час тижня GPS (Time of Week) */
    bool   is_valid;    /* Прапорець цілісності й коректності декодування */
} gps_klobuchar_decoded_t;

/**
 * Декодує сирі біти супутникового кадру GPS у фізичні параметри Klobuchar.
 */
static inline void gps_klobuchar_decode(const gps_klobuchar_raw_t* raw, uint32_t tow, gps_klobuchar_decoded_t* out) {
    out->alpha[0] = raw->alpha0_raw * pow(2.0, -30);
    out->alpha[1] = raw->alpha1_raw * pow(2.0, -27);
    out->alpha[2] = raw->alpha2_raw * pow(2.0, -24);
    out->alpha[3] = raw->alpha3_raw * pow(2.0, -24);

    out->beta[0]  = raw->beta0_raw  * pow(2.0, 11);
    out->beta[1]  = raw->beta1_raw  * pow(2.0, 14);
    out->beta[2]  = raw->beta2_raw  * pow(2.0, 16);
    out->beta[3]  = raw->beta3_raw  * pow(2.0, 16);

    out->tow_sec  = tow;
    out->is_valid = true;
}
