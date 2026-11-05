#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include "EspCipsendFsm.hpp"

// Заглушка для апаратного UART мікроконтролера (для демонстрації)
class HardwareUart {
public:
    void write(const uint8_t* data, size_t len) {
        std::cout << "[UART TX]: ";
        for (size_t i = 0; i < len; ++i) {
            std::cout << static_cast<char>(data[i]);
        }
        std::cout << std::endl;
        
        // Імітація відповідей від модему ESP8266
        std::string txStr(reinterpret_cast<const char*>(data), len);
        if (txStr.find("AT+CIPSEND") != std::string::npos) {
            rxQueue_.push_back('\r');
            rxQueue_.push_back('\n');
            rxQueue_.push_back('>');
            rxQueue_.push_back(' ');
        } else if (txStr.find("Hello") != std::string::npos) {
            rxQueue_.push_back('\r');
            rxQueue_.push_back('\n');
            std::string ok = "SEND OK\r\n";
            rxQueue_.insert(rxQueue_.end(), ok.begin(), ok.end());
        }
    }
    
    bool available() const {
        return !rxQueue_.empty();
    }
    
    char read() {
        if (rxQueue_.empty()) return 0;
        char c = rxQueue_.front();
        rxQueue_.erase(rxQueue_.begin());
        return c;
    }
    
private:
    std::vector<char> rxQueue_;
};

HardwareUart uart;

// Функція для отримання поточного часу в мілісекундах (адаптується під платформу)
uint32_t getSystemMillis() {
    auto now = std::chrono::steady_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch());
    return static_cast<uint32_t>(ms.count());
}

int main() {
    std::cout << "Starting ESP8266 CIPSEND FSM Demo..." << std::endl;

    // Створюємо скінченний автомат
    EspCipsendFsm fsm(
        [](const uint8_t* data, size_t len) { uart.write(data, len); }, // Функція відправки 
        getSystemMillis,                                                // Функція отримання часу
        3000                                                            // Тайм-аут 3000 мс
    );

    // Налаштовуємо зворотні виклики (callbacks)
    fsm.setOnSuccess([]() {
        std::cout << "[APP]: Data sent successfully! State is now IDLE." << std::endl;
    });

    fsm.setOnError([](EspCipsendFsm::Error err) {
        std::cout << "[APP]: Error occurred during transmission. Code: " << static_cast<int>(err) << std::endl;
    });

    // Підготовка даних для відправки
    std::string payload = "Hello, ESP8266!";
    int linkId = 0; // Для режиму multiple connections (AT+CIPMUX=1)

    // Ініціюємо відправку
    if (fsm.startSend(linkId, reinterpret_cast<const uint8_t*>(payload.data()), payload.length())) {
        std::cout << "[APP]: Transmission initiated." << std::endl;
    } else {
        std::cout << "[APP]: FSM is busy or invalid parameters." << std::endl;
    }

    // Головний неблокуючий цикл (імітація роботи мікроконтролера)
    while (fsm.getState() != EspCipsendFsm::State::Idle) {
        // 1. Оновлюємо стан автомата (відстеження тайм-аутів)
        fsm.tick();

        // 2. Читаємо вхідні дані з UART
        while (uart.available()) {
            char c = uart.read();
            fsm.processRxByte(c);
        }

        // 3. Тут мікроконтролер міг би виконувати інші корисні завдання
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    std::cout << "Done." << std::endl;
    return 0;
}
