#ifndef DAMPER_ACTUATOR_PORT_H
#define DAMPER_ACTUATOR_PORT_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file damper_actuator_port.h
 * @brief Доменний інтерфейс вихідного порту (Egress Port) сервоприводу заслінки.
 *
 * У гексагональній архітектурі доменне ядро не володіє інформацією про мережеві
 * протоколи (CAN, Modbus, LIN), формати кадрів чи специфіку заліза. Взаємодія
 * з виконавчим механізмом здійснюється виключно через абстрактний контракт порту.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Доменні коди результатів виконання команд актуатора.
 *
 * Повністю абстраговані від кодів помилок апаратних драйверів і протоколів шини.
 */
typedef enum {
    DAMPER_STATUS_OK = 0,               /**< Команду успішно сформовано та прийнято до відправки */
    DAMPER_STATUS_INVALID_ARG = 1,      /**< Неприпустимі параметри команди (NaN, нескінченність або від'ємна швидкість) */
    DAMPER_STATUS_BUS_ERROR = 2,        /**< Апаратна помилка шини зв'язку (скидання шини, помилка передачі) */
    DAMPER_STATUS_TIMEOUT = 3,          /**< Вичерпано ліміт часу очікування квитування чи готовності каналу */
    DAMPER_STATUS_NOT_INITIALIZED = 4   /**< Вихідний порт або пов'язаний адаптер не ініціалізовано */
} damper_status_t;

/**
 * @brief Режими функціонування приводу заслінки в доменній моделі.
 */
typedef enum {
    DAMPER_MODE_POSITION = 0,           /**< Штатний режим позиційного регулювання кута */
    DAMPER_MODE_CALIBRATE = 1,          /**< Режим калібрування нульової точки та упорів */
    DAMPER_MODE_EMERGENCY_SHUTDOWN = 2  /**< Аварійне скидання моменту та зупинка */
} damper_mode_t;

/**
 * @brief Доменна команда позиціонування сервоприводу заслінки.
 *
 * Оперує фізичними величинами (градуси, кутова швидкість у градусах за секунду),
 * унеможливлюючи появу "магічних" чисел або низькорівневих бітових масок у ядрі.
 */
typedef struct {
    float   target_angle_deg;       /**< Цільовий кут повороту заслінки [-10.0 .. 110.0] градусів */
    float   max_speed_deg_per_sec;  /**< Максимальна допустима кутова швидкість [0.0 .. 180.0] град/с */
    uint8_t hold_torque_pct;        /**< Відсоток номінального моменту утримання [0 .. 100]% */
    bool    hold_torque;            /**< Ознака ввімкнення утримання моменту після зупинки */
} damper_position_cmd_t;

/* Попереднє оголошення типу структури порту */
typedef struct damper_actuator_port damper_actuator_port_t;

/**
 * @brief Таблиця віртуальних методів (vtable) вихідного порту актуатора.
 *
 * Забезпечує поліморфізм мовою C: ядро викликає операції через покажчики на функції,
 * а конкретний вихідний адаптер надає їх реалізацію.
 */
typedef struct {
    damper_status_t (*set_position)(damper_actuator_port_t *self, const damper_position_cmd_t *cmd);
    damper_status_t (*emergency_stop)(damper_actuator_port_t *self);
    damper_status_t (*calibrate)(damper_actuator_port_t *self);
} damper_actuator_ops_t;

/**
 * @brief Екземпляр інтерфейсу порту актуатора.
 */
struct damper_actuator_port {
    const damper_actuator_ops_t *ops;
};

/**
 * @brief Зручні інлайн-обгортки для виклику операцій порту з доменного коду.
 */
static inline damper_status_t damper_port_set_position(
    damper_actuator_port_t *port, const damper_position_cmd_t *cmd)
{
    if (port == NULL || port->ops == NULL || port->ops->set_position == NULL) {
        return DAMPER_STATUS_NOT_INITIALIZED;
    }
    return port->ops->set_position(port, cmd);
}

static inline damper_status_t damper_port_emergency_stop(damper_actuator_port_t *port)
{
    if (port == NULL || port->ops == NULL || port->ops->emergency_stop == NULL) {
        return DAMPER_STATUS_NOT_INITIALIZED;
    }
    return port->ops->emergency_stop(port);
}

static inline damper_status_t damper_port_calibrate(damper_actuator_port_t *port)
{
    if (port == NULL || port->ops == NULL || port->ops->calibrate == NULL) {
        return DAMPER_STATUS_NOT_INITIALIZED;
    }
    return port->ops->calibrate(port);
}

/**
 * @brief Отримання рядкового представлення статусу для логування.
 */
static inline const char *damper_status_to_string(damper_status_t status)
{
    switch (status) {
        case DAMPER_STATUS_OK:              return "DAMPER_STATUS_OK";
        case DAMPER_STATUS_INVALID_ARG:     return "DAMPER_STATUS_INVALID_ARG";
        case DAMPER_STATUS_BUS_ERROR:       return "DAMPER_STATUS_BUS_ERROR";
        case DAMPER_STATUS_TIMEOUT:         return "DAMPER_STATUS_TIMEOUT";
        case DAMPER_STATUS_NOT_INITIALIZED: return "DAMPER_STATUS_NOT_INITIALIZED";
        default:                            return "DAMPER_STATUS_UNKNOWN";
    }
}

#ifdef __cplusplus
}
#endif

#endif /* DAMPER_ACTUATOR_PORT_H */
