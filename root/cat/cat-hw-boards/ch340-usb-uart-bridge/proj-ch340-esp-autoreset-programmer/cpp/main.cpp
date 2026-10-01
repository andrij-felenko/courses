#include "esp32_autoreset.hpp"
#include <iostream>
#include <exception>

int main(int argc, char* argv[]) {
    std::string_view port_name = "/dev/ttyUSB0";
    if (argc > 1) {
        port_name = argv[1];
    }

    try {
        std::cout << "Ініціалізація керування CH340 на порту: " << port_name << "\n";
        
        /* Створення об'єкта класу з відкриттям порту через RAII */
        Esp32AutoReset reset_controller(port_name);

        /* Переведення ESP32 у режим завантаження для прошивки */
        reset_controller.enter_bootloader(std::chrono::milliseconds(100));

        /* Симуляція паузи передачі бінарного образу */
        std::cout << "Симуляція запису прошивки...\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));

        /* Виконання підсумкового перезапуску для старту нової прошивки */
        reset_controller.hard_reset(std::chrono::milliseconds(50));

        std::cout << "Операція успішно завершена.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
