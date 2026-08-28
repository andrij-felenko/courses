#include <iostream>
#include <cstdint>

namespace fleet::arbitrage {

struct WaveMetrics {
    uint32_t succeeded{0};
    uint32_t failed{0};
    uint32_t rolledBack{0};
    uint32_t silenced{0};

    [[nodiscard]] constexpr uint32_t totalEvaluated() const noexcept {
        return succeeded + failed + rolledBack + silenced;
    }
};

struct ArbitrageThresholds {
    uint32_t minSampleSize{100};
    double maxFailRatePct{1.0};
    double maxRollbackRatePct{0.5};
    double maxSilenceRatePct{0.2};
};

class StopTheLineArbiter {
public:
    [[nodiscard]] static bool evaluate(const WaveMetrics& m, const ArbitrageThresholds& t) noexcept {
        const uint32_t total = m.totalEvaluated();
        if (total < t.minSampleSize) {
            return false;
        }

        const double failRate = (static_cast<double>(m.failed) / total) * 100.0;
        const double rbRate = (static_cast<double>(m.rolledBack) / total) * 100.0;
        const double silenceRate = (static_cast<double>(m.silenced) / total) * 100.0;

        if (failRate > t.maxFailRatePct || 
            rbRate > t.maxRollbackRatePct || 
            silenceRate > t.maxSilenceRatePct) {
            
            std::cerr << "[STOP-THE-LINE] Спрацював аварійний вимикач! "
                      << "Fail: " << failRate << "%, RB: " << rbRate 
                      << "%, Silence: " << silenceRate << "%\n";
            return true;
        }

        return false;
    }
};

} // namespace fleet::arbitrage
