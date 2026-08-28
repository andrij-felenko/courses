#include <cstdint>
#include <concepts>
#include <expected>
#include <span>

namespace embedded::bus {

template <typename I2cDriver>
class I2cMuxTca9548a {
public:
    enum class MuxError : uint8_t {
        InvalidChannel,
        BusError
    };

    constexpr explicit I2cMuxTca9548a(I2cDriver& driver, uint8_t addr = 0x70) noexcept
        : m_driver{driver}, m_addr{addr} {}

    [[nodiscard]] std::expected<void, MuxError> select_channel(uint8_t channel) noexcept {
        if (channel > 7) {
            return std::unexpected(MuxError::InvalidChannel);
        }
        const uint8_t mask = static_cast<uint8_t>(1u << channel);
        if (!m_driver.write(m_addr, std::span<const uint8_t>(&mask, 1))) {
            return std::unexpected(MuxError::BusError);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, MuxError> disable_all_channels() noexcept {
        const uint8_t mask = 0x00;
        if (!m_driver.write(m_addr, std::span<const uint8_t>(&mask, 1))) {
            return std::unexpected(MuxError::BusError);
        }
        return {};
    }

private:
    I2cDriver& m_driver;
    uint8_t m_addr;
};

} // namespace embedded::bus
