#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    const char *name;
    float prep_time_s;       /* Час підготовки до передачі (с) */
    float prep_current_ma;   /* Струм підготовки (мА) */
    float tx_power_ma;       /* Струм випромінювача (мА) */
    float tx_speed_kbps;     /* Ефективна швидкість каналу (кбіт/с) */
    float header_bytes;      /* Службові заголовки протоколу (байти) */
    float rx_time_s;         /* Час очікування підтвердження / RX (с) */
    float rx_current_ma;     /* Струм приймача під час RX (мА) */
    float post_time_s;       /* Час переходу в сон (с) */
    float post_current_ma;   /* Струм переходу в сон (мА) */
    float sleep_current_ua;  /* Струм глибокого сну радіомодуля (мкА) */
} RadioProfile;

typedef struct {
    float battery_capacity_mah;  /* Номінальна ємність джерела живлення */
    float self_discharge_pct_yr; /* Річний саморозряд батареї (%) */
    float derating_factor;       /* Температурний/імпульсний коефіцієнт (0.7-0.9) */
    float system_sleep_ua;       /* Фоновий струм MCU та датчиків у сні (мкА) */
} PowerSource;

typedef struct {
    float cycle_charge_mas;      /* Заряд однієї передачі (мА*с) */
    float avg_current_ua;        /* Середній струм споживання (мкА) */
    float battery_life_years;    /* Очікуваний термін роботи (років) */
    float airtime_ms;            /* Чистий час у ефірі (мс) */
} EnergyResult;

bool evaluate_energy_profile(const RadioProfile *prof,
                             const PowerSource *pwr,
                             uint32_t payload_bytes,
                             uint32_t interval_seconds,
                             EnergyResult *out_res) {
    if (!prof || !pwr || !out_res || interval_seconds == 0) {
        return false;
    }

    float total_bytes = (float)payload_bytes + prof->header_bytes;
    float bits = total_bytes * 8.0f;
    float tx_time_s = (prof->tx_speed_kbps > 0.0f) 
                      ? (bits / (prof->tx_speed_kbps * 1000.0f)) 
                      : 0.001f;

    /* Обчислення заряду за фазами (мА * с) */
    float q_prep = prof->prep_current_ma * prof->prep_time_s;
    float q_tx   = prof->tx_power_ma * tx_time_s;
    float q_rx   = prof->rx_current_ma * prof->rx_time_s;
    float q_post = prof->post_current_ma * prof->post_time_s;
    float q_cycle_mas = q_prep + q_tx + q_rx + q_post;

    /* Струми у сні та середній струм */
    float total_sleep_ua = prof->sleep_current_ua + pwr->system_sleep_ua;
    float cycle_avg_ma = q_cycle_mas / (float)interval_seconds;
    float avg_current_ua = (cycle_avg_ma * 1000.0f) + total_sleep_ua;

    /* Врахування саморозряду батареї */
    float hours_in_year = 365.25f * 24.0f;
    float self_discharge_ma = (pwr->battery_capacity_mah * (pwr->self_discharge_pct_yr / 100.0f)) 
                              / hours_in_year;
    float self_discharge_ua = self_discharge_ma * 1000.0f;

    float effective_capacity_mah = pwr->battery_capacity_mah * pwr->derating_factor;
    float total_drain_ua = avg_current_ua + self_discharge_ua;

    float life_hours = (total_drain_ua > 0.0f) 
                       ? (effective_capacity_mah * 1000.0f / total_drain_ua) 
                       : 0.0f;
    float life_years = life_hours / hours_in_year;

    out_res->cycle_charge_mas   = q_cycle_mas;
    out_res->avg_current_ua     = avg_current_ua;
    out_res->battery_life_years = life_years;
    out_res->airtime_ms         = tx_time_s * 1000.0f;

    return true;
}

int main(void) {
    /* Базові профілі трансиверів для телеметрії */
    const RadioProfile profiles[] = {
        {
            .name = "BLE 5.0 (2 Mbps)",
            .prep_time_s = 0.0015f, .prep_current_ma = 4.0f,
            .tx_power_ma = 12.0f,   .tx_speed_kbps = 1400.0f,
            .header_bytes = 14.0f,
            .rx_time_s = 0.0010f,   .rx_current_ma = 8.0f,
            .post_time_s = 0.0005f, .post_current_ma = 2.0f,
            .sleep_current_ua = 1.2f
        },
        {
            .name = "LoRaWAN EU868 (SF7, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 5.47f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.0600f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        {
            .name = "LoRaWAN EU868 (SF12, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 0.29f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.3500f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        {
            .name = "NB-IoT (PSM Mode, 23 dBm)",
            .prep_time_s = 0.2500f, .prep_current_ma = 25.0f,
            .tx_power_ma = 180.0f,  .tx_speed_kbps = 32.0f,
            .header_bytes = 48.0f,
            .rx_time_s = 0.8000f,   .rx_current_ma = 40.0f,
            .post_time_s = 0.0500f, .post_current_ma = 15.0f,
            .sleep_current_ua = 3.5f
        },
        {
            .name = "LTE Cat-1 (Active / Disconnect)",
            .prep_time_s = 2.5000f, .prep_current_ma = 80.0f,
            .tx_power_ma = 260.0f,  .tx_speed_kbps = 1000.0f,
            .header_bytes = 90.0f,
            .rx_time_s = 1.5000f,   .rx_current_ma = 65.0f,
            .post_time_s = 0.3000f, .post_current_ma = 40.0f,
            .sleep_current_ua = 15.0f
        }
    };

    /* Літієва батарея Li-SOCl2 типорозміру AA (3.6 В, 2600 мА*год) */
    const PowerSource battery = {
        .battery_capacity_mah = 2600.0f,
        .self_discharge_pct_yr = 1.0f,
        .derating_factor = 0.85f,
        .system_sleep_ua = 2.0f
    };

    const uint32_t payload_len = 24;            /* 24 байти показів давачів */
    const uint32_t send_period = 3600;          /* 1 раз на годину */

    size_t count = sizeof(profiles) / sizeof(profiles[0]);
    for (size_t i = 0; i < count; ++i) {
        EnergyResult res;
        if (evaluate_energy_profile(&profiles[i], &battery, payload_len, send_period, &res)) {
            printf("[%s]\n", profiles[i].name);
            printf("  Час у ефірі: %.1f мс\n", res.airtime_ms);
            printf("  Заряд сеансу: %.3f мА*с\n", res.cycle_charge_mas);
            printf("  Середній струм: %.2f мкА\n", res.avg_current_ua);
            printf("  Автономність: %.2f років\n\n", res.battery_life_years);
        }
    }

    return 0;
}
