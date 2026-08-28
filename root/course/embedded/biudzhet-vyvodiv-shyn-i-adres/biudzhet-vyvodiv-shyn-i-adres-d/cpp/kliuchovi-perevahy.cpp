#include <cstdint>
#include <span>
#include <expected>

enum class I2cError {
    BusError,
    NackAddress,
    NackData,
    Timeout
};

class I2cMaster {
public:
    virtual std::expected<void, I2cError> writeByte(uint8_t devAddr, uint8_t data) = 0;
    virtual std::expected<void, I2cError> readBytes(uint8_t devAddr, uint8_t reg, std::span<uint8_t> buffer) = 0;
    virtual ~I2cMaster() = default;
};

/* RAII-селектор каналу I2C-комутатора TCA9548A */
class ScopedI2cChannel {
public:
    ScopedI2cChannel(I2cMaster& bus, uint8_t muxAddr, uint8_t channel)
        : bus_(bus), muxAddr_(muxAddr) {
        if (channel < 8) {
            uint8_t mask = static_cast<uint8_t>(1U << channel);
            status_ = bus_.writeByte(muxAddr_, mask);
        } else {
            status_ = std::unexpected(I2cError::BusError);
        }
    }

    ~ScopedI2cChannel() {
        /* Автоматично ізолюємо шину після виходу з області видимості */
        (void)bus_.writeByte(muxAddr_, 0x00);
    }

    [[nodiscard]] bool isValid() const {
        return status_.has_value();
    }

    [[nodiscard]] I2cError error() const {
        return status_.error();
    }

private:
    I2cMaster& bus_;
    uint8_t muxAddr_;
    std::expected<void, I2cError> status_;
};
