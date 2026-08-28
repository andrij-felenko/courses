#ifndef CHARLIEPLEX_API_H
#define CHARLIEPLEX_API_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Фізичні режими роботи виводу в матриці Чарліплексингу.
 */
typedef enum {
    CHARLIE_PIN_HIZ  = 0, /**< Вхід, високий опір (Pull-Up/Down примусово вимкнено) */
    CHARLIE_PIN_HIGH = 1, /**< Вихід, високий рівень (+VCC, активне джерело струму) */
    CHARLIE_PIN_LOW  = 2  /**< Вихід, низький рівень (GND, активний стік струму) */
} CharliePinState;

/**
 * @brief Статуси виконання функцій API.
 */
typedef enum {
    CHARLIE_OK               =  0, /**< Успішне виконання операції */
    CHARLIE_ERR_INVALID_ARG  = -1, /**< Передано невалідний покажчик або нульовий розмір */
    CHARLIE_ERR_OUT_OF_BOUND = -2, /**< Індекс світлодіода виходить за межі діапазону N*(N-1) */
    CHARLIE_ERR_UNINITIALIZED= -3  /**< Драйвер не було ініціалізовано перед викликом */
} CharlieStatus;

/**
 * @brief Впорядкована пара виводів для підключення одного діода.
 */
typedef struct {
    uint8_t anode_pin;   /**< Індекс лінії, до якої підключено анод */
    uint8_t cathode_pin; /**< Індекс лінії, до якої підключено катод */
} CharlieLedDef;

/**
 * @brief Апаратні функції адаптера портів (Hardware Abstraction Layer).
 */
typedef struct {
    void (*set_pin_state)(uint8_t pin_index, CharliePinState state);
    void (*enter_critical)(void);
    void (*exit_critical)(void);
} CharlieHalConfig;

/**
 * @brief Контекст екземпляра драйвера матриці.
 */
typedef struct {
    const CharlieHalConfig *hal;
    const CharlieLedDef *led_map;
    uint8_t *frame_buffer;
    uint16_t led_count;
    uint8_t pin_count;
    uint8_t pwm_levels;
    uint16_t current_led_idx;
    uint8_t current_pwm_step;
    bool is_initialized;
} CharlieMatrixContext;

#ifdef __cplusplus
}
#endif

#endif /* CHARLIEPLEX_API_H */
