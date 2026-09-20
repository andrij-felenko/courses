#include "CC1101.hpp"
#include <iostream>

// Заглушка апаратного рівня (HAL) для демонстрації
class DummySpi : public SpiHal {
public:
    void init() override {}
    uint8_t transfer(uint8_t data) override { return 0; }
    void cs_low() override {}
    void cs_high() override {}
    bool is_miso_low() override { return true; }
    bool get_gdo0() override { return false; }
};

int main() {
    DummySpi spi;
    CC1101 radio(spi);
    
    // Ініціалізація модуля
    radio.init();
    
    // Відправка тестового пакета
    std::vector<uint8_t> packet = {0xDE, 0xAD, 0xBE, 0xEF};
    if (radio.send(packet)) {
        std::cout << "Packet queued for transmission.\n";
    }
    
    // Неблокуючий суперцикл
    while (true) {
        // Оновлюємо стан трансивера
        radio.update();
        
        // Перевіряємо наявність отриманих даних
        std::vector<uint8_t> rx_data;
        if (radio.receive(rx_data)) {
            std::cout << "Received " << rx_data.size() << " bytes.\n";
        }
        
        // Інші завдання виконуються без затримок
        break; // У прикладі виходимо з циклу відразу
    }
    
    return 0;
}
