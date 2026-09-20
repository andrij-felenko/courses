#include <cstdint>

struct DipParsedConfig {
    enum class Status { OK, ERR_INVALID_MODE };

    std::uint8_t i2c_address;
    std::uint8_t operation_mode;
    bool turbo_enabled;
    Status status;
};

class DipConfigParser {
public:
    static constexpr std::uint8_t MAX_VALID_MODES = 5;

    static DipParsedConfig parse(std::uint8_t norm_byte) {
        DipParsedConfig cfg;
        cfg.i2c_address = DipFieldExtractor::extractField(norm_byte, 4, 0);

        std::uint8_t raw_mode = DipFieldExtractor::extractField(norm_byte, 3, 4);
        if (raw_mode < MAX_VALID_MODES) {
            cfg.operation_mode = raw_mode;
            cfg.status = DipParsedConfig::Status::OK;
        } else {
            cfg.operation_mode = 0; // Безпечний fallback state
            cfg.status = DipParsedConfig::Status::ERR_INVALID_MODE;
        }

        cfg.turbo_enabled = DipFieldExtractor::extractFlag(norm_byte, 7);
        return cfg;
    }
};
