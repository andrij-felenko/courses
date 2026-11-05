#include "HatMonitor.hpp"
#include <iostream>
#include <exception>

int main() {
    std::cout << "=== Система діагностики міжплатного стека HAT (М2.5 Fastener Kit) ===\n";

    try {
        // У реальному середовищіLinux шина зазвичай "/dev/i2c-1", а адреса шилда 0x48 або 0x50.
        // Для демонстрації та захисту від відсутності обладнання обгортаємо в try-catch.
        std::string_view i2c_device = "/dev/i2c-1";
        uint8_t hat_address = 0x48; // Стандартна адреса сенсора на HAT

        std::cout << "Ініціалізація HatMonitor на шині " << i2c_device 
                  << " з адресою 0x" << std::hex << static_cast<int>(hat_address) << std::dec << "...\n";

        HatMonitor monitor(i2c_device, hat_address);

        // Запуск діагностичного стрес-тесту для перевірки надійності механічного контакту
        monitor.runStressTest(50);

        // Формування та виведення звіту про якість монтажу
        monitor.printReport();

    } catch (const std::exception& e) {
        std::cerr << "[Помилка ініціалізації/виконання]: " << e.what() << "\n";
        std::cerr << "Порада: переконайтеся, що ви запускаєте програму на Linux-системі з підтримкою I2C "
                  << "та наявністю прав доступу до /dev/i2c-X (або запустіть у режимі симуляції).\n";
        return 1;
    }

    return 0;
}
