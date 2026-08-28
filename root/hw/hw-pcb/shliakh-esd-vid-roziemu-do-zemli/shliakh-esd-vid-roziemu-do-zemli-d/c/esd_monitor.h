/* esd_monitor.h — Драйвер моніторингу та телеметрії транзієнтних подій ESD (C99) */
#ifndef ESD_MONITOR_H
#define ESD_MONITOR_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Структура лічильників та параметрів телеметрії */
typedef struct {
    uint32_t esd_strike_count;     /* Загальна кількість зафіксованих ESD-ударів */
    uint32_t last_timestamp_ms;    /* Часова мітка останнього спрацьовування (мс) */
    uint16_t max_voltage_peak_mv;  /* Зафіксована максимальна пікова напруга (мВ) */
    bool     is_transceiver_locked;/* Ознака апаратного зависання інтерфейсу */
} EsdTelemetryState;

/* Ініціалізація апаратного компаратора перенапруги та переривань */
void esd_monitor_init(void);

/* Обробник переривання від апаратного детектора перенапруги */
void esd_monitor_isr_handler(uint16_t detected_peak_mv);

/* Отримання поточного стану телеметрії */
void esd_monitor_get_state(EsdTelemetryState* out_state);

/* Програмне відновлення та скидання живлення трансивера після розряду */
bool esd_recover_transceiver(void);

#ifdef __cplusplus
}
#endif

#endif /* ESD_MONITOR_H */
