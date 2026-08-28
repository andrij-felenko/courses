#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <expected>
#include <string_view>

constexpr double SPEED_OF_LIGHT = 299792458.0;
constexpr double ITU_REF_FREQ_THZ = 193.10;
constexpr double PLANCK_CONST = 6.62607015e-34;
constexpr double OSNR_BW_HZ = 12.5e9;

struct DwdmChannel {
    int index;
    double frequency_thz;
    double wavelength_nm;
};

struct LinkSimulationResult {
    double total_distance_km;
    double final_osnr_db;
    double total_dispersion_ps_nm;
    double rx_power_dbm;
    bool is_viable;
};

class DwdmSimulator {
public:
    static std::vector<DwdmChannel> generateItuGrid(int num_channels, double start_m, double step_thz) {
        std::vector<DwdmChannel> channels;
        channels.reserve(num_channels);

        for (int i = 0; i < num_channels; ++i) {
            double m = start_m + static_cast<double>(i);
            double f_thz = ITU_REF_FREQ_THZ + m * step_thz;
            double f_hz = f_thz * 1.0e12;
            double lambda_m = SPEED_OF_LIGHT / f_hz;

            channels.push_back(DwdmChannel{
                .index = i + 1,
                .frequency_thz = f_thz,
                .wavelength_nm = lambda_m * 1.0e9
            });
        }
        return channels;
    }

    static LinkSimulationResult simulate(int num_spans, double span_len_km, double alpha_db_km,
                                         double disp_coeff, double tx_dbm, double edfa_nf_db,
                                         double mux_loss_db, double demux_loss_db) {
        const double total_dist = num_spans * span_len_km;
        const double total_disp = total_dist * disp_coeff;

        const double span_loss_db = span_len_km * alpha_db_km;
        const double gain_linear = std::pow(10.0, span_loss_db / 10.0);
        const double nf_linear = std::pow(10.0, edfa_nf_db / 10.0);

        const double p_in_dbm = tx_dbm - mux_loss_db - span_loss_db;
        const double p_in_watts = 1.0e-3 * std::pow(10.0, p_in_dbm / 10.0);

        const double f_hz = ITU_REF_FREQ_THZ * 1.0e12;
        const double p_ase_span = nf_linear * (gain_linear - 1.0) * PLANCK_CONST * f_hz * OSNR_BW_HZ;
        const double p_ase_total = p_ase_span * static_cast<double>(num_spans);

        const double osnr_linear = (p_in_watts * gain_linear) / p_ase_total;
        const double final_osnr_db = 10.0 * std::log10(osnr_linear);

        const double rx_power = tx_dbm - mux_loss_db - demux_loss_db;

        const bool viable = (final_osnr_db >= 18.0) && (std::abs(total_disp) <= 8000.0);

        return LinkSimulationResult{
            .total_distance_km = total_dist,
            .final_osnr_db = final_osnr_db,
            .total_dispersion_ps_nm = total_disp,
            .rx_power_dbm = rx_power,
            .is_viable = viable
        };
    }
};

int main() {
    constexpr int num_channels = 40;
    const auto grid = DwdmSimulator::generateItuGrid(num_channels, -20.0, 0.1);

    std::cout << "=== ITU-T DWDM Grid (Перші 5 каналів із " << num_channels << ") ===\n";
    std::cout << std::fixed << std::setprecision(2);
    for (int i = 0; i < 5; ++i) {
        std::cout << "Канал " << std::setw(2) << std::setfill('0') << grid[i].index
                  << ": " << grid[i].frequency_thz << " ТГц | "
                  << grid[i].wavelength_nm << " нм\n";
    }

    const auto res = DwdmSimulator::simulate(5, 80.0, 0.22, 17.0, 0.0, 5.5, 4.0, 4.0);

    std::cout << "\n=== Результати моделювання оптичного тракту ===\n";
    std::cout << "Загальна відстань: " << res.total_distance_km << " км (5 прольотів по 80 км)\n";
    std::cout << "Підсумковий OSNR:   " << res.final_osnr_db << " дБ (поріг: >= 18.0 дБ)\n";
    std::cout << "Сумарна дисперсія:  " << res.total_dispersion_ps_nm << " пс/нм\n";
    std::cout << "Потужність на Rx:   " << res.rx_power_dbm << " дБм\n";
    std::cout << "Статус магістралі:  " << (res.is_viable ? "ПРОЙДЕНО (ОК)" : "ПОМИЛКА (Потрібен DSP/EDFA)") << '\n';

    return 0;
}
