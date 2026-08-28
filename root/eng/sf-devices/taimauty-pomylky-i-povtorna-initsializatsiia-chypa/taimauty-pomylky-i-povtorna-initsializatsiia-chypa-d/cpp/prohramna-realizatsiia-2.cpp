#include <cstdint>
#include <chrono>
#include <array>
#include "stm32f4xx.h"

struct HardwareBusConfig {
    BusPin power_switch;
    BusPin reset_pin;
    std::array<BusPin, 2> comm_pins; // SCL/SDA або SCK/MOSI
};

class PowerCycleManager {
public:
    explicit PowerCycleManager(HardwareBusConfig config) noexcept : cfg_{config} {}

    void execute() const noexcept {
        // 1. Ізоляція: переведення всіх ліній в аналоговий режим Hi-Z
        for (const auto& pin : cfg_.comm_pins) {
            set_analog_hiz(pin);
        }
        if (cfg_.reset_pin.port) {
            set_analog_hiz(cfg_.reset_pin);
        }

        // 2. Зняття напруги живлення
        cfg_.power_switch.set_low();

        // 3. Пауза для повного розряду ємностей
        delay_ms(50);

        // 4. Увімкнення напруги живлення
        cfg_.power_switch.set_high();

        // 5. Час стабілізації схеми POR чипа
        delay_ms(20);

        // 6. Відновлення виводу nRESET у високий рівень
        if (cfg_.reset_pin.port) {
            cfg_.reset_pin.set_high();
            cfg_.reset_pin.port->MODER &= ~(3U << (cfg_.reset_pin.pin * 2));
            cfg_.reset_pin.port->MODER |= (1U << (cfg_.reset_pin.pin * 2)); // Output
        }
    }

private:
    HardwareBusConfig cfg_;

    static void set_analog_hiz(const BusPin& pin) noexcept {
        pin.port->MODER |= (3U << (pin.pin * 2));   // Analog Mode
        pin.port->PUPDR &= ~(3U << (pin.pin * 2));  // No Pull
    }

    static void delay_ms(uint32_t ms) noexcept {
        for (uint32_t i = 0; i < ms; ++i) {
            const uint32_t start = DWT->CYCCNT;
            const uint32_t ticks = SystemCoreClock / 1000U;
            while ((DWT->CYCCNT - start) < ticks);
        }
    }
};
