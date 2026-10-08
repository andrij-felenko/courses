#include "aht20_driver.hpp"
#include "aht20_crc.hpp"

#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

/**
 * @brief Допоміжна функція для перетворення статусу помилки в текстовий опис.
 */
const char* status_to_string(aht20::Aht20Status status) {
    switch (status) {
        case aht20::Aht20Status::Success:          return "Успішно (Success)";
        case aht20::Aht20Status::ErrI2cTransfer:   return "Помилка передачі I2C (I2C Transfer Error)";
        case aht20::Aht20Status::ErrNotCalibrated: return "Давач не відкалібрований (Not Calibrated)";
        case aht20::Aht20Status::ErrTimeout:       return "Таймаут очікування даних (Timeout)";
        case aht20::Aht20Status::ErrCrcMismatch:   return "Невідповідність контрольної суми CRC8";
        case aht20::Aht20Status::ErrDeviceBusy:    return "Пристрій зайнятий (Device Busy)";
        default:                                   return "Невідома помилка";
    }
}

int main() {
    std::cout << "========================================================\n";
    std::cout << " Драйвер AHT20: RAII-ініціалізація та контроль CRC8     \n";
    std::cout << "========================================================\n\n";

    // Створення об'єкта драйвера з RAII-ініціалізацією та автоматичним контролем калібрування.
    // За замовчуванням увімкнено mock_mode = true для гарантованого виконання без підключеного заліза.
    aht20::Aht20Driver driver("/dev/i2c-1", aht20::DEFAULT_I2C_ADDR, true);

    std::cout << "[Інфо] Перевірка статусу після ініціалізації..." << std::endl;
    uint8_t status_byte = 0;
    aht20::Aht20Status status = driver.read_status_byte(status_byte);

    if (status == aht20::Aht20Status::Success) {
        std::cout << "[ОК] Статус байт: 0x" << std::hex << std::uppercase
                  << static_cast<int>(status_byte) << std::dec << std::endl;
        std::cout << "     Прапорець калібрування (Bit 3): "
                  << ((status_byte & aht20::Aht20Driver::STATUS_CALIBRATED_MASK) ? "Встановлено" : "ВІДСУТНІЙ")
                  << std::endl;
    } else {
        std::cerr << "[Помилка] Не вдалося зчитати статус: " << status_to_string(status) << std::endl;
        return 1;
    }

    std::cout << "\n--- Запуск періодичного опитування давача AHT20 ---\n";

    constexpr int MEASUREMENT_COUNT = 5;
    for (int i = 1; i <= MEASUREMENT_COUNT; ++i) {
        std::cout << "\nВимірювання #" << i << ":" << std::endl;

        aht20::Aht20Data data;
        aht20::Aht20Status result = driver.read_sample(data);

        if (result == aht20::Aht20Status::Success && data.valid) {
            std::cout << std::fixed << std::setprecision(2);
            std::cout << "  Температура : " << data.temperature_c << " °C" << std::endl;
            std::cout << "  Вологість   : " << data.humidity_rh << " %RH" << std::endl;
            std::cout << "  Контроль CRC: [ОК] Верифікацію CRC8 пройдено успішно." << std::endl;
        } else {
            std::cerr << "  [Помилка зчитування]: " << status_to_string(result) << std::endl;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    std::cout << "\n--- Демонстрація процедури програмного скидання (Soft Reset) ---\n";
    aht20::Aht20Status reset_res = driver.soft_reset();
    if (reset_res == aht20::Aht20Status::Success) {
        std::cout << "[ОК] М'яке скидання AHT20 виконано успішно." << std::endl;
    } else {
        std::cerr << "[Помилка] Спроба Soft Reset завершилася невдало: " << status_to_string(reset_res) << std::endl;
    }

    std::cout << "\nРоботу завершено коректно. RAII-об'єкти автоматично звільняють ресурси." << std::endl;
    return 0;
}
