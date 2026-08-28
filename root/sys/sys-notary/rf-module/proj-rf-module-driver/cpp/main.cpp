#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

enum class RfMode : uint8_t {
    Sleep   = 0x00,
    Standby = 0x01,
    Tx      = 0x03,
    Rx      = 0x05
};

enum class RfError {
    HardwareTimeout,
    InvalidParameter,
    SpiFailure
};

/* Абстрактний апаратний шинний інтерфейс */
class ISpiBus {
public:
    virtual ~ISpiBus() = default;
    virtual void select(bool enable) noexcept = 0;
    virtual uint8_t transfer(uint8_t byte) noexcept = 0;
};

/* Клас керування ВЧ-фронтендом (T/R Switch & PA Enable) */
class IRfFrontend {
public:
    virtual ~IRfFrontend() = default;
    virtual void setTxEnabled(bool enable) noexcept = 0;
};

class RfModule {
public:
    explicit RfModule(ISpiBus& spi, IRfFrontend& frontend) noexcept
        : spi_(spi), frontend_(frontend) {}

    ~RfModule() {
        (void)setMode(RfMode::Sleep);
    }

    [[nodiscard]] std::expected<void, RfError> init() noexcept {
        spi_.select(false);
        frontend_.setTxEnabled(false);

        auto res = setMode(RfMode::Standby);
        if (!res) return res;

        uint8_t mode = readReg(RegOpMode);
        if ((mode & 0x07) != static_cast<uint8_t>(RfMode::Standby)) {
            return std::unexpected(RfError::HardwareTimeout);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, RfError> setMode(RfMode mode) noexcept {
        frontend_.setTxEnabled(mode == RfMode::Tx);
        writeReg(RegOpMode, static_cast<uint8_t>(mode));
        return {};
    }

    [[nodiscard]] std::expected<void, RfError> sendPacket(std::span<const uint8_t> payload) noexcept {
        if (payload.empty() || payload.size() > 255) {
            return std::unexpected(RfError::InvalidParameter);
        }

        auto res = setMode(RfMode::Standby);
        if (!res) return res;

        writeReg(RegPayloadLen, static_cast<uint8_t>(payload.size()));

        spi_.select(true);
        spi_.transfer(RegFifo | SpiWriteMask);
        for (uint8_t byte : payload) {
            spi_.transfer(byte);
        }
        spi_.select(false);

        return setMode(RfMode::Tx);
    }

    void handleInterrupt() noexcept {
        uint8_t flags = readReg(RegIrqFlags);
        if (flags & TxDoneMask) {
            writeReg(RegIrqFlags, TxDoneMask);
            (void)setMode(RfMode::Standby);
        }
    }

private:
    static constexpr uint8_t RegOpMode     = 0x01;
    static constexpr uint8_t RegFifo       = 0x00;
    static constexpr uint8_t RegIrqFlags   = 0x12;
    static constexpr uint8_t RegPayloadLen = 0x22;
    static constexpr uint8_t SpiWriteMask  = 0x80;
    static constexpr uint8_t TxDoneMask    = 0x08;

    ISpiBus& spi_;
    IRfFrontend& frontend_;

    void writeReg(uint8_t reg, uint8_t val) noexcept {
        spi_.select(true);
        spi_.transfer(reg | SpiWriteMask);
        spi_.transfer(val);
        spi_.select(false);
    }

    [[nodiscard]] uint8_t readReg(uint8_t reg) noexcept {
        spi_.select(true);
        spi_.transfer(reg & ~SpiWriteMask);
        uint8_t val = spi_.transfer(0x00);
        spi_.select(false);
        return val;
    }
};
