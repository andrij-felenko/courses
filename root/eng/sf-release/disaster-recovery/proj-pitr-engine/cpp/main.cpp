#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <expected>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <array>

namespace storage::dr {

constexpr uint32_t WAL_MAGIC_V1 = 0x57414C31; // "WAL1"

enum class OperationType : uint8_t {
    InsertOrUpdate = 1,
    Delete = 2,
    Truncate = 3
};

enum class RecoveryError {
    FileNotFound,
    InvalidMagic,
    CorruptedPayloadSize,
    ChecksumMismatch,
    PrematureEndOfFile
};

#pragma pack(push, 1)
struct WalRecordHeader {
    uint32_t magic{WAL_MAGIC_V1};
    uint64_t lsn{0};
    uint64_t timestamp_ms{0};
    OperationType op_type{OperationType::InsertOrUpdate};
    uint32_t payload_len{0};
    uint32_t crc32{0};
};

struct WalPayloadData {
    char key[32]{};
    char value[64]{};
};
#pragma pack(pop)

/* ── Швидке обчислення CRC32 ─────────────────────────────────────────────── */
class Crc32 {
public:
    static uint32_t calculate(const uint8_t* data, size_t length) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (size_t i = 0; i < length; ++i) {
            crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
        }
        return crc ^ 0xFFFFFFFF;
    }

private:
    static constexpr auto generate_table() {
        std::array<uint32_t, 256> tbl{};
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t c = i;
            for (int j = 0; j < 8; ++j) {
                c = (c & 1) ? (0xEDB88320L ^ (c >> 1)) : (c >> 1);
            }
            tbl[i] = c;
        }
        return tbl;
    }
    static inline constexpr auto table = generate_table();
};

/* ── База даних у пам'яті з підтримкою знімків ───────────────────────────── */
class InMemoryStore {
public:
    void put(std::string_view key, std::string_view val) {
        store_[std::string(key)] = std::string(val);
    }

    void erase(std::string_view key) {
        store_.erase(std::string(key));
    }

    void truncate() noexcept {
        store_.clear();
    }

    void set_metadata(uint64_t lsn, uint64_t ts) noexcept {
        last_lsn_ = lsn;
        last_ts_ = ts;
    }

    void dump() const {
        std::cout << "=== СТАН БАЗИ ДАНИХ (LSN: " << last_lsn_ << ") ===
";
        for (const auto& [k, v] : store_) {
            std::cout << "  [" << k << "] => "" << v << ""
";
        }
        std::cout << "========================================
";
    }

private:
    std::unordered_map<std::string, std::string> store_;
    uint64_t last_lsn_{0};
    uint64_t last_ts_{0};
};

/* ── Рушій відновлення Point-in-Time Recovery ────────────────────────────── */
class PitrCoordinator {
public:
    static std::expected<size_t, RecoveryError> replay_wal_segment(
        InMemoryStore& db,
        const std::string& wal_path,
        std::chrono::milliseconds target_stop_time) 
    {
        std::ifstream file(wal_path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(RecoveryError::FileNotFound);
        }

        size_t records_applied = 0;
        const auto target_ts = static_cast<uint64_t>(target_stop_time.count());

        while (file.peek() != EOF) {
            WalRecordHeader header;
            if (!file.read(reinterpret_cast<char*>(&header), sizeof(WalRecordHeader))) {
                break;
            }

            if (header.magic != WAL_MAGIC_V1) {
                return std::unexpected(RecoveryError::InvalidMagic);
            }

            if (header.payload_len != sizeof(WalPayloadData)) {
                return std::unexpected(RecoveryError::CorruptedPayloadSize);
            }

            WalPayloadData payload;
            if (!file.read(reinterpret_cast<char*>(&payload), sizeof(WalPayloadData))) {
                return std::unexpected(RecoveryError::PrematureEndOfFile);
            }

            // Перевірка контрольної суми
            const auto computed_crc = Crc32::calculate(
                reinterpret_cast<const uint8_t*>(&payload), sizeof(WalPayloadData));
            
            if (computed_crc != header.crc32) {
                return std::unexpected(RecoveryError::ChecksumMismatch);
            }

            // Критерій зупинки PITR
            if (header.timestamp_ms > target_ts) {
                std::cout << ">> [PITR C++] Досягнуто часової точки зупинки: " 
                          << header.timestamp_ms << " ms > Target: " << target_ts 
                          << " ms. Зупинка REDO.
";
                break;
            }

            // Застосування операції
            switch (header.op_type) {
                case OperationType::InsertOrUpdate:
                    db.put(payload.key, payload.value);
                    break;
                case OperationType::Delete:
                    db.erase(payload.key);
                    break;
                case OperationType::Truncate:
                    db.truncate();
                    break;
            }

            db.set_metadata(header.lsn, header.timestamp_ms);
            ++records_applied;
        }

        return records_applied;
    }
};

} // namespace storage::dr

int main() {
    using namespace storage::dr;
    using namespace std::chrono_literals;

    std::cout << "=== ДЕМОНСТРАЦІЯ РУШІЯ POINT-IN-TIME RECOVERY (C++) ===
";

    InMemoryStore db;
    // 1. Початковий стан із базового знімка (02:00:00 UTC)
    db.put("user:101", "Alice (Account: 500)");
    db.put("user:102", "Bob (Account: 1200)");
    db.set_metadata(1000, 100000);
    db.dump();

    // 2. Створення двійкового сегмента WAL
    const std::string wal_file = "test_wal_cpp.bin";
    {
        std::ofstream out(wal_file, std::ios::binary);
        
        auto write_rec = [&](uint64_t lsn, uint64_t ts, OperationType op, 
                             const char* k, const char* v) {
            WalRecordHeader h;
            h.lsn = lsn;
            h.timestamp_ms = ts;
            h.op_type = op;
            h.payload_len = sizeof(WalPayloadData);
            
            WalPayloadData p{};
            std::strncpy(p.key, k, sizeof(p.key) - 1);
            std::strncpy(p.value, v, sizeof(p.value) - 1);
            
            h.crc32 = Crc32::calculate(reinterpret_cast<const uint8_t*>(&p), sizeof(WalPayloadData));
            
            out.write(reinterpret_cast<const char*>(&h), sizeof(h));
            out.write(reinterpret_cast<const char*>(&p), sizeof(p));
        };

        // Транзакція 1: Оновлення Alice (150000 ms)
        write_rec(1001, 150000, OperationType::InsertOrUpdate, "user:101", "Alice (Account: 750)");
        // Транзакція 2: Додавання Charlie (154000 ms)
        write_rec(1002, 154000, OperationType::InsertOrUpdate, "user:103", "Charlie (Account: 300)");
        // Транзакція 3: Руйнівний TRUNCATE (156000 ms)
        write_rec(1003, 156000, OperationType::Truncate, "*", "ALL");
    }

    // 3. Відновлення до точки 155000 ms (до моменту виконання TRUNCATE)
    const auto target_time = 155000ms;
    std::cout << "[PITR] Запуск відновлення до мітки " << target_time.count() << " ms...
";

    auto result = PitrCoordinator::replay_wal_segment(db, wal_file, target_time);
    if (result.has_value()) {
        std::cout << "Успішно відтворено операцій: " << result.value() << "
";
        db.dump();
    } else {
        std::cerr << "Помилка відновлення!
";
    }

    std::remove(wal_file.c_str());
    return 0;
}
