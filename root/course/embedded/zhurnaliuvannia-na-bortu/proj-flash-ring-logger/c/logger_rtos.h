/* Прив'язка журналу до FreeRTOS: рекурсивний м'ютекс на шину й фонова задача,
 * що переносить кадри з черги переривань у Flash.
 *
 * Цей модуль збирається лише під ціль — на хості FreeRTOS немає, тож
 * test_recovery.c працює з ядром напряму. */

#ifndef LOGGER_RTOS_H
#define LOGGER_RTOS_H

#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"

#include "flash_logger.h"
#include "isr_stage.h"

typedef struct {
    flash_logger_t   *core;
    isr_stage_t      *stage;
    SemaphoreHandle_t mutex;
    TaskHandle_t      drain_task;
} logger_rtos_t;

/* Створює м'ютекс і фонову задачу. Ядро вже має бути ініціалізоване
 * flash_logger_init(), а черга — isr_stage_init(). */
bool logger_rtos_start(logger_rtos_t *lr, flash_logger_t *core, isr_stage_t *stage);

/* Запис із звичайної задачі: мітку часу бере з тіків планувальника. */
log_status_t logger_rtos_write(logger_rtos_t *lr, log_level_t level, uint8_t module_id,
                               uint32_t token_id, const uint8_t *payload, uint8_t payload_len);

/* Запис із переривання: лише кладе кадр у чергу й будить фонову задачу. */
void logger_rtos_write_from_isr(logger_rtos_t *lr, log_level_t level, uint8_t module_id,
                                uint32_t token_id, uint16_t arg16);

/* Вивантаження пачки під тим самим м'ютексом — шина в модема й у журналу спільна. */
log_status_t logger_rtos_read_batch(logger_rtos_t *lr, uint8_t *out, size_t out_cap,
                                    uint32_t *out_sector, size_t *out_len, uint32_t *out_records);

log_status_t logger_rtos_commit_tail(logger_rtos_t *lr, uint32_t sector_idx);

#endif /* LOGGER_RTOS_H */
