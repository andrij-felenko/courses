#include <cstdint>

struct SystemConfig {
    uint8_t i2c_address{0x30};
    uint8_t baudrate_index{0};
    bool debug_mode_enabled{false};
    bool is_valid{false};

    static SystemConfig parse(uint8_t debounced_byte) noexcept {
        SystemConfig cfg;
        const uint8_t raw_addr = extract_bitfield(debounced_byte, 0, 3);
        const uint8_t raw_baud = extract_bitfield(debounced_byte, 3, 2);
        const uint8_t raw_dbg  = extract_bitfield(debounced_byte, 5, 1);

        cfg.i2c_address = static_cast<uint8_t>(0x30U + raw_addr);
        cfg.baudrate_index = raw_baud;
        cfg.debug_mode_enabled = (raw_dbg != 0);
        cfg.is_valid = (raw_baud <= 3);

        return cfg;
    }
};
