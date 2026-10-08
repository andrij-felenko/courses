#include "qmc5883l.hpp"
#include "compass_calibrator.hpp"
#include "compass_renderer.hpp"

#include <iostream>
#include <vector>
#include <map>
#include <chrono>
#include <thread>
#include <iomanip>

// ============================================================================
// Програмна реалізація симулятора шини I2C для робочого прикладу без апаратного заліза
// ============================================================================

class MockI2CBus : public I2CBus {
public:
    MockI2CBus() {
        // За замовчуванням заповнюємо регістр стану (0x06) прапорцем DRDY (0x01)
        m_registers[QMC5883L::DEFAULT_I2C_ADDR][static_cast<std::uint8_t>(QMC5883L::Register::STATUS)] = 0x01;
    }

    bool writeRegister(std::uint8_t devAddr, std::uint8_t regAddr, std::uint8_t data) override {
        m_registers[devAddr][regAddr] = data;
        return true;
    }

    bool readRegister(std::uint8_t devAddr, std::uint8_t regAddr, std::uint8_t& data) override {
        data = m_registers[devAddr][regAddr];
        return true;
    }

    bool readBytes(std::uint8_t devAddr, std::uint8_t regAddr, std::uint8_t* buffer, std::size_t length) override {
        if (devAddr == QMC5883L::DEFAULT_I2C_ADDR && regAddr == static_cast<std::uint8_t>(QMC5883L::Register::OUT_X_L)) {
            // Симуляція обертання пристрою по колу для генерації векторів магнітного поля
            static float angleRad = 0.0f;
            angleRad += 0.05f; // Покроковий поворот

            // Сирі показники магнітометра з урахуванням зміщення жорсткого та м'якого заліза
            // Наприклад: зміщення X = +450 LSB, Y = -220 LSB
            float rawX = 1800.0f * std::cos(angleRad) + 450.0f;
            float rawY = 1600.0f * std::sin(angleRad) - 220.0f;
            float rawZ = 500.0f;

            std::int16_t ix = static_cast<std::int16_t>(rawX);
            std::int16_t iy = static_cast<std::int16_t>(rawY);
            std::int16_t iz = static_cast<std::int16_t>(rawZ);

            buffer[0] = static_cast<std::uint8_t>(ix & 0xFF);
            buffer[1] = static_cast<std::uint8_t>((ix >> 8) & 0xFF);
            buffer[2] = static_cast<std::uint8_t>(iy & 0xFF);
            buffer[3] = static_cast<std::uint8_t>((iy >> 8) & 0xFF);
            buffer[4] = static_cast<std::uint8_t>(iz & 0xFF);
            buffer[5] = static_cast<std::uint8_t>((iz >> 8) & 0xFF);

            return true;
        }

        for (std::size_t i = 0; i < length; ++i) {
            buffer[i] = m_registers[devAddr][regAddr + static_cast<std::uint8_t>(i)];
        }
        return true;
    }

private:
    std::map<std::uint8_t, std::map<std::uint8_t, std::uint8_t>> m_registers;
};

// ============================================================================
// Головна функція програми (main)
// ============================================================================

int main() {
    std::cout << "========================================================\n";
    std::cout << "   Цифровий компас на базі QMC5883L та OLED SSD1306    \n";
    std::cout << "========================================================\n\n";

    // 1. Створення об'єкта шини I2C
    MockI2CBus i2cBus;

    // 2. Ініціалізація низькорівневого драйвера магнітометра
    QMC5883L compass(i2cBus, QMC5883L::DEFAULT_I2C_ADDR);

    std::cout << "[I2C] Ініціалізація сенсора QMC5883L (ODR=200Hz, Range=8G, OSR=512)... ";
    if (!compass.begin(QMC5883L::Mode::Continuous,
                       QMC5883L::ODR::Hz200,
                       QMC5883L::Range::G8,
                       QMC5883L::OSR::OSR512)) {
        std::cerr << "ПОМИЛКА!\nПомилка зв'язку з пристроєм QMC5883L на шині I2C.\n";
        return 1;
    }
    std::cout << "УСПІШНО.\n";

    // 3. Ініціалізація дисплея SSD1306 та модулів обробки
    CompassRenderer renderer(i2cBus);
    if (!renderer.initDisplay()) {
        std::cout << "[OLED] Запуск дисплея (симуляція кадрового буфера).\n";
    }

    CompassCalibrator calibrator;
    // Встановлюємо географічне магнітне схилення для Києва (приблизно +6.5°)
    calibrator.setDeclinationDegrees(6.5f);

    // 4. Процедура автокалібрування сенсора
    std::cout << "\n[CALIBRATION] Початок процедури автокалібрування магнітометра.\n";
    std::cout << "[CALIBRATION] Обертайте сенсор на 360 градусів у горизонтальній площині...\n";
    calibrator.startCalibration();

    for (int sample = 0; sample < 100; ++sample) {
        Vector3D rawVec{};
        if (compass.readVector(rawVec)) {
            Vector3D correctedVec{};
            calibrator.process(rawVec, correctedVec);
            renderer.render(0.0f, true);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    calibrator.stopCalibration();
    std::cout << "[CALIBRATION] Автокалібрування завершено успішно!\n";

    // 5. Основний цикл обробки даних реального часу
    std::cout << "\n[RUN] Запуск основного циклу вимірювання та рендерингу компаса:\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "  N  | Raw Vector (G)       | Corr Vector (G)      | Azimuth  \n";
    std::cout << "--------------------------------------------------------\n";

    for (int iteration = 1; iteration <= 20; ++iteration) {
        if (compass.isDataReady()) {
            Vector3D rawVec{};
            if (compass.readVector(rawVec)) {
                Vector3D correctedVec{};
                float azimuth = calibrator.process(rawVec, correctedVec);

                // Оновлення зображення на OLED-дисплеї
                renderer.render(azimuth, false);
                renderer.updateDisplay();

                // Виведення текстового моніторингу у консоль
                std::cout << std::setw(4) << iteration << " | "
                          << std::fixed << std::setprecision(2)
                          << "X:" << std::setw(5) << rawVec.x
                          << " Y:" << std::setw(5) << rawVec.y << " | "
                          << "X:" << std::setw(5) << correctedVec.x
                          << " Y:" << std::setw(5) << correctedVec.y << " | "
                          << std::setw(6) << std::setprecision(1) << azimuth << "°\n";
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    std::cout << "--------------------------------------------------------\n";
    std::cout << "Робота моніторингу цифрового компаса завершена успішно.\n";

    return 0;
}
