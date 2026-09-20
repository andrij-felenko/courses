#ifndef PENDANT_TYPES_H
#define PENDANT_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @brief Стани подвійного каналу кнопки аварійного зупину (E-Stop).
 */
typedef enum {
    ESTOP_OK = 0,                ///< Обидва канали замкнені (нормальна робота)
    ESTOP_TRIGGERED,             ///< Кнопку натиснуто (розмикання ланцюга)
    ESTOP_FAULT_DISCREPANCY      ///< Помилка неузгодженості каналів (розсинхронізація)
} estop_state_t;

/**
 * @brief Стани 3-позиційного клавіша дозволу (Enabling Switch / Deadman Switch).
 */
typedef enum {
    ENABLING_OFF_RELEASED = 0,   ///< Позиція 1: Клавіш відпущено (рух заборонено)
    ENABLING_CENTER_ENABLED,     ///< Позиція 2: Середнє утримання (рух ДОЗВОЛЕНО)
    ENABLING_PANIC_COMPRESSED,   ///< Позиція 3: Панічне стискання (рух заборонено)
    ENABLING_FAULT_DISCREPANCY   ///< Помилка неузгодженості каналів
} enabling_switch_state_t;

/**
 * @brief Контекст крос-моніторингу двоканальних кіл безпеки.
 */
typedef struct {
    uint8_t estop_ch1;           ///< Сирий стан 1-го каналу E-Stop (1 - OK, 0 - розімкнено)
    uint8_t estop_ch2;           ///< Сирий стан 2-го каналу E-Stop (1 - OK, 0 - розімкнено)
    uint8_t enabling_ch1;        ///< Стан 1-го каналу клавіша дозволу (0, 1, 2)
    uint8_t enabling_ch2;        ///< Стан 2-го каналу клавіша дозволу (0, 1, 2)

    estop_state_t estop_status;           ///< Обчислений стан E-Stop
    enabling_switch_state_t enabling_status; ///< Обчислений стан клавіша дозволу
    uint32_t discrepancy_start_ms;        ///< Таймер фіксації неузгодженості
    bool discrepancy_active;              ///< Прапор активного відліку неузгодженості
    bool safety_ok;                       ///< Загальний результуючий дозвіл руху (Safety OK)
} pendant_safety_state_t;

/**
 * @brief Контекст 3D-джойстика (Jog Stick) для ручного позиціонування робота.
 */
typedef struct {
    uint16_t raw_x;              ///< Сире значення ADC по осі X (0..4095)
    uint16_t raw_y;              ///< Сире значення ADC по осі Y (0..4095)
    uint16_t raw_z;              ///< Сире значення ADC по осі Z (0..4095)

    int16_t norm_x;              ///< Нормалізована швидкість по осі X (-1000..+1000)
    int16_t norm_y;              ///< Нормалізована швидкість по осі Y (-1000..+1000)
    int16_t norm_z;              ///< Нормалізована швидкість по осі Z (-1000..+1000)

    uint16_t deadband;           ///< Поріг нечутливої зони навколо центру ADC (наприклад, 100)
} pendant_joystick_t;

/**
 * @brief Упакований бінарний кадр телеметрії пульта для передачі по шині.
 */
#pragma pack(push, 1)
typedef struct {
    uint8_t header[2];           ///< Заголовок кадру (0xAA, 0x55)
    uint8_t safety_flags;        ///< Бітові прапори станів безпеки
    int16_t jog_x;               ///< Швидкість по осі X
    int16_t jog_y;               ///< Швидкість по осі Y
    int16_t jog_z;               ///< Швидкість по осі Z
    uint16_t crc16;              ///< Контрольна сума CRC-16 (Modbus)
} pendant_frame_t;
#pragma pack(pop)

#endif // PENDANT_TYPES_H
