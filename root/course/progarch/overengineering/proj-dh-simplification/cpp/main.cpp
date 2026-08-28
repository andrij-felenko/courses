// ============================================================================
// ВАРІАНТ B (Прагматичний): Модульний моноліт на C++20
// Одне транзакційне коло: агрегація + перевірка правил + Outbox усередині БД
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <optional>
#include <expected>
#include <memory>
#include <chrono>

struct TelemetryMetric {
    std::string device_id;
    std::string home_id;
    double energy_kwh;
    double temperature_c;
    int64_t timestamp;
};

struct AggregateResult {
    std::string home_id;
    double total_energy_kwh;
    double avg_temperature_c;
    bool threshold_exceeded;
};

// Модель Outbox-події для транзакційного збереження
struct OutboxEvent {
    std::string aggregate_type;
    std::string aggregate_id;
    std::string event_type;
    std::string payload_json;
};

// Чіткий доменний сервіс без мережевого оверхеду
class HomeAnalyticsAggregator {
public:
    enum class Error { DatabaseError, InvalidMetrics };

    // Транзакційна обробка: обчислення й формування сповіщення в єдиній сесії
    std::expected<AggregateResult, Error> process_hourly_batch(
        const std::string& home_id,
        const std::vector<TelemetryMetric>& metrics,
        double max_energy_threshold) 
    {
        if (metrics.empty()) {
            return std::unexpected(Error::InvalidMetrics);
        }

        double total_energy = 0.0;
        double temp_sum = 0.0;

        for (const auto& m : metrics) {
            total_energy += m.energy_kwh;
            temp_sum += m.temperature_c;
        }

        double avg_temp = temp_sum / static_cast<double>(metrics.size());
        bool alert_needed = (total_energy > max_energy_threshold);

        // Симуляція атомарної БД-транзакції:
        // db.transaction([&](auto& tx) {
        //     tx.execute("INSERT INTO hourly_aggregates ...", home_id, total_energy, avg_temp);
        //     if (alert_needed) {
        //         tx.execute("INSERT INTO outbox_events ...", "HomeAggregate", home_id, "HIGH_ENERGY_ALERT");
        //     }
        // });

        return AggregateResult{
            .home_id = home_id,
            .total_energy_kwh = total_energy,
            .avg_temperature_c = avg_temp,
            .threshold_exceeded = alert_needed
        };
    }
};

int main() {
    HomeAnalyticsAggregator aggregator;
    std::vector<TelemetryMetric> sample = {
        {"dev-1", "home-42", 1.8, 21.5, 1700000000},
        {"dev-2", "home-42", 2.1, 22.1, 1700000060}
    };

    auto res = aggregator.process_hourly_batch("home-42", sample, 3.0);
    if (res) {
        std::cout << "[Оптимум] Успішно обчислено для дому " << res->home_id 
                  << ": сумарна енергія = " << res->total_energy_kwh 
                  << " кВт·год, поріг перевищено = " << (res->threshold_exceeded ? "ТАК" : "НІ") 
                  << "\n";
    }
    return 0;
}
