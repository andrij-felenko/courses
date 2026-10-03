#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include "esp8266_https_client.hpp"

// Симуляція системного таймера (мілісекунди)
static uint32_t get_system_ticks_ms() {
    using namespace std::chrono;
    return static_cast<uint32_t>(duration_cast<milliseconds>(
        steady_clock::now().time_since_epoch()).count());
}

// Симуляція затримки мікроконтролера
static void delay_ms(uint32_t ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

int main() {
    std::cout << "--- ESP8266 HTTPS Client (AT SSL/TLS) ---" << std::endl;

    // Створення кільцевого буфера UART для асинхронного RX
    UartRingBuffer<2048> uart_rx_ring;

    // Callback відправки байтів у UART порт хоста
    auto uart_tx_callback = [&uart_rx_ring](const uint8_t* data, size_t length) {
        std::string cmd(reinterpret_cast<const char*>(data), length);
        std::cout << "[UART TX] -> " << cmd;

        // Імітація реакцій прошивки ESP8266 AT у кільцевий буфер RX
        if (cmd.rfind("AT+CIPSSLCCONF=", 0) == 0 ||
            cmd.rfind("AT+CIPSSLCSNI=", 0) == 0 ||
            cmd.rfind("AT+CIPSSLCSZ=", 0) == 0) {
            std::string resp = "OK\r\n";
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(resp.data()), resp.size());
        } else if (cmd.rfind("AT+CIPSTART=", 0) == 0) {
            std::string resp = "CONNECT\r\n\r\nOK\r\n";
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(resp.data()), resp.size());
        } else if (cmd.rfind("AT+CIPSEND=", 0) == 0) {
            std::string resp = ">\r\n";
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(resp.data()), resp.size());
        } else if (cmd.rfind("GET ", 0) == 0) {
            std::string resp = "SEND OK\r\n";
            // Формування підробленого кадру +IPD з відповіддю HTTP
            std::string http_payload = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\",\"ssl\":true}";
            std::string ipd_frame = "+IPD," + std::to_string(http_payload.size()) + ":" + http_payload + "\r\nCLOSED\r\n";
            
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(resp.data()), resp.size());
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(ipd_frame.data()), ipd_frame.size());
        } else if (cmd.rfind("POST ", 0) == 0) {
            std::string resp = "SEND OK\r\n";
            std::string http_payload = "HTTP/1.1 201 Created\r\nContent-Type: application/json\r\n\r\n{\"created\":true,\"id\":102}";
            std::string ipd_frame = "+IPD," + std::to_string(http_payload.size()) + ":" + http_payload + "\r\nCLOSED\r\n";

            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(resp.data()), resp.size());
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(ipd_frame.data()), ipd_frame.size());
        } else if (cmd.rfind("AT+CIPCLOSE", 0) == 0) {
            std::string resp = "CLOSED\r\nOK\r\n";
            uart_rx_ring.push_bytes(reinterpret_cast<const uint8_t*>(resp.data()), resp.size());
        }
    };

    // Ініціалізація клієнта HTTPS
    EspHttpsClient client(uart_rx_ring, uart_tx_callback, get_system_ticks_ms, delay_ms);

    // Конфігурація параметрів SSL/TLS
    TlsConfig config;
    config.auth_mode = TlsAuthMode::NoAuth;
    config.sni_hostname = "api.example.com";
    config.buffer_size = 4096; // Резервування DRAM у модулі

    std::cout << "\n[1] Конфігурація TLS сесії..." << std::endl;
    if (client.configure_tls(config)) {
        std::cout << "[УСПІХ] TLS налаштовано успішно." << std::endl;
    } else {
        std::cerr << "[ПОМИЛКА] Помилка налаштування TLS." << std::endl;
        return 1;
    }

    // 1. HTTPS GET запит
    std::cout << "\n[2] Виконання HTTPS GET запиту..." << std::endl;
    HttpResponseBuffer response;
    if (client.execute_get("api.example.com", 443, "/v1/status", response)) {
        std::cout << "[УСПІХ] Статус код: " << response.status_code << " (" << response.status_text << ")" << std::endl;
        std::cout << "Заголовки:" << std::endl;
        for (const auto& [hdr, val] : response.headers) {
            std::cout << "  " << hdr << ": " << val << std::endl;
        }
        std::cout << "Тіло відповіді: " << response.body << std::endl;
    } else {
        std::cerr << "[ПОМИЛКА] Помилка виконання HTTPS GET." << std::endl;
    }

    // 2. HTTPS POST запит (JSON телеметрія)
    std::cout << "\n[3] Виконання HTTPS POST запиту..." << std::endl;
    HttpResponseBuffer post_response;
    std::string json_payload = "{\"sensor\":\"temp_sensor_1\",\"value\":24.8}";
    if (client.execute_post("api.example.com", 443, "/v1/telemetry", "application/json", json_payload, post_response)) {
        std::cout << "[УСПІХ] Статус код POST: " << post_response.status_code << std::endl;
        std::cout << "Тіло POST відповіді: " << post_response.body << std::endl;
    } else {
        std::cerr << "[ПОМИЛКА] Помилка виконання HTTPS POST." << std::endl;
    }

    std::cout << "\n--- Завершення роботи клієнта HTTPS ---" << std::endl;
    return 0;
}
