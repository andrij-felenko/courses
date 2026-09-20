#include "can_frame_packer.h"
#include <math.h>
#include <string.h>

/**
 * @brief Квантування фізичної величини з безпечним обмеженням (clamping) та округленням.
 */
uint16_t can_quantize_signal(
    float phys_value,
    float min_phys,
    float max_phys,
    float offset,
    float scale,
    uint16_t raw_max
) {
    if (scale <= 0.0f) {
        return 0U;
    }

    /* Захист від NaN: у разі недійсного числа фіксуємо мінімальну безпечну межу */
    if (isnan(phys_value)) {
        phys_value = min_phys;
    }

    /* Безпечне насичення (clamping) величини у допустимих фізичних межах */
    if (phys_value < min_phys) {
        phys_value = min_phys;
    } else if (phys_value > max_phys) {
        phys_value = max_phys;
    }

    /* Розрахунок дискретного значення за формулою: raw = (phys - offset) / scale */
    float raw_float = ((phys_value - offset) / scale) + 0.5f;
    if (raw_float < 0.0f) {
        return 0U;
    }

    uint32_t raw_uint = (uint32_t)raw_float;
    if (raw_uint > (uint32_t)raw_max) {
        raw_uint = (uint32_t)raw_max;
    }

    return (uint16_t)raw_uint;
}

/**
 * @brief Відновлення фізичної величини за формулою: phys = offset + (raw * scale).
 */
float can_dequantize_signal(uint16_t raw_value, float offset, float scale) {
    return offset + ((float)raw_value * scale);
}

/**
 * @brief Інкремент 4-бітного циклічного лічильника (0 .. 15).
 */
uint8_t can_increment_counter(uint8_t current_counter) {
    return (uint8_t)((current_counter + 1U) & DAMPER_COUNTER_MASK);
}

/**
 * @brief Обчислення контрольної суми CRC-8 (AUTOSAR / SAE J1850).
 *
 * Поліном: 0x2F (x^8 + x^5 + x^3 + x^2 + x + 1).
 * Стартове значення: 0xFF, фінальна інверсія (XOR): 0xFF.
 */
uint8_t can_calculate_crc8(const uint8_t *data, size_t length) {
    if (data == NULL || length == 0U) {
        return 0U;
    }

    uint8_t crc = CAN_CRC8_INITIAL_VALUE;

    for (size_t i = 0U; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0U; bit < 8U; ++bit) {
            if ((crc & 0x80U) != 0U) {
                crc = (uint8_t)((crc << 1U) ^ CAN_CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1U);
            }
        }
    }

    return (uint8_t)(crc ^ CAN_CRC8_FINAL_XOR);
}

/**
 * @brief Пакує сигнали у фіксований 8-байтний буфер CAN за специфікацією DBC.
 */
void can_pack_damper_frame(const can_damper_signals_t *signals, can_raw_frame_t *frame) {
    if (signals == NULL || frame == NULL) {
        return;
    }

    memset(frame->data, 0, sizeof(frame->data));
    frame->can_id = CAN_ID_DAMPER_CMD;
    frame->dlc = CAN_FRAME_PAYLOAD_SIZE;

    /* 1. Квантування цільового кута (12 бітів) */
    uint16_t raw_angle = can_quantize_signal(
        signals->target_angle_deg,
        DAMPER_ANGLE_MIN_DEG,
        DAMPER_ANGLE_MAX_DEG,
        DAMPER_ANGLE_OFFSET_DEG,
        DAMPER_ANGLE_SCALE_DEG,
        DAMPER_ANGLE_RAW_MAX
    );

    /* 2. Квантування максимальної кутової швидкості (16 бітів) */
    uint16_t raw_speed = can_quantize_signal(
        signals->max_speed_deg_per_sec,
        DAMPER_SPEED_MIN_DPS,
        DAMPER_SPEED_MAX_DPS,
        DAMPER_SPEED_OFFSET_DPS,
        DAMPER_SPEED_SCALE_DPS,
        DAMPER_SPEED_RAW_MAX
    );

    /*
     * 3. Розміщення Little-Endian (Intel) для цільового кута:
     *    - Байт 0: молодші 8 бітів кута [7:0]
     *    - Байт 1: старші 4 біти кута [11:8] у бітах [3:0]
     *    - Байт 1: код режиму керування [3:0] у бітах [7:4]
     */
    frame->data[0] = (uint8_t)(raw_angle & 0x00FFU);
    frame->data[1] = (uint8_t)((raw_angle >> 8U) & 0x000FU);
    frame->data[1] |= (uint8_t)((signals->command_mode & 0x0FU) << 4U);

    /*
     * 4. Розміщення Big-Endian (Motorola) для кутової швидкості:
     *    - Байт 2: старший байт швидкості [15:8] (MSB за меншою адресою пам'яті)
     *    - Байт 3: молодший байт швидкості [7:0]  (LSB за більшою адресою пам'яті)
     */
    frame->data[2] = (uint8_t)((raw_speed >> 8U) & 0x00FFU);
    frame->data[3] = (uint8_t)(raw_speed & 0x00FFU);

    /*
     * 5. Байт 4: Прапорці дискретного керування
     *    - Біт 0: Дозвіл моменту (TorqueEnable)
     *    - Біт 1: Аварійна зупинка (EmergencyStop)
     *    - Біти [7:2]: Резервні нулі
     */
    uint8_t flags = 0U;
    if (signals->torque_enable) {
        flags |= (1U << 0);
    }
    if (signals->emergency_stop) {
        flags |= (1U << 1);
    }
    frame->data[4] = flags;

    /*
     * 6. Байт 5: Відсоток моменту утримання [0 .. 100]% з безпечним обмеженням
     */
    uint8_t torque_pct = signals->hold_torque_pct;
    if (torque_pct > DAMPER_TORQUE_MAX_PCT) {
        torque_pct = DAMPER_TORQUE_MAX_PCT;
    }
    frame->data[5] = torque_pct;

    /*
     * 7. Байт 6: Службові поля цілісності
     *    - Біти [3:0]: 4-бітний rolling counter (0 .. 15)
     *    - Біти [7:4]: Ознака серцебиття / статусу зв'язку (фіксований патерн 0x50)
     */
    uint8_t counter_nibble = signals->rolling_counter & DAMPER_COUNTER_MASK;
    frame->data[6] = (uint8_t)(counter_nibble | 0x50U);

    /*
     * 8. Байт 7: Контрольна сума CRC-8, обчислена над першими 7 байтами кадру (0..6)
     */
    frame->data[7] = can_calculate_crc8(frame->data, 7U);
}

/**
 * @brief Розпаковує сигнали із сирого 8-байтного кадру CAN.
 */
void can_unpack_damper_frame(const can_raw_frame_t *frame, can_damper_signals_t *signals) {
    if (frame == NULL || signals == NULL) {
        return;
    }

    /* Відновлення цільового кута (Little-Endian / Intel) */
    uint16_t raw_angle = (uint16_t)frame->data[0] |
                         (((uint16_t)(frame->data[1] & 0x0FU)) << 8U);
    signals->target_angle_deg = can_dequantize_signal(
        raw_angle, DAMPER_ANGLE_OFFSET_DEG, DAMPER_ANGLE_SCALE_DEG);

    /* Відновлення режиму команди */
    signals->command_mode = (uint8_t)((frame->data[1] >> 4U) & 0x0FU);

    /* Відновлення швидкості (Big-Endian / Motorola) */
    uint16_t raw_speed = (((uint16_t)frame->data[2]) << 8U) |
                         ((uint16_t)frame->data[3]);
    signals->max_speed_deg_per_sec = can_dequantize_signal(
        raw_speed, DAMPER_SPEED_OFFSET_DPS, DAMPER_SPEED_SCALE_DPS);

    /* Відновлення прапорців керування */
    signals->torque_enable = (frame->data[4] & (1U << 0)) != 0U;
    signals->emergency_stop = (frame->data[4] & (1U << 1)) != 0U;

    /* Відновлення відсотка моменту */
    signals->hold_torque_pct = frame->data[5];

    /* Відновлення циклічного лічильника */
    signals->rolling_counter = frame->data[6] & DAMPER_COUNTER_MASK;
}
