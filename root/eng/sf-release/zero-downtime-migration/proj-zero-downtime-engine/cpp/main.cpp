#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <cstdint>
#include <memory>
#include <expected>
#include <span>

namespace migration {

struct Record {
    int64_t id{0};
    std::string email;
    std::chrono::milliseconds updated_at{0};
    uint32_t checksum{0};
};

struct MigrationStats {
    int64_t last_processed_id{0};
    int64_t total_migrated{0};
    int64_t total_skipped_due_to_race{0};
    int64_t checksum_mismatches{0};
};

class MigrationEngine {
public:
    static constexpr size_t kBatchSize = 1000;
    static constexpr auto kMaxAllowedLag = std::chrono::milliseconds(1500);
    static constexpr auto kDefaultSleep = std::chrono::milliseconds(10);

    MigrationEngine() = default;

    std::expected<MigrationStats, std::string> run() {
        std::vector<Record> batch_buffer;
        batch_buffer.reserve(kBatchSize);

        std::cout << "=== СТАРТ ФОНОВОГО РУШІЯ МІГРАЦІЇ (C++) ===\n";

        while (true) {
            const auto current_lag = measure_replication_lag();
            if (current_lag > kMaxAllowedLag) {
                std::cout << "[ДРОСЕЛЮВАННЯ] Лаг " << current_lag.count() 
                          << " мс перевищує ліміт. Пауза...\n";
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
                continue;
            }

            batch_buffer.clear();
            fetch_source_batch(stats_.last_processed_id, batch_buffer, kBatchSize);

            if (batch_buffer.empty()) {
                std::cout << "Усі історичні дані успішно оброблено.\n";
                break;
            }

            if (!apply_conditional_upsert(batch_buffer)) {
                return std::unexpected("Критична помилка застосування пачки до цільової БД");
            }

            stats_.last_processed_id = batch_buffer.back().id;
            std::cout << "[ПРОГРЕС] Оброблено до ID: " << stats_.last_processed_id
                      << " | Успішно: " << stats_.total_migrated
                      << " | Пропущено через гонку: " << stats_.total_skipped_due_to_race << "\n";

            std::this_thread::sleep_for(kDefaultSleep);
        }

        return stats_;
    }

private:
    MigrationStats stats_;

    static uint32_t compute_crc(const Record& r) noexcept {
        uint32_t hash = 5381;
        for (const char ch : r.email) {
            hash = ((hash << 5) + hash) + static_cast<uint8_t>(ch);
        }
        hash = ((hash << 5) + hash) + static_cast<uint32_t>(r.updated_at.count() & 0xFFFFFFFF);
        return hash;
    }

    std::chrono::milliseconds measure_replication_lag() const noexcept {
        return std::chrono::milliseconds(120);
    }

    void fetch_source_batch(int64_t after_id, std::vector<Record>& out, size_t limit) const {
        for (size_t i = 0; i < limit && (after_id + static_cast<int64_t>(i) + 1) <= 5000; ++i) {
            Record r;
            r.id = after_id + static_cast<int64_t>(i) + 1;
            r.email = "user_" + std::to_string(r.id) + "@company.ua";
            r.updated_at = std::chrono::milliseconds(1700000000000LL + r.id * 10);
            r.checksum = compute_crc(r);
            out.push_back(std::move(r));
        }
    }

    bool apply_conditional_upsert(std::span<const Record> batch) noexcept {
        for (const auto& record : batch) {
            const auto target_updated_at = (record.id % 250 == 0)
                ? (record.updated_at + std::chrono::milliseconds(5000))
                : std::chrono::milliseconds(0);

            if (target_updated_at > record.updated_at) {
                stats_.total_skipped_due_to_race++;
            } else {
                stats_.total_migrated++;
            }

            if (compute_crc(record) != record.checksum) {
                stats_.checksum_mismatches++;
            }
        }
        return true;
    }
};

} // namespace migration

int main() {
    migration::MigrationEngine engine;
    auto result = engine.run();

    if (!result) {
        std::cerr << "Помилка міграції: " << result.error() << "\n";
        return 1;
    }

    const auto& stats = *result;
    std::cout << "=== ПІДСУМОК МІГРАЦІЇ ===\n"
              << "Всього перенесено рядків: " << stats.total_migrated << "\n"
              << "Захищено свіжих мутацій: " << stats.total_skipped_due_to_race << "\n"
              << "Розходжень хешів: " << stats.checksum_mismatches << "\n";

    return 0;
}
