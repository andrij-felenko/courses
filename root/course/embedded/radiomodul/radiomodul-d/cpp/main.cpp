#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace RadioDriver {

enum class Command : uint8_t {
    SoftReset = 0x30,
    SynthOn   = 0x31,
    XoscOff   = 0x32,
    Calibrate = 0x33,
    EnterRx   = 0x34,
    EnterTx   = 0x35,
    EnterIdle = 0x36,
    FlushRx   = 0x3A,
    FlushTx   = 0x3B,
    NoOp      = 0x3D
};

enum class Register : uint8_t {
    IoConfig0  = 0x00,
    PacketLen  = 0x06,
    PacketCtrl = 0x08,
    Freq2      = 0x0D,
    Freq1      = 0x0E,
    Freq0      = 0x0F,
    ModemCfg2  = 0x12,
    Rssi       = 0x34,
    RxBytes    = 0x3B,
    Fifo       = 0x3F
};

struct Packet {
    std::array<uint8_t, 64> data{};
    uint8_t                 length{0};
    int8_t                  rssiDbm{0};
};

template <typename SpiHal>
class Transceiver {
public:
    explicit Transceiver(SpiHal& hal) : hal_(hal) {}

    void init() noexcept {
        hal_.setCs(true);
        hal_.delayUs(100);

        strobe(Command::SoftReset);
        hal_.delayUs(200);

        // GDO0 переривання при валідному прийомі (0x06)
        writeRegister(Register::IoConfig0, 0x06);

        // Packet Control: Variable Length, CRC Enabled, Whitening Enabled
        writeRegister(Register::PacketCtrl, 0x45);
        writeRegister(Register::PacketLen, 64);

        // GFSK, 16-bit Sync Word detection
        writeRegister(Register::ModemCfg2, 0x12);

        // 868.0 MHz несуча
        writeRegister(Register::Freq2, 0x21);
        writeRegister(Register::Freq1, 0x62);
        writeRegister(Register::Freq0, 0x76);

        strobe(Command::EnterIdle);
    }

    bool send(std::span<const uint8_t> payload) noexcept {
        if (payload.empty() || payload.size() > 63) return false;

        strobe(Command::EnterIdle);
        strobe(Command::FlushTx);

        hal_.setCs(false);
        hal_.transfer(static_cast<uint8_t>(Register::Fifo) | 0x40U); // Burst Write
        hal_.transfer(static_cast<uint8_t>(payload.size()));
        for (const uint8_t byte : payload) {
            hal_.transfer(byte);
        }
        hal_.setCs(true);

        strobe(Command::EnterTx);

        uint32_t timeout = 50000;
        while (!hal_.getIrq() && --timeout > 0) hal_.delayUs(10);
        while (hal_.getIrq() && --timeout > 0) hal_.delayUs(10);

        strobe(Command::EnterIdle);
        return (timeout > 0);
    }

    std::optional<Packet> receive() noexcept {
        const uint8_t rxStatus = readRegister(Register::RxBytes);

        // Перевірка переповнення FIFO (біт 7)
        if ((rxStatus & 0x80U) != 0U) {
            strobe(Command::EnterIdle);
            strobe(Command::FlushRx);
            strobe(Command::EnterRx);
            return std::nullopt;
        }

        if ((rxStatus & 0x7FU) == 0U) {
            return std::nullopt;
        }

        hal_.setCs(false);
        hal_.transfer(static_cast<uint8_t>(Register::Fifo) | 0xC0U); // Burst Read
        const uint8_t pktLen = hal_.transfer(0x00);

        if (pktLen > 63) {
            hal_.setCs(true);
            strobe(Command::FlushRx);
            return std::nullopt;
        }

        Packet pkt{};
        pkt.length = pktLen;
        for (size_t i = 0; i < pktLen; ++i) {
            pkt.data[i] = hal_.transfer(0x00);
        }

        const uint8_t rawRssi = hal_.transfer(0x00);
        const uint8_t lqiCrc  = hal_.transfer(0x00);
        hal_.setCs(true);

        // Перевірка CRC OK (біт 7)
        if ((lqiCrc & 0x80U) == 0U) {
            return std::nullopt;
        }

        if (rawRssi >= 128U) {
            pkt.rssiDbm = static_cast<int8_t>((static_cast<int16_t>(rawRssi) - 256) / 2) - 74;
        } else {
            pkt.rssiDbm = static_cast<int8_t>(rawRssi / 2) - 74;
        }

        return pkt;
    }

    void startListening() noexcept {
        strobe(Command::EnterRx);
    }

private:
    void writeRegister(Register reg, uint8_t val) noexcept {
        hal_.setCs(false);
        hal_.transfer(static_cast<uint8_t>(reg) & 0x3FU);
        hal_.transfer(val);
        hal_.setCs(true);
    }

    uint8_t readRegister(Register reg) noexcept {
        hal_.setCs(false);
        hal_.transfer(static_cast<uint8_t>(reg) | 0x80U);
        const uint8_t val = hal_.transfer(0x00);
        hal_.setCs(true);
        return val;
    }

    uint8_t strobe(Command cmd) noexcept {
        hal_.setCs(false);
        const uint8_t status = hal_.transfer(static_cast<uint8_t>(cmd));
        hal_.setCs(true);
        return status;
    }

    SpiHal& hal_;
};

} // namespace RadioDriver
