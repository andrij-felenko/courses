#ifndef CLOCK_SAFE_H
#define CLOCK_SAFE_H

/*
 * Безпечний запуск дерева тактування. Жодне очікування готовності генератора
 * не є нескінченним: незапаяний кварц або мертвий PLL мусять давати прошивку,
 * що працює повільніше, а не «цеглину», яка висить у циклі очікування.
 */

#include <stdint.h>

typedef enum {
    CLOCK_SRC_HSI = 0,   /* внутрішній генератор напряму, 16 МГц */
    CLOCK_SRC_HSI_PLL,   /* PLL від внутрішнього генератора      */
    CLOCK_SRC_HSE_PLL    /* PLL від зовнішнього кварцу           */
} clock_source_t;

typedef enum {
    CLOCK_OK = 0,
    CLOCK_ERR_HSE_TIMEOUT,    /* кварц не завівся — працюємо від HSI  */
    CLOCK_ERR_PLL_TIMEOUT,    /* PLL не захопився                     */
    CLOCK_ERR_SWITCH_TIMEOUT, /* перемикач SYSCLK не прийняв джерело  */
    CLOCK_ERR_BAD_PLL         /* коефіцієнти поза межами документації */
} clock_status_t;

typedef struct {
    clock_source_t source;
    uint32_t       sysclk_hz;
    clock_status_t status;
} clock_state_t;

/* Налаштовує тактування; за будь-якої невдачі лишає живу систему на HSI. */
clock_state_t clock_safe_init(void);

/* Поточна частота ядра (Гц). */
uint32_t clock_safe_sysclk_hz(void);

/* Затримка на систем-таймері; враховує реально досягнуту частоту. */
void clock_safe_delay_ms(uint32_t ms);

const char *clock_status_str(clock_status_t status);

#endif /* CLOCK_SAFE_H */
