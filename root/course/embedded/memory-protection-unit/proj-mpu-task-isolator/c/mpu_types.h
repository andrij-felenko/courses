#ifndef MPU_TYPES_H
#define MPU_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Базові адреси системних блоків Cortex-M */
#define SCS_BASE            (0xE000E000UL)
#define MPU_BASE            (SCS_BASE + 0x0D90UL)
#define SCB_BASE            (SCS_BASE + 0x0D00UL)

/* Регістри MPU (PMSAv7 та PMSAv8 спільні зміщення) */
#define MPU_TYPE_REG        (*(volatile uint32_t *)(MPU_BASE + 0x00UL))
#define MPU_CTRL_REG        (*(volatile uint32_t *)(MPU_BASE + 0x04UL))
#define MPU_RNR_REG         (*(volatile uint32_t *)(MPU_BASE + 0x08UL))
#define MPU_RBAR_REG        (*(volatile uint32_t *)(MPU_BASE + 0x0CUL))
#define MPU_RASR_REG        (*(volatile uint32_t *)(MPU_BASE + 0x10UL)) /* PMSAv7 */
#define MPU_RLAR_REG        (*(volatile uint32_t *)(MPU_BASE + 0x10UL)) /* PMSAv8 */
#define MPU_MAIR0_REG       (*(volatile uint32_t *)(MPU_BASE + 0x30UL)) /* PMSAv8 */
#define MPU_MAIR1_REG       (*(volatile uint32_t *)(MPU_BASE + 0x34UL)) /* PMSAv8 */

/* Системні регістри SCB для діагностики відмов */
#define SCB_CFSR_REG        (*(volatile uint32_t *)(SCB_BASE + 0x28UL))
#define SCB_MMFAR_REG       (*(volatile uint32_t *)(SCB_BASE + 0x34UL))
#define SCB_SHCSR_REG       (*(volatile uint32_t *)(SCB_BASE + 0x24UL))

/* Біти MPU_CTRL */
#define MPU_CTRL_ENABLE_MSK         (1UL << 0)
#define MPU_CTRL_HFNMIENA_MSK       (1UL << 1)
#define MPU_CTRL_PRIVDEFENA_MSK     (1UL << 2)

/* Прапорці SCB_SHCSR для MemManage */
#define SCB_SHCSR_MEMFAULTENA_MSK   (1UL << 16)

/* Біти SCB_CFSR / MMFSR (MemManage Fault Status) */
#define MMFSR_IACCVIOL_MSK          (1UL << 0)
#define MMFSR_DACCVIOL_MSK          (1UL << 1)
#define MMFSR_MUNSTKERR_MSK         (1UL << 3)
#define MMFSR_MSTKERR_MSK           (1UL << 4)
#define MMFSR_MLSPERR_MSK           (1UL << 5)
#define MMFSR_MMARVALID_MSK         (1UL << 7)

/* Права доступу AP (Access Permissions) */
typedef enum {
    MPU_AP_NO_ACCESS        = 0x0U, /* Priv: No,   Unpriv: No   */
    MPU_AP_PRIV_RW_UNPRIV_NO = 0x1U, /* Priv: RW,   Unpriv: No   */
    MPU_AP_PRIV_RW_UNPRIV_RO = 0x2U, /* Priv: RW,   Unpriv: RO   */
    MPU_AP_PRIV_RW_UNPRIV_RW = 0x3U, /* Priv: RW,   Unpriv: RW   */
    MPU_AP_PRIV_RO_UNPRIV_NO = 0x5U, /* Priv: RO,   Unpriv: No   */
    MPU_AP_PRIV_RO_UNPRIV_RO = 0x6U  /* Priv: RO,   Unpriv: RO   */
} mpu_access_perm_t;

/* Тип пам'яті та кешованість */
typedef enum {
    MPU_ATTR_DEVICE_nGnRnE  = 0x0U, /* Периферія, суворий порядок */
    MPU_ATTR_DEVICE_nGnRE   = 0x1U, /* Периферія з буферизацією */
    MPU_ATTR_NORMAL_WT      = 0x2U, /* Звичайна пам'ять, Write-Through */
    MPU_ATTR_NORMAL_WB_WA   = 0x3U, /* Звичайна пам'ять, Write-Back, Write-Allocate */
    MPU_ATTR_NORMAL_NONCACHE= 0x4U  /* Звичайна пам'ять без кешу (DMA буфери) */
} mpu_memory_attr_t;

/* Архітектурний профіль MPU */
typedef enum {
    MPU_ARCH_PMSAV7, /* Cortex-M3 / M4 / M7 */
    MPU_ARCH_PMSAV8  /* Cortex-M23 / M33 / M55 / M85 */
} mpu_arch_t;

/* Опис статичного або динамічного регіону */
typedef struct {
    uint8_t           region_number;
    uint32_t          base_address;
    uint32_t          size_bytes;       /* Для PMSAv7 має бути 2^N */
    mpu_access_perm_t access_perm;
    mpu_memory_attr_t memory_attr;
    bool              execute_never;    /* XN прапорець */
    uint8_t           subregion_disable;/* SRD маска для PMSAv7 (0 = усі увімкнені) */
} mpu_region_config_t;

/* Структура стек-фрейму Cortex-M, збереженого апаратно при винятку */
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
} mpu_fault_stack_frame_t;

/* Звіт про аварійну ситуацію порушення пам'яті */
typedef struct {
    uint8_t  fault_status_flags; /* Вміст MMFSR */
    uint32_t fault_address;      /* Вміст MMFAR (якщо дійсний) */
    bool     is_address_valid;
    uint32_t fault_pc;           /* Адреса винної інструкції з стек-фрейму */
    uint32_t fault_lr;
    uint32_t fault_psr;
    bool     occurred_in_psp;    /* True якщо збій стався у непривілейованому стеку задачі */
} mpu_fault_report_t;

#endif /* MPU_TYPES_H */
