#include "logger_rtos.h"

#define DRAIN_TASK_STACK_WORDS 512u
#define DRAIN_IDLE_PERIOD_MS   500u

/* Рекурсивний, а не звичайний: службовий запис про дефектний сектор
 * народжується всередині flash_logger_write(), тобто вже під захопленим
 * м'ютексом. Зі звичайним м'ютексом задача заклинила б сама на собі. */
static void lock(logger_rtos_t *lr)
{
    (void)xSemaphoreTakeRecursive(lr->mutex, portMAX_DELAY);
}

static void unlock(logger_rtos_t *lr)
{
    (void)xSemaphoreGiveRecursive(lr->mutex);
}

static void drain_task(void *arg)
{
    logger_rtos_t *lr = (logger_rtos_t *)arg;

    for (;;) {
        /* Прокидаємося або від сповіщення з ISR, або раз на пів секунди —
         * друге потрібне, щоб не проґавити кадр, покладений у чергу рівно
         * тоді, коли задача вже виходила з очікування. */
        (void)ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(DRAIN_IDLE_PERIOD_MS));

        lock(lr);
        (void)isr_stage_drain(lr->stage, lr->core);
        unlock(lr);
    }
}

bool logger_rtos_start(logger_rtos_t *lr, flash_logger_t *core, isr_stage_t *stage)
{
    lr->core = core;
    lr->stage = stage;
    lr->drain_task = NULL;

    lr->mutex = xSemaphoreCreateRecursiveMutex();
    if (lr->mutex == NULL) {
        return false;
    }

    /* Найнижчий пріоритет над бездіяльною задачею: журнал не має права
     * відбирати такти в керування. */
    const BaseType_t ok = xTaskCreate(drain_task, "logdrain", DRAIN_TASK_STACK_WORDS,
                                      lr, tskIDLE_PRIORITY + 1, &lr->drain_task);
    if (ok != pdPASS) {
        vSemaphoreDelete(lr->mutex);
        lr->mutex = NULL;
        return false;
    }
    return true;
}

log_status_t logger_rtos_write(logger_rtos_t *lr, log_level_t level, uint8_t module_id,
                               uint32_t token_id, const uint8_t *payload, uint8_t payload_len)
{
    const uint32_t now_ms = (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);

    lock(lr);
    const log_status_t st = flash_logger_write(lr->core, level, module_id, now_ms,
                                               token_id, payload, payload_len);
    unlock(lr);
    return st;
}

void logger_rtos_write_from_isr(logger_rtos_t *lr, log_level_t level, uint8_t module_id,
                                uint32_t token_id, uint16_t arg16)
{
    isr_frame_t frame;
    frame.level        = (uint8_t)level;
    frame.module_id    = module_id;
    frame.arg16        = arg16;
    frame.timestamp_ms = (uint32_t)(xTaskGetTickCountFromISR() * portTICK_PERIOD_MS);
    frame.token_id     = token_id;

    /* Черга повна — кадр гине, і це правильно: тримати переривання
     * заради журналу не можна. Утрату порахує сама черга. */
    (void)isr_stage_push(lr->stage, &frame);

    BaseType_t woken = pdFALSE;
    vTaskNotifyGiveFromISR(lr->drain_task, &woken);
    portYIELD_FROM_ISR(woken);
}

log_status_t logger_rtos_read_batch(logger_rtos_t *lr, uint8_t *out, size_t out_cap,
                                    uint32_t *out_sector, size_t *out_len, uint32_t *out_records)
{
    lock(lr);
    const log_status_t st = flash_logger_read_batch(lr->core, out, out_cap,
                                                    out_sector, out_len, out_records);
    unlock(lr);
    return st;
}

log_status_t logger_rtos_commit_tail(logger_rtos_t *lr, uint32_t sector_idx)
{
    lock(lr);
    const log_status_t st = flash_logger_commit_tail(lr->core, sector_idx);
    unlock(lr);
    return st;
}
