#ifndef VTOR_RELOCATE_H
#define VTOR_RELOCATE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file vtor_relocate.h
 * @brief Карта пам'яті ST-Link V2.1, системні регістри Cortex-M та інтерфейс релокації VTOR.
 */

/* ========================================================================== */
/* Базові адреси карти пам'яті ST-Link V2.1 (STM32F103)                        */
/* ========================================================================== */

#define STLINK_V21_FLASH_BASE        (0x08000000UL) /* Початок Flash-пам'яті мікроконтролера */
#define STLINK_V21_BOOT_BASE         (0x08000000UL) /* Базова адреса фірмового Bootloader ST-Link */
#define DAPLINK_APP_BASE             (0x08004000UL) /* Базова адреса завантажувача/прошивки DAPLink (зсув 16 КБ) */
#define STLINK_V21_SRAM_BASE         (0x20000000UL) /* Початок оперативної пам'яті SRAM */
#define STLINK_V21_SRAM_SIZE         (0x00005000UL) /* Розмір SRAM: 20 КБ (STM32F103CB) */
#define STLINK_V21_SRAM_END          (STLINK_V21_SRAM_BASE + STLINK_V21_SRAM_SIZE) /* Верхня межа SRAM */

/* Маска вирівнювання адреси VTOR (таблиця векторів має бути вирівняна на 128 байтів) */
#define VTOR_ALIGNMENT_MASK          (0x3FFFFF80UL)
#define VTOR_ALIGNMENT_BYTES         (128UL)

/* ========================================================================== */
/* Регістри ARM Cortex-M System Control Space (SCS)                            */
/* ========================================================================== */

#define SCS_BASE                     (0xE000E000UL)

/* Структура регістрів SysTick */
typedef struct {
    volatile uint32_t CTRL;  /* Control and Status Register */
    volatile uint32_t LOAD;  /* Reload Value Register */
    volatile uint32_t VAL;   /* Current Value Register */
    volatile uint32_t CALIB; /* Calibration Register */
} systick_reg_t;

#define SYSTICK_REG                  ((systick_reg_t *)(SCS_BASE + 0x0010UL))

/* Структура регістрів NVIC */
typedef struct {
    volatile uint32_t ISER[8]; /* Interrupt Set-Enable Registers */
    uint32_t RESERVED0[24];
    volatile uint32_t ICER[8]; /* Interrupt Clear-Enable Registers */
    uint32_t RESERVED1[24];
    volatile uint32_t ISPR[8]; /* Interrupt Set-Pending Registers */
    uint32_t RESERVED2[24];
    volatile uint32_t ICPR[8]; /* Interrupt Clear-Pending Registers */
    uint32_t RESERVED3[24];
    volatile uint32_t IABR[8]; /* Interrupt Active Bit Registers */
    uint32_t RESERVED4[56];
    volatile uint8_t  IP[240];  /* Interrupt Priority Registers */
} nvic_reg_t;

#define NVIC_REG                     ((nvic_reg_t *)(SCS_BASE + 0x0100UL))

/* Структура регістрів SCB (System Control Block) */
typedef struct {
    volatile uint32_t CPUID;   /* CPUID Base Register */
    volatile uint32_t ICSR;    /* Interrupt Control and State Register */
    volatile uint32_t VTOR;    /* Vector Table Offset Register */
    volatile uint32_t AIRCR;   /* Application Interrupt and Reset Control Register */
    volatile uint32_t SCR;     /* System Control Register */
    volatile uint32_t CCR;     /* Configuration and Control Register */
    volatile uint8_t  SHP[12];  /* System Handlers Priority Registers */
    volatile uint32_t SHCSR;   /* System Handler Control and State Register */
} scb_reg_t;

#define SCB_REG                      ((scb_reg_t *)(SCS_BASE + 0x0D00UL))

/* ========================================================================== */
/* Типи даних та структури                                                     */
/* ========================================================================== */

/**
 * @brief Статуси виконання операцій низькорівневої релокації VTOR.
 */
typedef enum {
    VTOR_SUCCESS             =  0, /* Операцію виконано успішно */
    VTOR_ERR_NULL_ARG        = -1, /* Передано пустий вказівник */
    VTOR_ERR_BAD_ALIGNMENT   = -2, /* Адреса векторів не вирівняна на 128 байтів */
    VTOR_ERR_INVALID_MSP     = -3, /* Значення MSP виходить за межі SRAM */
    VTOR_ERR_INVALID_RESET   = -4, /* Адреса Reset Handler некоректна або без Thumb-біта */
    VTOR_ERR_OUT_OF_BOUNDS   = -5  /* Адреса Flash виходить за межі фізичної пам'яті */
} vtor_status_t;

/**
 * @brief Вказівник на функцію без параметрів для здійснення переходу на Reset Handler завантажувача.
 */
typedef void (*bootloader_jump_t)(void);

/**
 * @brief Структура параметрів карти пам'яті з базовими адресами Bootloader та Application Flash.
 */
typedef struct {
    uint32_t bootloader_base_addr; /* Базова адреса Flash для Bootloader (0x08000000) */
    uint32_t app_base_addr;        /* Базова адреса Flash для застосунку/DAPLink (0x08004000) */
    uint32_t flash_end_addr;       /* Верхня межа Flash-пам'яті мікроконтролера */
    uint32_t sram_start_addr;      /* Початкова адреса SRAM (0x20000000) */
    uint32_t sram_end_addr;        /* Кінцева адреса SRAM (0x20005000) */
} vtor_config_t;

/**
 * @brief Структура заголовка таблиці векторів для читання початкового значення MSP та адреси виклику скидання.
 */
typedef struct {
    uint32_t initial_msp;        /* Початкове значення вказівника стека (Main Stack Pointer) */
    uint32_t reset_handler_addr; /* Адреса точки входу обробника скидання (Reset Handler) */
} daplink_header_t;

/* ========================================================================== */
/* Прототипи функцій                                                           */
/* ========================================================================== */

/**
 * @brief Ініціалізує структуру конфігурації карти пам'яті за замовчуванням для ST-Link V2.1.
 * 
 * @param config Вказівник на структуру конфігурації vtor_config_t.
 * @return vtor_status_t Результат ініціалізації.
 */
vtor_status_t vtor_init_default_config(vtor_config_t *config);

/**
 * @brief Зчитує та верифікує заголовок таблиці векторів за вказаною адресою.
 * 
 * @param vector_table_addr Адреса початку таблиці векторів у Flash.
 * @param config Конфігурація пам'яті.
 * @param header Вихідна структура заголовка daplink_header_t.
 * @return vtor_status_t Результат верифікації.
 */
vtor_status_t vtor_verify_header(uint32_t vector_table_addr, 
                                 const vtor_config_t *config, 
                                 daplink_header_t *header);

/**
 * @brief Вимикає всі системні переривання NVIC та таймер SysTick.
 */
void vtor_disable_interrupts_and_systick(void);

/**
 * @brief Встановлює нове значення регістра SCB->VTOR з вирівнюванням та бар'єрами пам'яті.
 * 
 * @param vector_table_addr Нова адреса таблиці векторів переривань.
 * @return vtor_status_t Результат встановлення регістра.
 */
vtor_status_t vtor_set_offset(uint32_t vector_table_addr);

/**
 * @brief Безпечно готує процесор та здійснює перехід до завантажувача DAPLink.
 * 
 * @param vector_table_addr Адреса таблиці векторів target прошивки.
 * @param config Конфігурація пам'яті.
 * @return vtor_status_t Статус у разі помилки (при успіху функція не повертає керування).
 */
vtor_status_t vtor_jump_to_bootloader(uint32_t vector_table_addr, 
                                      const vtor_config_t *config);

#endif /* VTOR_RELOCATE_H */
