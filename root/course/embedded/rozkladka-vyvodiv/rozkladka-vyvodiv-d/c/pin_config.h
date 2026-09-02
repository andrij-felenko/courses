#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

/*
 * Опис розкладки виводів STM32F4 у типах + перевірка опису до першого
 * запису в регістр. Заголовок CMSIS від виробника ("stm32f4xx.h") дає
 * GPIO_TypeDef, GPIOA..GPIOH, RCC та __disable_irq().
 */

#include "stm32f4xx.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Межі з технічного опису родини (розділи Absolute maximum ratings та I/O). */
#define PIN_MAX_CURRENT_MA    20U   /* струм одного звичайного виводу        */
#define PIN_BACKUP_MAX_MA      3U   /* PC13..PC15 — домен резервного живлення */
#define PORT_MAX_CURRENT_MA   80U   /* сума по всіх 16 ніжках одного порту   */
#define CHIP_MAX_CURRENT_MA  150U   /* сума по виводах живлення кристала     */

/* Поле MODER, два біти на ніжку. */
typedef enum {
    PIN_MODE_INPUT  = 0U,
    PIN_MODE_OUTPUT = 1U,
    PIN_MODE_ALT    = 2U,
    PIN_MODE_ANALOG = 3U
} pin_mode_t;

/* Поле OSPEEDR: крутизна фронту, а не частота сигналу. */
typedef enum {
    PIN_SPEED_LOW       = 0U,  /* t_rise ~25-30 нс, мінімум завад */
    PIN_SPEED_MEDIUM    = 1U,  /* t_rise ~10-12 нс */
    PIN_SPEED_HIGH      = 2U,  /* t_rise ~4-6 нс   */
    PIN_SPEED_VERY_HIGH = 3U   /* t_rise ~1.5 нс, спектр до ~233 МГц */
} pin_speed_t;

typedef enum {
    PIN_PULL_NONE = 0U,
    PIN_PULL_UP   = 1U,
    PIN_PULL_DOWN = 2U
} pin_pull_t;

typedef enum {
    PIN_PUSH_PULL  = 0U,
    PIN_OPEN_DRAIN = 1U   /* I2C та інші лінії з монтажним "І" */
} pin_otype_t;

/* Електричний клас із таблиці виводів технічного опису. */
typedef enum {
    PIN_CLASS_TT,      /* стандартний цифровий, межа VDD + 0.3 В        */
    PIN_CLASS_FT,      /* цифровий, витримує 5.5 В (немає діода на VDD) */
    PIN_CLASS_TTA,     /* заведений на мультиплексор АЦП/ЦАП            */
    PIN_CLASS_BACKUP,  /* PC13..PC15, домен резервного живлення         */
    PIN_CLASS_SYSTEM   /* PA13/PA14 — шина налагодження SWD             */
} pin_class_t;

/* Один рядок таблиці розпіновки плати. */
typedef struct {
    const char*   signal;   /* назва ланцюга зі схеми            */
    GPIO_TypeDef* port;
    uint8_t       pin;      /* 0..15                             */
    pin_mode_t    mode;
    uint8_t       af;       /* AF0..AF15, значуще лише для ALT   */
    pin_speed_t   speed;
    pin_pull_t    pull;
    pin_otype_t   otype;
    pin_class_t   klass;
    uint16_t      load_ma;  /* оголошений струм навантаження, мА */
} pin_desc_t;

typedef enum {
    PIN_OK = 0,
    PIN_ERR_UNKNOWN_PORT,     /* вказівник не схожий на порт GPIO        */
    PIN_ERR_PIN_RANGE,        /* номер ніжки поза 0..15                  */
    PIN_ERR_DEBUG_PIN,        /* спроба забрати PA13/PA14 у SWD          */
    PIN_ERR_CLASS_MISMATCH,   /* клас у таблиці суперечить самій ніжці    */
    PIN_ERR_ANALOG_ON_DIGITAL,/* аналоговий режим на не-АЦП виводі       */
    PIN_ERR_AF_RANGE,         /* номер альтернативної функції > 15       */
    PIN_ERR_AF_UNUSED,        /* AF заданий там, де режим не ALT         */
    PIN_ERR_SLEW_TOO_FAST,    /* надлишкова крутизна фронту (EMI)        */
    PIN_ERR_BACKUP_ALT,       /* альтернативна функція в домені RTC      */
    PIN_ERR_BACKUP_SPEED,     /* швидкість > 2 МГц у домені RTC          */
    PIN_ERR_BACKUP_CURRENT,   /* понад 3 мА на PC13..PC15                */
    PIN_ERR_PIN_CURRENT,      /* понад 20 мА на одній ніжці              */
    PIN_ERR_PORT_CURRENT,     /* понад 80 мА сумарно по порту            */
    PIN_ERR_CHIP_CURRENT,     /* понад 150 мА сумарно по кристалу        */
    PIN_ERR_DUPLICATE,        /* два сигнали претендують на одну ніжку   */
    PIN_ERR_LOCK_FAILED       /* послідовність LCKR не підтвердилася     */
} pin_status_t;

typedef struct {
    pin_status_t code;
    const char*  signal;  /* сигнал, на якому спрацювала перевірка       */
    const char*  rival;   /* другий претендент на ніжку, інакше NULL     */
    uint32_t     value;   /* що просили                                  */
    uint32_t     limit;   /* що дозволено                                */
} pin_error_t;

/*
 * Звіряє ВСЮ таблицю з межами й лише потім чіпає регістри: часткова
 * розкладка гірша за жодну, бо вивід уже перемкнувся, а помилку видно.
 * Повертає false і заповнює *err (якщо err != NULL) на першій же ваді.
 */
bool pin_apply_layout(const pin_desc_t* layout, size_t count, pin_error_t* err);

/*
 * Звільняє JTDI (PA15), JTDO/SWO (PB3) та NJTRST (PB4) під звичайний GPIO
 * і замикає PA13/PA14 апаратним замком LCKR до наступного скидання.
 */
bool pin_secure_debug_port(pin_error_t* err);

const char* pin_status_text(pin_status_t code);

uint16_t pin_port_budget_ma(const GPIO_TypeDef* port);
uint16_t pin_chip_budget_ma(void);

#endif /* PIN_CONFIG_H */
