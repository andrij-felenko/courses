#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>
#include <algorithm>
#include <format>
#include <sstream>
#include <iomanip>

namespace postmortem {

enum class Phase {
    DefectInjected,
    TriggerEvent,
    ImpactStarted,
    DetectedByAlert,
    AcknowledgedByOncall,
    MitigationApplied,
    ImpactEnded,
    FullyResolved,
    Unknown
};

[[nodiscard]] constexpr std::string_view phase_to_string(Phase phase) noexcept {
    switch (phase) {
        case Phase::DefectInjected:        return "defect_injected";
        case Phase::TriggerEvent:          return "trigger_event";
        case Phase::ImpactStarted:         return "impact_started";
        case Phase::DetectedByAlert:       return "detected_by_alert";
        case Phase::AcknowledgedByOncall:  return "acknowledged_by_oncall";
        case Phase::MitigationApplied:     return "mitigation_applied";
        case Phase::ImpactEnded:           return "impact_ended";
        case Phase::FullyResolved:         return "fully_resolved";
        case Phase::Unknown:               return "unknown";
    }
    return "unknown";
}

[[nodiscard]] constexpr Phase string_to_phase(std::string_view sv) noexcept {
    if (sv == "defect_injected")        return Phase::DefectInjected;
    if (sv == "trigger_event")          return Phase::TriggerEvent;
    if (sv == "impact_started")         return Phase::ImpactStarted;
    if (sv == "detected_by_alert")      return Phase::DetectedByAlert;
    if (sv == "acknowledged_by_oncall") return Phase::AcknowledgedByOncall;
    if (sv == "mitigation_applied")     return Phase::MitigationApplied;
    if (sv == "impact_ended")           return Phase::ImpactEnded;
    if (sv == "fully_resolved")         return Phase::FullyResolved;
    return Phase::Unknown;
}

using TimePoint = std::chrono::system_clock::time_point;

struct TimelineEvent {
    TimePoint timestamp;
    Phase phase;
    std::string component;
    std::string description;
    std::string source_url;
};

struct IncidentMetrics {
    std::chrono::seconds mttd{0}; // Mean Time to Detect (Impact -> Detect)
    std::chrono::seconds mtta{0}; // Mean Time to Acknowledge (Detect -> Ack)
    std::chrono::seconds mttm{0}; // Mean Time to Mitigate (Ack -> Mitigation)
    std::chrono::seconds mttr{0}; // Mean Time to Resolve (Impact -> Resolve)
    std::chrono::seconds total_impact_duration{0};
};

enum class ValidationError {
    EmptyTimeline,
    NonMonotonicTimestamps,
    MissingImpactStart,
    MissingResolution,
    MitigationBeforeDetection,
    AckBeforeDetection
};

class TimelineReconstructor {
public:
    void add_event(TimelineEvent event) {
        events_.push_back(std::move(event));
    }

    [[nodiscard]] std::expected<IncidentMetrics, ValidationError> process_and_validate() {
        if (events_.empty()) {
            return std::unexpected(ValidationError::EmptyTimeline);
        }

        // Сортування за часом
        std::stable_sort(events_.begin(), events_.end(), [](const auto& a, const auto& b) {
            return a.timestamp < b.timestamp;
        });

        std::optional<TimePoint> t_impact;
        std::optional<TimePoint> t_detect;
        std::optional<TimePoint> t_ack;
        std::optional<TimePoint> t_mitigate;
        std::optional<TimePoint> t_impact_end;
        std::optional<TimePoint> t_resolve;

        for (const auto& ev : events_) {
            switch (ev.phase) {
                case Phase::ImpactStarted:         t_impact = ev.timestamp; break;
                case Phase::DetectedByAlert:       t_detect = ev.timestamp; break;
                case Phase::AcknowledgedByOncall:  t_ack = ev.timestamp; break;
                case Phase::MitigationApplied:     t_mitigate = ev.timestamp; break;
                case Phase::ImpactEnded:           t_impact_end = ev.timestamp; break;
                case Phase::FullyResolved:         t_resolve = ev.timestamp; break;
                default: break;
            }
        }

        if (!t_impact.has_value()) {
            return std::unexpected(ValidationError::MissingImpactStart);
        }
        if (!t_resolve.has_value() && !t_impact_end.has_value()) {
            return std::unexpected(ValidationError::MissingResolution);
        }

        // Перевірка інваріантів причинно-наслідкового зв'язку
        if (t_detect && t_ack && *t_ack < *t_detect) {
            return std::unexpected(ValidationError::AckBeforeDetection);
        }
        if (t_detect && t_mitigate && *t_mitigate < *t_detect) {
            return std::unexpected(ValidationError::MitigationBeforeDetection);
        }

        IncidentMetrics metrics;
        if (t_detect && t_impact) {
            metrics.mttd = std::chrono::duration_cast<std::chrono::seconds>(*t_detect - *t_impact);
        }
        if (t_ack && t_detect) {
            metrics.mtta = std::chrono::duration_cast<std::chrono::seconds>(*t_ack - *t_detect);
        }
        if (t_mitigate && t_ack) {
            metrics.mttm = std::chrono::duration_cast<std::chrono::seconds>(*t_mitigate - *t_ack);
        }
        if (t_resolve && t_impact) {
            metrics.mttr = std::chrono::duration_cast<std::chrono::seconds>(*t_resolve - *t_impact);
        }
        if (t_impact_end && t_impact) {
            metrics.total_impact_duration = std::chrono::duration_cast<std::chrono::seconds>(*t_impact_end - *t_impact);
        } else if (t_resolve && t_impact) {
            metrics.total_impact_duration = metrics.mttr;
        }

        return metrics;
    }

    [[nodiscard]] const std::vector<TimelineEvent>& events() const noexcept {
        return events_;
    }

private:
    std::vector<TimelineEvent> events_;
};

} // namespace postmortem

int main() {
    using namespace std::chrono_literals;
    auto now = std::chrono::system_clock::now();

    postmortem::TimelineReconstructor reconstructor;

    reconstructor.add_event({
        now,
        postmortem::Phase::ImpactStarted,
        "checkout-gateway",
        "Стрибок 5xx помилок через блокування пулу HikariCP",
        "https://monitoring.internal/alerts/500"
    });

    reconstructor.add_event({
        now + 120s,
        postmortem::Phase::DetectedByAlert,
        "alertmanager",
        "Спрацював алерт High5xxErrorRate (burn rate > 14x)",
        "https://alertmanager.internal/#/alert/412"
    });

    reconstructor.add_event({
        now + 300s,
        postmortem::Phase::AcknowledgedByOncall,
        "pagerduty",
        "Черговий інженер підтвердив інцидент",
        "https://pagerduty.internal/inc/841"
    });

    reconstructor.add_event({
        now + 1500s,
        postmortem::Phase::MitigationApplied,
        "feature-flags",
        "Вимкнено виклик зовнішнього податкового шлюзу",
        "https://flags.internal/tax-fallback"
    });

    reconstructor.add_event({
        now + 2400s,
        postmortem::Phase::FullyResolved,
        "checkout-gateway",
        "Черги розвантажилися, p99 латентність повернулася до норми",
        "https://grafana.internal/d/health"
    });

    auto res = reconstructor.process_and_validate();
    if (!res) {
        std::cerr << "Помилка валідації таймлайну!\n";
        return 1;
    }

    const auto& m = *res;
    std::cout << "=== МЕТРИКИ ІНЦИДЕНТУ ===\n";
    std::cout << "MTTD (Час до виявлення):     " << m.mttd.count() / 60 << " хв " << m.mttd.count() % 60 << " с\n";
    std::cout << "MTTA (Час реакції чергового): " << m.mtta.count() / 60 << " хв " << m.mtta.count() % 60 << " с\n";
    std::cout << "MTTM (Час до пом'якшення):   " << m.mttm.count() / 60 << " хв " << m.mttm.count() % 60 << " с\n";
    std::cout << "MTTR (Повний час відновлення): " << m.mttr.count() / 60 << " хв " << m.mttr.count() % 60 << " с\n";

    return 0;
}
