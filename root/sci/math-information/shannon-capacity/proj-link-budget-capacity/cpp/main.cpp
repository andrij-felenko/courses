#include <iostream>
#include <iomanip>
#include <string_view>
#include <vector>
#include <cmath>
#include <numbers>

struct LinkParams {
    std::string_view name;
    double freq_hz;        // несуча частота, Гц
    double bandwidth_hz;   // ширина смуги B, Гц
    double tx_power_dbm;   // потужність передавача P_tx, дБм
    double tx_gain_dbi;    // коефіцієнт підсилення антени передавача G_tx, дБі
    double rx_gain_dbi;    // коефіцієнт підсилення антени приймача G_rx, дБі
    double path_loss_db;   // сумарні втрати сигналу на трасі, дБ
    double noise_fig_db;   // коефіцієнт шуму приймача NF, дБ
    double shannon_gap_db; // розрив Шеннона для коду, дБ
};

struct LinkResult {
    double noise_floor_dbm; // поріг шуму у смузі, дБм
    double rx_power_dbm;    // потужність сигналу на вході приймача, дБм
    double snr_db;          // відношення сигнал/шум, дБ
    double snr_linear;      // відношення сигнал/шум у лінійній шкалі
    double capacity_bps;    // теоретична ємність Шеннона, біт/с
    double practical_bps;   // practical bit rate, біт/с
    double spectral_eff;    // спектральна ефективність, біт/с/Гц
};

class ShannonLinkCalculator {
public:
    static constexpr double ThermalNoiseDensityDbm = -174.0; // дБм/Гц при T = 290 K

    [[nodiscard]] static constexpr LinkResult calculate(const LinkParams& link) noexcept {
        LinkResult res{};
        
        // 1. Розрахунок порогу шуму: N_total = -174 + 10*log10(B) + NF
        res.noise_floor_dbm = ThermalNoiseDensityDbm + 10.0 * std::log10(link.bandwidth_hz) + link.noise_fig_db;
        
        // 2. Потужність на приймачі: P_rx = P_tx + G_tx + G_rx - PathLoss
        res.rx_power_dbm = link.tx_power_dbm + link.tx_gain_dbi + link.rx_gain_dbi - link.path_loss_db;
        
        // 3. Відношення сигнал/шум
        res.snr_db = res.rx_power_dbm - res.noise_floor_dbm;
        res.snr_linear = std::pow(10.0, res.snr_db / 10.0);
        
        // 4. Теоретична ємність за Шенноном: C = B * log2(1 + SNR)
        res.capacity_bps = link.bandwidth_hz * std::log2(1.0 + res.snr_linear);
        res.spectral_eff = res.capacity_bps / link.bandwidth_hz;
        
        // 5. Практична швидкість із розривом Гапа Gamma
        const double gap_linear = std::pow(10.0, link.shannon_gap_db / 10.0);
        res.practical_bps = link.bandwidth_hz * std::log2(1.0 + res.snr_linear / gap_linear);
        
        return res;
    }
};

void print_report(const LinkParams& p, const LinkResult& r) {
    std::cout << "====================================================\n"
              << "Сценарій: " << p.name << "\n"
              << "----------------------------------------------------\n"
              << std::fixed << std::setprecision(2)
              << "  Частота / смуга:       " << (p.freq_hz / 1e9) << " ГГц / " << (p.bandwidth_hz / 1e6) << " МГц\n"
              << "  Рівень шуму N_total:   " << r.noise_floor_dbm << " дБм\n"
              << "  Прийнятий сигнал P_rx: " << r.rx_power_dbm << " дБм\n"
              << "  Відношення SNR:        " << r.snr_db << " дБ (x" << std::setprecision(3) << r.snr_linear << ")\n"
              << std::setprecision(2)
              << "  Спектральна ефективн.: " << r.spectral_eff << " біт/с/Гц\n"
              << "  Ємність Шеннона C:     " << (r.capacity_bps / 1e6) << " Мбіт/с\n"
              << "  Практична швидкість:   " << (r.practical_bps / 1e6) << " Мбіт/с (розрив " << p.shannon_gap_db << " дБ)\n\n";
}

int main() {
    const std::vector<LinkParams> scenarios = {
        {
            .name = "Wi-Fi 6 (802.11ax, 5 ГГц, кімната 5 м)",
            .freq_hz = 5.18e9,
            .bandwidth_hz = 80.0e6,
            .tx_power_dbm = 20.0,
            .tx_gain_dbi = 3.0,
            .rx_gain_dbi = 3.0,
            .path_loss_db = 68.0,
            .noise_fig_db = 6.0,
            .shannon_gap_db = 2.0
        },
        {
            .name = "5G NR (Sub-6 GHz, міська забудова 800 м)",
            .freq_hz = 3.5e9,
            .bandwidth_hz = 100.0e6,
            .tx_power_dbm = 43.0,
            .tx_gain_dbi = 15.0,
            .rx_gain_dbi = 0.0,
            .path_loss_db = 112.0,
            .noise_fig_db = 7.0,
            .shannon_gap_db = 2.0
        },
        {
            .name = "LoRa (868 МГц, дальній лінк IoT 10 км)",
            .freq_hz = 868.0e6,
            .bandwidth_hz = 125.0e3,
            .tx_power_dbm = 14.0,
            .tx_gain_dbi = 2.0,
            .rx_gain_dbi = 2.0,
            .path_loss_db = 140.0,
            .noise_fig_db = 5.0,
            .shannon_gap_db = 1.5
        }
    };

    for (const auto& sc : scenarios) {
        const auto res = ShannonLinkCalculator::calculate(sc);
        print_report(sc, res);
    }
    return 0;
}
