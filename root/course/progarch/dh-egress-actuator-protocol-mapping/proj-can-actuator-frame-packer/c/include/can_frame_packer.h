#ifndef CAN_FRAME_PACKER_H
#define CAN_FRAME_PACKER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file can_frame_packer.h
 * @brief Низькорівневе кодування сигналів кадру CAN за специфікацією DBC.
 *
 * Специфікація кадру керування заслінкою (Damper_Command, CAN ID: 0x140, DLC: 8):
 *
 * 1. TargetAngle (Цільовий кут):
 *    - DBC: SG_ Damper_TargetAngle : 0|12@1+ (0.05,-10.0) [-10.0|110.0] "deg"
 *    - Формат: 12 бітів, Little-Endian (Intel / direct order)
 *    - Зсув: -10.0 град, Крок: 0.05 град/LSB (Raw = (Phys - (-10.0)) / 0.05)
 *    - Розміщення: Байт 0 (біти 0..7) та Байт 1 (біти 0..3)
 *
 * 2. CommandMode (Режим керування):
 *    - DBC: SG_ Damper_CommandMode : 12|4@1+ (1,0) [0|15] ""
 *    - Формат: 4 біти, Little-Endian
 *    - Розміщення: Байт 1 (біти 4..7)
 *
 * 3. MaxSpeed (Максимальна швидкість):
 *    - DBC: SG_ Damper_MaxSpeed : 16|16@0+ (0.1,0) [0.0|180.0] "deg/s"
 *    - Формат: 16 бітів, Big-Endian (Motorola / reverse byte order)
 *    - Зсув: 0.0 град/с, Крок: 0.1 град/с/LSB (Raw = Phys / 0.1)
 *    - Розміщення: Байт 2 (MSB [15:8]) та Байт 3 (LSB [7:0])
 *
 * 4. ControlFlags (Прапорці дискретного керування):
 *    - DBC: SG_ TorqueEnable : 32|1@1+ (1,0) [0|1] ""
 *    - DBC: SG_ EmergencyStop : 33|1@1+ (1,0) [0|1] ""
 *    - Розміщення: Байт 4 (біт 0: Torque, біт 1: Emergency, біти 2..7: Резерв)
 *
 * 5. HoldTorquePercent (Відсоток утримання моменту):
 *    - DBC: SG_ HoldTorquePercent : 40|8@1+ (1,0) [0|100] "%"
 *    - Розміщення: Байт 5 (біти 0..7)
 *
 * 6. RollingCounter (4-бітний циклічний лічильник):
 *    - DBC: SG_ RollingCounter : 48|4@1+ (1,0) [0|15] ""
 *    - Розміщення: Байт 6 (біти 0..3), біти 4..7 — Heartbeat маркер (0x50)
 *
 * 7. CRC-8 (Контрольна сума кадру за поліномом AUTOSAR / SAE J1850):
 *    - DBC: SG_ FrameCRC8 : 56|8@1+ (1,0) [0|255] ""
 *    - Поліном: 0x2F (x^8 + x^5 + x^3 + x^2 + x + 1), Init: 0xFF, Final XOR: 0xFF
 *    - Розраховується по байтах 0..6
 */

#ifdef __cplusplus
extern "C" {
#endif

#define CAN_FRAME_PAYLOAD_SIZE      8U
#define CAN_ID_DAMPER_CMD           0x140U

/* Параметри квантування кута заслінки (Little-Endian) */
#define DAMPER_ANGLE_OFFSET_DEG     (-10.0f)
#define DAMPER_ANGLE_SCALE_DEG      (0.05f)
#define DAMPER_ANGLE_MIN_DEG        (-10.0f)
#define DAMPER_ANGLE_MAX_DEG        (110.0f)
#define DAMPER_ANGLE_RAW_MAX        (4095U)     /* 12 бітів (0x0FFF) */

/* Параметри квантування кутової швидкості (Big-Endian) */
#define DAMPER_SPEED_OFFSET_DPS     (0.0f)
#define DAMPER_SPEED_SCALE_DPS      (0.1f)
#define DAMPER_SPEED_MIN_DPS        (0.0f)
#define DAMPER_SPEED_MAX_DPS        (180.0f)
#define DAMPER_SPEED_RAW_MAX        (65535U)    /* 16 бітів (0xFFFF) */

/* Межі моменту утримання */
#define DAMPER_TORQUE_MIN_PCT       (0U)
#define DAMPER_TORQUE_MAX_PCT       (100U)

/* Параметри 4-бітного циклічного лічильника */
#define DAMPER_COUNTER_MAX          (15U)
#define DAMPER_COUNTER_MASK         (0x0FU)

/* Поліном та ініціалізаційні константи CRC-8 (профіль AUTOSAR / CAN-FD CRC-8) */
#define CAN_CRC8_POLYNOMIAL         (0x2FU)     /* x^8 + x^5 + x^3 + x^2 + x + 1 */
#define CAN_CRC8_INITIAL_VALUE      (0xFFU)
#define CAN_CRC8_FINAL_XOR          (0xFFU)

/**
 * @brief Сирий 8-байтний кадр шини CAN 2.0.
 */
typedef struct {
    uint32_t can_id;                        /**< 11-бітний або 29-бітний ідентифікатор */
    uint8_t  dlc;                           /**< Кількість байтів корисного навантаження (8) */
    uint8_t  data[CAN_FRAME_PAYLOAD_SIZE];  /**< Буфер байтів кадру */
} can_raw_frame_t;

/**
 * @brief Непаковані розпаковані параметри сигналу для кодування у кадр.
 */
typedef struct {
    float   target_angle_deg;       /**< Фізичний кут повороту (-10.0 .. 110.0 град) */
    float   max_speed_deg_per_sec;  /**< Фізична кутова швидкість (0.0 .. 180.0 град/с) */
    uint8_t command_mode;           /**< Режим роботи (0..15) */
    bool    torque_enable;          /**< Прапорець дозволу моменту */
    bool    emergency_stop;         /**< Прапорець аварійної зупинки */
    uint8_t hold_torque_pct;        /**< Відсоток струму утримання (0..100) */
    uint8_t rolling_counter;        /**< Циклічний лічильник (0..15) */
} can_damper_signals_t;

/**
 * @brief Квантує неперервну фізичну величину у ціле число з безпечним обмеженням (clamping).
 *
 * @param phys_value Фізичне значення.
 * @param min_phys   Мінімальна фізична межа.
 * @param max_phys   Максимальна фізична межа.
 * @param offset     Зміщення за DBC.
 * @param scale      Масштабний коефіцієнт (крок LSB) за DBC.
 * @param raw_max    Максимальне цілочисельне значення за розрядністю бітового поля.
 * @return Квантоване цілочисельне значення.
 */
uint16_t can_quantize_signal(
    float phys_value,
    float min_phys,
    float max_phys,
    float offset,
    float scale,
    uint16_t raw_max
);

/**
 * @brief Відновлює неперервну величину з квантованого цілого числа.
 */
float can_dequantize_signal(uint16_t raw_value, float offset, float scale);

/**
 * @brief Обчислює контрольний код CRC-8 над заданим буфером байтів.
 *
 * @param data Вказівник на байти кадру.
 * @param length Кількість байтів (зазвичай 7 для обчислення 8-го байта).
 * @return Розраховане значення CRC-8.
 */
uint8_t can_calculate_crc8(const uint8_t *data, size_t length);

/**
 * @brief Інкрементує 4-бітний лічильник послідовності з переповненням за модулем 16.
 */
uint8_t can_increment_counter(uint8_t current_counter);

/**
 * @brief Пакує сигнали у фіксований 8-байтний буфер CAN-кадру за специфікацією DBC.
 *
 * @param signals Джерело непакованих параметрів.
 * @param frame   Цільовий сирий кадр CAN.
 */
void can_pack_damper_frame(const can_damper_signals_t *signals, can_raw_frame_t *frame);

/**
 * @brief Розпаковує сигнали із сирого 8-байтного кадру CAN (для верифікації та тестів).
 *
 * @param frame   Сирий кадр CAN.
 * @param signals Структура для запису відновлених фізичних параметрів.
 */
void can_unpack_damper_frame(const can_raw_frame_t *frame, can_damper_signals_t *signals);

#ifdef __cplusplus
}
#endif

#endif /* CAN_FRAME_PACKER_H */
