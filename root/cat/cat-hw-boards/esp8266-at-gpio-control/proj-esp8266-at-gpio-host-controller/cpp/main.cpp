#include "esp8266_at_gpio.hpp"
#include <iostream>
#include <chrono>
#include <thread>

// Емуляція відправки даних у фізичний послідовний порт UART
void uartTransmit(std::string_view data) {
    std::cout << "[UART TX] -> " << data;
}

// Проста симуляція системного таймера в мілісекундах
uint32_t getMillis() {
    using namespace std::chrono;
    return static_cast<uint32_t>(duration_cast<milliseconds>(
        steady_clock::now().time_since_epoch()).count());
}

int main() {
    std::cout << "Запуск системи неблокуючого C++ драйвера GPIO ESP8266...\n";

    // Створення екземпляра драйвера
    Esp8266GpioDriver driver(uartTransmit);

    // Налаштування обробника асинхронних сповіщень URC (+GPIOINDB)
    driver.setOnPinChanged([](int pin, GpioLevel level) {
        std::cout << "[URC EVENT] Зміна стану виводу GPIO" << pin
                  << ": новий рівень = " << (level == GpioLevel::High ? "HIGH" : "LOW") << "\n";
    });

    // 1. Початок конфігурації GPIO2 як виходу
    std::cout << "\n1. Запит налаштування GPIO2 як виходу...\n";
    driver.setPinDirection(2, GpioMode::Output);

    // Симуляція неблокуючого виконання в суперциклі
    for (int i = 0; i < 5; ++i) {
        uint32_t now = getMillis();
        driver.tick(now);

        // Симуляція надходження відповіді OK від ESP8266 через UART
        if (i == 2) {
            driver.feedRx("OK\r\n");
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // 2. Початок запису HIGH на GPIO2
    std::cout << "\n2. Запит встановлення HIGH на GPIO2...\n";
    driver.writePin(2, GpioLevel::High);

    for (int i = 0; i < 5; ++i) {
        uint32_t now = getMillis();
        driver.tick(now);

        if (i == 2) {
            driver.feedRx("OK\r\n");
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // 3. Симуляція надходження асинхронної події URC (+GPIOINDB:4,1)
    std::cout << "\n3. Симуляція вхідного асинхронного URC-повідомлення...\n";
    driver.feedRx("+GPIOINDB:4,1\r\n");

    std::cout << "\nДемонстрацію неблокуючого керування завершено успішно.\n";
    return 0;
}
