/* link_monitor.hpp — Ідіоматичний C++20 модуль моніторингу якості лінка */
#pragma once

#include <cstdint>
#include <array>
#include <bit>
#include <chrono>

class LinkMonitor {
public:
    static constexpr std::size_t WindowBits = 100;
    static constexpr std::size_t WordsCount = (WindowBits + 31) / 32;

    enum class State : uint8_t {
        Excellent,  // LQ >= 90%, SNR високий, затримок нема
        Degraded,   // LQ 70..89% або SNR на межі
        Critical,   // LQ < 70% або вік даних > 200 мс (Stage 1 Failsafe)
        Lost        // Вік даних >= 1000 мс (Stage 2 Повний RTL / Land)
    };

    struct Metrics {
        int16_t rssi_dbm{0};
        int8_t  snr_db{0};
        uint8_t lq_percent{0};
        uint32_t packet_age_ms{0};
        State state{State::Lost};
    };

    constexpr explicit LinkMonitor(uint32_t packet_rate_hz, uint32_t now_ms = 0) noexcept
        : expected_interval_ms_(packet_rate_hz > 0 ? (1000 / packet_rate_hz) : 10),
          last_packet_time_ms_(now_ms),
          last_slot_time_ms_(now_ms) {
        window_.fill(0);
    }

    void on_packet_received(int16_t rssi, int8_t snr, uint32_t now_ms) noexcept {
        last_rssi_ = rssi;
        last_snr_ = snr;
        last_packet_time_ms_ = now_ms;
        last_slot_time_ms_ = now_ms;
        push_bit(true);
    }

    void on_slot_missed(uint32_t now_ms) noexcept {
        last_slot_time_ms_ = now_ms;
        push_bit(false);
    }

    void update_scheduler(uint32_t now_ms) noexcept {
        while (now_ms - last_slot_time_ms_ >= expected_interval_ms_) {
            last_slot_time_ms_ += expected_interval_ms_;
            push_bit(false);
        }
    }

    [[nodiscard]] Metrics get_metrics(uint32_t now_ms) const noexcept {
        Metrics m;
        m.rssi_dbm = last_rssi_;
        m.snr_db = last_snr_;
        m.lq_percent = calculate_lq();
        m.packet_age_ms = (now_ms >= last_packet_time_ms_) ? (now_ms - last_packet_time_ms_) : 0;

        if (m.packet_age_ms >= 1000) {
            m.state = State::Lost;
        } else if (m.packet_age_ms >= 200 || m.lq_percent < 70) {
            m.state = State::Critical;
        } else if (m.lq_percent < 90 || m.snr_db < 2) {
            m.state = State::Degraded;
        } else {
            m.state = State::Excellent;
        }

        return m;
    }

    void set_packet_rate(uint32_t packet_rate_hz) noexcept {
        if (packet_rate_hz > 0) {
            expected_interval_ms_ = 1000 / packet_rate_hz;
        }
    }

private:
    void push_bit(bool success) noexcept {
        const std::size_t word_idx = head_idx_ / 32;
        const std::size_t bit_idx  = head_idx_ % 32;

        const uint32_t mask = 1UL << bit_idx;
        if (success) {
            window_[word_idx] |= mask;
        } else {
            window_[word_idx] &= ~mask;
        }

        head_idx_ = (head_idx_ + 1) % WindowBits;
    }

    [[nodiscard]] uint8_t calculate_lq() const noexcept {
        uint32_t total_set = 0;
        for (std::size_t i = 0; i < 3; ++i) {
            total_set += std::popcount(window_[i]);
        }
        total_set += std::popcount(window_[3] & 0x0000000FU);

        return static_cast<uint8_t>(total_set);
    }

    std::array<uint32_t, WordsCount> window_{};
    std::size_t head_idx_{0};
    uint32_t expected_interval_ms_{10};
    uint32_t last_packet_time_ms_{0};
    uint32_t last_slot_time_ms_{0};
    int16_t  last_rssi_{-120};
    int8_t   last_snr_{-20};
};
