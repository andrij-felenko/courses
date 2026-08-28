#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t TYPE;
    volatile uint32_t CTRL;
    volatile uint32_t RNR;
    volatile uint32_t RBAR;
    volatile uint32_t RASR;
} MpuHardware_t;

#define MPU_BASE ((MpuHardware_t *)0xE000ED90)

void MPU_ConfigNonCacheableDmaRegion(uint32_t base_address, uint32_t region_size_order) {
    // 1. Вимикаємо MPU перед зміною регістрів
    __asm volatile ("dmb" ::: "memory");
    MPU_BASE->CTRL = 0;

    // 2. Обираємо регіон 0
    MPU_BASE->RNR = 0;

    // 3. Встановлюємо базову адресу
    MPU_BASE->RBAR = base_address;

    // 4. Налаштовуємо атрибути пам'яті:
    // XN = 1 (заборона виконання коду)
    // AP = 0b011 (повний доступ Read/Write у привілейованому та користувацькому режимах)
    // TEX = 0b001, C = 0, B = 0, S = 1 (Normal Memory, Non-Cacheable, Shared)
    // SIZE = region_size_order, ENABLE = 1
    uint32_t rasr_config = (1u << 28) |               // XN = 1
                           (0x3u << 24) |             // AP = 0b011 (Full Access)
                           (0x1u << 19) |             // TEX = 0b001 (Non-cacheable)
                           (0u << 17) |               // C = 0
                           (0u << 16) |               // B = 0
                           (1u << 18) |               // S = 1 (Shareable)
                           ((region_size_order - 1) << 1) | // Розмір: 2^(order)
                           (1u << 0);                 // ENABLE = 1

    MPU_BASE->RASR = rasr_config;

    // 5. Вмикаємо MPU з фоновим регіоном за замовчуванням (PRIVDEFENA)
    MPU_BASE->CTRL = (1u << 2) | (1u << 0); // PRIVDEFENA | ENABLE

    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
}
