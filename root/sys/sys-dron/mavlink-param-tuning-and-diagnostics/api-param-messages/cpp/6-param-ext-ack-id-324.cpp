#include <cstdint>
#include <array>
#include <string_view>

enum class ParamAckResult : uint8_t {
    Accepted = 0,
    ValueUnsupported = 1,
    Failed = 2,
    InProgress = 3
};

struct ParamExtAckMsg {
    std::array<char, 16> id{};
    std::array<uint8_t, 128> value{};
    uint8_t type{0};
    ParamAckResult result{ParamAckResult::Failed};

    [[nodiscard]] bool is_accepted() const noexcept {
        return result == ParamAckResult::Accepted;
    }
};
