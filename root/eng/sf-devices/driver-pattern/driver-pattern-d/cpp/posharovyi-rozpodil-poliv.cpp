#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace driver {

enum class Status : uint8_t {
    Ok = 0,
    Busy,
    Timeout,
    Nack,
    BusError,
    InvalidParam
};

struct I2cConfig {
    uint32_t clock_speed_hz{100'000};
    uint16_t timeout_ms{50};
    uint8_t sda_pin{0};
    uint8_t scl_pin{0};
    bool enable_dma{false};
};

enum class I2cState : uint8_t {
    Uninitialized = 0,
    Idle,
    BusyTx,
    BusyRx,
    Error
};

class I2cDriver {
public:
    explicit I2cDriver(std::uintptr_t reg_base, const I2cConfig& config) noexcept
        : reg_base_(reg_base), config_(config), state_(I2cState::Uninitialized) {}

    [[nodiscard]] Status init() noexcept;
    
    [[nodiscard]] std::expected<size_t, Status> master_write(
        uint8_t dev_addr,
        std::span<const uint8_t> data) noexcept;

    [[nodiscard]] I2cState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t error_count() const noexcept { return errors_count_; }

private:
    std::uintptr_t reg_base_;
    I2cConfig config_;
    volatile I2cState state_;
    std::span<const uint8_t> tx_view_{};
    std::span<uint8_t> rx_view_{};
    uint32_t errors_count_{0};
};

} // namespace driver
