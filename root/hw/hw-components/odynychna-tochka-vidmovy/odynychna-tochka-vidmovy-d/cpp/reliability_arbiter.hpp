/* ============================================================================
 * ФАЙЛ: reliability_arbiter.hpp (C++20)
 * Ідіоматична об'єктно-орієнтована реалізація мажоритарного арбітражу та
 * відновлення шинних інтерфейсів з використанням RAII, концептів та std::expected
 * ============================================================================ */

#pragma once

#include <cstdint>
#include <concepts>
#include <array>
#include <span>
#include <expected>
#include <cmath>
#include <algorithm>

namespace reliability {

enum class BusError : uint8_t {
    SdaStuckLow,
    SclStuckLow,
    InvalidConfiguration
};

enum class ChannelState : uint8_t {
    Healthy = 0,
    Discrepancy,
    DisabledFaulty
};

/* Концепт для апаратного рівня доступу до GPIO */
template <typename T>
concept I2cGpioDriver = requires(T d, bool level, uint32_t us) {
    { d.set_scl_output() } -> std::same_as<void>;
    { d.set_sda_input() }  -> std::same_as<void>;
    { d.set_sda_output() } -> std::same_as<void>;
    { d.write_scl(level) } -> std::same_as<void>;
    { d.write_sda(level) } -> std::same_as<void>;
    { d.read_sda() }       -> std::same_as<bool>;
    { d.read_scl() }       -> std::same_as<bool>;
    { d.delay_us(us) }     -> std::same_as<void>;
};

/* Клас відновлення шини I2C */
template <I2cGpioDriver Driver>
class I2cBusRecoveryEngine {
public:
    explicit I2cBusRecoveryEngine(Driver& driver) noexcept : driver_(driver) {}

    [[nodiscard]] std::expected<void, BusError> recover() noexcept {
        driver_.set_sda_input();
        driver_.set_scl_output();
        driver_.write_scl(true);
        driver_.delay_us(5);

        if (!driver_.read_scl()) {
            return std::unexpected(BusError::SclStuckLow);
        }

        if (driver_.read_sda()) {
            return {}; /* Шина вже вільна */
        }

        bool freed = false;
        for (std::size_t i = 0; i < 9; ++i) {
            driver_.write_scl(false);
            driver_.delay_us(5);
            driver_.write_scl(true);
            driver_.delay_us(5);

            if (driver_.read_sda()) {
                freed = true;
                break;
            }
        }

        if (!freed) {
            return std::unexpected(BusError::SdaStuckLow);
        }

        /* Генерація протокольної умови STOP */
        driver_.set_sda_output();
        driver_.write_sda(false);
        driver_.delay_us(5);
        driver_.write_scl(true);
        driver_.delay_us(5);
        driver_.write_sda(true);
        driver_.delay_us(5);
        driver_.set_sda_input();

        if (!driver_.read_sda()) {
            return std::unexpected(BusError::SdaStuckLow);
        }

        return {};
    }

private:
    Driver& driver_;
};

/* Результат голосування 2oo3 */
template <typename T>
struct VoteResult {
    T value{};
    bool is_valid{false};
    std::array<ChannelState, 3> channel_states{ChannelState::Healthy, ChannelState::Healthy, ChannelState::Healthy};
    std::size_t active_channels{3};
    int failed_channel_index{-1};
};

/* Мажоритарний арбітр 2oo3 для довільних числових типів */
template <std::floating_point T>
class MajorityVoter2oo3 {
public:
    constexpr MajorityVoter2oo3(T tolerance, uint32_t fault_limit) noexcept
        : tolerance_(tolerance), fault_limit_(fault_limit) {}

    [[nodiscard]] VoteResult<T> vote(T ch_a, T ch_b, T ch_c) noexcept {
        VoteResult<T> result;
        result.is_valid = true;

        const std::array<T, 3> samples = {ch_a, ch_b, ch_c};

        for (std::size_t i = 0; i < 3; ++i) {
            if (disabled_[i]) {
                result.channel_states[i] = ChannelState::DisabledFaulty;
                result.active_channels--;
            }
        }

        const bool match_ab = std::abs(samples[0] - samples[1]) <= tolerance_;
        const bool match_bc = std::abs(samples[1] - samples[2]) <= tolerance_;
        const bool match_ac = std::abs(samples[0] - samples[2]) <= tolerance_;

        if (match_ab && match_bc) {
            result.value = (samples[0] + samples[1] + samples[2]) / static_cast<T>(3);
        } else if (match_ab) {
            result.value = (samples[0] + samples[1]) / static_cast<T>(2);
            flag_discrepancy(result, 2);
        } else if (match_bc) {
            result.value = (samples[1] + samples[2]) / static_cast<T>(2);
            flag_discrepancy(result, 0);
        } else if (match_ac) {
            result.value = (samples[0] + samples[2]) / static_cast<T>(2);
            flag_discrepancy(result, 1);
        } else {
            /* Повний збій системи — жодна пара не узгоджується */
            result.value = samples[0];
            result.is_valid = false;
            for (std::size_t i = 0; i < 3; ++i) {
                result.channel_states[i] = ChannelState::DisabledFaulty;
                fault_counts_[i]++;
            }
        }

        /* Автоматична ізоляція каналів, що перевищили ліміт дефектів */
        for (std::size_t i = 0; i < 3; ++i) {
            if (fault_counts_[i] >= fault_limit_) {
                disabled_[i] = true;
                result.channel_states[i] = ChannelState::DisabledFaulty;
            }
        }

        return result;
    }

    void reset_fault_counters() noexcept {
        fault_counts_.fill(0);
        disabled_.fill(false);
    }

private:
    void flag_discrepancy(VoteResult<T>& res, std::size_t channel_idx) noexcept {
        res.channel_states[channel_idx] = ChannelState::Discrepancy;
        res.failed_channel_index = static_cast<int>(channel_idx);
        fault_counts_[channel_idx]++;
    }

    T tolerance_;
    uint32_t fault_limit_;
    std::array<uint32_t, 3> fault_counts_{0, 0, 0};
    std::array<bool, 3> disabled_{false, false, false};
};

} // namespace reliability
