#include <cstdint>
#include <concepts>

enum class EncoderProtocol : uint8_t {
    SSI,
    BiSS_C
};

struct EncoderConfig {
    EncoderProtocol protocol{EncoderProtocol::BiSS_C};
    uint8_t singleturn_bits{14};
    uint8_t multiturn_bits{12};
    bool use_gray_code{true};
    uint32_t timeout_us{1000};
};

struct EncoderData {
    uint32_t raw_singleturn{0};
    uint32_t raw_multiturn{0};
    uint64_t full_position{0};
    bool error_flag{false};
    bool warning_flag{false};
    uint8_t crc_error_count{0};
};
