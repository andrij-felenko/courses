#include <string_view>
#include <functional>
#include <cstdint>

enum class AtResult : uint8_t {
    Ok = 0,
    Error,
    Timeout,
    Busy
};

struct AtCommandDescriptor {
    std::string_view cmd_str;
    std::string_view expect_prefix;
    uint32_t         timeout_ms{1000};
    uint8_t          max_retries{0};
    uint8_t          current_retry{0};
    std::function<void(AtResult, std::string_view)> callback{};
};
