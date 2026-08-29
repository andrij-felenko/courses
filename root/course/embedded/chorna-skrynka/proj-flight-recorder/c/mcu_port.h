/* mcu_port.h — те з апаратури Cortex-M, без чого реєстратор не працює:
 * критична секція, регістри System Control Block, скидання ядра, чистка D-Cache.
 * Усе — inline: панічний шлях не має права залежати від чужих модулів. */
#ifndef BLACKBOX_MCU_PORT_H
#define BLACKBOX_MCU_PORT_H

#include <stdint.h>
#include <stddef.h>

/* --- Регістри ядра (ARMv6-M/ARMv7-M, адреси фіксовані архітектурою) --- */
#define SCB_AIRCR_ADDR   0xE000ED0CU /* скидання ядра */
#define SCB_CFSR_ADDR    0xE000ED28U /* Configurable Fault Status */
#define SCB_HFSR_ADDR    0xE000ED2CU /* HardFault Status */
#define SCB_MMFAR_ADDR   0xE000ED34U /* адреса збою MPU */
#define SCB_BFAR_ADDR    0xE000ED38U /* адреса збою шини */
#define SCB_DCCMVAC_ADDR 0xE000EF68U /* clean D-Cache by address */

#define CFSR_MMARVALID   (1U << 7)
#define CFSR_BFARVALID   (1U << 15)

static inline uint32_t mcu_reg_read(uint32_t addr) {
    return *((volatile uint32_t*)addr);
}

static inline void mcu_reg_write(uint32_t addr, uint32_t value) {
    *((volatile uint32_t*)addr) = value;
}

/* --- Критична секція через PRIMASK ---
 * Повертаємо попередній стан, а не вмикаємо переривання наосліп: реєстратор
 * викликають і з обробників переривань, де переривання вже вимкнені. */
static inline uint32_t mcu_enter_critical(void) {
    uint32_t primask;
    __asm volatile("mrs %0, primask\n\t"
                   "cpsid i"
                   : "=r"(primask)
                   :
                   : "memory");
    return primask;
}

static inline void mcu_exit_critical(uint32_t primask) {
    __asm volatile("msr primask, %0" : : "r"(primask) : "memory");
}

/* --- Скидання ядра (AIRCR.SYSRESETREQ під ключем 0x05FA) --- */
static inline void mcu_system_reset(void) {
    __asm volatile("dsb" ::: "memory");
    mcu_reg_write(SCB_AIRCR_ADDR, 0x05FA0000U | (1U << 2));
    __asm volatile("dsb" ::: "memory");
    for (;;) {
        __asm volatile("nop");
    }
}

/* --- Примусова чистка ліній кешу даних ---
 * На M7 (STM32F7/H7, i.MX RT) кадри осідають у D-Cache, і автономний запис у
 * SPI віддав би на носій застарілу SRAM. Довжина лінії кешу — 32 байти.
 * Для ядер без кешу виклик порожній, тож панічний шлях однаковий скрізь. */
#if defined(BLACKBOX_HAS_DCACHE)
static inline void mcu_dcache_clean(const void* addr, size_t size) {
    uint32_t start = ((uint32_t)addr) & ~31U;
    uint32_t end   = ((uint32_t)addr) + (uint32_t)size;
    __asm volatile("dsb" ::: "memory");
    for (uint32_t line = start; line < end; line += 32U) {
        mcu_reg_write(SCB_DCCMVAC_ADDR, line);
    }
    __asm volatile("dsb" ::: "memory");
    __asm volatile("isb" ::: "memory");
}
#else
static inline void mcu_dcache_clean(const void* addr, size_t size) {
    (void)addr;
    (void)size;
}
#endif

/* Монотонний час у мілісекундах. Реалізує застосунок (лічильник SysTick):
 * реєстратор не може володіти системним тиком, він у нього лише позичає. */
uint32_t mcu_get_uptime_ms(void);

#endif /* BLACKBOX_MCU_PORT_H */
