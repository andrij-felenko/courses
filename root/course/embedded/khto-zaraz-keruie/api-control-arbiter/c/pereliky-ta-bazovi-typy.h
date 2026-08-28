#ifndef CONTROL_ARBITER_TYPES_H
#define CONTROL_ARBITER_TYPES_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Ідентифікатори джерел керування в порядку зменшення пріоритету.
 */
typedef enum {
    SOURCE_FAILSAFE    = 0,  /**< Аварійний контур безпеки (найвищий авторитет) */
    SOURCE_RC_PILOT    = 1,  /**< Ручний пульт пілота (ручне перехоплення стіками) */
    SOURCE_OFFBOARD    = 2,  /**< Бортовий комп'ютер / планувальник / AI-зір */
    SOURCE_GCS_MISSION = 3,  /**< Наземна станція / автопілотна місія за точками */
    SOURCE_COUNT       = 4,  /**< Загальна кількість підтримуваних джерел */
    SOURCE_NONE        = 255 /**< Жодне джерело не вибрано / безпечний дефолт */
} control_source_id_t;

/**
 * @brief Бітова маска станів життєздатності слота джерела.
 */
typedef enum {
    SOURCE_STATE_INACTIVE     = 0,       /**< Джерело вимкнене або ще не надсилало кадрів */
    SOURCE_STATE_ACTIVE       = (1 << 0),/**< Сигнал свіжий, таймаут не перевищено */
    SOURCE_STATE_TIMED_OUT    = (1 << 1),/**< Heartbeat або потік даних прострочено */
    SOURCE_STATE_PREEMPTED    = (1 << 2),/**< Джерело живе, але витіснене вищим пріоритетом */
    SOURCE_STATE_STICK_ACTIVE = (1 << 3) /**< Зафіксовано рух стіка поза зоною мертвої смуги */
} source_state_flags_t;

/**
 * @brief Тип цільової уставки для внутрішнього контуру стабілізації.
 */
typedef enum {
    SETPOINT_TYPE_ATTITUDE_RATE, /**< Кутові швидкості (рад/с) + нормалізований газ [0..1] */
    SETPOINT_TYPE_ATTITUDE_ANGLE,/**< Кути Ойлера (крен/тангаж/курс у рад) + газ [0..1] */
    SETPOINT_TYPE_VELOCITY_NED,  /**< Вектор швидкості у системі NED (м/с) + курс */
    SETPOINT_TYPE_POSITION_NED   /**< Координати цілі у системі NED (м) */
} setpoint_type_t;

/**
 * @brief Уніфікований контейнер уставки керування.
 */
typedef struct {
    uint64_t timestamp_us;       /**< Монотонна мітка часу створення/прийому кадру (мкс) */
    setpoint_type_t type;        /**< Фізичний режим уставки */
    float channels[4];           /**< Канали: [0]=Roll, [1]=Pitch, [2]=Yaw, [3]=Thrust */
    bool valid;                  /**< Прапорець цілісності та валідності даних */
} control_setpoint_t;

/**
 * @brief Параметри конфігурації арбітражу для конкретного джерела.
 */
typedef struct {
    uint32_t timeout_us;         /**< Поріг сторожового таймера неактивності (мкс) */
    float stick_deadband;        /**< Мертва смуга виявлення перехоплення стіком [0..1] */
    float max_slew_rate[4];      /**< Максимальна швидкість зміни каналів (од/с) */
    bool allow_stick_override;   /**< Дозвіл витіснення іншого джерела рухом стіків */
} source_config_t;

#endif /* CONTROL_ARBITER_TYPES_H */
