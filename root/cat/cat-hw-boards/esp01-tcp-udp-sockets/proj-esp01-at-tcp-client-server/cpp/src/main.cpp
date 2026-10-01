#include "esp01_socket.hpp"
#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <chrono>
#include <thread>

// Симуляція UART драйвера для демонстрації роботи на ПК
class SimulatedUartDriver : public ESP01UartDriver {
public:
    SimulatedUartDriver() = default;

    bool write_bytes(const uint8_t* data, size_t length) override {
        std::string tx_str(reinterpret_cast<const char*>(data), length);
        std::cout << "[UART TX]: " << tx_str;
        
        // Моделювання автоматичних відповідей модуля ESP-01
        if (tx_str.find("AT\r\n") != std::string::npos || tx_str.find("AT+CIPMUX=1\r\n") != std::string::npos) {
            inject_rx("OK\r\n");
        } else if (tx_str.find("AT+CIPSERVER=1") != std::string::npos) {
            inject_rx("OK\r\n");
        } else if (tx_str.find("AT+CIPSEND=") != std::string::npos) {
            inject_rx(">\r\n");
        } else if (tx_str.find("Hello ESP-01") != std::string::npos) {
            inject_rx("SEND OK\r\n");
            // Симулюємо вхідне TCP-повідомлення +IPD від клієнта
            inject_rx("+IPD,0,5:PONG\r\n");
        }
        return true;
    }

    size_t read_bytes(uint8_t* buffer, size_t max_length) override {
        size_t count = 0;
        while (count < max_length && !rx_queue_.empty()) {
            buffer[count++] = rx_queue_.front();
            rx_queue_.erase(rx_queue_.begin());
        }
        return count;
    }

    void flush_rx() override {
        rx_queue_.clear();
    }

    void inject_rx(std::string_view data) {
        for (char c : data) {
            rx_queue_.push_back(static_cast<uint8_t>(c));
        }
    }

private:
    std::vector<uint8_t> rx_queue_;
};

int main() {
    std::cout << "--- Запуск сервісу сокетів ESP-01 ---" << std::endl;

    SimulatedUartDriver uart;
    ESP01SocketClientServer esp_socket(uart);

    // 1. Ініціалізація модуля
    if (!esp_socket.begin()) {
        std::cerr << "Помилка ініціалізації ESP-01!" << std::endl;
        return 1;
    }
    std::cout << "Модуль ESP-01 успішно ініціалізовано." << std::endl;

    // 2. Запуск TCP-сервера на порту 8080
    if (esp_socket.start_server(8080)) {
        std::cout << "TCP Сервер запущено на порту 8080." << std::endl;
    }

    // 3. Симуляція вхідного з'єднання від клієнта
    uart.inject_rx("0,CONNECT\r\n");
    esp_socket.poll();

    if (esp_socket.is_link_active(0)) {
        std::cout << "Клієнт підключився до лінку 0." << std::endl;
    }

    // 4. Відправка даних клієнту
    const std::string msg = "Hello ESP-01";
    esp_socket.send_data(0, reinterpret_cast<const uint8_t*>(msg.data()), msg.size());

    // 5. Опитування та прийом відповіді
    esp_socket.poll();
    auto packet = esp_socket.read_packet();
    if (packet.has_value()) {
        std::string payload(packet->payload.begin(), packet->payload.end());
        std::cout << "Отримано пакет з лінку " << packet->link_id << ": " << payload << std::endl;
    }

    // 6. Симуляція відключення клієнта
    uart.inject_rx("0,CLOSED\r\n");
    esp_socket.poll();

    if (!esp_socket.is_link_active(0)) {
        std::cout << "Лінк 0 успішно закрито." << std::endl;
    }

    std::cout << "--- Завершення роботи ---" << std::endl;
    return 0;
}
