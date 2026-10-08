#include "i2c_bus.hpp"
#include "bme280.hpp"
#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

int main() {
    std::cout << "=== Драйвер Bosch BME280 у режимі Forced Mode (RAII C++) ===" << std::endl;

    // Ініціалізація RAII-ресурсу шини I2C
    const std::string i2c_device = "/dev/i2c-1";
    I2CBus bus(i2c_device);

    if (!bus.is_open()) {
        std::cerr << "Помилка: Не вдалося відкрити шину " << i2c_device << std::endl;
        return 1;
    }
    std::cout << "[ОК] Шину I2C успішно відкрито (" << i2c_device << ")" << std::endl;

    // Створення екземпляра драйвера BME280
    BME280 sensor(bus, BME280::I2C_ADDR_PRIMARY);

    if (!sensor.init()) {
        std::cerr << "Помилка: Не вдалося ініціалізувати давач BME280" << std::endl;
        return 1;
    }
    std::cout << "[ОК] Давач BME280 ініціалізовано, Chip ID підтверджено (0x60)" << std::endl;

    std::cout << "\nЗапуск циклу вимірювання за запитом (Forced Mode)...\n" << std::endl;

    // Цикл періодичного опитування сенсора (5 ітерацій для демонстрації)
    for (int cycle = 1; cycle <= 5; ++cycle) {
        Bme280Data data;

        // Запуск одного циклу вимірювання з переплануванням oversampling (T: x2, P: x16, H: x1)
        bool success = sensor.perform_single_measurement(
            data,
            Oversampling::X2,  // Температура
            Oversampling::X16, // Тиск
            Oversampling::X1   // Вологість
        );

        if (success) {
            std::cout << "--- Замір #" << cycle << " ---" << std::endl;
            std::cout << std::fixed << std::setprecision(2);
            std::cout << " Температура : " << data.temperature_c << " °C" << std::endl;
            std::cout << " Тиск        : " << data.pressure_pa / 100.0 << " hPa ("
                      << data.pressure_pa << " Pa)" << std::endl;
            std::cout << " Вологість   : " << data.humidity_pct << " %" << std::endl;
        } else {
            std::cerr << "Помилка: Не вдалося зчитати дані на кроці #" << cycle << std::endl;
        }

        // Інтервал між вимірюваннями (у Forced Mode сенсор у проміжку перебуває у Sleep Mode)
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    std::cout << "\nДемонстрацію завершено. Ресурси шини I2C звільняються автоматично." << std::endl;
    return 0;
}
