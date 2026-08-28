#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>
#include <format>

using namespace std::chrono;

enum class CvdState {
    Submitted,
    Triaged,
    InProgress,
    PatchReady,
    PreNotify,
    Disclosed,
    Emergency,
    Rejected
};

enum class CvdError {
    InvalidStateTransition,
    GracePeriodAlreadyApplied,
    GracePeriodNotAllowedInCurrentState,
    CaseAlreadyClosed,
    EmbargoNotExpired
};

class CvdCaseTracker {
public:
    explicit CvdCaseTracker(std::string_view case_id, sys_seconds submit_time)
        : case_id_(case_id), submitted_time_(submit_time), state_(CvdState::Submitted) {
        auto raw_deadline = submit_time + days(90);
        embargo_deadline_ = adjust_weekend_rollover(raw_deadline);
    }

    [[nodiscard]] const std::string& case_id() const noexcept { return case_id_; }
    [[nodiscard]] const std::string& cve_id() const noexcept { return cve_id_; }
    [[nodiscard]] CvdState state() const noexcept { return state_; }
    [[nodiscard]] sys_seconds embargo_deadline() const noexcept { return embargo_deadline_; }
    [[nodiscard]] bool is_grace_applied() const noexcept { return grace_applied_; }

    std::expected<void, CvdError> triage(std::string_view cve_id, bool accepted) {
        if (state_ != CvdState::Submitted) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        if (!accepted) {
            state_ = CvdState::Rejected;
            return {};
        }
        cve_id_ = cve_id;
        state_ = CvdState::Triaged;
        return {};
    }

    std::expected<void, CvdError> start_remediation() {
        if (state_ != CvdState::Triaged) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        state_ = CvdState::InProgress;
        return {};
    }

    std::expected<void, CvdError> mark_patch_ready() {
        if (state_ != CvdState::InProgress) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        state_ = CvdState::PatchReady;
        return {};
    }

    std::expected<void, CvdError> start_pre_notification() {
        if (state_ != CvdState::PatchReady) {
            return std::unexpected(CvdError::InvalidStateTransition);
        }
        state_ = CvdState::PreNotify;
        return {};
    }

    std::expected<void, CvdError> apply_grace_period() {
        if (grace_applied_) {
            return std::unexpected(CvdError::GracePeriodAlreadyApplied);
        }
        if (state_ != CvdState::InProgress && state_ != CvdState::PatchReady) {
            return std::unexpected(CvdError::GracePeriodNotAllowedInCurrentState);
        }
        embargo_deadline_ = adjust_weekend_rollover(embargo_deadline_ + days(14));
        grace_applied_ = true;
        return {};
    }

    std::expected<void, CvdError> trigger_emergency(sys_seconds event_time, bool in_the_wild, bool public_leak) {
        if (state_ == CvdState::Disclosed || state_ == CvdState::Rejected) {
            return std::unexpected(CvdError::CaseAlreadyClosed);
        }
        state_ = CvdState::Emergency;
        if (public_leak) {
            public_leak_ = true;
            embargo_deadline_ = event_time + days(2);
        } else if (in_the_wild) {
            in_the_wild_ = true;
            embargo_deadline_ = event_time + days(7);
        }
        return {};
    }

    std::expected<void, CvdError> disclose(sys_seconds current_time) {
        if (state_ == CvdState::Disclosed || state_ == CvdState::Rejected) {
            return std::unexpected(CvdError::CaseAlreadyClosed);
        }
        if (current_time < embargo_deadline_ && state_ != CvdState::Emergency && state_ != CvdState::PreNotify) {
            return std::unexpected(CvdError::EmbargoNotExpired);
        }
        state_ = CvdState::Disclosed;
        return {};
    }

private:
    static sys_seconds adjust_weekend_rollover(sys_seconds target_time) {
        sys_days dp = floor<days>(target_time);
        year_month_day ymd{dp};
        weekday wd{dp};
        if (wd == Saturday) {
            return target_time + days(2);
        }
        if (wd == Sunday) {
            return target_time + days(1);
        }
        return target_time;
    }

    std::string case_id_;
    std::string cve_id_;
    CvdState state_;
    sys_seconds submitted_time_;
    sys_seconds embargo_deadline_;
    bool in_the_wild_{false};
    bool public_leak_{false};
    bool grace_applied_{false};
};
