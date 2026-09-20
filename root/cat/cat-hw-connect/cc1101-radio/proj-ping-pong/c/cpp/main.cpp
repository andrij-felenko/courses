#include "cc1101.hpp"
#include <string_view>
#include <atomic>

// Фіктивна реалізація шини SPI для платформи
class HwSpi : public CC1101::ISpiBus {
public:
    void select() override { /* Наприклад: GPIO_ResetBits() */ }
    void deselect() override { /* Наприклад: GPIO_SetBits() */ }
    
    uint8_t transfer(uint8_t data) override {
        // Фіктивно. Реальне надсилання байта через SPI та повернення отриманого.
        return 0; 
    }
    
    void delayMs(uint32_t ms) override {
        // Затримка мікроконтролера, наприклад HAL_Delay(ms)
    }
};

enum class NodeRole { Ping, Pong };

// Атомарний прапорець переривання
std::atomic<bool> g_packetEvent{false};

// Обробник зовнішнього переривання GDO0
extern "C" void EXTI_IRQHandler() {
    g_packetEvent = true;
}

int main() {
    HwSpi spiBus;
    CC1101::Transceiver radio(spiBus);
    
    radio.init();
    
    NodeRole role = NodeRole::Ping;
    
    if (role == NodeRole::Pong) {
        radio.setRx();
    }
    
    while (true) {
        if (role == NodeRole::Ping) {
            std::string_view msg = "PING";
            std::span<const uint8_t> payload(
                reinterpret_cast<const uint8_t*>(msg.data()), msg.size()
            );
            
            radio.sendPacket(payload);
            spiBus.delayMs(10); // Затримка завершення передачі
            
            radio.setRx();
            g_packetEvent = false;
            
            // Очікування на відповідь
            while (!g_packetEvent) {
                // Зниження енергоспоживання / idle sleep
            }
            
            CC1101::Packet pkt;
            if (radio.receivePacket(pkt)) {
                // Обробка отриманого пакету
            }
            
            spiBus.delayMs(1000); // Чекаємо до наступного пінг-циклу
            
        } else if (role == NodeRole::Pong) {
            if (g_packetEvent) {
                g_packetEvent = false;
                
                CC1101::Packet pkt;
                if (radio.receivePacket(pkt)) {
                    std::string_view rxStr(
                        reinterpret_cast<const char*>(pkt.data.data()),
                        pkt.data.size()
                    );
                    
                    if (rxStr == "PING") {
                        std::string_view msg = "PONG";
                        std::span<const uint8_t> payload(
                            reinterpret_cast<const uint8_t*>(msg.data()), msg.size()
                        );
                        
                        spiBus.delayMs(5); // Затримка на підготовку
                        radio.sendPacket(payload);
                        spiBus.delayMs(10); // Очікування передавання
                        
                        radio.setRx(); // Назад у приймання
                    }
                }
            }
        }
    }
    
    return 0;
}
