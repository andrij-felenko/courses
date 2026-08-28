#include <iostream>
#include <iomanip>
#include <algorithm>
#include <string_view>

struct BatterySpec {
    double voltage_v{3.0};
    double capacity_mah{2400.0};
    double self_discharge_pct_year{1.0};
    double capacity_retention_factor{0.85};

    [[nodiscard]] constexpr double effective_capacity_mah() const noexcept {
        return capacity_mah * capacity_retention_factor;
    }

    [[nodiscard]] constexpr double self_discharge_leak_ua() const noexcept {
        return (effective_capacity_mah() * (self_discharge_pct_year / 100.0) * 1000.0) / 8760.0;
    }
};

struct TransceiverSpec {
    double deep_sleep_current_ua{10.0};
    double light_sleep_current_ma{1.2};
    double cpu_active_current_ma{20.0};
    double rx_current_ma{75.0};
    double tx_current_ma{240.0};
    double xtal_settle_time_ms{1.5};
    double rtc_drift_ppm{50.0};
};

struct SimulationResult {
    double cycle_charge_uc{0.0};
    double average_current_ua{0.0};
    double lifetime_days{0.0};
    double lifetime_years{0.0};
};

class WiFiPowerSimulator {
public:
    explicit constexpr WiFiPowerSimulator(BatterySpec battery, TransceiverSpec transceiver) noexcept
        : battery_(battery), trx_(transceiver) {}

    [[nodiscard]] SimulationResult simulate_cold_boot(double interval_seconds) const noexcept {
        const double q_active_uc = 40.0 * 20.0 + 200.0 * 75.0 + 120.0 * 95.0 + 1200.0 * 70.0 + 20.0 * 220.0;
        const double t_active_s = (40.0 + 200.0 + 120.0 + 1200.0 + 20.0) / 1000.0;
        const double t_sleep_s = std::max(0.0, interval_seconds - t_active_s);
        const double q_sleep_uc = (trx_.deep_sleep_current_ua / 1000.0) * (t_sleep_s * 1000.0);
        return compute_metrics(q_active_uc + q_sleep_uc, interval_seconds);
    }

    [[nodiscard]] SimulationResult simulate_fast_reconnect(double interval_seconds) const noexcept {
        const double q_active_uc = 5.0 * 15.0 + 35.0 * 85.0 + 15.0 * 220.0;
        const double t_active_s = (5.0 + 35.0 + 15.0) / 1000.0;
        const double t_sleep_s = std::max(0.0, interval_seconds - t_active_s);
        const double q_sleep_uc = (trx_.deep_sleep_current_ua / 1000.0) * (t_sleep_s * 1000.0);
        return compute_metrics(q_active_uc + q_sleep_uc, interval_seconds);
    }

    [[nodiscard]] SimulationResult simulate_dtim_light_sleep(int dtim_multiplier, double interval_seconds) const noexcept {
        const double t_dtim_s = dtim_multiplier * 0.1024;
        const double t_guard_ms = 2.0 * t_dtim_s * trx_.rtc_drift_ppm * 0.001 + trx_.xtal_settle_time_ms;
        constexpr double t_beacon_rx_ms = 1.2;

        const double q_beacon_uc = trx_.cpu_active_current_ma * trx_.xtal_settle_time_ms 
                                 + trx_.rx_current_ma * (t_guard_ms + t_beacon_rx_ms);
        const double q_dtim_sleep_uc = trx_.light_sleep_current_ma * (t_dtim_s * 1000.0 - (t_guard_ms + t_beacon_rx_ms));
        const double i_background_ma = (q_beacon_uc + q_dtim_sleep_uc) / (t_dtim_s * 1000.0);

        constexpr double q_tx_event_uc = 15.0 * 220.0;
        const double q_total_uc = (i_background_ma * interval_seconds * 1000.0) + q_tx_event_uc;
        return compute_metrics(q_total_uc, interval_seconds);
    }

    [[nodiscard]] SimulationResult simulate_wifi6_twt(double interval_seconds) const noexcept {
        constexpr double q_sp_uc = 10.0 * 70.0 + 5.0 * 220.0;
        constexpr double t_active_s = 15.0 / 1000.0;
        const double t_sleep_s = std::max(0.0, interval_seconds - t_active_s);
        const double q_sleep_uc = (trx_.deep_sleep_current_ua / 1000.0) * (t_sleep_s * 1000.0);
        return compute_metrics(q_sp_uc + q_sleep_uc, interval_seconds);
    }

private:
    [[nodiscard]] SimulationResult compute_metrics(double q_total_uc, double interval_seconds) const noexcept {
        SimulationResult res;
        res.cycle_charge_uc = q_total_uc;
        res.average_current_ua = (q_total_uc / (interval_seconds * 1000.0)) * 1000.0;

        const double eff_cap_mah = battery_.effective_capacity_mah();
        const double total_current_ma = (res.average_current_ua + battery_.self_discharge_leak_ua()) / 1000.0;
        const double life_hours = eff_cap_mah / total_current_ma;

        res.lifetime_days = life_hours / 24.0;
        res.lifetime_years = life_hours / 8760.0;
        return res;
    }

    BatterySpec battery_;
    TransceiverSpec trx_;
};

int main() {
    constexpr BatterySpec aa_cell{ 3.0, 2400.0, 1.0, 0.85 };
    constexpr TransceiverSpec esp32_spec{ 10.0, 1.2, 20.0, 75.0, 240.0, 1.5, 50.0 };
    constexpr double interval_s = 600.0; // 10 хвилин

    const WiFiPowerSimulator sim(aa_cell, esp32_spec);

    const auto print_row = [](std::string_view name, const SimulationResult& r) {
        std::cout << std::left << std::setw(30) << name << " | I_avg = " 
                  << std::right << std::setw(7) << std::fixed << std::setprecision(2) << r.average_current_ua << " uA | "
                  << "Життя = " << std::setw(6) << std::setprecision(1) << r.lifetime_days << " діб ("
                  << std::setw(4) << std::setprecision(2) << r.lifetime_years << " р)\n";
    };

    std::cout << "=== Порівняння стратегій живлення Wi-Fi (T_цикл = 10 хв, батарея 2400 мА·год) ===\n";
    print_row("Стратегія 1 (Cold Boot)", sim.simulate_cold_boot(interval_s));
    print_row("Стратегія 2 (Fast Reconnect)", sim.simulate_fast_reconnect(interval_s));
    print_row("Стратегія 3 (Light DTIM-3)", sim.simulate_dtim_light_sleep(3, interval_s));
    print_row("Стратегія 4 (Wi-Fi 6 TWT)", sim.simulate_wifi6_twt(interval_s));

    return 0;
}
