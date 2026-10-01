/*
 * main.cpp — Приклад прошивки мовою C++ для модулів ESP-01 та ESP-01S
 *
 * Концепція:
 * Ідіоматична реалізація на C++ із застосуванням класів, enum class, constexpr,
 * std::string_view та методології RAII для інкапсуляції роботи з периферією ESP8266.
 * Демонструє відмінності між ревізіями ESP-01 (без підтяжок) та ESP-01S (з вбудованими підтяжками).
 */

#include <Arduino.h>
#include <string_view>
#include <array>

namespace esp01 {

// Перерахування ревізій плат серії ESP-01
enum class ModuleRevision {
    Esp01,  // Класична плата ESP-01 (синій світлодіод на TX/GPIO1, відсутні підтяжки)
    Esp01S  // Оновлена плата ESP-01S (синій світлодіод на GPIO2, вбудовані підтяжки 12кОм)
};

// Перерахування режимів завантаження
enum class BootMode {
    FlashDownload,  // GPIO0 підключено до GND під час скидання
    NormalExecution // GPIO0 підключено до 3.3V під час скидання
};

// Константні параметри пінів
struct PinConfig {
    static constexpr uint8_t LedGpioEsp01S = 2; // GPIO2 активний низький (Active LOW)
    static constexpr uint8_t LedGpioEsp01  = 1; // GPIO1 (TXD) активний низький
    static constexpr uint32_t DefaultBaudRate = 115200;
};

// Клас інкапсуляції керування світлодіодом модуля
class ModuleLed {
public:
    explicit constexpr ModuleLed(uint8_t pin, bool active_low = true) noexcept
        : pin_(pin), active_low_(active_low), is_on_(false) {}

    // Ініціалізація виводу GPIO
    void init() const {
        pinMode(pin_, OUTPUT);
        turn_off();
    }

    // Увімкнення світлодіода
    void turn_on() {
        is_on_ = true;
        digitalWrite(pin_, active_low_ ? LOW : HIGH);
    }

    // Вимкнення світлодіода
    void turn_off() {
        is_on_ = false;
        digitalWrite(pin_, active_low_ ? HIGH : LOW);
    }

    // Перемикання стану (toggle)
    void toggle() {
        if (is_on_) {
            turn_off();
        } else {
            turn_on();
        }
    }

    [[nodiscard]] bool is_on() const noexcept { return is_on_; }
    [[nodiscard]] uint8_t get_pin() const noexcept { return pin_; }

private:
    uint8_t pin_;
    bool active_low_;
    bool is_on_{false};
};

// Клас діагностики та роботи з послідовним портом
class DiagnosticsController {
public:
    explicit DiagnosticsController(uint32_t baud_rate = PinConfig::DefaultBaudRate) noexcept
        : baud_rate_(baud_rate) {}

    void begin() const {
        Serial.begin(baud_rate_);
        // Очікування ініціалізації порту
        delay(100);
    }

    void print_banner(ModuleRevision rev) const {
        print_line("=======================================================");
        print_line("   Огляд та діагностика модулів ESP-01 / ESP-01S (C++) ");
        print_line("=======================================================");
        
        if (rev == ModuleRevision::Esp01S) {
            print_line("Виявлено режим: ESP-01S (Світлодіод на GPIO2, вбудована підтяжка)");
        } else {
            print_line("Виявлено режим: ESP-01 (Світлодіод на GPIO1/TXD, потрібна зовнішня підтяжка)");
        }

        print_line("\n--- Електрична специфікація та розпіновка ---");
        print_line(" 1. VCC    : 3.3 В (піковий струм до 300 мА!)");
        print_line(" 2. GND    : Загальний мінус");
        print_line(" 3. CH_PD  : Chip Enable (підтягнути до 3.3 В)");
        print_line(" 4. RST    : Hardware Reset (активний LOW, підтягнути до 3.3 В)");
        print_line(" 5. GPIO0  : LOW -> Flash Mode | HIGH -> Normal Run");
        print_line(" 6. GPIO2  : Підтяжка до 3.3 В при підйомі живлення");
        print_line(" 7. TX/RX  : Послідовний порт UART (3.3В логіка)");
        print_line("=======================================================\n");
    }

    void print_status(uint32_t cycle, bool led_state, uint8_t pin) const {
        Serial.print(F("[C++ Status] Цикл #"));
        Serial.print(cycle);
        Serial.print(F(" | Світлодіод (GPIO"));
        Serial.print(pin);
        Serial.print(F("): "));
        Serial.println(led_state ? F("УВІМКНЕНО (LOW)") : F("ВИМКНЕНО (HIGH)"));
    }

private:
    uint32_t baud_rate_;

    static void print_line(std::string_view message) {
        Serial.write(message.data(), message.size());
        Serial.println();
    }
};

} // namespace esp01

// Глобальні об'єкти системи (ініціалізуються для ESP-01S)
namespace {
    esp01::ModuleLed led(esp01::PinConfig::LedGpioEsp01S, true);
    esp01::DiagnosticsController diag(esp01::PinConfig::DefaultBaudRate);
    uint32_t cycle_count = 0;
}

void setup() {
    // Ініціалізація послідовного порту та GPIO
    diag.begin();
    led.init();

    // Виведення інформаційного банера при старті
    diag.print_banner(esp01::ModuleRevision::Esp01S);
}

void loop() {
    cycle_count++;
    
    // Перемикання стану індикатора
    led.toggle();
    
    // Передача діагностичної інформації в термінал
    diag.print_status(cycle_count, led.is_on(), led.get_pin());

    // Пауза між циклами блимання
    delay(1000);
}
