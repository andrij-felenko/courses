#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <span>
#include <sstream>
#include <iomanip>

// Структура сирого вхідного запису
struct RawRecord {
    std::string user_id;
    std::string email;          // Чутливі персональні дані (PII)
    std::string category;
    double amount;
    int64_t timestamp_ms;
};

// Структура очищеного агрегованого результату для вітрини
struct CategoryMetric {
    std::string category;
    double total_amount{0.0};
    uint64_t transaction_count{0};
};

// Імітатор криптографічного хешування для маскування PII (FNV-1a 64-bit)
std::string mask_pii(std::string_view pii) {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : pii) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 1099511628211ULL;
    }
    std::stringstream ss;
    ss << "anon_" << std::hex << std::setw(16) << std::setfill('0') << hash;
    return ss.str();
}

// ── 1. РЕЖИМ ETL: Трансформація в пам'яті конвеєра перед завантаженням ────────
class EtlPipelineEngine {
public:
    // Видобування -> Трансформація в оперативній пам'яті -> Завантаження вітрини
    std::vector<CategoryMetric> process_batch_etl(std::span<const RawRecord> batch) {
        std::unordered_map<std::string, CategoryMetric> in_memory_aggregation;

        for (const auto& record : batch) {
            // Валідація некоректних даних
            if (record.amount <= 0.0 || record.category.empty()) {
                continue;
            }

            // Маскування PII в пам'яті воркера (сирі дані не виходять за межі контуру)
            std::string masked_user = mask_pii(record.email);

            // Агрегація метрик на льоту
            auto& metric = in_memory_aggregation[record.category];
            metric.category = record.category;
            metric.total_amount += record.amount;
            metric.transaction_count += 1;
        }

        // Формування компактного результату для завантаження в аналітичну базу
        std::vector<CategoryMetric> destination_mart;
        destination_mart.reserve(in_memory_aggregation.size());
        for (auto& [cat, metric] : in_memory_aggregation) {
            destination_mart.push_back(std::move(metric));
        }

        return destination_mart;
    }
};

// ── 2. РЕЖИМ ELT: Скидання сирих даних та Push-Down трансформація ────────────
class MockWarehouseStorage {
public:
    // Сире сховище (Bronze Staging Layer)
    std::vector<RawRecord> raw_staging_table;

    // Пряме неблокуюче завантаження сирих даних
    void bulk_insert_raw(std::span<const RawRecord> batch) {
        raw_staging_table.insert(raw_staging_table.end(), batch.begin(), batch.end());
    }

    // Декларативна SQL-трансформація всередині рушія сховища (Push-Down)
    // Еквівалент: SELECT category, SUM(amount), COUNT(*) FROM raw_staging WHERE amount > 0 GROUP BY category
    std::vector<CategoryMetric> execute_pushdown_transform() {
        std::unordered_map<std::string, CategoryMetric> storage_engine_group_by;

        for (const auto& row : raw_staging_table) {
            if (row.amount > 0.0 && !row.category.empty()) {
                auto& m = storage_engine_group_by[row.category];
                m.category = row.category;
                m.total_amount += row.amount;
                m.transaction_count += 1;
            }
        }

        std::vector<CategoryMetric> gold_mart;
        gold_mart.reserve(storage_engine_group_by.size());
        for (auto& [cat, m] : storage_engine_group_by) {
            gold_mart.push_back(std::move(m));
        }
        return gold_mart;
    }
};

int main() {
    // Вхідний батч подій
    std::vector<RawRecord> incoming_events = {
        {"usr_1", "alice@example.com", "electronics", 1200.50, 1724180000000},
        {"usr_2", "bob@example.com", "books", 45.00, 1724180001000},
        {"usr_3", "charlie@example.com", "electronics", 350.00, 1724180002000},
        {"usr_4", "invalid@example.com", "books", -10.00, 1724180003000}, // Битий запис
        {"usr_5", "david@example.com", "home", 89.90, 1724180004000}
    };

    std::cout << "=== 1. Виконання конвеєра в режимі ETL ===\n";
    EtlPipelineEngine etl_engine;
    auto etl_result = etl_engine.process_batch_etl(incoming_events);
    for (const auto& row : etl_result) {
        std::cout << "Категорія: " << row.category 
                  << " | Сума: " << row.total_amount 
                  << " | Кількість: " << row.transaction_count << "\n";
    }

    std::cout << "\n=== 2. Виконання конвеєра в режимі ELT ===\n";
    MockWarehouseStorage warehouse;
    // Крок 1: Швидке скидання сирих рядків у Bronze Staging
    warehouse.bulk_insert_raw(incoming_events);
    std::cout << "Завантажено сирих рядків у Staging: " << warehouse.raw_staging_table.size() << "\n";

    // Крок 2: Push-down SQL-агрегація в шар Gold
    auto elt_result = warehouse.execute_pushdown_transform();
    for (const auto& row : elt_result) {
        std::cout << "Категорія: " << row.category 
                  << " | Сума: " << row.total_amount 
                  << " | Кількість: " << row.transaction_count << "\n";
    }

    return 0;
}
