#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <unordered_map>
#include <algorithm>

// Структура сирої незмінної події
struct RawEvent {
    std::string event_id;
    std::string user_id;
    int64_t amount_cents{0};
    std::string event_time; // ISO8601 UTC
};

// Структура історичного тарифу (SCD Type 2)
struct TariffRecord {
    std::string user_id;
    int discount_percent{0};
    std::string valid_from;
    std::string valid_to;
};

// Підсумковий агрегат для партиції
struct AggregatedMetric {
    std::string partition_date;
    std::string user_id;
    int64_t raw_total_cents{0};
    int64_t discounted_total_cents{0};
    int32_t events_count{0};
    std::string checksum_hash;
};

class IdempotentBackfillWorker {
public:
    // Пошук діючого тарифу на момент настання події (Point-in-Time AS-OF Join)
    static int find_as_of_discount(
        std::string_view user_id, 
        std::string_view event_time, 
        const std::vector<TariffRecord>& tariffs
    ) noexcept {
        for (const auto& t : tariffs) {
            if (t.user_id == user_id && event_time >= t.valid_from && event_time < t.valid_to) {
                return t.discount_percent;
            }
        }
        return 0; // Базовий тариф за замовчуванням
    }

    // Детермінована обробка чанка в пам'яті
    static std::vector<AggregatedMetric> compute_partition(
        std::string_view partition_date,
        std::string_view window_start,
        std::string_view window_end,
        const std::vector<RawEvent>& raw_stream,
        const std::vector<TariffRecord>& tariffs
    ) {
        std::unordered_map<std::string, AggregatedMetric> accumulator;

        for (const auto& ev : raw_stream) {
            // Сувора фільтрація за замкненим часовим вікном події
            if (ev.event_time < window_start || ev.event_time >= window_end) {
                continue;
            }

            int discount = find_as_of_discount(ev.user_id, ev.event_time, tariffs);
            int64_t discounted_amt = ev.amount_cents * (100 - discount) / 100;

            auto& entry = accumulator[ev.user_id];
            entry.partition_date = std::string(partition_date);
            entry.user_id = ev.user_id;
            entry.raw_total_cents += ev.amount_cents;
            entry.discounted_total_cents += discounted_amt;
            entry.events_count += 1;
        }

        std::vector<AggregatedMetric> result;
        result.reserve(accumulator.size());

        // Перевірка інваріантів якості даних (Data Quality Gate)
        for (auto& [uid, metric] : accumulator) {
            if (metric.discounted_total_cents > metric.raw_total_cents) {
                throw std::runtime_error("Аномалія: знижка більша за базову суму для користувача: " + uid);
            }
            if (metric.raw_total_cents < 0) {
                throw std::runtime_error("Аномалія: від'ємна виручка для користувача: " + uid);
            }
            result.push_back(std::move(metric));
        }

        return result;
    }
};

int main() {
    try {
        std::vector<TariffRecord> tariffs = {
            {"user_1", 10, "2026-08-01T00:00:00Z", "2026-08-15T00:00:00Z"},
            {"user_1", 20, "2026-08-15T00:00:00Z", "2026-09-01T00:00:00Z"}
        };

        std::vector<RawEvent> events = {
            {"e1", "user_1", 10000, "2026-08-10T12:00:00Z"}, // Потрапляє під знижку 10%
            {"e2", "user_1", 20000, "2026-08-20T15:30:00Z"}  // Потрапляє під знижку 20%
        };

        auto chunk_results = IdempotentBackfillWorker::compute_partition(
            "2026-08-10", "2026-08-10T00:00:00Z", "2026-08-11T00:00:00Z", events, tariffs
        );

        for (const auto& r : chunk_results) {
            std::cout << "Партиція: " << r.partition_date 
                      << " | Користувач: " << r.user_id
                      << " | Сире: " << r.raw_total_cents
                      << " | Зі знижкою: " << r.discounted_total_cents 
                      << " | Подій: " << r.events_count << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка бекфілу: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
