#include <iostream>
#include <chrono>
#include <thread>
#include "esp8266_relay_driver.hpp"
#include "uart_ring_buffer.hpp"

// Глобальний буфер UART RX для імітації фізичного порту хоста
static UartRingBuffer<256> g_uart_rx_buffer;

// Емуляція відправки байтів з ESP8266 у RX-буфер хоста
static void simulateEsp8266Response(std::string_view response) {
    for (char c : response) {
        g_uart_rx_buffer.push(static_cast<uint8_t>(c));
    }
}

// Передавач UART хоста (передає AT-команду в модуль ESP8266)
static void hostUartSend(std::string_view data) {
    std::cout << "[HOST TX -> ESP8266]: " << data;

    // Симуляція обробки команди ESP8266 та автоматичної відповіді AT-інтерпретатора
    if (data.find("AT+PINMODE=") != std::string_view::npos) {
        simulateEsp8266Response("OK\r\n");
    } else if (data.find("AT+PINWRITE=") != std::string_view::npos) {
        simulateEsp8266Response("OK\r\n");
    } else if (data.find("AT+PINREAD=5") != std::string_view::npos) {
        simulateEsp8266Response("+PINREAD:5,1\r\nOK\r\n");
    } else {
        simulateEsp8266Response("ERROR\r\n");
    }
}

// Отримання системного часу в мілісекундах
static uint32_t getSystemTicksMs() {
    using namespace std::chrono;
    static auto start_time = steady_clock::now();
    auto now = steady_clock::now();
    return static_cast<uint32_t>(duration_cast<milliseconds>(now - start_time).count());
}

// Затримка системного потоку у мілісекундах
static void systemDelayMs(uint32_t ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

int main() {
    std::cout << "--- Запуск драйвера реле ESP8266 через AT-команди UART ---\n\n";

    // 1. Ініціалізація класу-драйвера ESP8266
    Esp8266RelayDriver relay_driver(g_uart_rx_buffer, hostUartSend, getSystemTicksMs, systemDelayMs);

    // 2. Демонстрація перевірки конфігураційних виводів завантаження (strapping pins)
    constexpr uint8_t RELAY_PIN_SAFE = 5;  // GPIO5 (звичайний вивід)
    constexpr uint8_t RELAY_PIN_STRAP = 0; // GPIO0 (strapping pin)

    std::cout << "[INFO] Перевірка виводу GPIO" << static_cast<int>(RELAY_PIN_SAFE) 
              << " на strapping pin: " << (Esp8266RelayDriver::isStrappingPin(RELAY_PIN_SAFE) ? "Так" : "Ні") << "\n";
    std::cout << "[INFO] Перевірка виводу GPIO" << static_cast<int>(RELAY_PIN_STRAP) 
              << " на strapping pin: " << (Esp8266RelayDriver::isStrappingPin(RELAY_PIN_STRAP) ? "Так" : "Ні") << "\n\n";

    // 3. Ініціалізація виводу реле у режимі OUTPUT з початковим рівнем LOW
    std::cout << "--- Крок 1: Ініціалізація GPIO" << static_cast<int>(RELAY_PIN_SAFE) << " ---\n";
    DriverStatus status = relay_driver.initPin(RELAY_PIN_SAFE, GpioMode::Output, LogicLevel::Low);
    if (status == DriverStatus::Ok) {
        std::cout << "[SUCCESS] Вивід GPIO" << static_cast<int>(RELAY_PIN_SAFE) << " успішно ініціалізовано.\n\n";
    } else {
        std::cerr << "[ERROR] Помилка ініціалізації виводу!\n";
        return 1;
    }

    // 4. Безпечне керування силовим реле через RAII-обгортку RelayPinGuard
    std::cout << "--- Крок 2: Безпечна робота з реле за принципом RAII ---\n";
    {
        // Створюємо guard для GPIO5. При створенні реле перебуває в LOW (вимкнено)
        RelayPinGuard relay_guard(relay_driver, RELAY_PIN_SAFE, LogicLevel::Low);

        std::cout << "[RAII] Вмикаємо реле (переведення в HIGH)...\n";
        if (relay_guard.setState(LogicLevel::High) == DriverStatus::Ok) {
            std::cout << "[SUCCESS] Реле увімкнено. Поточний стан: "
                      << (relay_guard.currentLevel() == LogicLevel::High ? "HIGH" : "LOW") << "\n";
        }

        // 5. Перевірка фактичного стану виводу через AT+PINREAD
        std::cout << "[INFO] Зчитуємо стан виводу через AT+PINREAD...\n";
        LogicLevel read_level = LogicLevel::Low;
        if (relay_driver.readPin(RELAY_PIN_SAFE, read_level) == DriverStatus::Ok) {
            std::cout << "[SUCCESS] Прочитаний рівень з ESP8266: " 
                      << (read_level == LogicLevel::High ? "HIGH" : "LOW") << "\n";
        }

        std::cout << "[RAII] Вихід з локальної області видимості...\n";
        // При виході з блоку деструктор RelayPinGuard автоматично вимкне реле (LOW)
    }
    std::cout << "[RAII] Деструктор виконано, реле повернуто у безпечний стан LOW.\n\n";

    // 6. Демонстрація обробки помилок послідовного зв'язку
    std::cout << "--- Крок 3: Обробка збоїв зв'язку (симуляція таймауту) ---\n";
    // Перевизначаємо передавач для імітації відсутності відповіді від ESP8266
    hostUartSend = [](std::string_view data) {
        std::cout << "[HOST TX -> ESP8266 (БЕЗ ВІДПОВІДІ)]: " << data;
    };
    Esp8266RelayDriver silent_driver(g_uart_rx_buffer, hostUartSend, getSystemTicksMs, systemDelayMs);

    DriverStatus err_status = silent_driver.writePin(RELAY_PIN_SAFE, LogicLevel::High);
    if (err_status == DriverStatus::Timeout) {
        std::cout << "[SUCCESS] Таймаут успішно зафіксовано драйвером. Система захищена від зависання.\n";
    }

    std::cout << "\n--- Завершення демонстрації ---\n";
    return 0;
}
