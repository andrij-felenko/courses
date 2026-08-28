#include <cstdint>
#include <string_view>
#include <span>

constexpr uint32_t hashStringFnv1a(std::string_view str) {
    uint32_t hash = 0x811C9DC5;
    for (char c : str) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 0x01000193;
    }
    return hash;
}

inline constexpr uint32_t TokenAdcTimeout = hashStringFnv1a("ADC ch=%u timeout after %u ms");

struct [[gnu::packed]] AdcTimeoutPayload {
    uint8_t  channel;
    uint32_t timeoutMs;
};

void logAdcTimeout(uint8_t ch, uint32_t ms) {
    AdcTimeoutPayload payload{ch, ms};
    logEmit<LogLevel::Warn>(1, TokenAdcTimeout, std::as_bytes(std::span{&payload, 1}));
}
