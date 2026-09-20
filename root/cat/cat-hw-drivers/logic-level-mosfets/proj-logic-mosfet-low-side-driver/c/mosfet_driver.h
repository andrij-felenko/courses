#ifndef MOSFET_DRIVER_H
#define MOSFET_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file mosfet_driver.h
 * @brief Драйвер силового MOSFET-ключа логічного рівня (IRLZ44N, IRL540N, IRL2203N, FDD8447L).
 *
 * Драйвер забезпечує безпечне керування потужним навантаженням безпосередньо від
 * GPIO-виходів мікроконтролера з логічними рівнями 3.3 В або 5 В. Підтримуються
 * початкове притиснення затвора (pull-down), дискретне перемикання (ON/OFF)
 * та ШІМ-регулювання для запобігання тривалому перебуванню транзистора
 * в лінійному режимі та його перегріву.
 */

#define MOSFET_PIN_UNUSED       0xFF
#define MOSFET_PWM_MAX_DUTY     100

/**
 * @brief Статуси виконання функцій драйвера MOSFET.
 */
typedef enum {
    MOSFET_OK = 0,                 /**< Операція успішна */
    MOSFET_ERROR_INVALID_PARAM,    /**< Некоректний параметр */
    MOSFET_ERROR_NOT_INITIALIZED,  /**< Драйвер не ініціалізовано */
    MOSFET_ERROR_PWM_DISABLED      /**< Спроба виклику ШІМ для конфігурації без ШІМ */
} mosfet_status_t;

/**
 * @brief Режими роботи силового ключа.
 */
typedef enum {
    MOSFET_MODE_OFF = 0,  /**< Вимкнено: затвор притиснутий до GND, транзистор у відсічці */
    MOSFET_MODE_ON,       /**< Увімкнено: затвор на VCC, транзистор у насиченні (мінімальний R_DS(on)) */
    MOSFET_MODE_PWM       /**< ШІМ-регулювання: плавна зміна скважності імпульсів */
} mosfet_mode_t;

/**
 * @brief Логічний рівень напруги керування затвором від МК.
 */
typedef enum {
    MOSFET_DRIVE_3V3 = 0,  /**< Керування від 3.3 В (потрібен логічний MOSFET з V_GS(th) <= 1.5-2.0 В) */
    MOSFET_DRIVE_5V0       /**< Керування від 5.0 В (для логічних MOSFET з V_GS(th) <= 2.5 В) */
} mosfet_drive_voltage_t;

/**
 * @brief Вказівник на функцію апаратного запису цифрового виводу GPIO.
 * @param pin_id Номер виводу GPIO.
 * @param state Стан виводу (true = HIGH, false = LOW).
 */
typedef void (*mosfet_gpio_write_fn)(uint8_t pin_id, bool state);

/**
 * @brief Вказівник на функцію апаратного налаштування коефіцієнта заповнення ШІМ.
 * @param pwm_channel Номер каналу ШІМ-таймера.
 * @param duty_percent Коефіцієнт заповнення у відсотках (0..100).
 */
typedef void (*mosfet_pwm_set_duty_fn)(uint8_t pwm_channel, uint8_t duty_percent);

/**
 * @brief Структура апаратної конфігурації драйвера MOSFET.
 */
typedef struct {
    uint8_t gpio_pin;                      /**< Номер виводу GPIO для керування затвором */
    uint8_t pwm_channel;                   /**< Канал апаратного таймера ШІМ */
    bool use_pwm;                          /**< Прапорець дозволу ШІМ-регулювання */
    mosfet_drive_voltage_t drive_voltage;  /**< Рівень керуючої напруги мікроконтролера */
    mosfet_gpio_write_fn gpio_write;       /**< Функція зворотного виклику для запису GPIO */
    mosfet_pwm_set_duty_fn pwm_set_duty;   /**< Функція зворотного виклику для ШІМ */
} mosfet_config_t;

/**
 * @brief Дескриптор стану драйвера MOSFET.
 */
typedef struct {
    mosfet_config_t config;        /**< Апаратна конфігурація */
    mosfet_mode_t current_mode;    /**< Поточний режим роботи ключа */
    uint8_t current_duty_percent;  /**< Поточний коефіцієнт заповнення ШІМ (0..100) */
    bool is_initialized;           /**< Прапорець завершення ініціалізації */
} mosfet_driver_t;

/**
 * @brief Ініціалізація драйвера з гарантованим початковим притисненням затвора до землі (pull-down).
 * @param handle Дескриптор драйвера.
 * @param config Налаштування периферії та виводів МК.
 * @return MOSFET_OK або код помилки.
 */
mosfet_status_t mosfet_init(mosfet_driver_t *handle, const mosfet_config_t *config);

/**
 * @brief Примусове безпечне вимкнення силового ключа (притиснення затвора до GND).
 * @param handle Дескриптор драйвера.
 * @return MOSFET_OK або код помилки.
 */
mosfet_status_t mosfet_safe_shutdown(mosfet_driver_t *handle);

/**
 * @brief Дискретне перемикання стану силового ключа (ON / OFF).
 * @param handle Дескриптор драйвера.
 * @param turn_on true — увімкнути ключ (насичення), false — вимкнути (відсічка).
 * @return MOSFET_OK або код помилки.
 */
mosfet_status_t mosfet_set_state(mosfet_driver_t *handle, bool turn_on);

/**
 * @brief Встановлення скважності ШІМ для плавної зміни потужності навантаження.
 * @param handle Дескриптор драйвера.
 * @param duty_percent Коефіцієнт заповнення у відсотках (0..100%).
 * @return MOSFET_OK або код помилки.
 */
mosfet_status_t mosfet_set_duty(mosfet_driver_t *handle, uint8_t duty_percent);

/**
 * @brief Отримання поточного стану ключа та коефіцієнта заповнення.
 * @param handle Дескриптор драйвера.
 * @param mode Вказівник для запису поточного режиму.
 * @param duty_percent Вказівник для запису поточної скважності ШІМ.
 * @return MOSFET_OK або код помилки.
 */
mosfet_status_t mosfet_get_status(const mosfet_driver_t *handle, mosfet_mode_t *mode, uint8_t *duty_percent);

/**
 * @brief Оцінка сумісності MOSFET за пороговою напругою V_GS(th) та напругою керування МК.
 * @param drive_voltage Керуюча напруга МК (3.3 В або 5 В).
 * @param vgs_th_max_mv Максимальна порогова напруга затвора V_GS(th) у мілівольтах.
 * @return true — транзистор повністю відкривається в режим насичення; false — ризик роботи у лінійному режимі та перегріву.
 */
bool mosfet_is_logic_level_compatible(mosfet_drive_voltage_t drive_voltage, uint16_t vgs_th_max_mv);

#endif /* MOSFET_DRIVER_H */
