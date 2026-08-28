#include <iostream>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <expected>

namespace rf {

struct TxConfig {
    double power_dbm{14.0};       // Вихідна потужність (dBm)
    double cable_loss_db{1.0};    // Втрати кабелю (dB)
    double antenna_gain_dbi{2.15};// Підсилення антени (dBi)

    [[nodiscard]] constexpr double eirp() const noexcept {
        return power_dbm - cable_loss_db + antenna_gain_dbi;
    }
};

struct ChannelConfig {
    double frequency_mhz{868.0};  // Несуча частота (МГц)
    double distance_km{10.0};     // Відстань між вузлами (км)
    double atm_loss_db{0.5};      // Поглинання атмосферою (dB)
    double fade_margin_db{10.0};  // Запас на завмирання (dB)
    double misc_loss_db{1.5};     // Додаткові втрати (dB)

    [[nodiscard]] double fspl() const noexcept {
        return 20.0 * std::log10(distance_km) + 20.0 * std::log10(frequency_mhz) + 32.44;
    }

    [[nodiscard]] double total_path_loss() const noexcept {
        return fspl() + atm_loss_db + fade_margin_db + misc_loss_db;
    }
};

struct RxConfig {
    double antenna_gain_dbi{2.15};// Підсилення антени (dBi)
    double cable_loss_db{1.0};    // Втрати кабелю (dB)
    double bandwidth_hz{125000.0};// Смуга частот (Гц)
    double noise_figure_db{6.0};  // Коефіцієнт шуму (dB)
    double snr_min_db{-10.0};     // Поріг демодуляції (dB)

    [[nodiscard]] double thermal_noise_floor() const noexcept {
        return -173.98 + 10.0 * std::log10(bandwidth_hz);
    }

    [[nodiscard]] double sensitivity() const noexcept {
        return thermal_noise_floor() + noise_figure_db + snr_min_db;
    }
};

struct LinkResult {
    double eirp_dbm;
    double fspl_db;
    double path_loss_total_db;
    double rx_power_dbm;
    double sensitivity_dbm;
    double margin_db;
    double max_distance_km;
    bool is_viable;
};

enum class LinkError {
    InvalidFrequency,
    InvalidDistance,
    InvalidBandwidth
};

[[nodiscard]] std::expected<LinkResult, LinkError> 
calculate_budget(const TxConfig& tx, const ChannelConfig& ch, const RxConfig& rx) noexcept {
    if (ch.frequency_mhz <= 0.0) return std::unexpected(LinkError::InvalidFrequency);
    if (ch.distance_km <= 0.0)  return std::unexpected(LinkError::InvalidDistance);
    if (rx.bandwidth_hz <= 0.0) return std::unexpected(LinkError::InvalidBandwidth);

    LinkResult res;
    res.eirp_dbm = tx.eirp();
    res.fspl_db = ch.fspl();
    res.path_loss_total_db = ch.total_path_loss();
    res.rx_power_dbm = res.eirp_dbm - res.path_loss_total_db + rx.antenna_gain_dbi - rx.cable_loss_db;
    res.sensitivity_dbm = rx.sensitivity();
    res.margin_db = res.rx_power_dbm - res.sensitivity_dbm;
    res.is_viable = (res.margin_db >= 0.0);

    double fspl_max_db = res.eirp_dbm - ch.atm_loss_db - ch.fade_margin_db 
                         - ch.misc_loss_db + rx.antenna_gain_dbi - rx.cable_loss_db 
                         - res.sensitivity_dbm;

    double exp_val = (fspl_max_db - 20.0 * std::log10(ch.frequency_mhz) - 32.44) / 20.0;
    res.max_distance_km = std::pow(10.0, exp_val);

    return res;
}

} // namespace rf

int main() {
    rf::TxConfig tx{.power_dbm = 14.0, .cable_loss_db = 1.0, .antenna_gain_dbi = 2.15};
    rf::ChannelConfig ch{.frequency_mhz = 868.0, .distance_km = 10.0, .fade_margin_db = 10.0};
    rf::RxConfig rx{.bandwidth_hz = 125000.0, .snr_min_db = -10.0};

    auto budget_opt = rf::calculate_budget(tx, ch, rx);
    if (!budget_opt) {
        std::cerr << "Некоректні вхідні параметри радіолінії!\n";
        return 1;
    }

    const auto& res = budget_opt.value();

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ОБЧИСЛЕННЯ БЮДЖЕТУ РАДІОЛІНІЇ (C++23) ===\n";
    std::cout << "EIRP:                  " << std::showpos << res.eirp_dbm << " dBm\n";
    std::cout << "Втрати простору FSPL:  " << std::noshowpos << res.fspl_db << " dB\n";
    std::cout << "Прийнята потужність:  " << std::showpos << res.rx_power_dbm << " dBm\n";
    std::cout << "Поріг чутливості:      " << std::showpos << res.sensitivity_dbm << " dBm\n";
    std::cout << "Запас лінії (Margin):  " << std::showpos << res.margin_db << " dB "
              << (res.is_viable ? "[OK]" : "[FAIL]") << "\n";
    std::cout << "Гранична дальність:    " << std::noshowpos << res.max_distance_km << " км\n";

    return 0;
}
