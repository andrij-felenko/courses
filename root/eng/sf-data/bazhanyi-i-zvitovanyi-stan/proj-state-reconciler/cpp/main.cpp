#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <variant>
#include <optional>
#include <expected>
#include <chrono>
#include <random>
#include <cmath>

namespace edge::reconciler {

enum class ErrorCode {
    VersionConflict,
    ActuationFailed,
    RateLimited,
    InvalidPayload
};

using PropertyValue = std::variant<std::monostate, int64_t, double, bool, std::string>;

struct StateDocument {
    std::unordered_map<std::string, PropertyValue> properties;
    uint64_t version{0};
    std::chrono::system_clock::time_point timestamp{std::chrono::system_clock::now()};

    [[nodiscard]] std::optional<PropertyValue> get(std::string_view key) const {
        auto it = properties.find(std::string(key));
        if (it != properties.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void set(std::string_view key, PropertyValue val) {
        properties[std::string(key)] = std::move(val);
        timestamp = std::chrono::system_clock::now();
    }
};

struct DriftRecord {
    std::string key;
    PropertyValue desired;
    PropertyValue reported;
};

class ReconcilerEngine {
public:
    struct Policy {
        std::chrono::milliseconds base_backoff{50};
        std::chrono::milliseconds max_backoff{5000};
        double analog_deadband{0.2}; /* Гістерезис 0.2 одиниці */
        uint32_t current_attempt{0};
    };

    explicit ReconcilerEngine(Policy policy) 
        : policy_(policy), rng_(std::random_device{}()) {}

    [[nodiscard]] std::vector<DriftRecord> compute_drift(
        const StateDocument& desired,
        const StateDocument& reported) const 
    {
        std::vector<DriftRecord> drifts;

        for (const auto& [key, d_val] : desired.properties) {
            auto r_opt = reported.get(key);
            if (!r_opt.has_value()) {
                drifts.push_back({key, d_val, std::monostate{}});
                continue;
            }

            const auto& r_val = *r_opt;
            if (std::holds_alternative<double>(d_val) && std::holds_alternative<double>(r_val)) {
                double diff = std::abs(std::get<double>(d_val) - std::get<double>(r_val));
                if (diff > policy_.analog_deadband) {
                    drifts.push_back({key, d_val, r_val});
                }
            } else if (d_val != r_val) {
                drifts.push_back({key, d_val, r_val});
            }
        }
        return drifts;
    }

    std::expected<bool, ErrorCode> reconcile(
        const StateDocument& desired,
        StateDocument& reported,
        uint64_t expected_version) 
    {
        /* Оптимістична перевірка колізій */
        if (desired.version < expected_version) {
            return std::unexpected(ErrorCode::VersionConflict);
        }

        auto drifts = compute_drift(desired, reported);
        if (drifts.empty()) {
            policy_.current_attempt = 0;
            return false; /* Дрейфу немає, система у спокої */
        }

        std::cout << "  [Дрейф C++] Виявлено розбіжностей: " << drifts.size() << '\n';

        for (const auto& drift : drifts) {
            if (!actuate_hardware(drift.key, drift.desired)) {
                policy_.current_attempt++;
                auto wait_time = calculate_backoff();
                std::cout << "  [Збій C++] Помилка актуатора " << drift.key 
                          << ", відкат на " << wait_time.count() << " мс\n";
                return std::unexpected(ErrorCode::ActuationFailed);
            }
            /* Фіксація нового стану локально */
            reported.set(drift.key, drift.desired);
        }

        reported.version = desired.version;
        policy_.current_attempt = 0;
        return true; /* Успішно узгоджено */
    }

private:
    Policy policy_;
    mutable std::mt19937 rng_;

    [[nodiscard]] std::chrono::milliseconds calculate_backoff() const {
        uint64_t multiplier = 1ULL << std::min(policy_.current_attempt, 10U);
        auto raw_limit = policy_.base_backoff * multiplier;
        auto capped = std::min(raw_limit, policy_.max_backoff);
        
        std::uniform_int_distribution<uint64_t> dist(0, capped.count());
        return std::chrono::milliseconds(dist(rng_));
    }

    [[nodiscard]] bool actuate_hardware(const std::string& key, const PropertyValue& val) const {
        std::cout << "  [Актуватор C++] Встановлення параметра " << key << '\n';
        return true;
    }
};

} // namespace edge::reconciler
