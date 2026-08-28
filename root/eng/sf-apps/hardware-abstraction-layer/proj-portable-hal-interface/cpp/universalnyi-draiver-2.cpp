/* ========================================================================= */
/* Шаблонний драйвер SPI Flash W25Q128 на C++20                             */
/* ========================================================================= */

namespace storage {

template <hal::SpiMaster Spi, hal::GpioPin CsPin>
class W25qFlash {
public:
    static constexpr uint8_t CmdWriteEnable  = 0x06;
    static constexpr uint8_t CmdReadStatus1  = 0x05;
    static constexpr uint8_t CmdReadData     = 0x03;
    static constexpr uint8_t CmdPageProgram  = 0x02;
    static constexpr uint8_t CmdJedecId      = 0x9F;
    static constexpr uint8_t StatusBusyMask  = 0x01;
    static constexpr size_t  PageSize        = 256;

    W25qFlash(Spi& spi, CsPin cs) noexcept : spi_(spi), cs_(cs) {}

    hal::Status init() noexcept {
        cs_.set_level(hal::PinLevel::High);

        const std::array<uint8_t, 1> cmd{CmdJedecId};
        std::array<uint8_t, 3> id{};

        cs_.set_level(hal::PinLevel::Low);
        auto s = spi_.write(cmd, 100);
        if (hal::is_ok(s)) {
            s = spi_.read(id, 100);
        }
        cs_.set_level(hal::PinLevel::High);

        if (!hal::is_ok(s)) return s;
        if (id[0] != 0xEF) return hal::Status::Error;

        return hal::Status::Ok;
    }

    hal::Status read(uint32_t addr, std::span<uint8_t> buf) noexcept {
        if (buf.empty()) return hal::Status::InvalidArg;

        auto s = wait_busy(1000);
        if (!hal::is_ok(s)) return s;

        const std::array<uint8_t, 4> cmd_buf{
            CmdReadData,
            static_cast<uint8_t>((addr >> 16) & 0xFF),
            static_cast<uint8_t>((addr >> 8) & 0xFF),
            static_cast<uint8_t>(addr & 0xFF)
        };

        cs_.set_level(hal::PinLevel::Low);
        s = spi_.write(cmd_buf, 100);
        if (hal::is_ok(s)) {
            s = spi_.read(buf, 1000);
        }
        cs_.set_level(hal::PinLevel::High);
        return s;
    }

    hal::Status write_page(uint32_t addr, std::span<const uint8_t> data) noexcept {
        if (data.empty() || data.size() > PageSize) return hal::Status::InvalidArg;

        const std::array<uint8_t, 1> cmd_we{CmdWriteEnable};
        cs_.set_level(hal::PinLevel::Low);
        auto s = spi_.write(cmd_we, 100);
        cs_.set_level(hal::PinLevel::High);
        if (!hal::is_ok(s)) return s;

        const std::array<uint8_t, 4> cmd_buf{
            CmdPageProgram,
            static_cast<uint8_t>((addr >> 16) & 0xFF),
            static_cast<uint8_t>((addr >> 8) & 0xFF),
            static_cast<uint8_t>(addr & 0xFF)
        };

        cs_.set_level(hal::PinLevel::Low);
        s = spi_.write(cmd_buf, 100);
        if (hal::is_ok(s)) {
            s = spi_.write(data, 500);
        }
        cs_.set_level(hal::PinLevel::High);
        if (!hal::is_ok(s)) return s;

        return wait_busy(100);
    }

private:
    hal::Status wait_busy(uint32_t timeout_ms) noexcept {
        const std::array<uint8_t, 1> cmd{CmdReadStatus1};
        std::array<uint8_t, 1> status{0};

        for (uint32_t i = 0; i < timeout_ms; ++i) {
            cs_.set_level(hal::PinLevel::Low);
            spi_.write(cmd, 10);
            spi_.read(status, 10);
            cs_.set_level(hal::PinLevel::High);

            if (!(status[0] & StatusBusyMask)) {
                return hal::Status::Ok;
            }
        }
        return hal::Status::Timeout;
    }

    Spi& spi_;
    CsPin cs_;
};

} // namespace storage
