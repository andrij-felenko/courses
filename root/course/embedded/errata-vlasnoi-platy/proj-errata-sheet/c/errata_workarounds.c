/* errata_workarounds.c — Реалізація програмних обхідних шляхів для Rev A (C99) */
#include <stdint.h>
#include <stdbool.h>

/* Визначення ревізій плати */
typedef enum {
    BOARD_REV_UNKNOWN = 0,
    BOARD_REV_A       = 1,
    BOARD_REV_B       = 2
} board_rev_t;

/* Емуляція регістрового доступу до апаратних пінів */
typedef enum {
    PIN_MODE_INPUT_FLOATING,
    PIN_MODE_OUTPUT_PP,
    PIN_MODE_AF_OD
} pin_mode_t;

typedef enum {
    PIN_STATE_LOW  = 0,
    PIN_STATE_HIGH = 1
} pin_state_t;

/* Прототипи платформних функцій введення/виведення */
extern void hal_gpio_set_mode(uint8_t port, uint8_t pin, pin_mode_t mode);
extern void hal_gpio_write(uint8_t port, uint8_t pin, pin_state_t state);
extern pin_state_t hal_gpio_read(uint8_t port, uint8_t pin);
extern void hal_delay_ms(uint32_t ms);
extern bool hal_i2c_init_bus(void);
extern void hal_i2c_deinit_bus(void);

/* Призначення апаратних виводів */
#define PORT_PWR   0
#define PIN_PWR    4   /* Керування VDD давача */
#define PORT_I2C   1
#define PIN_SDA    7   /* Лінія даних */
#define PIN_SCL    6   /* Лінія такту */

/* =========================================================================
 * 1. Безпечний Power-Cycle давача з ізоляцією шини (ERR-HW-001)
 * ========================================================================= */

/**
 * @brief Повний цикл безпечного скидання живлення давача.
 * Усуває паразитно підживлене блокування через ESD-діоди.
 */
bool errata_sensor_safe_power_cycle(board_rev_t rev) {
    if (rev == BOARD_REV_A) {
        /* КРОК 1: Деініціалізація апаратного контролера I2C */
        hal_i2c_deinit_bus();

        /* КРОК 2: Ізоляція шини — переведення SDA та SCL у High-Z без підтяжок */
        hal_gpio_set_mode(PORT_I2C, PIN_SDA, PIN_MODE_INPUT_FLOATING);
        hal_gpio_set_mode(PORT_I2C, PIN_SCL, PIN_MODE_INPUT_FLOATING);

        /* КРОК 3: Зняття живлення з лінії VDD */
        hal_gpio_set_mode(PORT_PWR, PIN_PWR, PIN_MODE_OUTPUT_PP);
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_LOW);

        /* КРОК 4: Витримка паузи розряджання блокувальних конденсаторів */
        hal_delay_ms(30);

        /* КРОК 5: Подача живлення */
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_HIGH);

        /* КРОК 6: Пауза стабілізації джерела живлення та внутрішнього POR давача */
        hal_delay_ms(15);

        /* КРОК 7: Повторна ініціалізація шини I2C */
        hal_gpio_set_mode(PORT_I2C, PIN_SDA, PIN_MODE_AF_OD);
        hal_gpio_set_mode(PORT_I2C, PIN_SCL, PIN_MODE_AF_OD);

        return hal_i2c_init_bus();
    } else {
        /* У ревізії B є апаратний вивід скидання RESET */
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_LOW);
        hal_delay_ms(2);
        hal_gpio_write(PORT_PWR, PIN_PWR, PIN_STATE_HIGH);
        hal_delay_ms(5);
        return true;
    }
}

/* =========================================================================
 * 2. Періодичний таймерний фільтр брязкоту контактів (ERR-HW-003)
 * ========================================================================= */

typedef struct {
    uint8_t port;
    uint8_t pin;
    uint8_t history;     /* Зсувний регістр історії вибірок */
    bool    stable_state;/* Відфільтрований стабільний стан */
} debouncer_t;

void debouncer_init(debouncer_t *deb, uint8_t port, uint8_t pin) {
    deb->port = port;
    deb->pin = pin;
    deb->history = 0xFF;
    deb->stable_state = true;
    hal_gpio_set_mode(port, pin, PIN_MODE_INPUT_FLOATING);
}

/**
 * @brief Викликається щостійно в системному таймері (наприклад, кожні 10 мс).
 * @return true, якщо зафіксовано подію натискання (перехід у LOW).
 */
bool debouncer_update(debouncer_t *deb) {
    pin_state_t raw = hal_gpio_read(deb->port, deb->pin);

    /* Зсуваємо історію та додаємо новий відлік */
    deb->history = (uint8_t)((deb->history << 1) | (raw == PIN_STATE_HIGH ? 1 : 0));

    /* Якщо всі останні 8 відліків (80 мс) стабільно нулі, фіксуємо натискання */
    if (deb->history == 0x00 && deb->stable_state == true) {
        deb->stable_state = false;
        return true; /* Подія: Кнопку натиснуто */
    }

    /* Якщо всі останні 8 відліків стабільно одиниці, фіксуємо відпускання */
    if (deb->history == 0xFF && deb->stable_state == false) {
        deb->stable_state = true;
    }

    return false;
}
