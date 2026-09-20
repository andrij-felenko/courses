#ifndef JOYSTICK_CALIBRATOR_HPP
#define JOYSTICK_CALIBRATOR_HPP

#include <cstdint>
#include <cstddef>
#include <vector>

// Упакована структура даних профілю калібрування джойстика.
// Збереження мінімуму, максимуму, центру по двох осях, радіуса мертвої зони та CRC16.
#pragma pack(push, 1)
struct CalibrationProfile {
    int16_t minX{0};             // Мінімальне виміряне значення АЦП по осі X
    int16_t maxX{4095};          // Максимальне виміряне значення АЦП по осі X
    int16_t centerX{2048};       // Розрахований центр (нейтраль) осі X
    int16_t minY{0};             // Мінімальне виміряне значення АЦП по осі Y
    int16_t maxY{4095};          // Максимальне виміряне значення АЦП по осі Y
    int16_t centerY{2048};       // Розрахований центр (нейтраль) осі Y
    float deadbandRadius{0.08f}; // Радіус мертвої зони у відносних одиницях (0.0..1.0)
    uint16_t crc{0xFFFF};        // Контрольна сума CRC16-CCITT для валідації цілісності
};
#pragma pack(pop)

// Вихідні нормалізовані координати джойстика у симетричному діапазоні [-1.0, 1.0]
struct NormalizedOutput {
    float x{0.0f};
    float y{0.0f};
};

// Клас для автоматичного калібрування, фільтрації дрейфу нуля та масштабування осей джойстика
class JoystickCalibrator {
public:
    // Конструктор за замовчуванням або із передачею збереженого профілю
    explicit JoystickCalibrator(const CalibrationProfile& profile = createDefaultProfile());

    // Обчислення контрольної суми CRC16-CCITT для довільного блоку пам'яті
    static uint16_t calculateCRC16(const uint8_t* data, size_t length);

    // Розрахунок контрольної суми CRC16 для структури профілю (без врахування самого поля crc)
    static uint16_t calculateProfileCRC(const CalibrationProfile& profile);

    // Перевірка цілісності профілю через порівняння розрахованої та збереженої CRC16
    static bool validateProfile(const CalibrationProfile& profile);

    // Створення стандартного безпечного профілю за замовчуванням
    static CalibrationProfile createDefaultProfile();

    // Автоматичне визначення нейтрального положення (усереднення вибірок у стані спокою)
    void autoCalibrateNeutral(const std::vector<int16_t>& rawSamplesX,
                              const std::vector<int16_t>& rawSamplesY);

    // Оновлення крайніх меж відхилення важеля під час калібрувального руху
    void updateLimits(int16_t rawX, int16_t rawY);

    // Обробка сирих значень АЦП: компенсація дрейфу, нормалізація до [-1.0, 1.0] та радіальна мертва зона
    NormalizedOutput processRawInput(int16_t rawX, int16_t rawY) const;

    // Геттер поточного конфігураційного профілю
    const CalibrationProfile& getProfile() const { return profile_; }

    // Встановлення нового профілю з оновленням контрольної суми
    void setProfile(const CalibrationProfile& profile);

    // Оновлення поля CRC16 у поточному профілі
    void updateCRC();

private:
    CalibrationProfile profile_;
};

#endif // JOYSTICK_CALIBRATOR_HPP
