#include <cstdint>
#include <expected>

namespace protection {

struct Milliamperes { int32_t value{0}; };
struct Millivolts { uint32_t value{0}; };

enum class FaultReason : uint8_t {
    OverCurrent,
    OverVoltage,
    CommunicationLoss
};

class BenchSafetyGuard {
public:
    constexpr BenchSafetyGuard(Milliamperes limit, Millivolts max_v) noexcept
        : m_limit{limit}, m_max_voltage{max_v} {}

    [[nodiscard]] std::expected<void, FaultReason> validate(int16_t raw_curr, uint16_t raw_volt) noexcept {
        int32_t curr_ma = (static_cast<int32_t>(raw_curr) * 200) / 1000;
        uint32_t volt_mv = (static_cast<uint32_t>(raw_volt) * 1250) / 1000;

        if (curr_ma > m_limit.value) {
            return std::unexpected(FaultReason::OverCurrent);
        }
        if (volt_mv > m_max_voltage.value) {
            return std::unexpected(FaultReason::OverVoltage);
        }

        return {};
    }

private:
    Milliamperes m_limit;
    Millivolts m_max_voltage;
};

} // namespace protection
