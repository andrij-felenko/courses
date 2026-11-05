#include <stdint.h>
#include <stdbool.h>

/* Число ітерацій для 32-розрядної точності */
#define CORDIC_NUM_ITERATIONS 31

/* Масштабний множник A_N = 1/K у форматі Q2.30: 0.607252935 * 2^30 */
#define CORDIC_GAIN_INV_Q30 INT32_C(652032896)

/* Таблиця кутів arctan(2^-i) у форматі BAM (360 градусів = 2^32, тобто pi = 0x80000000) */
static const int32_t cordic_angles_bam[CORDIC_NUM_ITERATIONS] = {
    0x20000000, 0x12E4051E, 0x09FB385B, 0x051111D4,
    0x028B0D43, 0x0145D7E1, 0x00A2F61E, 0x00517C55,
    0x0028BE53, 0x00145F2F, 0x000A2F98, 0x000517CC,
    0x00028BE6, 0x000145F3, 0x0000A2FA, 0x0000517D,
    0x000028BE, 0x0000145F, 0x00000A30, 0x00000518,
    0x0000028C, 0x00000146, 0x000000A3, 0x00000051,
    0x00000029, 0x00000014, 0x0000000A, 0x00000005,
    0x00000003, 0x00000001, 0x00000001
};

/* Обчислення sin(theta) та cos(theta) у режимі обертання */
void cordic_calc_sin_cos(int32_t angle_bam, int32_t* out_sin_q30, int32_t* out_cos_q30) {
    int32_t x;
    int32_t y;
    int32_t z;

    /* Редукція квадранта: приведення кута до діапазону [-pi/2, +pi/2] */
    if (angle_bam > 0x40000000) {
        /* Другий квадрант: зміщення на -pi */
        x = -CORDIC_GAIN_INV_Q30;
        y = 0;
        z = (int32_t)((uint32_t)angle_bam - 0x80000000U);
    } else if (angle_bam < -0x40000000) {
        /* Третій квадрант: зміщення на +pi */
        x = -CORDIC_GAIN_INV_Q30;
        y = 0;
        z = (int32_t)((uint32_t)angle_bam + 0x80000000U);
    } else {
        /* Перший і четвертий квадранти */
        x = CORDIC_GAIN_INV_Q30;
        y = 0;
        z = angle_bam;
    }

    /* Основний ітераційний конвеєр CORDIC */
    for (int i = 0; i < CORDIC_NUM_ITERATIONS; ++i) {
        int32_t x_shift = x >> i;
        int32_t y_shift = y >> i;

        if (z >= 0) {
            x -= y_shift;
            y += x_shift;
            z -= cordic_angles_bam[i];
        } else {
            x += y_shift;
            y -= x_shift;
            z += cordic_angles_bam[i];
        }
    }

    *out_cos_q30 = x;
    *out_sin_q30 = y;
}

/* Перетворення декартових координат у полярні (векторний режим CORDIC) */
void cordic_calc_polar(int32_t x_in_q30, int32_t y_in_q30, int32_t* out_mag_q30, int32_t* out_phase_bam) {
    int32_t x;
    int32_t y;
    int32_t z;

    /* Попереднє розгортання: якщо x < 0, повертаємо вектор на 180 градусів */
    if (x_in_q30 < 0) {
        x = -x_in_q30;
        y = -y_in_q30;
        z = (y_in_q30 >= 0) ? (int32_t)0x7FFFFFFF : (int32_t)0x80000000;
    } else {
        x = x_in_q30;
        y = y_in_q30;
        z = 0;
    }

    /* Ітерації для обнулення координати Y */
    for (int i = 0; i < CORDIC_NUM_ITERATIONS; ++i) {
        int32_t x_shift = x >> i;
        int32_t y_shift = y >> i;

        if (y >= 0) {
            x += y_shift;
            y -= x_shift;
            z += cordic_angles_bam[i];
        } else {
            x -= y_shift;
            y += x_shift;
            z -= cordic_angles_bam[i];
        }
    }

    /* Масштабування модуля на A_N = 1/K: (x * A_N) >> 30 */
    int64_t scaled_mag = ((int64_t)x * CORDIC_GAIN_INV_Q30) >> 30;
    *out_mag_q30 = (int32_t)scaled_mag;
    *out_phase_bam = z;
}
