#include <mutex>
#include <iostream>

static std::once_flag init_flag;

void init_hardware_driver() {
    std::cout << "Ініціалізація апаратного драйвера (C++11)...\n";
}

void process_request() {
    std::call_once(init_flag, init_hardware_driver);
    // Безпечна робота з ініціалізованим обладнанням
}
