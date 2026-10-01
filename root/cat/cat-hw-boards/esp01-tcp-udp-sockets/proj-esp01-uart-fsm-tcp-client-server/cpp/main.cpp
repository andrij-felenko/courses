#include "Esp01Socket.hpp"
#include <iostream>
#include <vector>

// Приклад конкретної реалізації апаратної передачі UART для ПК або конкретного МК.
class ConcreteEsp01Socket : public Esp01Socket {
public:
    ConcreteEsp01Socket(uint8_t linkId = 0) : Esp01Socket(linkId) {}

    void hardwareUartWrite(uint8_t byte) override {
        // У реальному МК тут викликається Serial.write(byte) або UART_TX_REG = byte.
        // Для демонстрації виводимо символи команд у консоль.
        std::cout << static_cast<char>(byte);
    }

    // Симуляція надходження відповіді від ESP-01 у приймач UART.
    void simulateRxData(const char* data) {
        std::size_t len = std::strlen(data);
        for (std::size_t i = 0; i < len; ++i) {
            onUartRxByte(static_cast<uint8_t>(data[i]));
        }
    }
};

int main() {
    std::cout << "=== Ініціалізація неблокуючого сокета ESP-01 ===" << std::endl;

    ConcreteEsp01Socket socket(0);
    socket.begin();

    std::cout << "\n=== Відправлення команди підключення TCP ===" << std::endl;
    socket.connect(SocketType::TCP, "192.168.1.100", 8080);

    // Імітуємо надходження відповіді від прошивки "0,CONNECT\r\n"
    socket.simulateRxData("0,CONNECT\r\n");
    socket.update();

    if (socket.state() == SocketState::Connected) {
        std::cout << "\n[OK] З'єднання успішно встановлено!" << std::endl;
    }

    // Передаємо дані у сокет (наприклад, HTTP GET запит)
    const char* request = "GET /api/data HTTP/1.1\r\nHost: 192.168.1.100\r\n\r\n";
    socket.write(reinterpret_cast<const uint8_t*>(request), std::strlen(request));

    std::cout << "\n=== Виклик неблокуючого оновлення socket.update() ===" << std::endl;
    socket.update();

    // Імітуємо надходження вхідного пакета даних: +IPD,0,13:Hello Server!
    std::cout << "\n=== Симуляція приймання пакету +IPD,0,13:Hello Server! ===" << std::endl;
    socket.simulateRxData("+IPD,0,13:Hello Server!");
    socket.update();

    // Перевіряємо доступні дані в RX буфері
    if (socket.available() > 0) {
        uint8_t rxBuffer[64] = {0};
        std::size_t readBytes = socket.read(rxBuffer, sizeof(rxBuffer) - 1);
        rxBuffer[readBytes] = '\0';
        std::cout << "[Отримано дані]: " << reinterpret_cast<char*>(rxBuffer) << std::endl;
    }

    // Розриваємо з'єднання
    std::cout << "\n=== Закриття сокета ===" << std::endl;
    socket.disconnect();
    socket.simulateRxData("0,CLOSED\r\n");
    socket.update();

    if (socket.state() == SocketState::Disconnected) {
        std::cout << "[OK] Сокет успішно закрито." << std::endl;
    }

    return 0;
}
