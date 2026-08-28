// Програмний ведучий I2C (Bit-Banging) з точним дотриманням UM10204 (C++20)
#pragma once
#include <cstdint>
#include <chrono>
#include <span>
#include <expected>
#include <concepts>

namespace i2c::bitbang {

using namespace std::chrono_literals;

enum class Error : uint8_t {
    Timeout,
    NackReceived,
    BusBusy,
    ArbitrationLost
};

struct TimingConfig {
    std::chrono::nanoseconds t_low{1300ns};
    std::chrono::nanoseconds t_high{600ns};
    std::chrono::nanoseconds t_su_dat{100ns};
    std::chrono::nanoseconds t_hd_dat{300ns};
    std::chrono::nanoseconds t_hd_sta{600ns};
    std::chrono::nanoseconds t_su_sta{600ns};
    std::chrono::nanoseconds t_su_sto{600ns};
    std::chrono::nanoseconds t_buf{1300ns};
    std::chrono::milliseconds timeout{100ms};
};

template <typename GpioPolicy, typename TimerPolicy>
class SoftwareI2cMaster {
public:
    explicit constexpr SoftwareI2cMaster(TimingConfig timing = TimingConfig{}) noexcept
        : timing_{timing} {}

    [[nodiscard]] std::expected<void, Error> start() noexcept {
        GpioPolicy::sda_hiz();
        if (auto res = wait_scl_high(); !res) return res;
        TimerPolicy::delay_ns(timing_.t_su_sta.count());

        GpioPolicy::sda_low();
        TimerPolicy::delay_ns(timing_.t_hd_sta.count());

        GpioPolicy::scl_low();
        TimerPolicy::delay_ns(timing_.t_low.count());
        return {};
    }

    [[nodiscard]] std::expected<void, Error> stop() noexcept {
        GpioPolicy::scl_low();
        GpioPolicy::sda_low();
        TimerPolicy::delay_ns(timing_.t_low.count());

        if (auto res = wait_scl_high(); !res) return res;
        TimerPolicy::delay_ns(timing_.t_su_sto.count());

        GpioPolicy::sda_hiz();
        TimerPolicy::delay_ns(timing_.t_buf.count());
        return {};
    }

    [[nodiscard]] std::expected<void, Error> write_byte(uint8_t byte) noexcept {
        for (int8_t i = 7; i >= 0; --i) {
            if ((byte >> i) & 1U) {
                GpioPolicy::sda_hiz();
            } else {
                GpioPolicy::sda_low();
            }
            TimerPolicy::delay_ns(timing_.t_su_dat.count());

            if (auto res = wait_scl_high(); !res) return res;
            TimerPolicy::delay_ns(timing_.t_high.count());

            GpioPolicy::scl_low();
            TimerPolicy::delay_ns(timing_.t_hd_dat.count());
        }

        // 9-й такт: перевірка квитанції ACK/NACK
        GpioPolicy::sda_hiz();
        TimerPolicy::delay_ns(timing_.t_su_dat.count());

        if (auto res = wait_scl_high(); !res) return res;
        TimerPolicy::delay_ns(timing_.t_high.count());

        const bool nack = GpioPolicy::sda_read();
        GpioPolicy::scl_low();
        TimerPolicy::delay_ns(timing_.t_low.count());

        if (nack) {
            return std::unexpected(Error::NackReceived);
        }
        return {};
    }

    [[nodiscard]] std::expected<uint8_t, Error> read_byte(bool send_ack) noexcept {
        uint8_t byte = 0;
        GpioPolicy::sda_hiz();

        for (int8_t i = 7; i >= 0; --i) {
            if (auto res = wait_scl_high(); !res) return std::unexpected(res.error());
            TimerPolicy::delay_ns(timing_.t_high.count());

            if (GpioPolicy::sda_read()) {
                byte |= static_cast<uint8_t>(1U << i);
            }

            GpioPolicy::scl_low();
            TimerPolicy::delay_ns(timing_.t_low.count());
        }

        // 9-й такт: стробування квитанції ведучим
        if (send_ack) {
            GpioPolicy::sda_low();
        } else {
            GpioPolicy::sda_hiz();
        }
        TimerPolicy::delay_ns(timing_.t_su_dat.count());

        if (auto res = wait_scl_high(); !res) return std::unexpected(res.error());
        TimerPolicy::delay_ns(timing_.t_high.count());

        GpioPolicy::scl_low();
        GpioPolicy::sda_hiz();
        TimerPolicy::delay_ns(timing_.t_low.count());

        return byte;
    }

    [[nodiscard]] std::expected<void, Error> write_transaction(
        uint8_t device_address, std::span<const uint8_t> buffer) noexcept {
        if (auto res = start(); !res) return res;

        // Передача адреси веденого зі знятим бітом R/W (0 = Write)
        const uint8_t addr_byte = static_cast<uint8_t>(device_address << 1U);
        if (auto res = write_byte(addr_byte); !res) {
            (void)stop();
            return res;
        }

        for (const auto val : buffer) {
            if (auto res = write_byte(val); !res) {
                (void)stop();
                return res;
            }
        }

        return stop();
    }

private:
    [[nodiscard]] std::expected<void, Error> wait_scl_high() noexcept {
        GpioPolicy::scl_hiz();
        const auto start_tick = TimerPolicy::get_ticks();

        while (!GpioPolicy::scl_read()) {
            if (TimerPolicy::ticks_to_ms(TimerPolicy::get_ticks() - start_tick) >= timing_.timeout.count()) {
                return std::unexpected(Error::Timeout);
            }
        }
        return {};
    }

    TimingConfig timing_;
};

} // namespace i2c::bitbang
