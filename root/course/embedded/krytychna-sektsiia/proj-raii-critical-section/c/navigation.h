#ifndef NAVIGATION_H
#define NAVIGATION_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Телеметричний пакет навігації: пишеться з переривання GNSS (100 Гц),
 * читається фоновим циклом для радіопередачі.
 */
typedef struct {
    int32_t  latitude;      /* 1e-7 градуса */
    int32_t  longitude;     /* 1e-7 градуса */
    int32_t  altitude_mm;
    uint64_t timestamp_us;
} navigation_data_t;

void     navigation_init(void);
void     navigation_update(const navigation_data_t *fix);   /* контекст: ISR */
bool     navigation_get_snapshot(navigation_data_t *out);   /* контекст: задача */
uint32_t navigation_updates(void);

/* Крок фонового циклу: віддати радіоканалу узгоджений знімок. */
void telemetry_step(void);

/* Символ із векторної таблиці. */
void GNSS_IRQHandler(void);

/*
 * Драйвери плати: у прошивці їх дає BSP, у хостових тестах — фейки.
 * gnss_read_fix повертає false, якщо кадр битий або ще не готовий.
 */
bool gnss_read_fix(navigation_data_t *out);
void radio_send(const navigation_data_t *fix);

#endif /* NAVIGATION_H */
