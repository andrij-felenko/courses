#include <stdint.h>
#include <stdbool.h>

/* Безпечний розбір сирих 12-бітних відліків акселерометра */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} accel_raw_t;

/* Розбір кадру з лівим вирівнюванням (Left-aligned, LIS3DH default) */
accel_raw_t parse_accel_left_aligned(const uint8_t buf[6]) {
    accel_raw_t out;
    /* Збираємо 16-бітне слово та зсуваємо арифметично на 4 розряди вправо */
    int16_t raw_x = (int16_t)((uint16_t)buf[0] | ((uint16_t)buf[1] << 8));
    int16_t raw_y = (int16_t)((uint16_t)buf[2] | ((uint16_t)buf[3] << 8));
    int16_t raw_z = (int16_t)((uint16_t)buf[4] | ((uint16_t)buf[5] << 8));

    out.x = raw_x >> 4;
    out.y = raw_y >> 4;
    out.z = raw_z >> 4;
    return out;
}

/* Розбір кадру з правим вирівнюванням (Right-aligned, 12-бітний АЦП) */
accel_raw_t parse_accel_right_aligned(const uint8_t buf[6]) {
    accel_raw_t out;
    uint16_t u_x = (uint16_t)buf[0] | ((uint16_t)buf[1] << 8);
    uint16_t u_y = (uint16_t)buf[2] | ((uint16_t)buf[3] << 8);
    uint16_t u_z = (uint16_t)buf[4] | ((uint16_t)buf[5] << 8);

    /* Знакове розширення через подвійний арифметичний зсув */
    out.x = (int16_t)(u_x << 4) >> 4;
    out.y = (int16_t)(u_y << 4) >> 4;
    out.z = (int16_t)(u_z << 4) >> 4;
    return out;
}
