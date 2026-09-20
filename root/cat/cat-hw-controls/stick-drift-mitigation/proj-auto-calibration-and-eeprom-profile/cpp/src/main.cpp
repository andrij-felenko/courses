#include "joystick_calibrator.hpp"
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>

// Модель для симуляції читання та запису даних в енергонезалежну пам'ять (EEPROM/Flash)
struct SimulatedEEPROM {
    CalibrationProfile storedProfile;
    bool isWritten{false};

    bool readProfile(CalibrationProfile& outProfile) const {
        if (!isWritten) return false;
        outProfile = storedProfile;
        return true;
    }

    void writeProfile(const CalibrationProfile& profile) {
        storedProfile = profile;
        isWritten = true;
    }
};

int main() {
    std::cout << "=== Система калібрування джойстика та нейтралізації дрейфу нуля ===\n\n";

    SimulatedEEPROM eeprom;
    CalibrationProfile profileFromEEPROM;
    JoystickCalibrator calibrator;

    // 1. Спроба завантаження профілю з EEPROM та перевірка цілісності CRC16
    std::cout << "[1] Завантаження конфігураційного профілю з EEPROM...\n";
    if (eeprom.readProfile(profileFromEEPROM) && JoystickCalibrator::validateProfile(profileFromEEPROM)) {
        std::cout << "Профіль успішно завантажено та підтверджено через CRC16.\n";
        calibrator.setProfile(profileFromEEPROM);
    } else {
        std::cout << "ПОПЕРЕДЖЕННЯ: Профіль відсутній або пошкоджений (контрольна сума CRC16 не збігається)!\n";
        std::cout << "Автоматичне застосування безпечного дефолтного профілю (фолбек).\n";
        calibrator = JoystickCalibrator(JoystickCalibrator::createDefaultProfile());
    }

    // 2. Автоматичне вимірювання нейтралі при старті системи
    std::cout << "\n[2] Запуск автоматичного калібрування нейтрального положення...\n";
    // Замір 10 відліків АЦП у стані спокою з дрейфом (центр X ~ 2120, center Y ~ 1980)
    std::vector<int16_t> idleSamplesX = {2118, 2122, 2115, 2125, 2120, 2119, 2121, 2117, 2123, 2120};
    std::vector<int16_t> idleSamplesY = {1978, 1982, 1985, 1979, 1980, 1981, 1977, 1983, 1980, 1979};

    calibrator.autoCalibrateNeutral(idleSamplesX, idleSamplesY);
    const CalibrationProfile& currentProfile = calibrator.getProfile();

    std::cout << "Новий обчислений центр осі X: " << currentProfile.centerX << " (базовий: 2048)\n";
    std::cout << "Новий обчислений центр осі Y: " << currentProfile.centerY << " (базовий: 2048)\n";

    // 3. Запис оновленого профілю в EEPROM із новою CRC16
    std::cout << "\n[3] Збереження профілю в EEPROM з розрахунком CRC16...\n";
    eeprom.writeProfile(calibrator.getProfile());
    std::cout << "Збережена контрольна сума CRC16: 0x" << std::hex << std::uppercase << calibrator.getProfile().crc << std::dec << "\n";

    // 4. Демонстрація відхилення пошкоджених даних під час перевірки CRC16
    std::cout << "\n[4] Тест захисту від пошкодження пам'яті:\n";
    CalibrationProfile corruptedProfile = eeprom.storedProfile;
    corruptedProfile.centerX = 9999; // Пошкодження поля без оновлення CRC
    if (!JoystickCalibrator::validateProfile(corruptedProfile)) {
        std::cout << "УСПІХ: Виявлено пошкодження профілю (CRC16 не збігається), профіль відхилено.\n";
    }

    // 5. Симуляція роботи: обробка різних положень важеля джойстика
    std::cout << "\n[5] Виконання обробки сигналів АЦП (з урахуванням дрейфу та мертвої зони):\n";
    std::cout << std::fixed << std::setprecision(3);

    struct TestCase {
        std::string description;
        int16_t rawX;
        int16_t rawY;
    };

    std::vector<TestCase> testCases = {
        {"Нейтраль із дрейфом (всередині мертвої зони)", 2122, 1981},
        {"Мале відхилення (на межі мертвої зони)", 2250, 1980},
        {"Повне відхилення вправо по X", 4095, 1980},
        {"Повне відхилення вліво по X", 0, 1980},
        {"Діагональне відхилення вгору-вправо", 3800, 3800},
        {"Повне відхилення вниз по Y", 2120, 0}
    };

    for (const auto& test : testCases) {
        NormalizedOutput out = calibrator.processRawInput(test.rawX, test.rawY);
        std::cout << " - " << std::left << std::setw(48) << test.description
                  << " Raw(" << std::setw(4) << test.rawX << ", " << std::setw(4) << test.rawY << ")"
                  << " -> Norm X: " << std::setw(6) << out.x
                  << " | Norm Y: " << std::setw(6) << out.y << "\n";
    }

    std::cout << "\nОбробку виконано успішно.\n";
    return 0;
}
