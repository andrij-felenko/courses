#include "PhaseSelectorController.hpp"

namespace hw_controls {

PhaseSelectorController::PhaseSelectorController(const VoltageThresholds& thresholds,
                                                 const TimerConfig& timers)
    : thresholds_(thresholds), timers_(timers) {}

bool PhaseSelectorController::isPhaseValid(PhaseId phase, float voltage) const noexcept {
    if (active_phase_ == phase) {
        return (voltage >= (thresholds_.u_min - thresholds_.u_hysteresis)) &&
               (voltage <= (thresholds_.u_max + thresholds_.u_hysteresis));
    }
    return (voltage >= thresholds_.u_min) && (voltage <= thresholds_.u_max);
}

PhaseId PhaseSelectorController::selectBestPhase(const PhaseMeasurements& m) const noexcept {
    if (isPhaseValid(PhaseId::L1, m.u_l1)) return PhaseId::L1;
    if (isPhaseValid(PhaseId::L2, m.u_l2)) return PhaseId::L2;
    if (isPhaseValid(PhaseId::L3, m.u_l3)) return PhaseId::L3;
    return PhaseId::None;
}

void PhaseSelectorController::update(const PhaseMeasurements& m, uint32_t dt_ms) {
    state_timer_ms_ += dt_ms;

    switch (state_) {
        case FsmState::Init: {
            const PhaseId best = selectBestPhase(m);
            if (best != PhaseId::None) {
                target_phase_ = best;
                state_ = FsmState::BreakBeforeMake;
                state_timer_ms_ = 0;
            } else {
                state_ = FsmState::AllPhasesFault;
            }
            break;
        }

        case FsmState::Monitoring: {
            const float current_u = (active_phase_ == PhaseId::L1) ? m.u_l1 :
                                    (active_phase_ == PhaseId::L2) ? m.u_l2 : m.u_l3;

            const bool current_valid = isPhaseValid(active_phase_, current_u);
            const bool l1_recovered = (active_phase_ != PhaseId::L1) && isPhaseValid(PhaseId::L1, m.u_l1);

            if (!current_valid) {
                fault_timer_ms_ += dt_ms;
                if (fault_timer_ms_ >= timers_.t_delay_ms) {
                    active_phase_ = PhaseId::None;
                    target_phase_ = selectBestPhase(m);
                    state_ = FsmState::BreakBeforeMake;
                    state_timer_ms_ = 0;
                    fault_timer_ms_ = 0;
                }
            } else {
                fault_timer_ms_ = 0;
                if (l1_recovered) {
                    target_phase_ = PhaseId::L1;
                    state_ = FsmState::ReturnDelay;
                    state_timer_ms_ = 0;
                }
            }
            break;
        }

        case FsmState::ReturnDelay: {
            const float current_u = (active_phase_ == PhaseId::L1) ? m.u_l1 :
                                    (active_phase_ == PhaseId::L2) ? m.u_l2 : m.u_l3;

            if (!isPhaseValid(active_phase_, current_u)) {
                active_phase_ = PhaseId::None;
                target_phase_ = selectBestPhase(m);
                state_ = FsmState::BreakBeforeMake;
                state_timer_ms_ = 0;
            } else if (!isPhaseValid(PhaseId::L1, m.u_l1)) {
                state_ = FsmState::Monitoring;
            } else if (state_timer_ms_ >= timers_.t_return_ms) {
                active_phase_ = PhaseId::None;
                state_ = FsmState::BreakBeforeMake;
                state_timer_ms_ = 0;
            }
            break;
        }

        case FsmState::BreakBeforeMake: {
            if (state_timer_ms_ >= timers_.t_dead_ms) {
                if (target_phase_ != PhaseId::None) {
                    active_phase_ = target_phase_;
                    state_ = FsmState::Monitoring;
                } else {
                    state_ = FsmState::AllPhasesFault;
                }
            }
            break;
        }

        case FsmState::AllPhasesFault: {
            const PhaseId best = selectBestPhase(m);
            if (best != PhaseId::None) {
                target_phase_ = best;
                state_ = FsmState::BreakBeforeMake;
                state_timer_ms_ = 0;
            }
            break;
        }
    }
}

} // namespace hw_controls
