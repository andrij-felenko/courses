#include <algorithm>
#include <cmath>
#include <cstdint>

enum class VtolState : uint8_t {
    Hover = 0,
    TransitionFw,
    FixedWing,
    TransitionMc,
    FailsafeRecovery
};

struct TransitionParameters {
    float vBlendStart{6.0f};     // Початок змішування рулів (м/с)
    float vStall{13.0f};         // Швидкість звалювання (м/с)
    float vTrans{16.0f};         // Швидкість повного переходу (м/с)
    float maxTransTimeSec{12.0f};// Максимальний час переходу (с)
    float maxSinkRateMps{2.5f};  // Поріг небезпечного просідання (м/с)
    float prespoolThrottle{0.2f};// Холостий газ роторів при зворотному переході
};

struct ControllerOutputs {
    float pusherThrottle{0.0f};
    float liftRotorsWeight{1.0f};
    float surfacesBlendFactor{0.0f};
    bool emergencyAssistActive{false};
};

class VtolTransitionManager {
public:
    explicit constexpr VtolTransitionManager(const TransitionParameters& params) noexcept
        : params_(params) {}

    void reset() noexcept {
        state_ = VtolState::Hover;
        elapsedTimeSec_ = 0.0f;
        outputs_ = ControllerOutputs{};
    }

    [[nodiscard]] ControllerOutputs update(float iasMps,
                                           float sinkRateMps,
                                           float dtSec,
                                           bool commandToFw,
                                           bool commandToMc) noexcept
    {
        switch (state_) {
        case VtolState::Hover:
            handleHover(commandToFw);
            break;

        case VtolState::TransitionFw:
            handleTransitionFw(iasMps, sinkRateMps, dtSec);
            break;

        case VtolState::FixedWing:
            handleFixedWing(commandToMc);
            break;

        case VtolState::TransitionMc:
            handleTransitionMc(iasMps, dtSec);
            break;

        case VtolState::FailsafeRecovery:
            handleFailsafe(iasMps, sinkRateMps);
            break;
        }

        return outputs_;
    }

    [[nodiscard]] VtolState state() const noexcept { return state_; }

private:
    void handleHover(bool commandToFw) noexcept {
        outputs_.pusherThrottle = 0.0f;
        outputs_.liftRotorsWeight = 1.0f;
        outputs_.surfacesBlendFactor = 0.0f;
        outputs_.emergencyAssistActive = false;
        elapsedTimeSec_ = 0.0f;

        if (commandToFw) {
            state_ = VtolState::TransitionFw;
            elapsedTimeSec_ = 0.0f;
        }
    }

    void handleTransitionFw(float iasMps, float sinkRateMps, float dtSec) noexcept {
        elapsedTimeSec_ += dtSec;
        outputs_.pusherThrottle = 1.0f;

        // Перевірка небезпечного просідання та перевищення ліміту часу
        if (sinkRateMps > params_.maxSinkRateMps || elapsedTimeSec_ > params_.maxTransTimeSec) {
            outputs_.emergencyAssistActive = true;
            state_ = VtolState::FailsafeRecovery;
            return;
        }

        // Розрахунок вагового коефіцієнта аеродинамічних поверхонь
        if (iasMps < params_.vBlendStart) {
            outputs_.surfacesBlendFactor = 0.0f;
        } else {
            const float span = params_.vTrans - params_.vBlendStart;
            outputs_.surfacesBlendFactor = std::clamp((iasMps - params_.vBlendStart) / span, 0.0f, 1.0f);
        }

        // Квадратичне розвантаження роторів із компенсацією нелінійності ESC
        if (iasMps >= params_.vTrans) {
            outputs_.liftRotorsWeight = 0.0f;
            outputs_.pusherThrottle = 0.65f;
            outputs_.surfacesBlendFactor = 1.0f;
            state_ = VtolState::FixedWing;
        } else {
            const float speedRatio = std::clamp(iasMps / params_.vTrans, 0.0f, 1.0f);
            const float forceDeficit = 1.0f - (speedRatio * speedRatio);
            outputs_.liftRotorsWeight = std::sqrt(forceDeficit);
        }
    }

    void handleFixedWing(bool commandToMc) noexcept {
        outputs_.pusherThrottle = 0.65f;
        outputs_.liftRotorsWeight = 0.0f;
        outputs_.surfacesBlendFactor = 1.0f;
        outputs_.emergencyAssistActive = false;
        elapsedTimeSec_ = 0.0f;

        if (commandToMc) {
            state_ = VtolState::TransitionMc;
            elapsedTimeSec_ = 0.0f;
        }
    }

    void handleTransitionMc(float iasMps, float dtSec) noexcept {
        elapsedTimeSec_ += dtSec;
        outputs_.pusherThrottle = 0.0f;

        if (iasMps > params_.vStall) {
            outputs_.liftRotorsWeight = params_.prespoolThrottle;
            outputs_.surfacesBlendFactor = 1.0f;
        } else {
            const float mcRatio = std::clamp(iasMps / params_.vStall, 0.0f, 1.0f);
            const float weight = 1.0f - (mcRatio * mcRatio);
            outputs_.liftRotorsWeight = std::clamp(std::sqrt(weight) + params_.prespoolThrottle, 0.0f, 1.0f);
            outputs_.surfacesBlendFactor = mcRatio;
        }

        if (iasMps < params_.vBlendStart) {
            outputs_.liftRotorsWeight = 1.0f;
            outputs_.surfacesBlendFactor = 0.0f;
            state_ = VtolState::Hover;
        }
    }

    void handleFailsafe(float iasMps, float sinkRateMps) noexcept {
        outputs_.pusherThrottle = 0.0f;
        outputs_.liftRotorsWeight = 1.0f;
        outputs_.surfacesBlendFactor = 0.0f;

        if (iasMps < params_.vBlendStart && sinkRateMps < 0.5f) {
            outputs_.emergencyAssistActive = false;
            state_ = VtolState::Hover;
        }
    }

    TransitionParameters params_;
    VtolState state_{VtolState::Hover};
    float elapsedTimeSec_{0.0f};
    ControllerOutputs outputs_{};
};
