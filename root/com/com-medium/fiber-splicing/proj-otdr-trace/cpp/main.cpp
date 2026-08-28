#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <string_view>
#include <expected>

enum class OtdrEventType {
    SpliceFusion,
    Connector,
    Gainer,
    FiberEnd
};

struct OtdrEvent {
    double distance_m;
    OtdrEventType type;
    double loss_db;
    double return_loss_db;
};

struct OtdrTraceView {
    std::span<const double> distances_m;
    std::span<const double> powers_dbm;
    double pulse_width_ns;
};

enum class OtdrAnalysisError {
    InvalidTraceData,
    TraceTooShort
};

class OtdrAnalyzer {
public:
    static std::expected<std::vector<OtdrEvent>, OtdrAnalysisError>
    analyze(const OtdrTraceView& trace, double noise_floor_dbm = -100.0) {
        if (trace.distances_m.size() != trace.powers_dbm.size()) {
            return std::unexpected(OtdrAnalysisError::InvalidTraceData);
        }
        if (trace.distances_m.size() < 5) {
            return std::unexpected(OtdrAnalysisError::TraceTooShort);
        }

        std::vector<OtdrEvent> events;
        constexpr double backscatter_slope = 0.0002;

        const size_t n = trace.distances_m.size();
        for (size_t i = 2; i < n - 2; ++i) {
            const double dist = trace.distances_m[i];
            const double p_prev = trace.powers_dbm[i - 1];
            const double p_curr = trace.powers_dbm[i];
            const double p_next = trace.powers_dbm[i + 1];

            if (p_curr <= noise_floor_dbm && p_prev > noise_floor_dbm) {
                events.push_back(OtdrEvent{
                    .distance_m = dist,
                    .type = OtdrEventType::FiberEnd,
                    .loss_db = p_prev - noise_floor_dbm,
                    .return_loss_db = 0.0
                });
                break;
            }

            if (p_curr > p_prev + 0.5 && p_curr > p_next + 0.5) {
                const double p_after = trace.powers_dbm[i + 3];
                const double loss = p_prev - p_after;
                const double rl = p_curr - p_prev + 10.0 * std::log10(trace.pulse_width_ns);

                events.push_back(OtdrEvent{
                    .distance_m = dist,
                    .type = OtdrEventType::Connector,
                    .loss_db = loss,
                    .return_loss_db = rl
                });
                i += 3;
                continue;
            }

            const double step = p_prev - p_next - (trace.distances_m[i + 1] - trace.distances_m[i - 1]) * backscatter_slope;
            if (std::abs(step) >= 0.03) {
                events.push_back(OtdrEvent{
                    .distance_m = dist,
                    .type = (step > 0) ? OtdrEventType::SpliceFusion : OtdrEventType::Gainer,
                    .loss_db = step,
                    .return_loss_db = 0.0
                });
                i += 2;
            }
        }

        return events;
    }

    static std::string_view event_type_to_string(OtdrEventType type) noexcept {
        switch (type) {
            case OtdrEventType::SpliceFusion: return "Зварний шов";
            case OtdrEventType::Connector:    return "Конектор";
            case OtdrEventType::Gainer:       return "Гейнер (підйом)";
            case OtdrEventType::FiberEnd:     return "Кінець волокна";
        }
        return "Невідомо";
    }
};

int main() {
    const std::vector<double> dists = {0, 500, 999, 1000, 1001, 1500, 1999, 2000, 2001, 2005, 2500, 3000};
    const std::vector<double> powers = {0.0, -0.1, -0.2, -0.25, -0.25, -0.35, -0.45, +12.0, -0.85, -0.86, -0.96, -110.0};

    OtdrTraceView trace{
        .distances_m = dists,
        .powers_dbm = powers,
        .pulse_width_ns = 50.0
    };

    auto result = OtdrAnalyzer::analyze(trace);
    if (!result) {
        std::cerr << "Помилка аналізу OTDR-траси!\n";
        return 1;
    }

    std::cout << "Знайдено оптичних подій: " << result->size() << "\n";
    for (const auto& ev : *result) {
        std::cout << "Подія на " << ev.distance_m << " м: "
                  << "тип=" << OtdrAnalyzer::event_type_to_string(ev.type)
                  << ", втрати=" << ev.loss_db << " дБ"
                  << ", RL=" << ev.return_loss_db << " дБ\n";
    }

    return 0;
}
