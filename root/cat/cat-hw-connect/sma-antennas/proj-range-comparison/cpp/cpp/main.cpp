#include "Radio.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    try {
        Radio radio("/dev/spidev0.0");
        std::cout << "Радіомодуль ініціалізовано. Початок зчитування RSSI..." << std::endl;
        
        for (int i = 0; i < 5; ++i) {
            int8_t rssi = radio.getRssi();
            std::cout << "Якість зв'язку (RSSI): " << static_cast<int>(rssi) << " дБм" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
