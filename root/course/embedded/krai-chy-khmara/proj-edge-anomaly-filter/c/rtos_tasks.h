#ifndef EDGE_RTOS_TASKS_H
#define EDGE_RTOS_TASKS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Контракт плати. Ці функції реалізує BSP конкретного виробу — драйвер АЦП
 * і драйвер радіомодема; тут лише те, чого тримаються задачі.
 */

/* Блокується до готовності чергової вибірки (переривання DMA АЦП).
   false — перетворення не завершилося у відведений час. */
bool adc_read_sample(float *out, uint32_t timeout_ms);

void radio_wake(void);                                  /* Sleep -> активний режим */
void radio_sleep(void);                                 /* вимкнути PA, глибокий сон */
bool radio_send(const uint8_t *frame, size_t len);      /* віддати кадр в ефір */
bool radio_wait_ack(uint32_t timeout_ms);               /* дочекатися підтвердження */

/* Створює чергу й обидві задачі. Кличеться з main() до vTaskStartScheduler().
   Уся пам'ять статична, тож false означає лише невідповідність конфігурації
   FreeRTOS (немає configSUPPORT_STATIC_ALLOCATION). */
bool telemetry_start(void);

/* Лічильники для діагностики. Черга переповнюється, коли радіо не встигає;
   втрачені звіти треба бачити, а не здогадуватися про них. */
uint32_t telemetry_dropped_reports(void);
uint32_t telemetry_failed_transmissions(void);

#endif /* EDGE_RTOS_TASKS_H */
