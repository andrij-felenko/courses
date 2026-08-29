/* report.h — друк бюджету. Рахує latency.c, форматує цей модуль.
 *
 * Розділення не косметичне: на бортовій діагностиці той самий lat_budget
 * піде в телеметрію, а не в термінал, і рахунок туди їде без printf.
 */
#ifndef REPORT_H
#define REPORT_H

#include <stddef.h>
#include "latency.h"

/* Повна таблиця ланок тракту з підсумком і поділом на електроніку й фізику. */
void rep_pipeline(const lat_pipeline *p);

/* Що затримка робить із контуром: фазовий зсув на частоті маневрування
   control_hz і сліпий шлях на швидкості speed_mps. */
void rep_dynamics(const char *label, lat_budget b, double control_hz, double speed_mps);

/* Один рядок на тракт: typ, max, джитер, найтовща ланка. */
void rep_compare(const char *heading, const lat_pipeline *const *pipes, size_t count);

#endif /* REPORT_H */
