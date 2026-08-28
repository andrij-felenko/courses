// Реалізація HAL для ESP32 мовою C++
#include "soc/gpio_struct.h"
#include "esp_timer.h"

struct Esp32I2cHal {
    static constexpr uint32_t SclPin = 22;
    static constexpr uint32_t SdaPin = 21;

    static void set_scl_low() noexcept {
        GPIO.out_w1tc = (1ULL << SclPin);
    }
    static void set_scl_high_z() noexcept {
        GPIO.out_w1ts = (1ULL << SclPin);
    }
    static bool read_scl() noexcept {
        return (GPIO.in >> SclPin) & 0x1;
    }
    static void set_sda_low() noexcept {
        GPIO.out_w1tc = (1ULL << SdaPin);
    }
    static void set_sda_high_z() noexcept {
        GPIO.out_w1ts = (1ULL << SdaPin);
    }
    static bool read_sda() noexcept {
        return (GPIO.in >> SdaPin) & 0x1;
    }
    static void delay_half_period() noexcept {
        uint64_t start = esp_timer_get_time();
        while ((esp_timer_get_time() - start) < 5) {}
    }
    static uint32_t current_time_us() noexcept {
        return static_cast<uint32_t>(esp_timer_get_time());
    }
};
