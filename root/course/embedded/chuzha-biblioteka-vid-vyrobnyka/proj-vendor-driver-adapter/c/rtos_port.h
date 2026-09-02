/*
 * Порт до операційної системи: м'ютекс і затримка.
 * Один заголовок для двох світів — реального FreeRTOS на мікроконтролері
 * і хостової збірки, під якою бігають модульні тести.
 */
#ifndef RTOS_PORT_H
#define RTOS_PORT_H

#include <stdbool.h>
#include <stdint.h>

#if defined(SYS_PORT_FREERTOS)
#include "FreeRTOS.h"
#include "semphr.h"
typedef SemaphoreHandle_t sys_mutex_t;
#else
#include <pthread.h>
typedef pthread_mutex_t sys_mutex_t;
#endif

/* Поріг, за яким затримку віддають планувальнику, а не спалюють такти. */
#define SYS_LONG_DELAY_US 1000U

bool sys_mutex_init(sys_mutex_t *m);
void sys_mutex_destroy(sys_mutex_t *m);
bool sys_mutex_lock(sys_mutex_t *m);
void sys_mutex_unlock(sys_mutex_t *m);

/* Гібридна затримка: довга — квант планувальника, коротка — лічильник тактів. */
void sys_delay_us(uint32_t period_us);

/* Монотонний час у мілісекундах; переповнення допустиме — порівнюємо різницю. */
uint32_t sys_uptime_ms(void);

#endif /* RTOS_PORT_H */
