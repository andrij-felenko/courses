#include "AHT20.hpp"
#include <iostream>

// Симуляція реалізації шини I2C для демонстрації роботи драйвера
class MockI2CBus : public I2CBus {
public:
    bool write(uint8_t address, const uint8_t* data, std::size_t length) override {
        if (address != AHT20::DEFAULT_ADDRESS || data == nullptr || length == 0) {
            return false;
        }

        // Перевірка команди запуску вимірювання (0xAC 0x33 0x00)
        if (length == 3 && data[0] == 0xAC && data[1] == 0x33 && data[2] == 0x00) {
            isMeasuring_ = true;
            return true;
        }

        // Перевірка команди ініціалізації (0xBE 0x08 0x00)
        if (length == 3 && data[0] == 0xBE) {
            isCalibrated_ = true;
            return true;
        }

        return true;
    }

    bool read(uint8_t address, uint8_t* data, std::size_t length) override {
        if (address != AHT20::DEFAULT_ADDRESS || data == nullptr || length == 0) {
            return false;
        }

        // Читання 1 байта стану
        if (length == 1) {
            data[0] = 0x08; // Біт 3 встановлено (відкалібровано)
            return true;
        }

        // Читання 7 байтів вимірювання
        if (length == 7) {
            // Бай 0: статус (не зайнятий, відкалібрований)
            data[0] = 0x08;

            // Еталонні значення для тестування:
            // Вологість ~ 55% -> raw = 576716 (0x8CD0C)
            // Температура ~ 23.5 C -> raw = 385351 (0x5E147)
            data[1] = 0x8C;
            data[2] = 0xD0;
            data[3] = 0xC5; // Старша нібла вологості 0xC, молодша нібла температури 0x5
            data[4] = 0xE1;
            data[5] = 0x47;

            // Обчислення коректного CRC-8 для 6 байтів даних
            data[6] = AHT20::calculateCRC8(data, 6);
            isMeasuring_ = false;
            return true;
        }

        return false;
    }

private:
    bool isCalibrated_{true};
    bool isMeasuring_{false};
};

int main() {
    MockI2CBus i2cBus;
    AHT20 sensor(i2cBus);

    std::cout << "--- Запуск драйвера AHT20 ---" << std::endl;

    // Ініціалізація давача
    if (!sensor.reset()) {
        std::cout << "Помилка ініціалізації давача AHT20!" << std::endl;
        return 1;
    }
    std::cout << "Давач успішно ініціалізовано та відкалібровано." << std::endl;

    uint32_t systemTimeMs = 1000; // Умовний системний час

    // Запуск першого вимірювання
    if (sensor.startMeasurement(systemTimeMs)) {
        std::cout << "Запущено вимірювання о " << systemTimeMs << " мс." << std::endl;
    }

    // Симуляція неблокуючого циклу обробки (Event Loop)
    while (sensor.getState() == DriverState::Measuring) {
        systemTimeMs += 20; // Крок таймера 20 мс

        if (sensor.update(systemTimeMs)) {
            std::cout << "Вимірювання завершено о " << systemTimeMs << " мс." << std::endl;

            Measurement result = sensor.getMeasurement();
            if (result.isValid) {
                std::cout << "Температура: " << result.temperature << " C" << std::endl;
                std::cout << "Вологість: " << result.humidity << " %" << std::endl;
            } else {
                std::cout << "Отримано некоректні дані вимірювання!" << std::endl;
            }
        } else {
            std::cout << "Очікування завершення вимірювання... Час: " << systemTimeMs << " мс" << std::endl;
        }
    }

    return 0;
}
