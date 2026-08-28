#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <algorithm>
#include <cstdint>

enum class EntryType {
    Data,
    Tombstone
};

struct StorageRecord {
    int64_t id;
    int64_t timestamp;
    EntryType type;
    std::string key;
    std::string value;
};

class StorageTable {
public:
    void append(int64_t id, std::string_view key, std::string_view value, int64_t ts, EntryType type) {
        records_.push_back({id, ts, type, std::string(key), std::string(value)});
    }

    [[nodiscard]] size_t size() const noexcept { return records_.size(); }
    [[nodiscard]] const std::vector<StorageRecord>& records() const noexcept { return records_; }

    // 1. Keyset Batch Purge: ітеративне видалення застарілих надгробків (Erase-Remove Idiom)
    size_t purge_batch(int64_t cutoff_ts, int64_t& cursor_id, size_t limit) {
        size_t purged_count = 0;

        auto it = std::remove_if(records_.begin(), records_.end(), [&](const StorageRecord& r) {
            if (r.id > cursor_id && r.type == EntryType::Tombstone && r.timestamp < cutoff_ts && purged_count < limit) {
                cursor_id = r.id;
                ++purged_count;
                return true; // Фізично видаляємо з пам'яті
            }
            return false;
        });

        records_.erase(it, records_.end());
        return purged_count;
    }

    // 2. LSM Tombstone Compaction: злиття рівнів з урахуванням часу життя надгробка
    static StorageTable compact_levels(const StorageTable& level_new, 
                                       const StorageTable& level_old, 
                                       int64_t current_ts, 
                                       int64_t gc_grace_seconds = 864000) {
        StorageTable merged;
        size_t i = 0, j = 0;
        const auto& recs_new = level_new.records();
        const auto& recs_old = level_old.records();

        while (i < recs_new.size() || j < recs_old.size()) {
            if (i < recs_new.size() && j < recs_old.size()) {
                if (recs_new[i].key == recs_old[j].key) {
                    // Конфлікт ключів: новіший запис поглинає старий
                    if (recs_new[i].type == EntryType::Tombstone) {
                        // Якщо надгробок ще захищений grace period, зберігаємо його
                        if (current_ts - recs_new[i].timestamp < gc_grace_seconds) {
                            merged.append(recs_new[i].id, recs_new[i].key, "", recs_new[i].timestamp, EntryType::Tombstone);
                        }
                    } else {
                        merged.append(recs_new[i].id, recs_new[i].key, recs_new[i].value, recs_new[i].timestamp, EntryType::Data);
                    }
                    ++i;
                    ++j; // Старий запис повністю відкинуто
                } else if (recs_new[i].key < recs_old[j].key) {
                    merged.append(recs_new[i].id, recs_new[i].key, recs_new[i].value, recs_new[i].timestamp, recs_new[i].type);
                    ++i;
                } else {
                    merged.append(recs_old[j].id, recs_old[j].key, recs_old[j].value, recs_old[j].timestamp, recs_old[j].type);
                    ++j;
                }
            } else if (i < recs_new.size()) {
                merged.append(recs_new[i].id, recs_new[i].key, recs_new[i].value, recs_new[i].timestamp, recs_new[i].type);
                ++i;
            } else {
                merged.append(recs_old[j].id, recs_old[j].key, recs_old[j].value, recs_old[j].timestamp, recs_old[j].type);
                ++j;
            }
        }
        return merged;
    }

private:
    std::vector<StorageRecord> records_;
};

int main() {
    StorageTable db;
    db.append(1, "user:1", "Alice", 100, EntryType::Data);
    db.append(2, "user:2", "Bob", 200, EntryType::Tombstone);
    db.append(3, "user:3", "Charlie", 300, EntryType::Data);
    db.append(4, "user:4", "David", 250, EntryType::Tombstone);

    int64_t cursor = 0;
    const int64_t cutoff = 500;
    size_t batch = 0;

    std::cout << "Початок батчевого очищення таблиці...\n";
    while (true) {
        size_t deleted = db.purge_batch(cutoff, cursor, 2);
        if (deleted == 0) break;
        ++batch;
        std::cout << "Батч #" << batch << ": успішно видалено " << deleted 
                  << " записів. Курсор id=" << cursor << "\n";
    }

    std::cout << "Залишилося живих записів у таблиці: " << db.size() << "\n";
    return 0;
}
