#include <iostream>
#include <algorithm>

class WiFiEnergyModel {
public:
    static constexpr double calculate_average_current_ua(
        double active_charge_uc,
        double sleep_current_ua,
        double interval_seconds) noexcept 
    {
        if (interval_seconds <= 0.0) return 0.0;
        const double sleep_charge_uc = sleep_current_ua * interval_seconds;
        return (active_charge_uc + sleep_charge_uc) / interval_seconds;
    }

    static constexpr double estimate_lifetime_years(
        double nominal_capacity_mah,
        double capacity_derating,
        double annual_self_discharge_pct,
        double average_current_ua) noexcept 
    {
        const double effective_capacity_mah = nominal_capacity_mah * capacity_derating;
        const double self_discharge_current_ua = 
            (effective_capacity_mah * (annual_self_discharge_pct / 100.0) * 1000.0) / 8760.0;
        const double total_load_ma = (average_current_ua + self_discharge_current_ua) / 1000.0;
        
        if (total_load_ma <= 0.0) return 0.0;
        return effective_capacity_mah / (total_load_ma * 8760.0);
    }
};
