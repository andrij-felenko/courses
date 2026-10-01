#ifndef ESP8266_RESET_H
#define ESP8266_RESET_H

#include <stdint.h>
#include <stdbool.h>

/* Адреси регістрів GPIO ESP8266 */
#define GPIO_BASE                   0x60000300
#define GPIO_IN_REG                 (*(volatile uint32_t *)(GPIO_BASE + 0x18))
#define GPIO_ENABLE_REG             (*(volatile uint32_t *)(GPIO_BASE + 0x0C))

/* Маски сигнальних конфігураційних виводів завантаження (strapping pins) */
#define GPIO0_PIN_BIT               (1 << 0)
#define GPIO2_PIN_BIT               (1 << 2)

/* Перерашування причин скидання мікроконтролера ESP8266 */
typedef enum {
    REASON_DEFAULT_RST      = 0,  /* Звичайне увімкнення живлення (Power ON) */
    REASON_WDT_RST          = 1,  /* Апаратне скидання сторожовим таймером (WDT) */
    REASON_EXCEPTION_RST    = 2,  /* Скидання через програмне виключення (Exception) */
    REASON_SOFT_WDT_RST     = 3,  /* Програмний сторожовий таймер */
    REASON_SOFT_RESTART     = 4,  /* Програмний перезапуск через system_restart */
    REASON_DEEP_SLEEP_AWAKE = 5,  /* Пробудження з режиму глибокого сну */
    REASON_EXT_SYS_RST      = 6   /* Зовнішнє апаратне скидання (лінія RST / Auto-Reset DTR/RTS) */
} rst_reason_t;

/* Структура системної інформації про причину скидання */
typedef struct {
    rst_reason_t reason;          /* Код причини скидання */
    uint32_t     exccause;        /* Код виключення (якщо причина EXCEPTION) */
    uint32_t     epc1;            /* Лічильник команд EPC1 */
    uint32_t     epc2;            /* Лічильник команд EPC2 */
    uint32_t     epc3;            /* Лічильник команд EPC3 */
    uint32_t     excvaddr;        /* Адреса помилки доступу */
    uint32_t     depc;            /* Лічильник команд DEPC */
} rst_info_t;

/**
 * Опитування стану виводів GPIO0 та GPIO2 під час запусків
 */
static inline bool is_gpio0_low(void) {
    return (GPIO_IN_REG & GPIO0_PIN_BIT) == 0;
}

static inline bool is_gpio2_high(void) {
    return (GPIO_IN_REG & GPIO2_PIN_BIT) != 0;
}

/**
 * Перевірка, чи скидання відбулося апаратно від лінії RST/Auto-Reset
 */
static inline bool is_auto_reset_triggered(const rst_info_t *info) {
    return (info != NULL) && (info->reason == REASON_EXT_SYS_RST);
}

#endif /* ESP8266_RESET_H */
