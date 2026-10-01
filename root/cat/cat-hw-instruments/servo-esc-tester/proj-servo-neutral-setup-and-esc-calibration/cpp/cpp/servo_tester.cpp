#include "servo_tester.hpp"

namespace hw {

void ServoTester::init() {
    mode_ = Mode::Neutral;
    pulseUs_ = NeutralPulseUs;
    sweepDir_ = 1;
    lastSweepMs_ = 0;
    lastBtnState_ = false;
    lastBtnDebounceMs_ = 0;
    escState_ = EscCalibState::Idle;
    escStateStartMs_ = 0;
}

void ServoTester::setMode(Mode newMode) {
    mode_ = newMode;
    if (mode_ == Mode::Neutral) {
        pulseUs_ = NeutralPulseUs;
    } else if (mode_ == Mode::AutoSweep) {
        sweepDir_ = 1;
    }
}

void ServoTester::updateManual(uint16_t adcVal) {
    if (mode_ != Mode::Manual || escState_ != EscCalibState::Idle) {
        return;
    }
    pulseUs_ = mapAdcToPulse(adcVal);
}

void ServoTester::updateSweep(uint32_t currentMs) {
    if (mode_ != Mode::AutoSweep || escState_ != EscCalibState::Idle) {
        return;
    }

    if (currentMs - lastSweepMs_ >= SweepIntervalMs) {
        lastSweepMs_ = currentMs;

        if (sweepDir_ > 0) {
            if (pulseUs_ + SweepStepUs >= MaxPulseUs) {
                pulseUs_ = MaxPulseUs;
                sweepDir_ = -1;
            } else {
                pulseUs_ += SweepStepUs;
            }
        } else {
            if (pulseUs_ <= MinPulseUs + SweepStepUs) {
                pulseUs_ = MinPulseUs;
                sweepDir_ = 1;
            } else {
                pulseUs_ -= SweepStepUs;
            }
        }
    }
}

void ServoTester::handleButton(bool rawButtonState, uint32_t currentMs) {
    if (rawButtonState != lastBtnState_) {
        if (currentMs - lastBtnDebounceMs_ >= DebounceMs) {
            lastBtnDebounceMs_ = currentMs;
            lastBtnState_ = rawButtonState;

            if (rawButtonState) {
                const auto nextModeInt = (static_cast<uint8_t>(mode_) + 1) % 3;
                setMode(static_cast<Mode>(nextModeInt));
            }
        }
    }
}

void ServoTester::startEscCalibration(uint32_t currentMs) {
    escState_ = EscCalibState::HighThrottle;
    escStateStartMs_ = currentMs;
    pulseUs_ = MaxPulseUs;
}

void ServoTester::updateEscCalibration(uint32_t currentMs) {
    if (escState_ == EscCalibState::Idle) {
        return;
    }

    switch (escState_) {
        case EscCalibState::HighThrottle:
            pulseUs_ = MaxPulseUs;
            if (currentMs - escStateStartMs_ >= 3000U) {
                escState_ = EscCalibState::LowThrottle;
                escStateStartMs_ = currentMs;
                pulseUs_ = MinPulseUs;
            }
            break;

        case EscCalibState::LowThrottle:
            pulseUs_ = MinPulseUs;
            if (currentMs - escStateStartMs_ >= 3000U) {
                escState_ = EscCalibState::Completed;
                escStateStartMs_ = currentMs;
            }
            break;

        case EscCalibState::Completed:
            escState_ = EscCalibState::Idle;
            setMode(Mode::Neutral);
            break;

        default:
            escState_ = EscCalibState::Idle;
            break;
    }
}

} // namespace hw
