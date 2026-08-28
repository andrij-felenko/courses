#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <optional>
#include <cstdint>
#include <format>

namespace security {

enum class RegimeFlags : uint32_t {
    None  = 0,
    CRA   = 1U << 0,
    NIS2  = 1U << 1,
    GDPR  = 1U << 2,
    SEC   = 1U << 3
};

inline constexpr RegimeFlags operator|(RegimeFlags a, RegimeFlags b) noexcept {
    return static_cast<RegimeFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

inline constexpr bool has_flag(RegimeFlags mask, RegimeFlags flag) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(flag)) != 0;
}

enum class Severity {
    Low,
    Medium,
    High,
    Critical
};

enum class IncidentState {
    New,
    Triaged,
    EarlyWarningDispatched,
    DetailedNoticeDispatched,
    FinalReportDispatched,
    Closed
};

class IncidentTriageEngine {
public:
    using Clock = std::chrono::system_clock;
    using TimePoint = std::chrono::time_point<Clock>;

    struct IncidentDetails {
        uint64_t id{0};
        Severity severity{Severity::Low};
        IncidentState state{IncidentState::New};
        RegimeFlags regimes{RegimeFlags::None};
        TimePoint detected_at{};
        TimePoint awareness_at{};
        std::optional<TimePoint> early_warning_deadline{};
        std::optional<TimePoint> detailed_notice_deadline{};
        std::optional<TimePoint> final_report_deadline{};
        bool has_active_exploit{false};
        bool pii_compromised{false};
        bool operational_outage{false};
    };

    explicit IncidentTriageEngine(uint64_t id, TimePoint detected = Clock::now()) {
        ctx_.id = id;
        ctx_.detected_at = detected;
        ctx_.awareness_at = detected;
        ctx_.state = IncidentState::New;
    }

    void set_exploit_observed(bool active) noexcept { ctx_.has_active_exploit = active; }
    void set_pii_compromised(bool compromised) noexcept { ctx_.pii_compromised = compromised; }
    void set_operational_outage(bool outage) noexcept { ctx_.operational_outage = outage; }
    void set_severity(Severity sev) noexcept { ctx_.severity = sev; }

    void evaluate_regimes() {
        ctx_.regimes = RegimeFlags::None;

        if (ctx_.has_active_exploit) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::CRA;
        }
        if (ctx_.operational_outage || ctx_.severity >= Severity::High) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::NIS2;
        }
        if (ctx_.pii_compromised) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::GDPR;
        }
        if (ctx_.severity == Severity::Critical) {
            ctx_.regimes = ctx_.regimes | RegimeFlags::SEC;
        }

        if (has_flag(ctx_.regimes, RegimeFlags::CRA) || has_flag(ctx_.regimes, RegimeFlags::NIS2)) {
            ctx_.early_warning_deadline = ctx_.awareness_at + std::chrono::hours(24);
            ctx_.detailed_notice_deadline = ctx_.awareness_at + std::chrono::hours(72);
            ctx_.final_report_deadline = ctx_.awareness_at + std::chrono::hours(24 * 30);
        } else if (has_flag(ctx_.regimes, RegimeFlags::GDPR)) {
            ctx_.early_warning_deadline = std::nullopt;
            ctx_.detailed_notice_deadline = ctx_.awareness_at + std::chrono::hours(72);
            ctx_.final_report_deadline = std::nullopt;
        }

        if (has_flag(ctx_.regimes, RegimeFlags::SEC)) {
            auto sec_deadline = add_business_days(ctx_.awareness_at, 4);
            if (!ctx_.detailed_notice_deadline || sec_deadline < *ctx_.detailed_notice_deadline) {
                ctx_.detailed_notice_deadline = sec_deadline;
            }
        }

        ctx_.state = IncidentState::Triaged;
    }

    void inspect_deadlines(TimePoint now = Clock::now()) const {
        if (ctx_.early_warning_deadline && ctx_.state < IncidentState::EarlyWarningDispatched) {
            auto diff = std::chrono::duration_cast<std::chrono::minutes>(*ctx_.early_warning_deadline - now);
            double hours = diff.count() / 60.0;
            if (hours < 0.0) {
                std::cout << std::format("[CRITICAL] Incident #{}: Early Warning deadline breached by {:.1f}h!\n",
                                         ctx_.id, -hours);
            } else if (hours <= 4.0) {
                std::cout << std::format("[WARNING] Incident #{}: Early Warning deadline in {:.1f}h.\n",
                                         ctx_.id, hours);
            }
        }

        if (ctx_.detailed_notice_deadline && ctx_.state < IncidentState::DetailedNoticeDispatched) {
            auto diff = std::chrono::duration_cast<std::chrono::minutes>(*ctx_.detailed_notice_deadline - now);
            double hours = diff.count() / 60.0;
            if (hours < 0.0) {
                std::cout << std::format("[CRITICAL] Incident #{}: Detailed Notification breached by {:.1f}h!\n",
                                         ctx_.id, -hours);
            } else if (hours <= 12.0) {
                std::cout << std::format("[ALERT] Incident #{}: Detailed Notification deadline in {:.1f}h.\n",
                                         ctx_.id, hours);
            }
        }
    }

    [[nodiscard]] const IncidentDetails& details() const noexcept { return ctx_; }

private:
    static TimePoint add_business_days(TimePoint start, int days) {
        TimePoint current = start;
        int added = 0;
        while (added < days) {
            current += std::chrono::hours(24);
            auto time_t_val = Clock::to_time_t(current);
            std::tm tm_buf{};
            gmtime_r(&time_t_val, &tm_buf);
            if (tm_buf.tm_wday != 0 && tm_buf.tm_wday != 6) {
                ++added;
            }
        }
        return current;
    }

    IncidentDetails ctx_;
};

} // namespace security
