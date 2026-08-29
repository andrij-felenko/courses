#include "isr_stage.h"

#include <string.h>

void isr_stage_init(isr_stage_t *stage)
{
    memset(stage->slots, 0, sizeof(stage->slots));
    atomic_init(&stage->head, 0u);
    atomic_init(&stage->tail, 0u);
    atomic_init(&stage->dropped, 0u);
}

bool isr_stage_push(isr_stage_t *stage, const isr_frame_t *frame)
{
    const unsigned head = atomic_load_explicit(&stage->head, memory_order_relaxed);
    const unsigned tail = atomic_load_explicit(&stage->tail, memory_order_acquire);

    /* Різниця беззнакова, тож переповнення лічильників рахунку не ламає. */
    if (head - tail >= ISR_STAGE_CAPACITY) {
        atomic_fetch_add_explicit(&stage->dropped, 1u, memory_order_relaxed);
        return false;
    }

    stage->slots[head & (ISR_STAGE_CAPACITY - 1u)] = *frame;

    /* release: слот заповнено ДО того, як задача побачить новий head. */
    atomic_store_explicit(&stage->head, head + 1u, memory_order_release);
    return true;
}

bool isr_stage_pop(isr_stage_t *stage, isr_frame_t *frame)
{
    const unsigned tail = atomic_load_explicit(&stage->tail, memory_order_relaxed);
    const unsigned head = atomic_load_explicit(&stage->head, memory_order_acquire);

    if (head == tail) {
        return false;
    }

    *frame = stage->slots[tail & (ISR_STAGE_CAPACITY - 1u)];
    atomic_store_explicit(&stage->tail, tail + 1u, memory_order_release);
    return true;
}

uint32_t isr_stage_take_dropped(isr_stage_t *stage)
{
    return (uint32_t)atomic_exchange_explicit(&stage->dropped, 0u, memory_order_relaxed);
}

uint32_t isr_stage_drain(isr_stage_t *stage, flash_logger_t *logger)
{
    uint32_t written = 0;
    uint32_t last_ts = logger->last_timestamp_ms;
    isr_frame_t frame;

    while (isr_stage_pop(stage, &frame)) {
        last_ts = frame.timestamp_ms;

        uint8_t payload[2];
        log_put_u16(payload, frame.arg16);

        if (flash_logger_write(logger, (log_level_t)frame.level, frame.module_id,
                               frame.timestamp_ms, frame.token_id,
                               payload, sizeof(payload)) != LOG_OK) {
            /* Кристал не бере запис. Далі черпати немає сенсу — решта кадрів
             * лишається в черзі до наступного заходу, а не гине по одному. */
            break;
        }
        written += 1;
    }

    const uint32_t dropped = isr_stage_take_dropped(stage);
    if (dropped > 0) {
        uint8_t payload[4];
        log_put_u32(payload, dropped);
        (void)flash_logger_write(logger, LOG_LEVEL_WARN, LOG_MODULE_LOGGER,
                                 last_ts, LOG_TOKEN_ISR_DROPS,
                                 payload, sizeof(payload));
    }

    return written;
}
