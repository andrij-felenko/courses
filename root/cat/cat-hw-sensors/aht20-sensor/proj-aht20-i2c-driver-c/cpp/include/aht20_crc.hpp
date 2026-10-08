#pragma once

#include <cstddef>
#include <cstdint>

namespace aht20 {

/**
 * @brief Клас для обчислення та перевірки контрольної суми CRC8 для давача AHT20.
 * Використовує поліном 0x31 (x^8 + x^5 + x^4 + 1) з початковим значенням 0xFF.
 */
class Aht20Crc8 {
public:
    /**
     * @brief Обчислює CRC8 для заданого масиву байтів.
     * @param data Вказівник на масив даних.
     * @param length Довжина масиву в байтах.
     * @param init Початкове значення регістра (за замовчуванням 0xFF).
     * @return Обчислена 8-бітна контрольна сума.
     */
    static uint8_t calculate(const uint8_t* data, size_t length, uint8_t init = 0xFF) noexcept {
        uint8_t crc = init;
        for (size_t i = 0; i < length; ++i) {
            crc ^= data[i];
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x80) {
                    crc = static_cast<uint8_t>((crc << 1) ^ 0x31);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    /**
     * @brief Перевіряє цілісність 7-байтового кадру AHT20.
     * @param frame Масив із 7 байтів (байти 0..5 - дані, байт 6 - контрольна сума).
     * @param length Загальна довжина кадру (мусить бути 7 байтів).
     * @return true, якщо CRC збігається, false - якщо кадр пошкоджено.
     */
    static bool verify(const uint8_t* frame, size_t length = 7) noexcept {
        if (frame == nullptr || length < 7) {
            return false;
        }
        const uint8_t expected_crc = frame[6];
        const uint8_t computed_crc = calculate(frame, 6);
        return expected_crc == computed_crc;
    }
};

} // namespace aht20
