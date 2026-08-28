#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>

struct CmcFilterSpec {
    double f_noise_hz;
    double target_att_db;
    double cy_farad;
    double cx_farad;
    double leak_ratio{0.015};     // 1.5% для секційної намотки
    double i_rms_amp{1.0};
    double dcr_ohm{0.25};
    double v_grid_rms{230.0};
    double f_grid_hz{50.0};
};

struct CmcFilterResult {
    double l_cm_henry;
    double l_leak_henry;
    double fc_cm_hz;
    double fc_dm_hz;
    double i_leak_ma;
    double p_loss_watts;
};

enum class FilterError {
    InvalidFrequency,
    InvalidCapacitance,
    ExcessiveLeakageCurrent
};

[[nodiscard]] constexpr std::expected<CmcFilterResult, FilterError>
design_mains_filter(const CmcFilterSpec& spec) noexcept
{
    if (spec.f_noise_hz <= 0.0 || spec.target_att_db <= 0.0) {
        return std::unexpected(FilterError::InvalidFrequency);
    }
    if (spec.cy_farad <= 0.0 || spec.cx_farad <= 0.0) {
        return std::unexpected(FilterError::InvalidCapacitance);
    }

    const double att_linear = std::pow(10.0, spec.target_att_db / 20.0);
    const double fc_cm = spec.f_noise_hz / std::sqrt(att_linear);

    constexpr double pi = std::numbers::pi;
    const double l_cm = 1.0 / (8.0 * pi * pi * fc_cm * fc_cm * spec.cy_farad);
    const double l_leak = l_cm * spec.leak_ratio;
    const double fc_dm = 1.0 / (2.0 * pi * std::sqrt(l_leak * spec.cx_farad));

    const double i_leak_ma = (2.0 * pi * spec.f_grid_hz * spec.v_grid_rms * (2.0 * spec.cy_farad)) * 1000.0;
    if (i_leak_ma > 3.5) {
        return std::unexpected(FilterError::ExcessiveLeakageCurrent);
    }

    const double p_loss = 2.0 * spec.i_rms_amp * spec.i_rms_amp * spec.dcr_ohm;

    return CmcFilterResult{
        .l_cm_henry = l_cm,
        .l_leak_henry = l_leak,
        .fc_cm_hz = fc_cm,
        .fc_dm_hz = fc_dm,
        .i_leak_ma = i_leak_ma,
        .p_loss_watts = p_loss
    };
}
