#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <string_view>
#include <numbers>
#include <optional>

namespace gnss {

inline constexpr double SPEED_OF_LIGHT = 299792458.0;
inline constexpr double FREQ_GPS_L1 = 1575.42e6;
inline constexpr double LAMBDA_L1 = SPEED_OF_LIGHT / FREQ_GPS_L1;
inline constexpr double CHIP_RATE_CA = 1.023e6;
inline constexpr double THERMAL_NOISE_DENSITY = -174.0; // дБм/Гц при 290 K

enum class JammerType {
    BarrageNoise,
    ContinuousWave,
    ChirpSwept,
    Pulsed
};

struct JammerProfile {
    JammerType type{JammerType::ChirpSwept};
    double power_watts{10.0};
    double tx_gain_dbi{3.0};
    double bandwidth_hz{30.0e6};
    double duty_cycle{1.0};

    [[nodiscard]] constexpr double spectral_factor_q() const noexcept {
        switch (type) {
            case JammerType::BarrageNoise:  return 1.1;
            case JammerType::ContinuousWave: return 0.7;
            case JammerType::ChirpSwept:    return 1.8;
            case JammerType::Pulsed:        return 1.4;
        }
        return 1.0;
    }

    [[nodiscard]] constexpr std::string_view type_name() const noexcept {
        switch (type) {
            case JammerType::BarrageNoise:  return "Barrage Noise";
            case JammerType::ContinuousWave: return "CW Tone";
            case JammerType::ChirpSwept:    return "Chirp/Swept-CW";
            case JammerType::Pulsed:        return "Pulsed Jammer";
        }
        return "Unknown";
    }
};

struct ReceiverProfile {
    double sat_power_dbm{-130.0};
    double rx_noise_fig_db{2.5};
    double rx_gain_dbi{0.0};
    double acq_threshold_js{27.0};
    double trk_threshold_js{45.0};
};

struct JammingZoneRadii {
    double acquisition_block_radius_m{0.0};
    double tracking_loss_radius_m{0.0};
};

struct LinkBudgetAssessment {
    double distance_m{0.0};
    double fspl_db{0.0};
    double received_jammer_dbm{0.0};
    double jammer_to_signal_db{0.0};
    double effective_cn0_db_hz{0.0};
    double adc_clipping_ratio{0.0};
    bool is_acquisition_blocked{false};
    bool is_tracking_lost{false};
};

class JammingSimulator {
public:
    explicit JammingSimulator(JammerProfile jammer, ReceiverProfile receiver = {})
        : jammer_(jammer), receiver_(receiver) {}

    [[nodiscard]] static double calculate_fspl(double distance_m) noexcept {
        distance_m = std::max(distance_m, 1.0);
        return 20.0 * std::log10(distance_m) + 
               20.0 * std::log10(4.0 * std::numbers::pi / LAMBDA_L1);
    }

    [[nodiscard]] LinkBudgetAssessment evaluate_at_distance(double distance_m) const noexcept {
        LinkBudgetAssessment assessment;
        assessment.distance_m = distance_m;
        assessment.fspl_db = calculate_fspl(distance_m);

        const double jammer_eirp_dbm = 10.0 * std::log10(jammer_.power_watts * 1000.0) + jammer_.tx_gain_dbi;
        assessment.received_jammer_dbm = jammer_eirp_dbm + receiver_.rx_gain_dbi - assessment.fspl_db;
        assessment.jammer_to_signal_db = assessment.received_jammer_dbm - receiver_.sat_power_dbm;

        // Номінальне та ефективне C/N0 за моделлю Беца
        const double cn0_nom_db_hz = receiver_.sat_power_dbm - THERMAL_NOISE_DENSITY - receiver_.rx_noise_fig_db;
        const double cn0_nom_lin = std::pow(10.0, cn0_nom_db_hz / 10.0);

        const double js_lin = std::pow(10.0, assessment.jammer_to_signal_db / 10.0);
        const double jammer_degradation = js_lin / (jammer_.spectral_factor_q() * CHIP_RATE_CA);

        const double cn0_eff_lin = 1.0 / ((1.0 / cn0_nom_lin) + jammer_degradation);
        assessment.effective_cn0_db_hz = 10.0 * std::log10(cn0_eff_lin);

        // Оцінка нелінійного кліпінгу АЦП
        if (assessment.received_jammer_dbm > -60.0) {
            assessment.adc_clipping_ratio = 1.0;
        } else if (assessment.received_jammer_dbm < -100.0) {
            assessment.adc_clipping_ratio = 0.33;
        } else {
            assessment.adc_clipping_ratio = 0.33 + 0.67 * ((assessment.received_jammer_dbm + 100.0) / 40.0);
        }

        assessment.is_acquisition_blocked = (assessment.jammer_to_signal_db >= receiver_.acq_threshold_js);
        assessment.is_tracking_lost = (assessment.jammer_to_signal_db >= receiver_.trk_threshold_js);

        return assessment;
    }

    [[nodiscard]] JammingZoneRadii compute_zones() const noexcept {
        const double jammer_eirp_dbm = 10.0 * std::log10(jammer_.power_watts * 1000.0) + jammer_.tx_gain_dbi;
        const double base_const = 20.0 * std::log10(4.0 * std::numbers::pi / LAMBDA_L1);

        const double max_p_j_acq = receiver_.sat_power_dbm + receiver_.acq_threshold_js;
        const double fspl_acq = jammer_eirp_dbm + receiver_.rx_gain_dbi - max_p_j_acq;
        const double r_acq = std::pow(10.0, (fspl_acq - base_const) / 20.0);

        const double max_p_j_trk = receiver_.sat_power_dbm + receiver_.trk_threshold_js;
        const double fspl_trk = jammer_eirp_dbm + receiver_.rx_gain_dbi - max_p_j_trk;
        const double r_trk = std::pow(10.0, (fspl_trk - base_const) / 20.0);

        return { r_acq, r_trk };
    }

private:
    JammerProfile jammer_;
    ReceiverProfile receiver_;
};

} // namespace gnss

int main() {
    using namespace gnss;

    const JammerProfile chirp_jammer{
        .type = JammerType::ChirpSwept,
        .power_watts = 10.0,
        .tx_gain_dbi = 3.0,
        .bandwidth_hz = 30.0e6,
        .duty_cycle = 1.0
    };

    const JammingSimulator simulator(chirp_jammer);
    const auto zones = simulator.compute_zones();

    const std::vector<double> test_distances = { 1000.0, 5000.0, 15000.0, 30000.0, 60000.0 };
    for (const double d : test_distances) {
        const auto res = simulator.evaluate_at_distance(d);
    }

    return 0;
}
