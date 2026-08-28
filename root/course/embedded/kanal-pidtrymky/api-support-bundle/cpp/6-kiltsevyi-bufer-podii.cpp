#include <cstdint>

namespace diagnostic {

struct [[gnu::packed]] LogEntry {
    std::uint32_t timestamp_ms{};
    std::uint8_t  subsystem_id{};
    std::uint8_t  severity{};
    std::uint16_t event_code{};
    std::uint32_t argument{};
    std::uint32_t caller_pc{};
};

} // namespace diagnostic
