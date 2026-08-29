#ifndef ACTUATOR_H
#define ACTUATOR_H

#include <stdbool.h>
#include <stdint.h>

#include "dedup.h"

/* Завдання для воркера: що саме крутити. */
typedef struct {
    char cmd_id[CMD_ID_MAX_LEN];
    int  target_pct;
} act_job_t;

/* --- Те, що реалізує плата (у прикладі — main.c) --- */
uint32_t hal_millis(void);        /* монотонний час від старту, мс */
uint32_t hal_epoch_sec(void);     /* час доби від NTP, с */
int      hal_position_pct(void);  /* датчик положення вала, 0..100 */
bool     hal_limit_closed(void);  /* кінцевик «закрито» */
bool     hal_limit_open(void);    /* кінцевик «відкрито» */
void     hal_drive_set(int target_pct);
void     hal_drive_stop(void);

/* Старт воркера. Тут же розбирається незавершений маневр, якщо плату
   перезавантажило просідання живлення. */
void actuator_init(uint32_t now_ms);

/* Виклик із мережевого колбеку: покласти наказ в інбокс.
   false — інбокс переповнений, оператору відповідаємо ERR_BUSY. */
bool actuator_submit(const act_job_t *job);

bool actuator_busy(void);
int  actuator_position(void);

/* Виклик на кожному витку швидкого циклу; ніколи не блокує. */
void actuator_poll(uint32_t now_ms);

#endif /* ACTUATOR_H */
