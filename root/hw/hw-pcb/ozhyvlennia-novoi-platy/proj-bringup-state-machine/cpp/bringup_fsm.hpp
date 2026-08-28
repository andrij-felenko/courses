// ============================================================================
// Bringup Diagnostic State Machine (Modern C++20 Zero-Allocation Implementation)
// File: bringup_fsm.hpp
// ============================================================================

#pragma once

#include <cstdint>
#include <cstddef>
#include <concepts>
#include <expected>
#include <span>
#include <array>
#include <bit>
#include <string_view>
#include <format>

namespace bringup {

enum class State : uint8_t {
    Idle = 0,
    PowerRailCheck,
    NrstVerify,
    ClockMeasure,
    SwdDiscovery,
    RecoveryTriage,
    ReportTelemetry,
    CompleteSuccess,
    CompleteFail
};

enum class ErrorCode : uint8_t {
    None = 0,
    PowerVoltageOutOfSpec,
    PowerNonMonotonic,
    PowerRippleExcessive,
    NrstStuckLow,
    NrstTimeout,
    ClockAbsent,
    ClockPpmExcessive,
    SwdNoResponse,
    SwdParityError,
    SwdInvalidIdcode,
    CoreHaltFailed
};

struct Telemetry {
    uint32_t  vdd_mean_mv{0};
    uint32_t  vdd_ripple_pp_mv{0};
    uint32_t  vdd_slew_rate_mv_per_us{0};
    bool      vdd_is_monotonic{false};
    uint32_t  nrst_release_delay_us{0};
    uint32_t  nrst_steady_state_mv{0};
    uint32_t  clock_freq_hz{0};
    int32_t   clock_ppm_error{0};
    uint32_t  swd_dpidr{0};
    uint8_t   swd_ack_status{0};
    bool      is_recovered{false};
    ErrorCode last_error{ErrorCode::None};
};

template <typename T>
concept BringupHal = requires(T hal, bool level, uint16_t* buf, std::size_t count, uint32_t val) {
    { hal.power_enable(level) } -> std::same_as<void>;
    { hal.start_adc_sampling(buf, count) } -> std::same_as<void>;
    { hal.is_adc_sampling_complete() } -> std::same_as<bool>;
    { hal.get_nrst_mv() } -> std::same_as<uint32_t>;
    { hal.drive_nrst(level) } -> std::same_as<void>;
    { hal.drive_boot0(level) } -> std::same_as<void>;
    { hal.measure_hse_freq_hz(val) } -> std::same_as<uint32_t>;
    { hal.swd_set_clk(level) } -> std::same_as<void>;
    { hal.swd_set_dio(level) } -> std::same_as<void>;
    { hal.swd_get_dio() } -> std::same_as<bool>;
    { hal.swd_set_dio_out(level) } -> std::same_as<void>;
    { hal.delay_us(val) } -> std::same_as<void>;
    { hal.get_system_time_ms() } -> std::same_as<uint32_t>;
};

template <BringupHal Hal, std::size_t BufferSize = 1024>
class BringupEngine {
public:
    explicit constexpr BringupEngine(Hal& hal) noexcept : hal_{hal} {}

    void start() noexcept {
        current_state_ = State::PowerRailCheck;
        start_time_ms_ = hal_.get_system_time_ms();
        retry_count_ = 0;
        telemetry_ = {};
        hal_.power_enable(true);
        hal_.start_adc_sampling(adc_buffer_.data(), adc_buffer_.size());
    }

    void process() noexcept {
        const uint32_t now = hal_.get_system_time_ms();

        switch (current_state_) {
        case State::Idle:
            break;

        case State::PowerRailCheck:
            process_power_rail(now);
            break;

        case State::NrstVerify:
            process_nrst(now);
            break;

        case State::ClockMeasure:
            process_clock();
            break;

        case State::SwdDiscovery:
            process_swd(now);
            break;

        case State::RecoveryTriage:
            process_recovery();
            break;

        case State::ReportTelemetry:
            current_state_ = (telemetry_.last_error == ErrorCode::None || telemetry_.is_recovered)
                             ? State::CompleteSuccess
                             : State::CompleteFail;
            break;

        case State::CompleteSuccess:
        case State::CompleteFail:
            break;
        }
    }

    [[nodiscard]] constexpr State current_state() const noexcept { return current_state_; }
    [[nodiscard]] const Telemetry& telemetry() const noexcept { return telemetry_; }

private:
    void process_power_rail(uint32_t now) noexcept {
        if (!hal_.is_adc_sampling_complete()) {
            if (now - start_time_ms_ > 100) {
                telemetry_.last_error = ErrorCode::PowerVoltageOutOfSpec;
                current_state_ = State::RecoveryTriage;
            }
            return;
        }

        std::size_t v_10_idx = 0, v_90_idx = 0;
        uint32_t sum = 0, min_val = 0xFFFF, max_val = 0;
        bool monotonic = true;
        constexpr uint16_t v_10_thresh = 330;
        constexpr uint16_t v_90_thresh = 2970;

        for (std::size_t i = 0; i < adc_buffer_.size(); ++i) {
            const uint16_t v = adc_buffer_[i];
            if (v_10_idx == 0 && v >= v_10_thresh) v_10_idx = i;
            if (v_90_idx == 0 && v >= v_90_thresh) v_90_idx = i;

            if (i > 0 && v_10_idx > 0 && v_90_idx == 0) {
                if (static_cast<int32_t>(v) - static_cast<int32_t>(adc_buffer_[i - 1]) < -30) {
                    monotonic = false;
                }
            }

            if (i >= adc_buffer_.size() - 256) {
                sum += v;
                min_val = std::min<uint32_t>(min_val, v);
                max_val = std::max<uint32_t>(max_val, v);
            }
        }

        telemetry_.vdd_is_monotonic = monotonic;
        telemetry_.vdd_mean_mv = sum / 256;
        telemetry_.vdd_ripple_pp_mv = max_val - min_val;

        if (v_90_idx > v_10_idx) {
            telemetry_.vdd_slew_rate_mv_per_us = (v_90_thresh - v_10_thresh) / static_cast<uint32_t>(v_90_idx - v_10_idx);
        }

        if (telemetry_.vdd_mean_mv < 3150 || telemetry_.vdd_mean_mv > 3450) {
            telemetry_.last_error = ErrorCode::PowerVoltageOutOfSpec;
            current_state_ = State::RecoveryTriage;
            return;
        }

        if (!monotonic) {
            telemetry_.last_error = ErrorCode::PowerNonMonotonic;
            current_state_ = State::RecoveryTriage;
            return;
        }

        if (telemetry_.vdd_ripple_pp_mv > 35) {
            telemetry_.last_error = ErrorCode::PowerRippleExcessive;
            current_state_ = State::RecoveryTriage;
            return;
        }

        current_state_ = State::NrstVerify;
        start_time_ms_ = now;
    }

    void process_nrst(uint32_t now) noexcept {
        const uint32_t nrst_mv = hal_.get_nrst_mv();
        telemetry_.nrst_steady_state_mv = nrst_mv;

        if (nrst_mv > 2640) {
            telemetry_.nrst_release_delay_us = (now - start_time_ms_) * 1000;
            current_state_ = State::ClockMeasure;
            return;
        }

        if (now - start_time_ms_ > 150) {
            telemetry_.last_error = (nrst_mv < 500) ? ErrorCode::NrstStuckLow : ErrorCode::NrstTimeout;
            current_state_ = State::RecoveryTriage;
        }
    }

    void process_clock() noexcept {
        const uint32_t freq = hal_.measure_hse_freq_hz(100);
        telemetry_.clock_freq_hz = freq;

        if (freq == 0) {
            telemetry_.last_error = ErrorCode::ClockAbsent;
            current_state_ = State::RecoveryTriage;
            return;
        }

        constexpr uint32_t target_freq = 25000000;
        const int64_t diff = static_cast<int64_t>(freq) - static_cast<int64_t>(target_freq);
        const int32_t ppm = static_cast<int32_t>((diff * 1000000) / target_freq);
        telemetry_.clock_ppm_error = ppm;

        if (ppm > 200 || ppm < -200) {
            telemetry_.last_error = ErrorCode::ClockPpmExcessive;
            current_state_ = State::RecoveryTriage;
            return;
        }

        current_state_ = State::SwdDiscovery;
    }

    void process_swd(uint32_t now) noexcept {
        swd_line_reset();
        swd_send_switch_sequence();
        swd_line_reset();

        auto res = swd_read_dp(0x00);
        if (!res.has_value()) {
            telemetry_.last_error = res.error();
            current_state_ = State::RecoveryTriage;
            return;
        }

        telemetry_.swd_dpidr = *res;
        swd_write_dp(0x04, 0x50000000);
        current_state_ = State::ReportTelemetry;
    }

    void process_recovery() noexcept {
        telemetry_.is_recovered = true;
        if (retry_count_ >= 3) {
            current_state_ = State::ReportTelemetry;
            return;
        }
        retry_count_++;

        hal_.drive_nrst(true);
        hal_.delay_us(5000);

        swd_line_reset();
        swd_send_switch_sequence();
        swd_line_reset();

        auto res = swd_read_dp(0x00);
        if (res.has_value()) {
            telemetry_.swd_dpidr = *res;
            swd_write_dp(0x04, 0x50000000);
            hal_.drive_nrst(false);
            current_state_ = State::ReportTelemetry;
            return;
        }

        hal_.drive_boot0(true);
        hal_.drive_nrst(true);
        hal_.delay_us(10000);
        hal_.drive_nrst(false);
        hal_.delay_us(20000);

        current_state_ = State::SwdDiscovery;
    }

    void swd_clk_pulse() noexcept {
        hal_.swd_set_clk(false);
        hal_.delay_us(1);
        hal_.swd_set_clk(true);
        hal_.delay_us(1);
    }

    void swd_line_reset() noexcept {
        hal_.swd_set_dio_out(true);
        hal_.swd_set_dio(true);
        for (std::size_t i = 0; i < 56; ++i) swd_clk_pulse();
    }

    void swd_send_switch_sequence() noexcept {
        constexpr uint16_t seq = 0xE79E;
        hal_.swd_set_dio_out(true);
        for (std::size_t i = 0; i < 16; ++i) {
            hal_.swd_set_dio(((seq >> i) & 1) != 0);
            swd_clk_pulse();
        }
    }

    [[nodiscard]] std::expected<uint32_t, ErrorCode> swd_read_dp(uint8_t addr_reg) noexcept {
        uint8_t req = 0x81 | static_cast<uint8_t>((addr_reg & 0x0C) << 1);
        uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
        req |= static_cast<uint8_t>(parity << 5);

        hal_.swd_set_dio_out(true);
        for (std::size_t i = 0; i < 8; ++i) {
            hal_.swd_set_dio(((req >> i) & 1) != 0);
            swd_clk_pulse();
        }

        hal_.swd_set_dio_out(false);
        swd_clk_pulse();

        uint8_t ack = 0;
        for (std::size_t i = 0; i < 3; ++i) {
            hal_.swd_set_clk(false);
            hal_.delay_us(1);
            if (hal_.swd_get_dio()) ack |= static_cast<uint8_t>(1 << i);
            hal_.swd_set_clk(true);
            hal_.delay_us(1);
        }
        telemetry_.swd_ack_status = ack;

        if (ack != 0x01) return std::unexpected(ErrorCode::SwdNoResponse);

        uint32_t data = 0;
        for (std::size_t i = 0; i < 32; ++i) {
            hal_.swd_set_clk(false);
            hal_.delay_us(1);
            if (hal_.swd_get_dio()) data |= (1UL << i);
            hal_.swd_set_clk(true);
            hal_.delay_us(1);
        }

        hal_.swd_set_clk(false);
        hal_.delay_us(1);
        const bool rcv_par = hal_.swd_get_dio();
        hal_.swd_set_clk(true);
        hal_.delay_us(1);

        hal_.swd_set_dio_out(true);
        hal_.swd_set_dio(false);
        for (std::size_t i = 0; i < 4; ++i) swd_clk_pulse();

        const bool calc_par = (std::popcount(data) % 2) != 0;
        if (rcv_par != calc_par) return std::unexpected(ErrorCode::SwdParityError);

        return data;
    }

    bool swd_write_dp(uint8_t addr_reg, uint32_t val) noexcept {
        uint8_t req = 0x81 | static_cast<uint8_t>((addr_reg & 0x0C) << 1);
        uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
        req |= static_cast<uint8_t>(parity << 5);

        hal_.swd_set_dio_out(true);
        for (std::size_t i = 0; i < 8; ++i) {
            hal_.swd_set_dio(((req >> i) & 1) != 0);
            swd_clk_pulse();
        }

        hal_.swd_set_dio_out(false);
        swd_clk_pulse();

        uint8_t ack = 0;
        for (std::size_t i = 0; i < 3; ++i) {
            hal_.swd_set_clk(false);
            hal_.delay_us(1);
            if (hal_.swd_get_dio()) ack |= static_cast<uint8_t>(1 << i);
            hal_.swd_set_clk(true);
            hal_.delay_us(1);
        }

        if (ack != 0x01) return false;

        swd_clock_pulse(hal);
        hal_.swd_set_dio_out(true);

        for (std::size_t i = 0; i < 32; ++i) {
            hal_.swd_set_dio(((val >> i) & 1) != 0);
            swd_clk_pulse();
        }

        const bool calc_par = (std::popcount(val) % 2) != 0;
        hal_.swd_set_dio(calc_par);
        swd_clock_pulse(hal);

        hal_.swd_set_dio(false);
        for (std::size_t i = 0; i < 4; ++i) swd_clk_pulse();

        return true;
    }

    Hal& hal_;
    State current_state_{State::Idle};
    Telemetry telemetry_{};
    std::array<uint16_t, BufferSize> adc_buffer_{};
    uint32_t start_time_ms_{0};
    uint8_t retry_count_{0};
};

} // namespace bringup
