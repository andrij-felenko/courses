// Файл: rf_link_budget.hpp
#ifndef RF_LINK_BUDGET_HPP
#define RF_LINK_BUDGET_HPP

#include <expected>
#include <cmath>
#include <span>

namespace rf {

enum class Status {
    Ok = 0,
    InvalidParam = -1,
    FreqOutOfRange = -2,
    ZeroDistance = -3
};

struct TxParams {
    float power_dbm{14.0f};
    float tx_cable_loss_db{0.5f};
    float antenna_gain_dbi{2.15f};

    [[nodiscard]] constexpr float eirp() const noexcept {
        return power_dbm - tx_cable_loss_db + antenna_gain_dbi;
    }
};

struct RxParams {
    float rx_antenna_gain_dbi{2.15f};
    float rx_cable_loss_db{0.5f};
    float bandwidth_hz{125000.0f};
    float noise_figure_db{5.0f};
    float required_snr_db{-10.0f};

    [[nodiscard]] float sensitivity() const noexcept {
        float thermal_floor = -173.98f + 10.0f * std::log10(bandwidth_hz);
        return thermal_floor + noise_figure_db + required_snr_db;
    }
};

struct ChannelParams {
    float frequency_mhz{868.0f};
    float distance_km{5.0f};
    float atmospheric_loss_db{0.2f};
    float fading_margin_db{10.0f};
    float polarization_loss_db{0.0f};

    [[nodiscard]] float fspl() const noexcept {
        return 20.0f * std::log10(distance_km) + 20.0f * std::log10(frequency_mhz) + 32.44f;
    }

    [[nodiscard]] float total_path_loss() const noexcept {
        return fspl() + atmospheric_loss_db + fading_margin_db + polarization_loss_db;
    }
};

struct BudgetReport {
    float eirp_dbm;
    float fspl_db;
    float total_path_loss_db;
    float rx_power_dbm;
    float sensitivity_dbm;
    float link_margin_db;
    float max_range_km;
};

class LinkPlanner {
public:
    [[nodiscard]] static std::expected<BudgetReport, Status> 
    compute(const TxParams& tx, const ChannelParams& ch, const RxParams& rx) noexcept {
        if (ch.frequency_mhz <= 0.0f) return std::unexpected(Status::FreqOutOfRange);
        if (ch.distance_km <= 0.0f)  return std::unexpected(Status::ZeroDistance);

        BudgetReport rep;
        rep.eirp_dbm = tx.eirp();
        rep.fspl_db = ch.fspl();
        rep.total_path_loss_db = ch.total_path_loss();
        rep.rx_power_dbm = rep.eirp_dbm - rep.total_path_loss_db + rx.rx_antenna_gain_dbi - rx.rx_cable_loss_db;
        rep.sensitivity_dbm = rx.sensitivity();
        rep.link_margin_db = rep.rx_power_dbm - rep.sensitivity_dbm;

        float fspl_max = rep.eirp_dbm - ch.atmospheric_loss_db - ch.fading_margin_db 
                         - ch.polarization_loss_db + rx.rx_antenna_gain_dbi - rx.rx_cable_loss_db 
                         - rep.sensitivity_dbm;

        float exp_v = (fspl_max - 20.0f * std::log10(ch.frequency_mhz) - 32.44f) / 20.0f;
        rep.max_range_km = std::pow(10.0f, exp_v);

        return rep;
    }
};

} // namespace rf

#endif // RF_LINK_BUDGET_HPP
