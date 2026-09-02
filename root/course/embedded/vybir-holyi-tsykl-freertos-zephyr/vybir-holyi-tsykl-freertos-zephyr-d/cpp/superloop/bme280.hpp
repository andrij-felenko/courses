#pragma once

// BME280 у forced-режимі. Замість коду помилки й errno — std::expected,
// замість «дані ще не готові» окремим прапорцем — std::optional усередині.
#include "board.hpp"

#include <array>
#include <cstdint>
#include <expected>
#include <optional>

namespace app {

class Bme280 {
public:
    struct Sample {
        board::ms stamp{};
        std::int32_t centi_celsius{0};
    };

    enum class Error { WrongChip, Bus, Stuck, NoSample };

    explicit Bme280(board::I2cBus &bus) noexcept : bus_{bus} {}

    std::expected<void, Error> begin() noexcept
    {
        std::array<std::uint8_t, 1> id{};
        std::array<std::uint8_t, 6> calib{};

        if (!bus_.read_regs(kRegId, id)) { return std::unexpected{Error::Bus}; }
        if (id[0] != kChipId) { return std::unexpected{Error::WrongChip}; }
        if (!bus_.read_regs(kRegCalibT, calib)) { return std::unexpected{Error::Bus}; }

        t1_ = static_cast<std::uint16_t>(calib[1] << 8 | calib[0]);
        t2_ = static_cast<std::int16_t>(calib[3] << 8 | calib[2]);
        t3_ = static_cast<std::int16_t>(calib[5] << 8 | calib[4]);

        // Фільтр вимкнено: у forced-режимі він лише розмазує одиночні виміри.
        if (!bus_.write_reg(kRegConfig, 0x00U)) { return std::unexpected{Error::Bus}; }
        state_ = State::Idle;
        return {};
    }

    void start(board::ms now) noexcept
    {
        if (state_ != State::Idle) {
            return; // попередній вимір ще не забрали
        }
        if (!bus_.write_reg(kRegCtrlMeas, kForcedX1)) {
            fault(now);
            return;
        }
        started_ = now;
        state_ = State::Measuring;
    }

    // Один крок автомата. nullopt — ще не готово; unexpected — датчик відпав.
    std::expected<std::optional<Sample>, Error> poll(board::ms now) noexcept
    {
        switch (state_) {
        case State::Idle:
            return std::optional<Sample>{};

        case State::Measuring: {
            if (now - started_ < kConversion) {
                return std::optional<Sample>{}; // ще рано — виходимо без очікування
            }
            std::array<std::uint8_t, 1> status{};
            if (!bus_.read_regs(kRegStatus, status)) {
                fault(now);
                return std::unexpected{Error::Bus};
            }
            if ((status[0] & 0x08U) != 0U) {
                if (now - started_ > kStuckAfter) {
                    fault(now);
                    return std::unexpected{Error::Stuck};
                }
                return std::optional<Sample>{};
            }
            state_ = State::Reading;
            return std::optional<Sample>{};
        }

        case State::Reading: {
            std::array<std::uint8_t, 3> raw{};
            if (!bus_.read_regs(kRegTempMsb, raw)) {
                fault(now);
                return std::unexpected{Error::Bus};
            }
            const std::int32_t adc = (std::int32_t{raw[0]} << 12) |
                                     (std::int32_t{raw[1]} << 4) |
                                     (std::int32_t{raw[2]} >> 4);
            if (adc == 0x80000) {
                fault(now);
                return std::unexpected{Error::NoSample};
            }
            state_ = State::Idle;
            return std::optional<Sample>{Sample{now, compensate(adc)}};
        }

        case State::Fault:
        default:
            if (now - started_ < kRetryPause) {
                return std::optional<Sample>{};
            }
            if (begin()) {
                state_ = State::Idle;
            } else {
                started_ = now;
            }
            return std::optional<Sample>{};
        }
    }

    [[nodiscard]] std::uint32_t errors() const noexcept { return errors_; }

private:
    enum class State { Idle, Measuring, Reading, Fault };

    static constexpr std::uint8_t kRegCalibT = 0x88U;
    static constexpr std::uint8_t kRegId = 0xD0U;
    static constexpr std::uint8_t kRegStatus = 0xF3U;
    static constexpr std::uint8_t kRegCtrlMeas = 0xF4U;
    static constexpr std::uint8_t kRegConfig = 0xF5U;
    static constexpr std::uint8_t kRegTempMsb = 0xFAU;
    static constexpr std::uint8_t kChipId = 0x60U;
    static constexpr std::uint8_t kForcedX1 = 0x21U;
    static constexpr board::ms kConversion{5};   // 1.25 + 2.3 мс за datasheet 9.1
    static constexpr board::ms kStuckAfter{50};
    static constexpr board::ms kRetryPause{1000};

    void fault(board::ms now) noexcept
    {
        ++errors_;
        state_ = State::Fault;
        started_ = now;
    }

    // Цілочисельна компенсація з datasheet, розділ 4.2.3.
    [[nodiscard]] std::int32_t compensate(std::int32_t adc) const noexcept
    {
        const std::int32_t var1 = (((adc >> 3) - (std::int32_t{t1_} << 1)) * std::int32_t{t2_}) >> 11;
        const std::int32_t d = (adc >> 4) - std::int32_t{t1_};
        const std::int32_t var2 = (((d * d) >> 12) * std::int32_t{t3_}) >> 14;
        return ((var1 + var2) * 5 + 128) >> 8;
    }

    board::I2cBus &bus_;
    State state_{State::Idle};
    board::ms started_{};
    std::uint32_t errors_{0};
    std::uint16_t t1_{0};
    std::int16_t t2_{0};
    std::int16_t t3_{0};
};

} // namespace app
