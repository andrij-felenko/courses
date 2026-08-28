#include "vector_table_types.h"

#define MPU_BASE_ADDR        0xE000ED90UL
#define MPU_TYPE_REG         (*(volatile uint32_t*)(MPU_BASE_ADDR + 0x00))
#define MPU_CTRL_REG         (*(volatile uint32_t*)(MPU_BASE_ADDR + 0x04))
#define MPU_RNR_REG          (*(volatile uint32_t*)(MPU_BASE_ADDR + 0x08))
#define MPU_RBAR_REG         (*(volatile uint32_t*)(MPU_BASE_ADDR + 0x0C))
#define MPU_RASR_REG         (*(volatile uint32_t*)(MPU_BASE_ADDR + 0x10))

static inline void dsb_barrier(void) { __asm__ volatile ("dsb 0xF" : : : "memory"); }
static inline void isb_barrier(void) { __asm__ volatile ("isb 0xF" : : : "memory"); }

vtm_status_t mpu_init_vector_protection(uintptr_t base_address, size_t size_bytes) {
    if ((base_address % VECTOR_TABLE_ALIGNMENT_BYTES) != 0) {
        return VTM_STATUS_ERROR_ALIGNMENT;
    }

    if (size_bytes > VECTOR_TABLE_ALIGNMENT_BYTES) {
        return VTM_STATUS_ERROR_MPU_CONFIG;
    }

    /* Перевірка підтримки MPU залізом */
    if ((MPU_TYPE_REG & 0xFF00) == 0) {
        return VTM_STATUS_ERROR_MPU_CONFIG;
    }

    /* 1. Тимчасове вимкнення MPU для безпечної конфігурації */
    MPU_CTRL_REG = 0;
    dsb_barrier();

    /* 2. Вибір регіону 7 */
    MPU_RNR_REG = VTM_MPU_REGION_NUMBER;

    /* 3. Базова адреса регіону */
    MPU_RBAR_REG = (base_address & ~0x1FUL);

    /* 4. Налаштування регістру RASR:
       - XN = 1 (Біт 28: Заборона виконання інструкцій)
       - AP = 0b110 (Біти 26..24: Privileged Read-Only, Unprivileged No Access)
       - TEX/C/B = 0b001000 (Normal memory, non-cacheable / inner write-back)
       - SIZE = 0b01001 (Біти 5..1: Розмір 2^(9+1) = 1024 байти)
       - ENABLE = 1 (Біт 0) */
    uint32_t rasr_val = (1UL << 28) | /* XN */
                        (6UL << 24) | /* AP = 110 (Privileged RO) */
                        (1UL << 19) | /* TEX = 001 */
                        (9UL << 1)  | /* SIZE = 9 -> 1024B */
                        (1UL << 0);   /* ENABLE */

    MPU_RASR_REG = rasr_val;

    /* 5. Увімкнення MPU:
       - PRIVDEFENA = 1 (Використання карти пам'яті за замовчуванням для фонового простору)
       - HFNMIENA = 0 (MPU вимкнено під час HardFault/NMI для уникнення зациклення)
       - ENABLE = 1 */
    MPU_CTRL_REG = (1UL << 2) | (1UL << 0);
    dsb_barrier();
    isb_barrier();

    return VTM_STATUS_OK;
}

void mpu_grant_write_access(void) {
    MPU_RNR_REG = VTM_MPU_REGION_NUMBER;
    uint32_t rasr = MPU_RASR_REG;
    /* Зміна AP на 0b001 (Privileged Read-Write) */
    rasr &= ~(7UL << 24);
    rasr |= (1UL << 24);
    MPU_RASR_REG = rasr;
    dsb_barrier();
    isb_barrier();
}

void mpu_restore_read_only_access(void) {
    MPU_RNR_REG = VTM_MPU_REGION_NUMBER;
    uint32_t rasr = MPU_RASR_REG;
    /* Зміна AP на 0b110 (Privileged Read-Only) */
    rasr &= ~(7UL << 24);
    rasr |= (6UL << 24);
    MPU_RASR_REG = rasr;
    dsb_barrier();
    isb_barrier();
}
