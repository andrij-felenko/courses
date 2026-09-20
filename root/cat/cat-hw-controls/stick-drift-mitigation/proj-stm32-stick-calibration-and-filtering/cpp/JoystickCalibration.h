#ifndef JOYSTICK_CALIBRATION_H
#define JOYSTICK_CALIBRATION_H

#include <cstdint>
#include <cstddef>

// Коди помилок роботи модуля калібрування
enum class JoystickError : uint8_t {
    OK = 0,               // Помилок немає
    INVALID_RANGE = 1,    // Некоректні межі діапазону АЦП (min >= max)
    CRC_MISMATCH = 2,     // Незбіг контрольної суми конфігурації NVM
    NOT_CALIBRATED = 3    // Центр або межі не відкалібровані
};

// Типи алгоритмів фільтрації мертвих зон
enum class DeadzoneType : uint8_t {
    ScaledRadial = 0,     // Масштабована радіальна мертва зона (Scaled Radial Deadzone)
    Axial = 1             // Незалежна осьова мертва зона (Axial Deadzone)
};

// Точка у сирих відліках АЦП
struct RawPoint {
    int16_t x{0};
    int16_t y{0};
};

// Точка у нормованих координатах [-1.0 .. +1.0]
struct NormalizedPoint {
    float x{0.0f};
    float y{0.0f};
};

// Структура конфігураційного профілю для збереження у NVM (EEPROM/Flash)
#pragma pack(push, 1)
struct JoystickConfig {
    int16_t center_x{2048};       // Сирий центр осі X
    int16_t center_y{2048};       // Сирий центр осі Y
    int16_t min_x{0};             // Мінімальний відлік АЦП по осі X
    int16_t max_x{4095};          // Максимальний відлік АЦП по осі X
    int16_t min_y{0};             // Мінімальний відлік АЦП по осі Y
    int16_t max_y{4095};          // Максимальний відлік АЦП по осі Y
    float deadzone_radial{0.08f}; // Радіусна мертва зона (0.08 = 8%)
    float deadzone_axial{0.05f};  // Осьова мертва зона (0.05 = 5%)
    uint8_t deadzone_type{0};     // 0 = ScaledRadial, 1 = Axial
    uint16_t crc16{0};            // Контрольна сума CRC16 профілю
};
#pragma pack(pop)

// Клас обробки та калібрування аналогового джойстика
class JoystickCalibration {
public:
    JoystickCalibration();

    // Ініціалізація та застосування конфігураційного профілю
    JoystickError begin(const JoystickConfig& config);

    // Зчитування та нормалізація сирих відліків АЦП
    NormalizedPoint process(int16_t raw_x, int16_t raw_y);

    // Налаштування мертвих зон
    void setDeadzoneRadial(float ratio);
    void setDeadzoneAxial(float ratio);
    void setDeadzoneType(DeadzoneType type);

    // Неблокуюче автокалібрування центральної нейтралі
    void startNeutralCalibration();
    void updateNeutralCalibration(int16_t raw_x, int16_t raw_y);
    void finishNeutralCalibration();

    // Неблокуюче калібрування крайніх меж відхилення
    void startRangeCalibration();
    void updateRangeCalibration(int16_t raw_x, int16_t raw_y);
    void finishRangeCalibration();

    // Статус процесу калібрування
    bool isCalibrating() const { return calibrating_neutral_ || calibrating_range_; }

    // Розрахунок та перевірка CRC16 для NVM
    static uint16_t calculateCRC16(const uint8_t* data, size_t length);
    bool validateConfig(const JoystickConfig& cfg) const;
    void updateConfigCRC(JoystickConfig& cfg);

    // Отримання поточної конфігурації
    const JoystickConfig& getConfig() const { return config_; }

private:
    JoystickConfig config_;

    // Прапорці та накопичувачі для неблокуючого автокалібрування
    bool calibrating_neutral_{false};
    bool calibrating_range_{false};

    int32_t sum_x_{0};
    int32_t sum_y_{0};
    uint32_t sample_count_{0};

    int16_t calib_min_x_{32767};
    int16_t calib_max_x_{-32768};
    int16_t calib_min_y_{32767};
    int16_t calib_max_y_{-32768};

    // Приватні математичні функції нормалізації та фільтрації
    float normalizeAxis(int16_t raw_val, int16_t center, int16_t min_val, int16_t max_val) const;
    void applyScaledRadialDeadzone(float in_x, float in_y, float deadzone, float& out_x, float& out_y) const;
    void applyAxialDeadzone(float in_x, float in_y, float deadzone, float& out_x, float& out_y) const;
};

#endif // JOYSTICK_CALIBRATION_H
