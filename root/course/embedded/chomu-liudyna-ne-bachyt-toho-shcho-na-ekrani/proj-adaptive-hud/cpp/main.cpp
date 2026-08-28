#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <cmath>
#include <optional>
#include <algorithm>
#include <span>

namespace Hmi {

enum class Severity {
    Normal = 0,
    Warning,
    Critical
};

enum class DisplayMode {
    Full = 0,
    Piloting,
    Emergency
};

enum class Priority {
    Low = 0,
    Medium,
    High
};

struct MetricLimits {
    float warn_threshold{0.0f};
    float crit_threshold{0.0f};
    float max_safe_rate{0.0f};    // Поріг dx/dt для детекції прихованого дрейфу
};

class TelemetryWidget {
public:
    TelemetryWidget(std::string name, Priority priority, MetricLimits limits)
        : name_(std::move(name)), priority_(priority), limits_(limits) {}

    void update(float new_val, std::chrono::milliseconds now) {
        if (last_update_) {
            const float dt = std::chrono::duration<float>(now - *last_update_).count();
            if (dt > 0.001f) {
                const float raw_rate = std::abs(new_val - value_) / dt;
                filtered_rate_ = (ema_alpha_ * raw_rate) + ((1.0f - ema_alpha_) * filtered_rate_);
            }
        }

        value_ = new_val;
        last_update_ = now;

        // Оцінка небезпеки: по абсолютній величині або швидкості дрейфу
        if (value_ >= limits_.crit_threshold) {
            severity_ = Severity::Critical;
        } else if (value_ >= limits_.warn_threshold ||
                  (limits_.max_safe_rate > 0.0f && filtered_rate_ >= limits_.max_safe_rate)) {
            severity_ = Severity::Warning;
        } else {
            severity_ = Severity::Normal;
        }
    }

    [[nodiscard]] const std::string& name() const noexcept { return name_; }
    [[nodiscard]] float value() const noexcept { return value_; }
    [[nodiscard]] float rate_of_change() const noexcept { return filtered_rate_; }
    [[nodiscard]] Severity severity() const noexcept { return severity_; }
    [[nodiscard]] Priority priority() const noexcept { return priority_; }
    [[nodiscard]] bool is_visible() const noexcept { return is_visible_; }

    void set_visible(bool visible) noexcept { is_visible_ = visible; }

private:
    std::string name_;
    Priority priority_;
    MetricLimits limits_;
    float value_{0.0f};
    float filtered_rate_{0.0f};
    Severity severity_{Severity::Normal};
    bool is_visible_{true};
    std::optional<std::chrono::milliseconds> last_update_{std::nullopt};
    static constexpr float ema_alpha_{0.25f};
};

class AdaptiveHudEngine {
public:
    void add_widget(TelemetryWidget widget) {
        widgets_.push_back(std::move(widget));
    }

    void update_metric(size_t index, float value, std::chrono::milliseconds now) {
        if (index < widgets_.size()) {
            widgets_[index].update(value, now);
        }
    }

    void evaluate(float stick_deflection, std::chrono::milliseconds now) {
        if (stick_deflection > 0.3f) {
            last_stick_activity_ = now;
        }

        const bool has_critical = std::any_of(widgets_.begin(), widgets_.end(), [](const auto& w) {
            return w.severity() == Severity::Critical;
        });

        const auto time_since_stick = last_stick_activity_
            ? (now - *last_stick_activity_)
            : std::chrono::milliseconds(99999);

        // Автомат станів візуального навантаження
        if (has_critical) {
            mode_ = DisplayMode::Emergency;
        } else if (time_since_stick < std::chrono::milliseconds(2000)) {
            mode_ = DisplayMode::Piloting;
        } else {
            mode_ = DisplayMode::Full;
        }

        // Розподіл видимості (Decluttering Policy)
        for (auto& w : widgets_) {
            switch (mode_) {
            case DisplayMode::Emergency:
                w.set_visible(w.severity() == Severity::Critical || w.priority() == Priority::High);
                break;
            case DisplayMode::Piloting:
                w.set_visible(w.priority() >= Priority::Medium || w.severity() != Severity::Normal);
                break;
            case DisplayMode::Full:
            default:
                w.set_visible(true);
                break;
            }
        }
    }

    void render_summary() const {
        std::cout << "\n=== СТАН HUD: ";
        switch (mode_) {
        case DisplayMode::Emergency: std::cout << "EMERGENCY (Фокус на відмові)\n"; break;
        case DisplayMode::Piloting:  std::cout << "PILOTING (Придушення шуму)\n"; break;
        case DisplayMode::Full:      std::cout << "FULL (Штатна панорама)\n"; break;
        }

        for (const auto& w : widgets_) {
            if (!w.is_visible()) continue;

            std::cout << "  " << (w.severity() == Severity::Critical ? "[!CRIT!] "
                               : w.severity() == Severity::Warning  ? "[ WARN ] "
                                                                    : "[  OK  ] ")
                      << w.name() << ": " << w.value()
                      << " (dx/dt: " << w.rate_of_change() << "/s)\n";
        }
    }

    [[nodiscard]] std::span<const TelemetryWidget> widgets() const noexcept {
        return widgets_;
    }

private:
    std::vector<TelemetryWidget> widgets_;
    DisplayMode mode_{DisplayMode::Full};
    std::optional<std::chrono::milliseconds> last_stick_activity_{std::nullopt};
};

} // namespace Hmi
