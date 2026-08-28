#include <stdint.h>
#include <stdbool.h>

#define SRAM_START_ADDR      0x20000000U
#define SRAM_END_ADDR        0x20080000U /* 512 КБ ОЗП для STM32F7/H7 */

/* Базові адреси Cortex-M SCB та NVIC */
#define SCB_VTOR             (*(volatile uint32_t *)0xE000ED08U)
#define SCB_CCR              (*(volatile uint32_t *)0xE000ED14U)
#define SCB_CSSELR           (*(volatile uint32_t *)0xE000ED84U)
#define SCB_CCR_DC_MASK      (1U << 16)
#define SCB_CCR_IC_MASK      (1U << 17)

#define SYSTICK_CTRL         (*(volatile uint32_t *)0xE000E010U)
#define SYSTICK_LOAD         (*(volatile uint32_t *)0xE000E014U)
#define SYSTICK_VAL          (*(volatile uint32_t *)0xE000E018U)

#define NVIC_ICER_BASE       ((volatile uint32_t *)0xE000E180U)
#define NVIC_ICPR_BASE       ((volatile uint32_t *)0xE000E280U)

/* RCC регістри STM32 */
#define RCC_CR               (*(volatile uint32_t *)0x40023800U)
#define RCC_CFGR             (*(volatile uint32_t *)0x40023808U)

typedef void (*entry_fn_t)(void);

static inline void disable_global_irq(void) {
    __asm volatile ("cpsid i" : : : "memory");
}

static inline void set_msp_register(uint32_t top_of_stack) {
    __asm volatile ("msr msp, %0" : : "r" (top_of_stack) : "memory");
}

static inline void barrier_sync(void) {
    __asm volatile ("dsb\n\tisb" : : : "memory");
}

static void deinit_cortex_core(void) {
    disable_global_irq();

    /* 1. Зупинка SysTick */
    SYSTICK_CTRL = 0U;
    SYSTICK_LOAD = 0U;
    SYSTICK_VAL = 0U;

    /* 2. Очищення й вимкнення кешів (Cortex-M7) */
    if (SCB_CCR & SCB_CCR_DC_MASK) {
        SCB_CCR &= ~SCB_CCR_DC_MASK; /* Вимкнення D-Cache */
    }
    if (SCB_CCR & SCB_CCR_IC_MASK) {
        SCB_CCR &= ~SCB_CCR_IC_MASK; /* Вимкнення I-Cache */
    }

    /* 3. Очищення активних та очікуючих переривань NVIC */
    for (uint32_t i = 0U; i < 8U; ++i) {
        NVIC_ICER_BASE[i] = 0xFFFFFFFFU;
        NVIC_ICPR_BASE[i] = 0xFFFFFFFFU;
    }

    /* 4. Скидання RCC на внутрішній генератор HSI (16 МГц) */
    RCC_CR |= 0x00000001U; /* HSI ON */
    while (!(RCC_CR & 0x00000002U)) { /* Очікування HSI RDY */ }
    RCC_CFGR = 0x00000000U; /* Вибір HSI як системного джерела */
    RCC_CR &= 0xFEF6FFFFU; /* Вимкнення HSE, CSS та PLL */

    barrier_sync();
}

bool boot_execute_jump(uint32_t vector_table_addr) {
    const uint32_t initial_msp = *(volatile uint32_t *)vector_table_addr;
    const uint32_t reset_handler_addr = *(volatile uint32_t *)(vector_table_addr + 4U);

    /* Перевірка валідності вершини стека: значення має лежати в межах SRAM */
    if (initial_msp < SRAM_START_ADDR || initial_msp > SRAM_END_ADDR) {
        return false;
    }

    /* Перевірка коректності біта Thumb (біт 0 має дорівнювати 1) */
    if ((reset_handler_addr & 0x00000001U) == 0U) {
        return false;
    }

    deinit_cortex_core();

    /* Релокація таблиці векторів */
    SCB_VTOR = vector_table_addr;
    barrier_sync();

    /* Встановлення головного покажчика стека та перехід */
    set_msp_register(initial_msp);

    entry_fn_t entry = (entry_fn_t)reset_handler_addr;
    entry();

    /* Сюди виконання ніколи не доходить */
    while (1) { }
    return true;
}
