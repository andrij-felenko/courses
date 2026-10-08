#include "esp_at_parser.hpp"
#include "uart_ring_buffer.hpp"
#include <iostream>
#include <string_view>
#include <vector>
#include <chrono>

// Імітатор апаратного переривання UART для наповнення кільцевого буфера
void simulateUartInterrupt(DefaultUartRingBuffer& ringBuffer, std::string_view rawData) {
    for (char c : rawData) {
        if (!ringBuffer.push(static_cast<uint8_t>(c))) {
            std::cout << "[ISR WARNING] Кільцевий буфер переповнено при прийомі байта!\n";
        }
    }
}

// Перетворення статусу у строковий вигляд для виводу
std::string_view statusToString(AtStatus status) {
    switch (status) {
        case AtStatus::OK:      return "OK";
        case AtStatus::ERROR:   return "ERROR";
        case AtStatus::BUSY:    return "BUSY";
        case AtStatus::TIMEOUT: return "TIMEOUT";
        default:                return "UNKNOWN";
    }
}

int main() {
    std::cout << "=== Демонстрація неблокуючого C++ парсера ESP-AT відповідей ===\n\n";

    // 1. Створення об'єкта кільцевого буфера та FSM-парсера
    DefaultUartRingBuffer rxRing;
    EspAtParser parser(rxRing);

    // 2. Реєстрація C++ std::function колбека для результатів команд
    parser.setStatusCallback([](AtStatus status, std::string_view payload) {
        std::cout << " -> [Колбек Статусу] Результат: " << statusToString(status);
        if (!payload.empty()) {
            std::cout << " | Корисне навантаження:\n" << payload;
        }
        std::cout << "\n";
    });

    // 3. Реєстрація C++ std::function колбека для спонтанних URC-сповіщень
    parser.setUrcCallback([](std::string_view tag, std::string_view data) {
        std::cout << " -> [Колбек URC] Тег: " << tag << " | Дані: " << data << "\n";
    });

    uint32_t simulatedTimeMs = 1000;

    // --- Сценарій 1: Системний запуск та URC сповіщення ---
    std::cout << "[Крок 1] Модуль ESP8266 надсилає системне сповіщення про готовність...\n";
    simulateUartInterrupt(rxRing, "\r\nready\r\nWIFI CONNECTED\r\nWIFI GOT IP\r\n");
    parser.update(simulatedTimeMs);

    // --- Сценарій 2: Виконання команди AT+GMR з відповіддю та корисним навантаженням ---
    std::cout << "\n[Крок 2] Відправка AT+GMR (запит версії прошивки)...\n";
    parser.sendCommand("AT+GMR", 1000, simulatedTimeMs);
    
    // Імітуємо фрагментований прийом даних через UART
    simulateUartInterrupt(rxRing, "AT version:1.7.4.0\r\nSDK version:3.0.4\r\n");
    parser.update(simulatedTimeMs); // Дані накопичені, чекаємо OK

    simulatedTimeMs += 50;
    simulateUartInterrupt(rxRing, "\r\nOK\r\n");
    parser.update(simulatedTimeMs); // Отримано OK, викликається колбек статусу

    // --- Сценарій 3: Отримання спонтанного мережевого пакету +IPD ---
    std::cout << "\n[Крок 3] Прийом спонтанних вхідних мережевих даних +IPD...\n";
    simulateUartInterrupt(rxRing, "+IPD,0,4:HELLO\r\n");
    parser.update(simulatedTimeMs);

    // --- Сценарій 4: Надсилання команди з відмовою (ERROR) ---
    std::cout << "\n[Крок 4] Відправка некоректної команди AT+INVALID...\n";
    simulatedTimeMs += 100;
    parser.sendCommand("AT+INVALID", 1000, simulatedTimeMs);
    simulateUartInterrupt(rxRing, "\r\nERROR\r\n");
    parser.update(simulatedTimeMs);

    // --- Сценарій 5: Симуляція таймауту очікування відповіді ---
    std::cout << "\n[Крок 5] Відправка AT+CWJAP з невідповідаючим модулем (перевірка таймауту)...\n";
    simulatedTimeMs += 100;
    parser.sendCommand("AT+CWJAP", 500, simulatedTimeMs);
    
    std::cout << "Виконуємо неблокуючі ітерації головного циклу...\n";
    for (int i = 0; i < 6; ++i) {
        simulatedTimeMs += 100; // Просування часу на 100 мс щоітерації
        parser.update(simulatedTimeMs);
    }

    std::cout << "\n=== Обробку завершено успішно ===\n";
    return 0;
}
