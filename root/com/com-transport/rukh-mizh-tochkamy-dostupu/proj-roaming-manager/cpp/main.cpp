#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <optional>
#include <chrono>
#include <algorithm>
#include <span>

namespace wifi {

using MacAddress = std::array<uint8_t, 6>;

struct ApCandidate {
    MacAddress bssid{};
    int8_t rssi{0};
    uint8_t channel{0};
    std::string ssid;

    [[nodiscard]] constexpr bool is_5ghz() const noexcept {
        return channel > 14;
    }
};

class RssiFilter {
public:
    explicit constexpr RssiFilter(float alpha = 0.2f) noexcept : alpha_(alpha) {}

    void update(int8_t raw_rssi) noexcept {
        if (!initialized_) {
            value_ = static_cast<float>(raw_rssi);
            initialized_ = true;
        } else {
            value_ = alpha_ * static_cast<float>(raw_rssi) + (1.0f - alpha_) * value_;
        }
    }

    [[nodiscard]] int8_t value() const noexcept {
        return static_cast<int8_t>(value_);
    }

    void reset() noexcept {
        initialized_ = false;
        value_ = 0.0f;
    }

private:
    float alpha_{0.2f};
    float value_{0.0f};
    bool initialized_{false};
};

class RoamingEngine {
public:
    struct Config {
        int8_t threshold_dbm{-75};
        int8_t hysteresis_db{6};
        int8_t band_5ghz_bonus_db{10};
        std::chrono::milliseconds holdoff_time{5000};
    };

    explicit RoamingEngine(std::string_view target_ssid, Config cfg = {})
        : target_ssid_(target_ssid), config_(cfg) {}

    void on_beacon_rssi(int8_t raw_rssi) noexcept {
        filter_.update(raw_rssi);
    }

    [[nodiscard]] bool should_trigger_scan() const noexcept {
        return filter_.value() < config_.threshold_dbm;
    }

    [[nodiscard]] std::optional<ApCandidate> select_best_candidate(
        std::span<const ApCandidate> scan_results,
        const MacAddress& current_bssid,
        std::chrono::steady_clock::time_point now) noexcept 
    {
        if (now - last_handover_time_ < config_.holdoff_time) {
            return std::nullopt; /* Захист від частих перемикань за таймером */
        }

        const int8_t required_rssi = filter_.value() + config_.hysteresis_db;
        const ApCandidate* best = nullptr;
        int16_t best_score = -32768;

        for (const auto& candidate : scan_results) {
            if (candidate.ssid != target_ssid_) {
                continue;
            }
            if (candidate.bssid == current_bssid) {
                continue;
            }

            if (candidate.rssi >= required_rssi) {
                int16_t score = candidate.rssi;
                if (candidate.is_5ghz()) {
                    score += config_.band_5ghz_bonus_db;
                }

                if (!best || score > best_score) {
                    best_score = score;
                    best = &candidate;
                }
            }
        }

        if (best) {
            last_handover_time_ = now;
            return *best;
        }

        return std::nullopt;
    }

    [[nodiscard]] int8_t filtered_rssi() const noexcept {
        return filter_.value();
    }

    void reset() noexcept {
        filter_.reset();
    }

private:
    std::string target_ssid_;
    Config config_;
    RssiFilter filter_;
    std::chrono::steady_clock::time_point last_handover_time_{};
};

} // namespace wifi
