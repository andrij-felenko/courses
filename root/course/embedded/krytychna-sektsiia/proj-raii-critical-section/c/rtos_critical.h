#ifndef RTOS_CRITICAL_H
#define RTOS_CRITICAL_H

/*
 * Критична секція FreeRTOS, що сама розрізняє контекст.
 *
 * taskENTER_CRITICAL() з обробника переривання — це спрацьований
 * configASSERT() і зупинка системи; для ISR існує окрема пара *_FROM_ISR,
 * яка повертає й приймає збережене значення BASEPRI.
 *
 * Усередині секції не можна кликати блокувальний API (xQueueSend,
 * vTaskDelay тощо): планувальник у цей час вимкнений.
 */

#include "FreeRTOS.h"
#include "task.h"

#include "critical_section.h"

typedef struct {
    UBaseType_t isr_state;
    bool        from_isr;
} rtos_section_t;

static inline rtos_section_t rtos_section_enter(void)
{
    rtos_section_t rs;

    rs.from_isr = in_interrupt_context();
    if (rs.from_isr) {
        rs.isr_state = taskENTER_CRITICAL_FROM_ISR();
    } else {
        rs.isr_state = 0U;
        taskENTER_CRITICAL();
    }
    return rs;
}

static inline void rtos_section_exit(rtos_section_t rs)
{
    if (rs.from_isr) {
        taskEXIT_CRITICAL_FROM_ISR(rs.isr_state);
    } else {
        taskEXIT_CRITICAL();
    }
}

static inline void rtos_section_cleanup_(const rtos_section_t *rs)
{
    rtos_section_exit(*rs);
}

#define CS_RTOS_BLOCK_IMPL_(rsvar, oncevar)                                    \
    for (rtos_section_t rsvar                                                  \
             __attribute__((cleanup(rtos_section_cleanup_)))                   \
             = rtos_section_enter(),                                           \
             *oncevar = &rsvar;                                                \
         oncevar != NULL;                                                      \
         oncevar = NULL)

/* Той самий блок, що й CRITICAL_BLOCK(), але через примітиви FreeRTOS. */
#define RTOS_CRITICAL_BLOCK() CS_RTOS_BLOCK_IMPL_(CS_ID(rs_), CS_ID(rs_once_))

/* --- Приклад спільного стану --------------------------------------------- */
/*
 * Лічильники радіолінка: їх чіпає і задача передавача, і обробник
 * переривання UART. Той самий блок працює в обох контекстах.
 */

typedef struct {
    uint32_t frames;
    uint32_t crc_errors;
} link_stats_t;

static link_stats_t g_link_stats;

static inline void link_stats_add_frame(bool crc_ok)
{
    RTOS_CRITICAL_BLOCK() {
        g_link_stats.frames++;
        if (!crc_ok) {
            g_link_stats.crc_errors++;
        }
    }
}

static inline link_stats_t link_stats_read(void)
{
    link_stats_t copy = { 0U, 0U };

    RTOS_CRITICAL_BLOCK() {
        copy = g_link_stats;
    }
    return copy;
}

#endif /* RTOS_CRITICAL_H */
