// self_test.cpp — BIST. I2C зроблено програмно: так бюджет часу видно
// прямо в коді, а не ховається в регістрі периферії. Замість «goto out»
// C-версії лінії відпускають деструктори.
#include "self_test.hpp"

#include <cstdint>

namespace diag {
namespace {

constexpr std::uint32_t kHalfBitUs = 5; // близько 100 кГц
constexpr std::uint8_t  kAddrRtc    = 0x68;
constexpr std::uint8_t  kAddrEeprom = 0x50;
constexpr std::uint16_t kAdcVrefMilliVolts = 3300;
constexpr std::uint16_t kAdcFullScale      = 4096;

class Deadline {
public:
    explicit Deadline(hw::Millis budget) noexcept : end_(hw::now() + budget) {}
    bool expired() const noexcept { return hw::now() >= end_; }

private:
    hw::Millis end_;
};

// Оренда шини на час тесту: під RTOS це м'ютекс, на голому залізі — no-op.
class BusLease {
public:
    explicit BusLease(hw::Millis timeout) noexcept : held_(hw::busTryLock(timeout)) {}
    ~BusLease()
    {
        if (held_) {
            hw::busUnlock();
        }
    }
    BusLease(const BusLease&)            = delete;
    BusLease& operator=(const BusLease&) = delete;

    explicit operator bool() const noexcept { return held_; }

private:
    bool held_;
};

// Власник ліній. Хай яка гілка нас вивела — тайм-аут, NACK чи успіх, —
// деструктор видасть STOP і відпустить SDA/SCL.
class BitBangBus {
public:
    BitBangBus() noexcept
    {
        hw::i2c::sdaRelease();
        hw::i2c::sclRelease();
    }
    ~BitBangBus()
    {
        stop();
        hw::i2c::sdaRelease();
        hw::i2c::sclRelease();
    }
    BitBangBus(const BitBangBus&)            = delete;
    BitBangBus& operator=(const BitBangBus&) = delete;

    // Ведений завис із SDA у нулі: дев'ять тактів SCL дають йому додати
    // недоотримані біти й відпустити лінію. Класичний прийом відновлення.
    std::expected<void, BusError> recover(const Deadline& deadline) noexcept
    {
        if (hw::i2c::sdaRead()) {
            return {};
        }
        for (int i = 0; i < 9 && !hw::i2c::sdaRead(); ++i) {
            if (auto pulse = sclHigh(deadline); !pulse) {
                return pulse;
            }
            sclLow();
        }
        if (!hw::i2c::sdaRead()) {
            return std::unexpected(BusError::StuckLow); // прибито намертво
        }
        stop();
        return {};
    }

    std::expected<void, BusError> start(const Deadline& deadline) noexcept
    {
        hw::i2c::sdaRelease();
        if (auto high = sclHigh(deadline); !high) {
            return high;
        }
        if (!hw::i2c::sdaRead()) {
            return std::unexpected(BusError::StuckLow);
        }
        hw::i2c::sdaLow();
        hw::delayUs(kHalfBitUs);
        sclLow();
        return {};
    }

    // true — адресат притиснув SDA до нуля, тобто відповів ACK.
    std::expected<bool, BusError> writeByte(std::uint8_t value, const Deadline& deadline) noexcept
    {
        for (int bit = 7; bit >= 0; --bit) {
            if (auto written = writeBit(((value >> bit) & 1u) != 0u, deadline); !written) {
                return std::unexpected(written.error());
            }
        }
        auto nack = readBit(deadline);
        if (!nack) {
            return std::unexpected(nack.error());
        }
        return !*nack;
    }

    void stop() noexcept
    {
        hw::i2c::sdaLow();
        hw::delayUs(kHalfBitUs);
        hw::i2c::sclRelease();
        hw::delayUs(kHalfBitUs);
        hw::i2c::sdaRelease();
        hw::delayUs(kHalfBitUs);
    }

private:
    // Відпустити SCL і дочекатися, поки ведений перестане тримати такт
    // (clock stretching). Тримає надто довго — виходимо за тайм-аутом.
    std::expected<void, BusError> sclHigh(const Deadline& deadline) noexcept
    {
        hw::i2c::sclRelease();
        while (!hw::i2c::sclRead()) {
            if (deadline.expired()) {
                return std::unexpected(BusError::Timeout);
            }
        }
        hw::delayUs(kHalfBitUs);
        return {};
    }

    void sclLow() noexcept
    {
        hw::i2c::sclLow();
        hw::delayUs(kHalfBitUs);
    }

    std::expected<void, BusError> writeBit(bool bit, const Deadline& deadline) noexcept
    {
        if (bit) {
            hw::i2c::sdaRelease();
        } else {
            hw::i2c::sdaLow();
        }
        hw::delayUs(1);
        if (auto high = sclHigh(deadline); !high) {
            return high;
        }
        sclLow();
        return {};
    }

    std::expected<bool, BusError> readBit(const Deadline& deadline) noexcept
    {
        hw::i2c::sdaRelease();
        hw::delayUs(1);
        if (auto high = sclHigh(deadline); !high) {
            return std::unexpected(high.error());
        }
        const bool level = hw::i2c::sdaRead();
        sclLow();
        return level;
    }
};

} // namespace

std::expected<void, BusError> probe(std::uint8_t address7) noexcept
{
    const Deadline deadline{ProbeTimeout};
    BitBangBus     bus;

    if (auto recovered = bus.recover(deadline); !recovered) {
        return recovered;
    }
    if (auto started = bus.start(deadline); !started) {
        return started;
    }
    const auto ack = bus.writeByte(static_cast<std::uint8_t>(address7 << 1), deadline); // біт 0 = запис
    if (!ack) {
        return std::unexpected(ack.error());
    }
    if (!*ack) {
        return std::unexpected(BusError::NoAck);
    }
    return {};
}

std::expected<Report, BusError> runBist() noexcept
{
    const BusLease lease{BusLockTimeout};
    if (!lease) {
        return std::unexpected(BusError::Busy); // шину тримає робоча задача
    }

    Report report{};
    report.busFree  = hw::i2c::sdaRead() && hw::i2c::sclRead();
    report.rtcOk    = probe(kAddrRtc).has_value();
    report.eepromOk = probe(kAddrEeprom).has_value();
    report.adcRaw   = hw::adcRaw(0);
    // Цілочисельно: у сервісній задачі плаваюча кома не потрібна.
    report.adcMilliVolts =
        static_cast<std::uint16_t>(std::uint32_t{report.adcRaw} * kAdcVrefMilliVolts / kAdcFullScale);
    return report;
}

} // namespace diag
