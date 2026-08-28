#include <iostream>

/* Еквівалентний C++ синтаксис атрибутів GNU */
extern "C" {
    [[gnu::constructor(150)]] void init_hardware_bus_cpp() {
        std::cout << "[C++ HW] Активація системної шини периферії\n";
    }

    [[gnu::destructor(150)]] void shutdown_hardware_bus_cpp() {
        std::cout << "[C++ HW] Вимкнення системної шини периферії\n";
    }
}
