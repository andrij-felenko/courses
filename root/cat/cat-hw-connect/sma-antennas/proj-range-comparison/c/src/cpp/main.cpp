#include <iostream>
#include <thread>
#include <chrono>
#include <vector>
#include <memory>
#include "RadioRssi.hpp"

int main() {
    std::cout << "Ініціалізація радіомодулів...\n";
    
    std::vector<std::unique_ptr<RadioRssi>> radios;
    
    try {
        radios.push_back(std::make_unique<RadioRssi>(RadioFrequency::Freq433MHz, 1));
        radios.push_back(std::make_unique<RadioRssi>(RadioFrequency::Freq2400MHz, 2));
    } catch (const std::exception& e) {
        std::cerr << "Помилка при ініціалізації: " << e.what() << '\n';
        return 1;
    }
    
    std::cout << "Початок зчитування показників антен SMA...\n";
    std::cout << "Натисніть Ctrl+C для виходу.\n\n";
    
    for (int i = 0; i < 10; ++i) {
        for (const auto& radio : radios) {
            try {
                int8_t rssi = radio->readRssi();
                
                std::string freqName = (radio->getFrequency() == RadioFrequency::Freq433MHz) 
                                       ? "433 MHz" : "2.4 GHz";
                                       
                std::cout << "[" << freqName << "] RSSI: " << static_cast<int>(rssi) << " dBm";
                
                if (rssi > -65) std::cout << " (Відмінний сигнал)";
                else if (rssi > -85) std::cout << " (Хороший сигнал)";
                else std::cout << " (Слабкий сигнал)";
                
                std::cout << '\n';
            } catch (const std::exception& e) {
                std::cerr << "Помилка зчитування: " << e.what() << '\n';
            }
        }
        std::cout << "---\n";
        
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    // Ресурси звільняються автоматично завдяки std::unique_ptr та RAII
    return 0;
}
