#include <stdio.h>
#include <stdbool.h>

typedef struct {
    double v_bat;               /* Напруга батареї, В */
    double cap_mah;             /* Паспортна ємність, мА·год */
    double self_discharge_pct;  /* Річний саморозряд, % */
    double k_use;               /* Коефіцієнт корисної ємності */
} BatterySpec;

typedef struct {
    double i_deep_sleep_ua;     /* Струм Deep-Sleep, мкА */
    double i_light_sleep_ma;    /* Струм Light-Sleep, мА */
    double i_cpu_active_ma;     /* Струм CPU Modem-Sleep, мА */
    double i_rx_ma;             /* Струм прийому RX, мА */
    double i_tx_ma;             /* Струм передачі TX (+18 dBm), мА */
    double t_xtal_settle_ms;    /* Час стабілізації PLL кварцу, мс */
    double rtc_drift_ppm;       /* Температурний дрейф RTC кварцу, ppm */
} TransceiverSpec;

typedef struct {
    double q_cycle_uc;          /* Заряд на один цикл, мкКл (мА·мс) */
    double i_avg_ua;            /* Середній струм споживання, мкА */
    double life_days;           /* Час автономної роботи, діб */
    double life_years;          /* Час автономної роботи, років */
} SimResult;

SimResult sim_cold_boot(const BatterySpec *bat, const TransceiverSpec *trx, double interval_s) {
    /* Фази: Boot (40мс/20мА), Scan 13ch (200мс/75мА), Assoc+WPA (120мс/95мА), DHCP (1200мс/70мА), TX Data (20мс/220мА) */
    double q_active_uc = 40.0 * 20.0 + 200.0 * 75.0 + 120.0 * 95.0 + 1200.0 * 70.0 + 20.0 * 220.0;
    double t_active_s = (40.0 + 200.0 + 120.0 + 1200.0 + 20.0) / 1000.0;
    double t_sleep_s = (interval_s > t_active_s) ? (interval_s - t_active_s) : 0.0;
    double q_sleep_uc = (trx->i_deep_sleep_ua / 1000.0) * (t_sleep_s * 1000.0);
    double q_total_uc = q_active_uc + q_sleep_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

SimResult sim_fast_reconnect(const BatterySpec *bat, const TransceiverSpec *trx, double interval_s) {
    /* Фази: Wake RTC (5мс/15мА), Ch Assoc PMKSA (35мс/85мА), Static IP TX (15мс/220мА) */
    double q_active_uc = 5.0 * 15.0 + 35.0 * 85.0 + 15.0 * 220.0;
    double t_active_s = (5.0 + 35.0 + 15.0) / 1000.0;
    double t_sleep_s = (interval_s > t_active_s) ? (interval_s - t_active_s) : 0.0;
    double q_sleep_uc = (trx->i_deep_sleep_ua / 1000.0) * (t_sleep_s * 1000.0);
    double q_total_uc = q_active_uc + q_sleep_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

SimResult sim_dtim_light_sleep(const BatterySpec *bat, const TransceiverSpec *trx, int dtim, double interval_s) {
    double t_dtim_s = dtim * 0.1024;
    double t_guard_ms = 2.0 * t_dtim_s * trx->rtc_drift_ppm * 0.001 + trx->t_xtal_settle_ms;
    double t_beacon_rx_ms = 1.2;
    double q_beacon_uc = trx->i_cpu_active_ma * trx->t_xtal_settle_ms + trx->i_rx_ma * (t_guard_ms + t_beacon_rx_ms);
    double q_dtim_sleep_uc = trx->i_light_sleep_ma * (t_dtim_s * 1000.0 - (t_guard_ms + t_beacon_rx_ms));
    double i_background_ma = (q_beacon_uc + q_dtim_sleep_uc) / (t_dtim_s * 1000.0);

    /* TX подія: 15 мс активності при 220 мА */
    double q_tx_event_uc = 15.0 * 220.0;
    double q_total_uc = (i_background_ma * interval_s * 1000.0) + q_tx_event_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

SimResult sim_wifi6_twt(const BatterySpec *bat, const TransceiverSpec *trx, double interval_s) {
    /* TWT SP: 10мс RX (70мА) + 5мс TX (220мА) */
    double q_sp_uc = 10.0 * 70.0 + 5.0 * 220.0;
    double t_active_s = 15.0 / 1000.0;
    double t_sleep_s = (interval_s > t_active_s) ? (interval_s - t_active_s) : 0.0;
    double q_sleep_uc = (trx->i_deep_sleep_ua / 1000.0) * (t_sleep_s * 1000.0);
    double q_total_uc = q_sp_uc + q_sleep_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

int main(void) {
    BatterySpec aa_lithium = { 3.0, 2400.0, 1.0, 0.85 };
    TransceiverSpec esp32 = { 10.0, 1.2, 20.0, 75.0, 240.0, 1.5, 50.0 };
    double interval_s = 600.0; /* Відправка даних раз на 10 хвилин */

    SimResult r_cold = sim_cold_boot(&aa_lithium, &esp32, interval_s);
    SimResult r_fast = sim_fast_reconnect(&aa_lithium, &esp32, interval_s);
    SimResult r_dtim = sim_dtim_light_sleep(&aa_lithium, &esp32, 3, interval_s);
    SimResult r_twt  = sim_wifi6_twt(&aa_lithium, &esp32, interval_s);

    printf("Стратегія 1 (Cold Boot):       I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_cold.i_avg_ua, r_cold.life_days, r_cold.life_years);
    printf("Стратегія 2 (Fast Reconnect):   I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_fast.i_avg_ua, r_fast.life_days, r_fast.life_years);
    printf("Стратегія 3 (Light DTIM-3):    I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_dtim.i_avg_ua, r_dtim.life_days, r_dtim.life_years);
    printf("Стратегія 4 (Wi-Fi 6 TWT):     I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_twt.i_avg_ua,  r_twt.life_days,  r_twt.life_years);

    return 0;
}
