#include <cstdint>

// Ідіоматичний C++: нульова ініціалізація за замовчуванням
struct SensorConfig {
    std::uint32_t timeout_ms{100};
    bool enable_crc{false};
    std::uint8_t retry_count{3};
};

void init_sensor() {
    // Усі поля гарантовано ініціалізовані безпечними значеннями
    SensorConfig cfg{};
    cfg.timeout_ms = 100;

    configure_hardware(&cfg);
}
