#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <functional>

namespace rtc {

struct DateTime {
    std::uint16_t year{2026};
    std::uint8_t  month{1};
    std::uint8_t  day{1};
    std::uint8_t  day_of_week{1};
    std::uint8_t  hours{0};
    std::uint8_t  minutes{0};
    std::uint8_t  seconds{0};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        if (seconds > 59 || minutes > 59 || hours > 23) return false;
        if (day == 0 || day > 31 || month == 0 || month > 12) return false;
        return true;
    }
};

enum class Error : std::uint8_t {
    BusFailure,
    OscillatorStopped,
    InvalidParameter,
    ProtocolError
};

class RtcDriver {
public:
    using ReadFn  = std::function<bool(std::uint8_t dev_addr, std::uint8_t reg_addr, std::span<std::uint8_t> data)>;
    using WriteFn = std::function<bool(std::uint8_t dev_addr, std::uint8_t reg_addr, std::span<const std::uint8_t> data)>;

    static constexpr std::uint8_t DefaultAddress   = 0x68;
    static constexpr std::uint8_t RegSeconds       = 0x00;
    static constexpr std::uint8_t RegControl       = 0x0E;
    static constexpr std::uint8_t RegStatus        = 0x0F;
    static constexpr std::uint8_t RegTempMsb       = 0x11;
    static constexpr std::uint8_t RegAlarm1Sec     = 0x07;

    static constexpr std::uint8_t StatusOsfBit     = 1 << 7;
    static constexpr std::uint8_t CtrlIntcnBit     = 1 << 2;
    static constexpr std::uint8_t CtrlA1ieBit      = 1 << 0;

    explicit RtcDriver(ReadFn r_fn, WriteFn w_fn, std::uint8_t addr = DefaultAddress) noexcept
        : read_(std::move(r_fn)), write_(std::move(w_fn)), addr_(addr) {}

    [[nodiscard]] std::expected<void, Error> init() const noexcept {
        if (!read_ || !write_) return std::unexpected(Error::ProtocolError);

        std::uint8_t status = 0;
        if (!read_(addr_, RegStatus, std::span<std::uint8_t>(&status, 1))) {
            return std::unexpected(Error::BusFailure);
        }

        if (status & StatusOsfBit) {
            return std::unexpected(Error::OscillatorStopped);
        }
        return {};
    }

    [[nodiscard]] std::expected<DateTime, Error> get_datetime() const noexcept {
        std::uint8_t buf[7]{};
        if (!read_(addr_, RegSeconds, std::span<std::uint8_t>(buf, 7))) {
            return std::unexpected(Error::BusFailure);
        }

        DateTime dt;
        dt.seconds     = bcd_to_bin(buf[0] & 0x7F);
        dt.minutes     = bcd_to_bin(buf[1] & 0x7F);
        dt.hours       = bcd_to_bin(buf[2] & 0x3F);
        dt.day_of_week = buf[3] & 0x07;
        dt.day         = bcd_to_bin(buf[4] & 0x3F);
        dt.month       = bcd_to_bin(buf[5] & 0x1F);
        
        const std::uint16_t century = (buf[5] & 0x80) ? 2100 : 2000;
        dt.year        = century + bcd_to_bin(buf[6]);

        return dt;
    }

    [[nodiscard]] std::expected<void, Error> set_datetime(const DateTime& dt) const noexcept {
        if (!dt.is_valid()) return std::unexpected(Error::InvalidParameter);

        std::uint8_t buf[7]{};
        buf[0] = bin_to_bcd(dt.seconds);
        buf[1] = bin_to_bcd(dt.minutes);
        buf[2] = bin_to_bcd(dt.hours);
        buf[3] = dt.day_of_week & 0x07;
        buf[4] = bin_to_bcd(dt.day);
        
        const std::uint8_t century_flag = (dt.year >= 2100) ? 0x80 : 0x00;
        buf[5] = bin_to_bcd(dt.month) | century_flag;
        buf[6] = bin_to_bcd(static_cast<std::uint8_t>(dt.year % 100));

        if (!write_(addr_, RegSeconds, std::span<const std::uint8_t>(buf, 7))) {
            return std::unexpected(Error::BusFailure);
        }

        /* Очищуємо прапорець зупинки кварцу */
        std::uint8_t status = 0;
        if (read_(addr_, RegStatus, std::span<std::uint8_t>(&status, 1))) {
            status &= static_cast<std::uint8_t>(~StatusOsfBit);
            write_(addr_, RegStatus, std::span<const std::uint8_t>(&status, 1));
        }
        return {};
    }

    [[nodiscard]] std::expected<float, Error> get_temperature() const noexcept {
        std::uint8_t raw[2]{};
        if (!read_(addr_, RegTempMsb, std::span<std::uint8_t>(raw, 2))) {
            return std::unexpected(Error::BusFailure);
        }

        const auto temp_msb = static_cast<std::int8_t>(raw[0]);
        const auto temp_lsb = static_cast<std::uint8_t>((raw[1] >> 6) & 0x03);

        return static_cast<float>(temp_msb) + (static_cast<float>(temp_lsb) * 0.25f);
    }

    [[nodiscard]] std::expected<void, Error> set_daily_alarm(std::uint8_t hours, std::uint8_t minutes, std::uint8_t seconds) const noexcept {
        if (hours > 23 || minutes > 59 || seconds > 59) {
            return std::unexpected(Error::InvalidParameter);
        }

        const std::uint8_t alarm_buf[4] = {
            bin_to_bcd(seconds),
            bin_to_bcd(minutes),
            bin_to_bcd(hours),
            0x80 /* A1M4 = 1: щоденне повторення */
        };

        if (!write_(addr_, RegAlarm1Sec, std::span<const std::uint8_t>(alarm_buf, 4))) {
            return std::unexpected(Error::BusFailure);
        }

        std::uint8_t ctrl = 0;
        if (!read_(addr_, RegControl, std::span<std::uint8_t>(&ctrl, 1))) {
            return std::unexpected(Error::BusFailure);
        }
        ctrl |= (CtrlIntcnBit | CtrlA1ieBit);
        if (!write_(addr_, RegControl, std::span<const std::uint8_t>(&ctrl, 1))) {
            return std::unexpected(Error::BusFailure);
        }
        return {};
    }

private:
    [[nodiscard]] static constexpr std::uint8_t bcd_to_bin(std::uint8_t bcd) noexcept {
        return static_cast<std::uint8_t>(((bcd >> 4) * 10) + (bcd & 0x0F));
    }

    [[nodiscard]] static constexpr std::uint8_t bin_to_bcd(std::uint8_t bin) noexcept {
        return static_cast<std::uint8_t>(((bin / 10) << 4) | (bin % 10));
    }

    ReadFn       read_;
    WriteFn      write_;
    std::uint8_t addr_;
};

} // namespace rtc
