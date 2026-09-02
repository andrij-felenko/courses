#ifndef TRACE_H
#define TRACE_H

#include <stdint.h>

/* Діагностичний пін під логічний аналізатор. Фронт — момент, коли арбітр
   побачив намір пілота; спад — коли готова уставка пішла в мікшер моторів
   і далі в DShot-кадр. Ширина імпульсу і є затримка реакції диспетчера:
   при 400 Гц вона мусить лишатися меншою за один період циклу, 2.5 мс. */
void     diag_pin_init(void);
void     diag_pin_high(void);
void     diag_pin_low(void);
uint32_t diag_pulse_last_us(void);
uint32_t diag_pulse_worst_us(void);
uint32_t diag_pulse_count(void);

#endif /* TRACE_H */
