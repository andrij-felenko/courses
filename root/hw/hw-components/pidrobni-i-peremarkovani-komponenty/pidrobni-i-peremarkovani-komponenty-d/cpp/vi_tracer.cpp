// vi_tracer.hpp / vi_tracer.cpp
#include <vector>
#include <array>
#include <span>
#include <cmath>
#include <algorithm>
#include <expected>
#include <string_view>

struct ViPoint {
    float voltage_v;
    float current_ma;
};

struct ViToleranceBand {
    float v_nom;
    float i_min_ma;
    float i_max_ma;
};

enum class TraceError {
    EmptyDataset,
    SizeMismatch,
    HardwareFault
};

struct TraceEvaluation {
    bool is_authentic{false};
    float max_deviation_ma{0.0f};
    std::size_t error_point_index{0};
};

class ViSignatureAnalyzer {
public:
    static constexpr float CurrentThresholdMa = 0.05f; // 50 uA tolerance

    [[nodiscard]] static std::expected<TraceEvaluation, TraceError>
    evaluate(std::span<const ViPoint> measured,
             std::span<const ViToleranceBand> golden_envelope) noexcept {
        if (measured.empty() || golden_envelope.empty()) {
            return std::unexpected(TraceError::EmptyDataset);
        }
        if (measured.size() != golden_envelope.size()) {
            return std::unexpected(TraceError::SizeMismatch);
        }

        TraceEvaluation result{.is_authentic = true, .max_deviation_ma = 0.0f, .error_point_index = 0};

        for (std::size_t i = 0; i < measured.size(); ++i) {
            const auto& m = measured[i];
            const auto& g = golden_envelope[i];

            float deviation = 0.0f;
            if (m.current_ma < g.i_min_ma) {
                deviation = g.i_min_ma - m.current_ma;
            } else if (m.current_ma > g.i_max_ma) {
                deviation = m.current_ma - g.i_max_ma;
            }

            result.max_deviation_ma = std::max(result.max_deviation_ma, deviation);

            if (deviation > CurrentThresholdMa) {
                result.is_authentic = false;
                result.error_point_index = i;
                return result; // Швидкий вихід при виявленні браку
            }
        }

        return result;
    }
};
