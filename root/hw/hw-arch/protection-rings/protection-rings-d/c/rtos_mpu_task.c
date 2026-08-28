/* rtos_mpu_task.c — налаштування MPU та перехід у Unprivileged Thread Mode
 * Платформа: ARM Cortex-M4 / Cortex-M7 (ARMv7-M, CMSIS-compliant)
 */
#include <stdint.h>
#include <stdbool.h>

/* Структури системних регістрів CMSIS */
#define MPU_BASE          (0xE000ED90UL)
#define SCB_BASE          (0xE000ED00UL)

typedef struct {
    volatile uint32_t TYPE;
    volatile uint32_t CTRL;
    volatile uint32_t RNR;
    volatile uint32_t RBAR;
    volatile uint32_t RASR;
} MPU_Type;

typedef struct {
    volatile uint32_t CPUID;
    volatile uint32_t ICSR;
    volatile uint32_t VTOR;
    volatile uint32_t AIRCR;
    volatile uint32_t SCR;
    volatile uint32_t CCR;
    volatile uint32_t SHPR[3];
    volatile uint32_t SHCSR;
    volatile uint32_t CFSR;
    volatile uint32_t HFSR;
    volatile uint32_t DFSR;
    volatile uint32_t MMFAR;
    volatile uint32_t BFAR;
} SCB_Type;

#define MPU               ((MPU_Type *)MPU_BASE)
#define SCB               ((SCB_Type *)SCB_BASE)

/* Бітові маски MPU RASR */
#define MPU_RASR_ENABLE_Msk     (1UL << 0)
#define MPU_RASR_SIZE_Pos       (1UL)
#define MPU_RASR_AP_Pos         (24UL)
#define MPU_RASR_XN_Pos         (28UL)

#define MPU_AP_PRIV_RW_USER_NO  (1UL << MPU_RASR_AP_Pos)
#define MPU_AP_PRIV_RW_USER_RO  (2UL << MPU_RASR_AP_Pos)
#define MPU_AP_PRIV_RW_USER_RW  (3UL << MPU_RASR_AP_Pos)
#define MPU_AP_PRIV_RO_USER_RO  (6UL << MPU_RASR_AP_Pos)

#define MPU_REGION_SIZE_32B     (4UL << MPU_RASR_SIZE_Pos)
#define MPU_REGION_SIZE_1KB     (9UL << MPU_RASR_SIZE_Pos)
#define MPU_REGION_SIZE_4KB     (11UL << MPU_RASR_SIZE_Pos)
#define MPU_REGION_SIZE_512KB   (18UL << MPU_RASR_SIZE_Pos)

/* Бар'єри пам'яті та синхронізації */
static inline void __dmb(void) { __asm__ volatile ("dmb 0xF" ::: "memory"); }
static inline void __dsb(void) { __asm__ volatile ("dsb 0xF" ::: "memory"); }
static inline void __isb(void) { __asm__ volatile ("isb 0xF" ::: "memory"); }

/* Конфігурація MPU регіонів для конкретної задачі */
void rtos_setup_task_mpu(uint32_t stack_base, uint32_t data_base) {
    __dsb();

    /* Вимикаємо MPU перед переконфігурацією */
    MPU->CTRL = 0;

    /* Регіон 0: Код Flash (0x08000000, 512 КБ) — Privileged RO/X, Unprivileged RO/X */
    MPU->RNR  = 0;
    MPU->RBAR = 0x08000000UL;
    MPU->RASR = MPU_RASR_ENABLE_Msk | MPU_REGION_SIZE_512KB | MPU_AP_PRIV_RO_USER_RO;

    /* Регіон 1: Стек задачі (stack_base, 1 КБ) — Privileged RW, Unprivileged RW, XN */
    MPU->RNR  = 1;
    MPU->RBAR = stack_base;
    MPU->RASR = MPU_RASR_ENABLE_Msk | MPU_REGION_SIZE_1KB | MPU_AP_PRIV_RW_USER_RW | (1UL << MPU_RASR_XN_Pos);

    /* Регіон 2: Дані задачі (data_base, 4 КБ) — Privileged RW, Unprivileged RW, XN */
    MPU->RNR  = 2;
    MPU->RBAR = data_base;
    MPU->RASR = MPU_RASR_ENABLE_Msk | MPU_REGION_SIZE_4KB | MPU_AP_PRIV_RW_USER_RW | (1UL << MPU_RASR_XN_Pos);

    /* Увімкнення обробника MemManage Fault у SCB */
    SCB->SHCSR |= (1UL << 16); /* MEMFAULTENA */

    /* Вмикаємо MPU: PRIVDEFENA (біт 2) = дозволити фонову пам'ять для привілейованого режиму */
    MPU->CTRL = (1UL << 0) | (1UL << 2);

    __dsb();
    __isb();
}

/* Запуск задачі в непривілейованому режимі */
void rtos_launch_unprivileged_task(void (*task_entry)(void), uint32_t task_psp_top) {
    /* 1. Завантажуємо адресу верхівки стека в PSP */
    __asm__ volatile ("msr psp, %0" :: "r"(task_psp_top) : "sp");

    /* 2. Перемикаємося на PSP (SPSEL = 1) та скидаємо привілеї (nPRIV = 1) */
    uint32_t control_val = (1UL << 1) | (1UL << 0); /* SPSEL=1, nPRIV=1 */
    __asm__ volatile (
        "msr control, %0 \n"
        "isb             \n"
        :: "r"(control_val) : "memory"
    );

    /* 3. Передаємо керування на точку входу непривілейованої задачі */
    task_entry();
}
