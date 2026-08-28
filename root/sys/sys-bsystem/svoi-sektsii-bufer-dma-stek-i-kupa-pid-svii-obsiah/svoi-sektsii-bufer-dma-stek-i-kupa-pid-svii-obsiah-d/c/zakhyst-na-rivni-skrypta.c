#include <stdint.h>

/* Регістри блоку MPU для архітектури ARMv7-M (Cortex-M7) */
#define MPU_TYPE_REG  (*(volatile uint32_t*)0xE000ED90)
#define MPU_CTRL_REG  (*(volatile uint32_t*)0xE000ED94)
#define MPU_RNR_REG   (*(volatile uint32_t*)0xE000ED98)
#define MPU_RBAR_REG  (*(volatile uint32_t*)0xE000ED9C)
#define MPU_RASR_REG  (*(volatile uint32_t*)0xE000EDA0)

void MPU_Configure_NonCacheable_D2(void) {
    /* Тимчасове вимкнення MPU */
    MPU_CTRL_REG = 0;

    /* Вибір слота регіону MPU № 0 */
    MPU_RNR_REG = 0;
    
    /* Базова адреса регіону: 0x30000000 (RAM_D2) */
    MPU_RBAR_REG = 0x30000000;

    /*
     * Налаштування бітів RASR (Region Attribute and Size Register):
     * XN = 1 (заборона виконання коду в буферах даних)
     * AP = 011 (повний доступ ядра на читання та запис)
     * TEX = 001, C = 0, B = 0 (Normal Non-Cacheable, Non-Shareable)
     * SIZE = 0x12 (розмір 2^(18+1) = 512 КБ, що покриває 288 КБ RAM_D2)
     * ENABLE = 1
     */
    MPU_RASR_REG = (1UL << 28) | (3UL << 24) | (1UL << 19) | (18UL << 1) | 1UL;

    /* Увімкнення MPU з збереженням фонової карти адрес (PRIVDEFENA) */
    MPU_CTRL_REG = (1UL << 2) | (1UL << 0);

    /* Бар'єри пам'яті для синхронізації конфігурації */
    __builtin_arm_dsb(15);
    __builtin_arm_isb(15);
}
