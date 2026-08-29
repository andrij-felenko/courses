#ifndef BSP_CLOCK_H
#define BSP_CLOCK_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Драйвер тактового дерева: кварц 8 МГц -> PLL -> SYSCLK 168 МГц,
 * з таймаутами на кожному очікуванні прапорця й аварійним поверненням
 * на внутрішній RC-генератор HSI, якщо кварц не завівся.
 */

typedef enum {
    CLOCK_OK = 0,
    CLOCK_ERR_HSE_TIMEOUT,      /* кварц не розгойдався */
    CLOCK_ERR_HSI_TIMEOUT,      /* не піднявся навіть внутрішній RC */
    CLOCK_ERR_PLL_TIMEOUT,      /* контур не захопив фазу */
    CLOCK_ERR_SWITCH_TIMEOUT,   /* мультиплексор SYSCLK не підтвердив перемикання */
    CLOCK_ERR_VOS_TIMEOUT,      /* регулятор напруги ядра не вийшов на рівень */
    CLOCK_ERR_FLASH_LATENCY     /* контролер Flash не прийняв нову затримку */
} clock_status_t;

#define CLOCK_HSI_HZ            16000000UL
#define CLOCK_HSE_HZ            8000000UL
#define CLOCK_PLL_HZ            168000000UL

/* Такти очікування Flash при 3.3 В: 168 МГц -> 5 WS, 16 МГц -> 0 WS */
#define CLOCK_FLASH_WS_168MHZ   5UL
#define CLOCK_FLASH_WS_16MHZ    0UL

/* Порожній цикл ~5·10^4 ітерацій: із запасом більший за час старту кварцу */
#define CLOCK_TIMEOUT_CYCLES    0x5000UL

/* Повна ініціалізація: 8 МГц кварц -> 168 МГц. При будь-якій невдачі
   тактування лишається робочим на HSI, а код помилки повертається вгору. */
clock_status_t clock_configure_pll168(void);

/* Аварійне зведення дерева на внутрішній RC-генератор 16 МГц */
void clock_fallback_to_hsi(void);

/* Поточна частота ядра — її питає і DVFS, і драйвери таймерів/UART */
uint32_t clock_sysclk_hz(void);
void     clock_notify_sysclk(uint32_t hz);

/* Спільні цеглинки, якими користується і DVFS */
bool           clock_wait_masked(volatile uint32_t *reg, uint32_t mask,
                                 uint32_t expected, uint32_t cycles);
clock_status_t clock_set_flash_latency(uint32_t wait_states);
void           clock_reset_flash_caches(void);
clock_status_t clock_set_voltage_scale(uint32_t vos_field);
void           clock_set_bus_prescalers(uint32_t hpre, uint32_t ppre1, uint32_t ppre2);

/* Скільки разів CSS ловив зрив кварцу; лічильник переживає скидання */
uint32_t clock_css_event_count(void);

#endif /* BSP_CLOCK_H */
