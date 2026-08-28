#include <stdint.h>
#include <stdbool.h>

#define MPU_TYPE_REG   (*(volatile uint32_t*)0xE000ED90)
#define MPU_CTRL_REG   (*(volatile uint32_t*)0xE000ED94)
#define MPU_RNR_REG    (*(volatile uint32_t*)0xE000ED98)
#define MPU_RBAR_REG   (*(volatile uint32_t*)0xE000ED9C)
#define MPU_RASR_REG   (*(volatile uint32_t*)0xE000EDA0)

extern uint32_t _srom;
extern uint32_t _erom;
extern uint32_t _sram;
extern uint32_t _eram;

void configure_mpu_regions_c(void) {
    /* Вимкнення MPU під час конфігурації */
    MPU_CTRL_REG = 0;

    /* Регіон 0: Flash пам'ять (ReadOnly, Executable, 512KB) */
    MPU_RNR_REG  = 0;
    MPU_RBAR_REG = 0x08000000 | 0x10; /* VALID=1, REGION=0 */
    /* SIZE=18 (512KB), AP=010 (Privileged RO), XN=0 (Executable), ENABLE=1 */
    MPU_RASR_REG = (0 << 28) | (2 << 24) | (18 << 1) | 1;

    /* Регіон 1: SRAM пам'ять (ReadWrite, Non-Executable, 128KB) */
    MPU_RNR_REG  = 1;
    MPU_RBAR_REG = 0x20000000 | 0x10;
    /* SIZE=16 (128KB), AP=011 (Privileged RW), XN=1 (Execute-Never), ENABLE=1 */
    MPU_RASR_REG = (1 << 28) | (3 << 24) | (16 << 1) | 1;

    /* Увімкнення MPU з фоновою картою пам'яті за замовчуванням */
    MPU_CTRL_REG = 0x05; /* ENABLE=1, PRIVDEFENA=1 */
    __builtin_arm_isb(15);
    __builtin_arm_dsb(15);
}
