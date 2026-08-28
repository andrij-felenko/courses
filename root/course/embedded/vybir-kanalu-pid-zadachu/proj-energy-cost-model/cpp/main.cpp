#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <iomanip>
#include <cmath>

struct RadioProfile {
    std::string_view name;
    float prep_time_s;       // Час підготовки до передачі (с)
    float prep_current_ma;   // Струм підготовки (мА)
    float tx_power_ma;       // Струм випромінювача (мА)
    float tx_speed_kbps;     // Ефективна швидкість каналу (кбіт/с)
    float header_bytes;      // Службові заголовки протоколу (байти)
    float rx_time_s;         // Час очікування підтвердження / RX (с)
    float rx_current_ma;     // Струм приймача під час RX (мА)
    float post_time_s;       // Час переходу в сон (с)
    float post_current_ma;   // Струм переходу в сон (мА)
    float sleep_current_ua;  // Струм глибокого сну радіомодуля (мкА)
};

struct PowerSource {
    float battery_capacity_mah;  // Номінальна ємність джерела живлення
    float self_discharge_pct_yr; // Річний саморозряд батареї (%)
    float derating_factor;       // Температурний/імпульсний коефіцієнт (0.7-0.9)
    float system_sleep_ua;       // Фоновий струм MCU та датчиків у сні (мкА)
};

struct EnergyResult {
    float cycle_charge_mas{0.0f};   // Заряд однієї передачі (мА*с)
    float avg_current_ua{0.0f};     // Середній струм споживання (мкА)
    float battery_life_years{0.0f}; // Очікуваний термін роботи (років)
    float airtime_ms{0.0f};         // Чистий час у ефірі (мс)
};

class EnergyBudgetCalculator {
public:
    [[nodiscard]] static constexpr EnergyResult evaluate(
        const RadioProfile& prof,
        const PowerSource& pwr,
        uint32_t payload_bytes,
        uint32_t interval_seconds) noexcept {
        if (interval_seconds == 0) {
            return {};
        }

        const float total_bytes = static_cast<float>(payload_bytes) + prof.header_bytes;
        const float bits = total_bytes * 8.0f;
        const float tx_time_s = (prof.tx_speed_kbps > 0.0f)
                                ? (bits / (prof.tx_speed_kbps * 1000.0f))
                                : 0.001f;

        // Обчислення заряду за фазами транзакції (мА * с)
        const float q_prep = prof.prep_current_ma * prof.prep_time_s;
        const float q_tx   = prof.tx_power_ma * tx_time_s;
        const float q_rx   = prof.rx_current_ma * prof.rx_time_s;
        const float q_post = prof.post_current_ma * prof.post_time_s;
        const float q_cycle_mas = q_prep + q_tx + q_rx + q_post;

        // Струми у сні та середній струм системи
        const float total_sleep_ua = prof.sleep_current_ua + pwr.system_sleep_ua;
        const float cycle_avg_ma = q_cycle_mas / static_cast<float>(interval_seconds);
        const float avg_current_ua = (cycle_avg_ma * 1000.0f) + total_sleep_ua;

        // Розрахунок впливу саморозряду батареї
        constexpr float hours_in_year = 365.25f * 24.0f;
        const float self_discharge_ma = (pwr.battery_capacity_mah * (pwr.self_discharge_pct_yr / 100.0f))
                                        / hours_in_year;
        const float self_discharge_ua = self_discharge_ma * 1000.0f;

        const float effective_capacity_mah = pwr.battery_capacity_mah * pwr.derating_factor;
        const float total_drain_ua = avg_current_ua + self_discharge_ua;

        const float life_hours = (total_drain_ua > 0.0f)
                                 ? (effective_capacity_mah * 1000.0f / total_drain_ua)
                                 : 0.0f;
        const float life_years = life_hours / hours_in_year;

        return {
            .cycle_charge_mas = q_cycle_mas,
            .avg_current_ua = avg_current_ua,
            .battery_life_years = life_years,
            .airtime_ms = tx_time_s * 1000.0f
        };
    }
};

int main() {
    constexpr std::array profiles{
        RadioProfile{
            .name = "BLE 5.0 (2 Mbps)",
            .prep_time_s = 0.0015f, .prep_current_ma = 4.0f,
            .tx_power_ma = 12.0f,   .tx_speed_kbps = 1400.0f,
            .header_bytes = 14.0f,
            .rx_time_s = 0.0010f,   .rx_current_ma = 8.0f,
            .post_time_s = 0.0005f, .post_current_ma = 2.0f,
            .sleep_current_ua = 1.2f
        },
        RadioProfile{
            .name = "LoRaWAN EU868 (SF7, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 5.47f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.0600f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        RadioProfile{
            .name = "LoRaWAN EU868 (SF12, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 0.29f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.3500f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        RadioProfile{
            .name = "NB-IoT (PSM Mode, 23 dBm)",
            .prep_time_s = 0.2500f, .prep_current_ma = 25.0f,
            .tx_power_ma = 180.0f,  .tx_speed_kbps = 32.0f,
            .header_bytes = 48.0f,
            .rx_time_s = 0.8000f,   .rx_current_ma = 40.0f,
            .post_time_s = 0.0500f, .post_current_ma = 15.0f,
            .sleep_current_ua = 3.5f
        },
        RadioProfile{
            .name = "LTE Cat-1 (Active / Disconnect)",
            .prep_time_s = 2.5000f, .prep_current_ma = 80.0f,
            .tx_power_ma = 260.0f,  .tx_speed_kbps = 1000.0f,
            .header_bytes = 90.0f,
            .rx_time_s = 1.5000f,   .rx_current_ma = 65.0f,
            .post_time_s = 0.3000f, .post_current_ma = 40.0f,
            .sleep_current_ua = 15.0f
        }
    };

    constexpr PowerSource battery{
        .battery_capacity_mah = 2600.0f,
        .self_discharge_pct_yr = 1.0f,
        .derating_factor = 0.85f,
        .system_sleep_ua = 2.0f
    };

    constexpr uint32_t payload_len = 24;
    constexpr uint32_t send_period = 3600;

    std::cout << std::fixed << std::setprecision(2);
    for (const auto& prof : profiles) {
        const auto res = EnergyBudgetCalculator::evaluate(prof, battery, payload_len, send_period);
        std::cout << "[" << prof.name << "]\n";
        std::cout << "  Час у ефірі: " << res.airtime_ms << " мс\n";
        std::cout << "  Заряд сеансу: " << std::setprecision(3) << res.cycle_charge_mas << " мА*с\n";
        std::cout << "  Середній струм: " << std::setprecision(2) << res.avg_current_ua << " мкА\n";
        std::cout << "  Автономність: " << res.battery_life_years << " років\n\n";
    }

    return 0;
}
