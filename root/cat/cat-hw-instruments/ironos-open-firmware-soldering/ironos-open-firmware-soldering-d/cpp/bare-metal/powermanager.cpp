#include <cstdint>
#include <algorithm>

class PowerManager {
public:
    struct Config {
        uint16_t uIdleMv;
        uint16_t uLoadMv;
        uint16_t uCutoffMv;
        uint16_t rTipMOhm;
    };

    static uint8_t computePwmLimit(const Config& cfg) noexcept {
        if (cfg.uLoadMv >= cfg.uIdleMv || cfg.uLoadMv <= cfg.uCutoffMv || cfg.rTipMOhm == 0) {
            return 255;
        }

        const uint32_t deltaUMv = cfg.uIdleMv - cfg.uLoadMv;
        const uint32_t currentMa = (static_cast<uint32_t>(cfg.uLoadMv) * 1000) / cfg.rTipMOhm;
        if (currentMa == 0) return 255;

        const uint32_t rSrcMOhm = (deltaUMv * 1000) / currentMa;
        const uint32_t allowedDropMv = cfg.uIdleMv - cfg.uCutoffMv;
        
        const uint32_t maxPwm = (allowedDropMv * cfg.rTipMOhm * 255) / 
                                (static_cast<uint32_t>(cfg.uCutoffMv) * rSrcMOhm);

        return static_cast<uint8_t>(std::min<uint32_t>(maxPwm, 255));
    }
};
