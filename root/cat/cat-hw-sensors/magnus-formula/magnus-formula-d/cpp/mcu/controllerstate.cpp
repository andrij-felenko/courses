#include <cmath>
#include <cstdint>

namespace Climate {

enum class ControllerState {
    Off,
    Heating,
    Fault
};

class AntiCondensationController {
public:
    struct Config {
        float marginOnC = 1.5f;
        float marginOffC = 3.5f;
        std::uint32_t maxHeatTimeSec = 300;
    };

    explicit AntiCondensationController(Config config) : config_(config) {}

    // Оновлення стану регулятора (C++)
    void process(float surfaceTempC, float dewPointC, bool sensorsValid, std::uint32_t currentTimeSec) noexcept {
        if (!sensorsValid || std::isnan(surfaceTempC) || std::isnan(dewPointC)) {
            state_ = ControllerState::Fault;
            heaterOutput_ = false;
            return;
        }

        const float margin = surfaceTempC - dewPointC;

        if (state_ == ControllerState::Off || state_ == ControllerState::Fault) {
            if (margin <= config_.marginOnC) {
                state_ = ControllerState::Heating;
                heaterOutput_ = true;
                heatStartTimeSec_ = currentTimeSec;
            }
        } else if (state_ == ControllerState::Heating) {
            if ((currentTimeSec - heatStartTimeSec_) >= config_.maxHeatTimeSec) {
                state_ = ControllerState::Fault;
                heaterOutput_ = false;
            } else if (margin >= config_.marginOffC) {
                state_ = ControllerState::Off;
                heaterOutput_ = false;
            }
        }
    }

    [[nodiscard]] bool isHeaterActive() const noexcept { return heaterOutput_; }
    [[nodiscard]] ControllerState getState() const noexcept { return state_; }

private:
    Config config_;
    ControllerState state_{ControllerState::Off};
    bool heaterOutput_{false};
    std::uint32_t heatStartTimeSec_{0};
};

} // namespace Climate
