/* bsp_bringup.h — Каркас безпечного запуску для Cortex-M / STM32 (C) */
#ifndef BSP_BRINGUP_H
#define BSP_BRINGUP_H

#include <stdint.h>
#include <stdbool.h>

/* Статуси джерела системного тактування */
typedef enum {
    CLOCK_SOURCE_HSI_FALLBACK = 0, /* Аварійний запуск від внутрішнього RC-генератора */
    CLOCK_SOURCE_HSE_CRYSTAL  = 1, /* Успішний запуск від зовнішнього кварцу */
    CLOCK_SOURCE_ERROR_TIMEOUT = 2  /* Таймаут збудження зовнішнього контуру */
} clock_source_status_t;

/* Причини останнього скидання мікроконтролера */
typedef enum {
    RESET_CAUSE_UNKNOWN      = 0,
    RESET_CAUSE_POWER_ON     = 1, /* Штатне увімкнення живлення (POR/PDR) */
    RESET_CAUSE_BROWNOUT     = 2, /* Аварійне просідання напруги живлення (BOR) */
    RESET_CAUSE_WATCHDOG     = 3, /* Спрацьовування сторожового таймера (IWDG/WWDG) */
    RESET_CAUSE_SOFTWARE     = 4  /* Програмне скидання ядра (NVIC_SystemReset) */
} reset_cause_t;

/* Структура телеметрії апаратного здоров'я плати */
typedef struct {
    uint32_t core_frequency_hz;       /* Реальна виміряна частота системної шини SYSCLK */
    clock_source_status_t clock_status; /* Поточне активне джерело тактування */
    reset_cause_t reset_reason;        /* Причина попереднього перезавантаження */
    bool debugger_connected;          /* Прапорець наявності активного підключення SWD/JTAG */
} hardware_health_t;

/* Безпечна ініціалізація тактування з фіксованим таймаутом і Fallback-механізмом */
clock_source_status_t bsp_clock_init_safe(uint32_t hse_timeout_cycles);

/* Паркування невикористаних виводів у режим Analog для усунення струмів витоку */
void bsp_gpio_park_unused_pins(void);

/* Неблокуюче виведення діагностичного повідомлення в ITM SWO або буфер логування */
void bsp_diag_log(const char* message);

/* Опитування регістра стану скидання RCC_CSR та збір діагностичного звіту */
hardware_health_t bsp_check_hardware_health(void);

#endif /* BSP_BRINGUP_H */
