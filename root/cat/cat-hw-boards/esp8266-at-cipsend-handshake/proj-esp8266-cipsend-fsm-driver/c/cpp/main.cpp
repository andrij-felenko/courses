#include "EspCipsend.hpp"
#include <iostream>
#include <cstring>
#include <span>

// Приклад реалізації апаратної платформи
class PlatformUart : public IUart {
public:
    void write(const uint8_t* data, uint16_t len) override {
        // Запис у регістри UART (заглушка)
    }

    bool readChar(uint8_t& c) override {
        // Читання з UART (заглушка)
        return false;
    }

    uint32_t getTickMs() const override {
        // Отримання системного часу (заглушка)
        static uint32_t ms = 0;
        return ms++;
    }
};

int main() {
    PlatformUart myUart;
    EspCipsend cipsend(myUart);

    const char* text = "Hello from C++ FSM!";
    auto payload = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(text), std::strlen(text));

    bool isSending = false;

    // Головний неблокуючий цикл
    while (true) {
        if (!isSending) {
            if (cipsend.start(payload, 5000)) {
                std::cout << "Starting C++ FSM transfer..." << std::endl;
                isSending = true;
            }
        }

        // Обслуговування автомата
        cipsend.tick();

        // Моніторинг стану
        if (isSending) {
            auto state = cipsend.getState();
            if (state == EspCipsend::State::Idle) {
                std::cout << "Transfer OK!" << std::endl;
                isSending = false;
                break;
            } else if (state == EspCipsend::State::Error) {
                std::cout << "Transfer Error!" << std::endl;
                isSending = false;
                break;
            }
        }
    }

    return 0;
}
