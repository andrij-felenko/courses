#include <stdio.h>

/* Розрахунок середнього струму Wi-Fi вузла в мікроамперах */
double wifi_calc_average_current_ua(double q_active_uc, double i_sleep_ua, double interval_s) {
    if (interval_s <= 0.0) return 0.0;
    double t_sleep_s = interval_s; /* Наближення для t_active << interval_s */
    double q_sleep_uc = i_sleep_ua * t_sleep_s;
    double q_total_uc = q_active_uc + q_sleep_uc;
    return q_total_uc / interval_s;
}

/* Розрахунок прогнозованого терміну служби батареї в роках */
double wifi_calc_battery_years(double cap_mah, double k_use, double self_leak_pct, double i_avg_ua) {
    double eff_cap_mah = cap_mah * k_use;
    double leak_ua = (eff_cap_mah * (self_leak_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (i_avg_ua + leak_ua) / 1000.0;
    if (total_current_ma <= 0.0) return 0.0;
    return eff_cap_mah / (total_current_ma * 8760.0);
}
