#include <array>
#include <string_view>
#include <functional>
#include <cstdint>
#include <span>

enum class HealthState : uint8_t {
    Nominal = 0,
    Degraded,
    Critical,
    Emergency
};

struct ComponentMetric {
    std::string_view                             name{};
    std::function<uint16_t()>                    collector{};
    uint16_t                                     weight{10};
    bool                                         is_critical{false};
    uint16_t                                     smoothed_score{1000};
    uint16_t                                     fault_count{0};
};

template <size_t MaxComponents = 8>
class HealthMonitor {
public:
    constexpr HealthMonitor() = default;

    bool register_component(std::string_view name, 
                            std::function<uint16_t()> collector,
                            uint16_t weight, 
                            bool is_critical) noexcept {
        if (component_count_ >= MaxComponents) {
            return false;
        }
        components_[component_count_++] = ComponentMetric{
            .name = name,
            .collector = std::move(collector),
            .weight = weight,
            .is_critical = is_critical,
            .smoothed_score = 1000,
            .fault_count = 0
        };
        return true;
    }

    void evaluate() noexcept {
        uint32_t weighted_sum = 0;
        uint32_t total_weight = 0;
        bool critical_failure = false;

        for (size_t i = 0; i < component_count_; ++i) {
            auto& comp = components_[i];
            const uint16_t raw_score = comp.collector ? comp.collector() : 0;

            // Цілочисельне експоненційне згладжування EWMA (alpha = 1/8)
            comp.smoothed_score = static_cast<uint16_t>(
                (raw_score + static_cast<uint32_t>(comp.smoothed_score) * 7) / 8
            );

            weighted_sum += static_cast<uint32_t>(comp.smoothed_score) * comp.weight;
            total_weight += comp.weight;

            if (comp.is_critical && comp.smoothed_score < 400) {
                critical_failure = true;
            }
        }

        system_score_ = (total_weight > 0) ? static_cast<uint16_t>(weighted_sum / total_weight) : 0;

        if (critical_failure) {
            system_score_ = 0;
            state_ = HealthState::Emergency;
        } else if (system_score_ >= 900) {
            state_ = HealthState::Nominal;
        } else if (system_score_ >= 700) {
            state_ = HealthState::Degraded;
        } else if (system_score_ >= 400) {
            state_ = HealthState::Critical;
        } else {
            state_ = HealthState::Emergency;
        }
    }

    [[nodiscard]] uint16_t system_score() const noexcept { return system_score_; }
    [[nodiscard]] HealthState state() const noexcept { return state_; }
    [[nodiscard]] std::span<const ComponentMetric> components() const noexcept {
        return std::span<const ComponentMetric>(components_.data(), component_count_);
    }

private:
    std::array<ComponentMetric, MaxComponents> components_{};
    size_t                                     component_count_{0};
    uint16_t                                   system_score_{1000};
    HealthState                                state_{HealthState::Nominal};
};
