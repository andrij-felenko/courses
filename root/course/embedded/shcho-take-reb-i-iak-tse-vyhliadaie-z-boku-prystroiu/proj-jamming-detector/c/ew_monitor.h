#ifndef EW_MONITOR_H
#define EW_MONITOR_H

#include <stdint.h>

#include "FreeRTOS.h"
#include "task.h"

/* Заводить чергу вибірок і потік телеметрії. Викликати один раз до
   vTaskStartScheduler(), пріоритет — нижчий за радіодрайвер. */
void ew_monitor_start(UBaseType_t priority);

/* Обробник переривання DIO1 трансивера: підключається до таблиці векторів. */
void ew_monitor_dio1_isr(void);

/* Скільки вибірок згоріло на переповненій черзі — суто діагностика. */
uint32_t ew_monitor_dropped(void);

#endif /* EW_MONITOR_H */
