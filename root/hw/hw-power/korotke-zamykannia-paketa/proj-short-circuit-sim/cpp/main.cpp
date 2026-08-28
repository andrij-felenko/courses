#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>

struct PackSimConfig {
    double v_ocv{67.2};              // Напруга холостого ходу пакета, В
    double l_loop{600e-9};           // Паразитна індуктивність контуру, Гн
    double r_cells{0.030};           // Внутрішній опір комірок, Ом
    double r_bus_base{0.010};        // Базовий опір шин та дротів за 20 °C, Ом
    double r_dson_base{0.002};       // Опір каналу всіх паралельних MOSFET за 25 °C, Ом
    double r_shunt{0.001};           // Опір струмовимірювального шунта, Ом
    double r_fault{0.001};           // Опір перемички КЗ, Ом
    double i2t_fuse_rating{1200.0};  // Номінальний I²t розплавлення запобіжника, А²·с
    double i2t_pcb_rating{2200.0};   // Граничний I²t доріжки друкованої плати, А²·с
    double scp_delay_sec{25e-6};     // Затримка апаратного компаратора BMS, с
    double mosfet_toff_sec{5e-6};    // Час спаду струму затвора при вимкненні, с
    double c_th_die{0.35};           // Теплоємність кристала кремнію MOSFET, Дж/°C
    double t_j_max{175.0};           // Максимально допустима температура кристала, °C
};

struct SimResult {
    double time_sec{0.0};
    double current{0.0};
    double i2t_accumulated{0.0};
    double t_junction{25.0};
    double v_ds_peak{0.0};
    bool fuse_blown{false};
    bool pcb_damaged{false};
    bool mosfet_destroyed{false};
    bool bms_tripped{false};
};

class BatteryShortCircuitSimulator {
public:
    explicit constexpr BatteryShortCircuitSimulator(PackSimConfig config) noexcept
        : cfg_{config} {}

    [[nodiscard]] SimResult simulate(double dt = 0.1e-6, double t_max = 500e-6) const noexcept {
        SimResult res{};
        res.v_ds_peak = cfg_.v_ocv;

        double current = 0.0;
        double t = 0.0;
        bool bms_opening = false;
        double bms_open_progress = 0.0;

        while (t < t_max) {
            const double r_dson = cfg_.r_dson_base * (1.0 + 0.005 * (res.t_junction - 25.0));
            const double r_bus = cfg_.r_bus_base * (1.0 + 0.00393 * (res.t_junction - 25.0));
            double r_active_dson = r_dson;

            if (bms_opening) {
                bms_open_progress += dt / cfg_.mosfet_toff_sec;
                if (bms_open_progress >= 1.0) {
                    bms_open_progress = 1.0;
                }
                r_active_dson = r_dson / (1.0 - 0.999 * bms_open_progress);
            }

            const double r_total = cfg_.r_cells + r_bus + r_active_dson + cfg_.r_shunt + cfg_.r_fault;
            const double di_dt = (cfg_.v_ocv - current * r_total) / cfg_.l_loop;

            current += di_dt * dt;
            if (current < 0.0) {
                current = 0.0;
            }

            res.i2t_accumulated += (current * current) * dt;

            const double p_loss_die = (current * current) * r_active_dson;
            res.t_junction += (p_loss_die / cfg_.c_th_die) * dt;

            if (res.t_junction >= cfg_.t_j_max && !res.mosfet_destroyed) {
                res.mosfet_destroyed = true;
            }

            if (res.i2t_accumulated >= cfg_.i2t_pcb_rating && !res.pcb_damaged) {
                res.pcb_damaged = true;
            }

            if (res.i2t_accumulated >= cfg_.i2t_fuse_rating && !res.fuse_blown) {
                res.fuse_blown = true;
                break;
            }

            if (t >= cfg_.scp_delay_sec && !res.bms_tripped && !bms_opening) {
                bms_opening = true;
                res.bms_tripped = true;
            }

            if (bms_opening && di_dt < 0.0) {
                const double v_spike = cfg_.v_ocv + cfg_.l_loop * std::abs(di_dt);
                if (v_spike > res.v_ds_peak) {
                    res.v_ds_peak = v_spike;
                }
            }

            if (bms_opening && bms_open_progress >= 1.0 && current < 1.0) {
                break;
            }

            t += dt;
        }

        res.time_sec = t;
        res.current = current;
        return res;
    }

private:
    PackSimConfig cfg_;
};

int main() {
    constexpr PackSimConfig config{};
    const BatteryShortCircuitSimulator sim{config};
    const SimResult r = sim.simulate();

    std::cout << "=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ КЗ БАТАРЕЇ 16S (67.2 В) ===\n"
              << std::fixed << std::setprecision(2)
              << "Час процесу:          " << (r.time_sec * 1e6) << " мкс\n"
              << "Накопичений I²t:      " << r.i2t_accumulated << " А²·с\n"
              << "Температура MOSFET:   " << r.t_junction << " °C\n"
              << "Піковий викид V_ds:   " << r.v_ds_peak << " В\n"
              << "BMS відсічка:         " << (r.bms_tripped ? "СПРАЦЮВАЛА" : "НІ") << '\n'
              << "Стан MOSFET:          " << (r.mosfet_destroyed ? "ПРОБИТО (ТЕПЛОВИЙ ВИБУХ)" : "ВЦІЛІЛИ") << '\n'
              << "Стан запобіжника:     " << (r.fuse_blown ? "ПЕРЕГОРІВ" : "ЦІЛИЙ") << '\n'
              << "Стан плати (PCB):     " << (r.pcb_damaged ? "ЗГОРІЛА" : "ВЦІЛІЛА") << '\n';

    return 0;
}
